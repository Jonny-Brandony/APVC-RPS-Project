"""
Hand tracking module for detection phase.
Handles pending hand tracking, locking, and player assignment.
"""
import time
from config import log, OK


def get_pending_hand_lock_state(track_id, game_state):
    """
    Determine the lock state of a pending hand.
    
    Args:
        track_id: Tracking ID of the hand
        game_state: Current game state object
    
    Returns:
        str: Lock state ('none', 'locking', 'locked_ok', 'locked_invalid')
    """
    if track_id not in game_state.pending_hands:
        return 'none'
    
    hand = game_state.pending_hands[track_id]
    sign = hand['sign']
    locked_sign = hand['locked']
    
    if locked_sign is None or sign != locked_sign:
        return 'none'
    
    if sign == OK:
        if hand['lock_start_time'] is not None:
            elapsed = time.time() - hand['lock_start_time']
            if elapsed >= game_state.lock_duration:
                return 'locked_ok'
            return 'locking'
        return 'locking'
    
    return 'locked_invalid'


def get_lock_progress(track_id, game_state):
    """
    Get lock progress as percentage (0-100).
    
    Args:
        track_id: Tracking ID of the hand
        game_state: Current game state object
    
    Returns:
        float: Progress percentage (0.0 to 100.0)
    """
    if track_id not in game_state.pending_hands:
        return 0.0
    
    hand = game_state.pending_hands[track_id]
    if hand['lock_start_time'] is None:
        return 0.0
    
    elapsed = time.time() - hand['lock_start_time']
    progress = min(100, (elapsed / game_state.lock_duration) * 100)
    return progress


def update_pending_hand_lock(hand_data, current_sign, current_time, game_state):
    """
    Update lock state for a pending hand.
    
    Args:
        hand_data: Dictionary containing hand tracking data
        current_sign: Currently detected sign
        current_time: Current timestamp
        game_state: Current game state object
    """
    locked_sign = hand_data['locked']
    
    if current_sign == locked_sign and locked_sign is not None:
        # Continue locking
        if hand_data['lock_start_time'] is None:
            hand_data['lock_start_time'] = current_time
    else:
        # Sign changed, reset lock
        hand_data['locked'] = current_sign
        hand_data['lock_start_time'] = None


def update_assigned_players(signs_by_id, game_state):
    """
    Update assigned players with current detections.
    
    Args:
        signs_by_id: Dictionary mapping track_id -> sign
        game_state: Current game state object
    """
    players = game_state.players
    current_time = time.time()
    
    for player_key, player_data in players.items():
        if player_data.id is not None and player_data.id in signs_by_id:
            player_data.last_seen = current_time
            player_data.sign = signs_by_id[player_data.id]
        elif player_data.id is not None:
            # Check for disconnection
            if current_time - player_data.last_seen > game_state.disconnect_timeout:
                log.info(f"{player_key} disconnected during detection.")
                player_data.id = None
                player_data.sign = None


def update_pending_hands(signs_by_id, game_state):
    """
    Update pending hands tracking and remove disconnected ones.
    
    Args:
        signs_by_id: Dictionary mapping track_id -> sign
        game_state: Current game state object
    """
    pending_hands = game_state.pending_hands
    current_time = time.time()
    hands_to_remove = []
    
    for track_id, hand_data in pending_hands.items():
        if track_id in signs_by_id:
            hand_data['last_seen'] = current_time
            hand_data['sign'] = signs_by_id[track_id]
            update_pending_hand_lock(hand_data, signs_by_id[track_id], current_time, game_state)
        else:
            # Hand not detected, check for timeout
            if current_time - hand_data['last_seen'] > game_state.disconnect_timeout:
                hands_to_remove.append(track_id)
    
    # Remove disconnected hands
    for track_id in hands_to_remove:
        del pending_hands[track_id]


def add_new_detections(signs_by_id, game_state):
    """
    Add new detections to pending hands.
    
    Args:
        signs_by_id: Dictionary mapping track_id -> sign
        game_state: Current game state object
    """
    players = game_state.players
    pending_hands = game_state.pending_hands
    current_time = time.time()
    
    assigned_ids = [p.id for p in players.values() if p.id is not None]
    
    for track_id, sign in signs_by_id.items():
        if track_id not in assigned_ids and track_id not in pending_hands:
            pending_hands[track_id] = {
                'sign': sign,
                'locked': None,
                'lock_start_time': None,
                'last_seen': current_time
            }
            log.info(f"Tracking new hand: ID {track_id}")


def assign_players_from_locked_hands(game_state):
    """
    Assign IDs from locked OK hands to available player slots.
    
    Args:
        game_state: Current game state object
    """
    players = game_state.players
    pending_hands = game_state.pending_hands
    current_time = time.time()
    
    available_slots = [k for k, v in players.items() if v.id is None]
    locked_ok_hands = [
        (track_id, hand) for track_id, hand in pending_hands.items()
        if get_pending_hand_lock_state(track_id, game_state) == 'locked_ok'
    ]
    
    for track_id, hand_data in locked_ok_hands:
        if available_slots:
            slot = available_slots.pop(0)
            player = players[slot]
            player.id = track_id
            player.sign = hand_data['sign']
            player.last_seen = current_time
            player.ready = True
            del pending_hands[track_id]
            log.info(f"Assigned {slot} to ID {track_id} (locked with OK)")


def check_transition_to_game(game_state):
    """
    Check if both players are assigned and transition to game phase.
    
    Args:
        game_state: Current game state object
    """
    players = game_state.players
    
    if all(p.id is not None for p in players.values()):
        game_state.phase = 'game'
        game_state.pending_hands = {}
        log.info("Both players assigned. Starting game phase.")
        game_state.start_game()


def update_player_detection(signs_by_id, game_state):
    """
    Handle detection phase with per-hand locking and ID assignment on OK lock.
    
    Args:
        signs_by_id: Dictionary mapping track_id -> sign
        game_state: Current game state object
    """
    update_assigned_players(signs_by_id, game_state)
    update_pending_hands(signs_by_id, game_state)
    add_new_detections(signs_by_id, game_state)
    assign_players_from_locked_hands(game_state)
    check_transition_to_game(game_state)

