"""
Game phase management module.
Handles game phase logic including locking and round processing.
"""
import time
from config import log, STOP, PLAYABLE_SIGNS
from game_state import reset_game_state
from game.rules import get_rps_winner


def check_and_lock(current_p1, current_p2, game_state):
    """
    Check if both players have locked their gestures.
    
    Args:
        current_p1: Current sign for player 1
        current_p2: Current sign for player 2
        game_state: Current game state dictionary
    
    Returns:
        bool: True if both players have locked for the required duration
    """
    players = game_state['players']
    
    if current_p1 == players['p1']['locked'] and \
       current_p2 == players['p2']['locked'] and \
       current_p1 is not None and current_p2 is not None:
        if players['p1']['lock_start_time'] is None:
            players['p1']['lock_start_time'] = time.time()
            players['p2']['lock_start_time'] = time.time()
            log.info(f"Positions locked: P1={current_p1}, P2={current_p2}")
        
        elapsed = time.time() - players['p1']['lock_start_time']
        if elapsed >= game_state['lock_duration']:
            return True
    else:
        # Reset lock if signs changed
        players['p1']['locked'] = current_p1
        players['p2']['locked'] = current_p2
        players['p1']['lock_start_time'] = None
        players['p2']['lock_start_time'] = None
    
    return False


def update_player_signs(signs_by_id, game_state):
    """
    Update player signs and check for disconnections.
    
    Args:
        signs_by_id: Dictionary mapping track_id -> sign
        game_state: Current game state dictionary
    
    Returns:
        tuple: (current_p1_sign, current_p2_sign) or (None, None) if disconnected
    """
    players = game_state['players']
    current_time = time.time()
    current_p1 = None
    current_p2 = None
    
    for player_key, player_data in players.items():
        if player_data['id'] is not None and player_data['id'] in signs_by_id:
            player_data['last_seen'] = current_time
            sign = signs_by_id[player_data['id']]
            if player_key == 'p1':
                current_p1 = sign
            else:
                current_p2 = sign
        elif player_data['id'] is not None:
            # Check disconnection
            if current_time - player_data['last_seen'] > game_state['disconnect_timeout']:
                log.info(f"{player_key} disconnected. Returning to detection phase.")
                reset_game_state(game_state)
                return None, None
    
    return current_p1, current_p2


def process_locked_round(game_state):
    """
    Process a locked round: determine winner and update scores.
    
    Args:
        game_state: Current game state dictionary
    """
    players = game_state['players']
    locked_p1 = players['p1']['locked']
    locked_p2 = players['p2']['locked']
    
    if locked_p1 == STOP and locked_p2 == STOP:
        reset_game_state(game_state)
        log.info("Game stopped by both players showing STOP.")
    elif locked_p1 in PLAYABLE_SIGNS and locked_p2 in PLAYABLE_SIGNS:
        winner = get_rps_winner(locked_p1, locked_p2)
        if winner == 'Player 1 Wins':
            players['p1']['score'] += 1
        elif winner == 'Player 2 Wins':
            players['p2']['score'] += 1
        game_state['round_result'] = f"{locked_p1} vs {locked_p2} - {winner}"
        log.info(f"Round result: {winner}")


def reset_locks(game_state):
    """
    Reset player locks after processing a round.
    
    Args:
        game_state: Current game state dictionary
    """
    players = game_state['players']
    players['p1']['locked'] = None
    players['p2']['locked'] = None
    players['p1']['lock_start_time'] = None
    players['p2']['lock_start_time'] = None


def update_game_phase(signs_by_id, game_state):
    """
    Handle game phase logic: update signs, check locks, process rounds.
    
    Args:
        signs_by_id: Dictionary mapping track_id -> sign
        game_state: Current game state dictionary
    """
    current_p1, current_p2 = update_player_signs(signs_by_id, game_state)
    
    if current_p1 is None or current_p2 is None:
        return  # Disconnection occurred
    
    locked = check_and_lock(current_p1, current_p2, game_state)
    
    if locked:
        if game_state['game_active']:
            process_locked_round(game_state)
        reset_locks(game_state)
    
    log.debug(f"Current Game State: {game_state}")

