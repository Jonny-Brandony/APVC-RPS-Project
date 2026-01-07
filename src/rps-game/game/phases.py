"""
Game phase management module.
Handles game phase logic including locking and round processing.
"""
import time
from config import log, STOP, PLAYABLE_SIGNS
from game.rules import get_rps_winner
from game.player_timeout import PlayerTimeoutManager


def check_and_lock(current_p1, current_p2, game_state):
    """
    Check if both players have locked their gestures.
    
    Args:
        current_p1: Current sign for player 1
        current_p2: Current sign for player 2
        game_state: Current game state object
    
    Returns:
        bool: True if both players have locked for the required duration
    """
    p1 = game_state.p1
    p2 = game_state.p2
    
    if current_p1 == p1.locked and \
       current_p2 == p2.locked and \
       current_p1 is not None and current_p2 is not None:
        if p1.lock_start_time is None:
            p1.lock_start_time = time.time()
            p2.lock_start_time = time.time()
            log.info(f"Positions locked: P1={current_p1}, P2={current_p2}")
        
        elapsed = time.time() - p1.lock_start_time
        if elapsed >= game_state.lock_duration:
            return True
    else:
        # Reset lock if signs changed
        p1.locked = current_p1
        p2.locked = current_p2
        p1.lock_start_time = None
        p2.lock_start_time = None
    
    return False


def update_player_signs(signs_by_id, game_state):
    """
    Update player signs and check for disconnections.
    
    Args:
        signs_by_id: Dictionary mapping track_id -> sign
        game_state: Current game state object
    
    Returns:
        tuple: (current_p1_sign, current_p2_sign) or (None, None) if disconnected
    """
    p1 = game_state.p1
    p2 = game_state.p2
    current_time = time.time()
    current_p1 = None
    current_p2 = None
    
    if p1.id is not None and p1.id in signs_by_id:
        p1.last_seen = current_time
        current_p1 = signs_by_id[p1.id]
    elif p1.id is not None:
        # Check disconnection
        if current_time - p1.last_seen > game_state.disconnect_timeout:
            log.info("p1 disconnected. Returning to detection phase.")
            game_state.reset_game_state()
            return None, None
    
    if p2.id is not None and p2.id in signs_by_id:
        p2.last_seen = current_time
        current_p2 = signs_by_id[p2.id]
    elif p2.id is not None:
        # Check disconnection
        if current_time - p2.last_seen > game_state.disconnect_timeout:
            log.info("p2 disconnected. Returning to detection phase.")
            game_state.reset_game_state()
            return None, None
    
    return current_p1, current_p2


def process_locked_round(game_state):
    """
    Process a locked round: determine winner and update scores.
    
    Args:
        game_state: Current game state object
    """
    locked_p1 = game_state.p1.locked
    locked_p2 = game_state.p2.locked
    
    if locked_p1 == STOP and locked_p2 == STOP:
        game_state.reset_game_state()
        log.info("Game stopped by both players showing STOP.")
    elif locked_p1 in PLAYABLE_SIGNS and locked_p2 in PLAYABLE_SIGNS:
        winner = get_rps_winner(locked_p1, locked_p2)
        if winner == 'Player 1 Wins':
            game_state.p1.score += 1
        elif winner == 'Player 2 Wins':
            game_state.p2.score += 1
        game_state.round_result = f"{locked_p1} vs {locked_p2} - {winner}"
        log.info(f"Round result: {winner}")


def reset_locks(game_state):
    """
    Reset player locks after processing a round.
    
    Args:
        game_state: Current game state object
    """
    game_state.p1.locked = None
    game_state.p2.locked = None
    game_state.p1.lock_start_time = None
    game_state.p2.lock_start_time = None


def check_player_visibility(signs_by_id, game_state):
    """
    Check if players are visible in current detections.
    
    Args:
        signs_by_id: Dictionary mapping track_id -> sign
        game_state: Current game state object
    
    Returns:
        tuple: (p1_visible, p2_visible)
    """
    p1_visible = game_state.p1.id is not None and game_state.p1.id in signs_by_id
    p2_visible = game_state.p2.id is not None and game_state.p2.id in signs_by_id
    return p1_visible, p2_visible


def update_game_phase(signs_by_id, game_state, timeout_manager):
    """
    Handle game phase logic: update signs, check locks, process rounds.
    
    Args:
        signs_by_id: Dictionary mapping track_id -> sign
        game_state: Current game state object
        timeout_manager: PlayerTimeoutManager instance
    """
    # Check player visibility for timeout management
    p1_visible, p2_visible = check_player_visibility(signs_by_id, game_state)
    timeout_reached = timeout_manager.update_visibility(p1_visible, p2_visible)
    
    if timeout_reached:
        log.warning("Player timeout reached. Resetting game state.")
        game_state.reset_game_state()
        timeout_manager.reset()
        return
    
    current_p1, current_p2 = update_player_signs(signs_by_id, game_state)
    
    if current_p1 is None or current_p2 is None:
        return  # Disconnection occurred
    
    locked = check_and_lock(current_p1, current_p2, game_state)
    
    if locked:
        if game_state.game_active:
            process_locked_round(game_state)
        reset_locks(game_state)
    
    log.debug(f"Current Game State: {game_state}")

