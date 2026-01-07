"""
Game state management module.
Handles initialization and reset of game state.
"""
import time
from config import log


def create_initial_state():
    """Create a new game state dictionary with default values."""
    return {
        'game_start_time': time.time(),
        'lock_duration': 2.0,
        'round_result': "",
        'game_active': False,
        'phase': 'detection',  # 'detection' or 'game'
        'players': {
            'p1': {
                'id': None,
                'sign': None,
                'last_seen': None,
                'ready': False,
                'score': 0,
                'locked': None,
                'lock_start_time': None
            },
            'p2': {
                'id': None,
                'sign': None,
                'last_seen': None,
                'ready': False,
                'score': 0,
                'locked': None,
                'lock_start_time': None
            }
        },
        'pending_hands': {},  # Temporary tracking for unassigned hands
        'ready_duration': 2.0,  # Time to hold OK to lock
        'disconnect_timeout': 120.0  # 2 minutes
    }


def reset_game_state(game_state):
    """Reset the game state to initial values."""
    game_state['game_start_time'] = time.time()
    game_state['lock_duration'] = 2.0
    game_state['round_result'] = ""
    game_state['game_active'] = False
    game_state['phase'] = 'detection'
    
    # Reset players
    for player_key in ['p1', 'p2']:
        game_state['players'][player_key].update({
            'id': None,
            'sign': None,
            'last_seen': None,
            'ready': False,
            'score': 0,
            'locked': None,
            'lock_start_time': None
        })
    
    game_state['pending_hands'] = {}
    game_state['ready_duration'] = 2.0
    game_state['disconnect_timeout'] = 120.0


def start_game(game_state):
    """Start the game phase and reset scores."""
    game_state['game_active'] = True
    game_state['game_start_time'] = time.time()
    game_state['players']['p1']['score'] = 0
    game_state['players']['p2']['score'] = 0
    game_state['players']['p1']['locked'] = None
    game_state['players']['p2']['locked'] = None
    game_state['players']['p1']['lock_start_time'] = None
    game_state['players']['p2']['lock_start_time'] = None
    game_state['round_result'] = ""

