"""
Game state management module.
Handles initialization and reset of game state.
"""
import enum
import time
from config import log

class GamePhase(enum.Enum):
    DETECTION = 'detection'
    GAME = 'game'

class GameState():
    """Class to manage the state of the RPS game."""

    def __init__(self):
        self.game_start_time = time.time()
        self.lock_duration = 2.0
        self.round_result = ""
        self.game_active = False
        self.phase = GamePhase.DETECTION  # 'detection' or 'game'
        self.pending_hands = {}  # Temporary tracking for unassigned hands
        self.ready_duration = 2.0  # Time to hold OK to lock
        self.disconnect_timeout = 120.0  # 2 minutes
        self.help_ui_visible = False
        self.p1 = Player()
        self.p2 = Player()
        
        log.debug("Initialized new game state.")
    def __str__(self):
        return f"GameState(game_start_time={self.game_start_time}, lock_duration={self.lock_duration}, round_result={self.round_result}, game_active={self.game_active}, phase={self.phase}, pending_hands={self.pending_hands}, ready_duration={self.ready_duration}, disconnect_timeout={self.disconnect_timeout}, p1={self.p1}, p2={self.p2})"
    def __repr__(self):
        return self.__str__()

    @property
    def players(self):
        """Return a dict-like interface for players for backward compatibility."""
        return {'p1': self.p1, 'p2': self.p2}

    def reset_game_state(self):
        """Reset the game state to initial values."""
        log.debug("Resetting game state.")
        self.game_start_time = time.time()
        self.lock_duration = 5.0
        self.round_result = ""
        self.game_active = False
        self.phase = GamePhase.DETECTION

        # Reset players
        del self.p1
        del self.p2
        self.p1 = Player()
        self.p2 = Player()

        self.pending_hands = {}
        self.ready_duration = 2.0
        self.disconnect_timeout = 120.0

    def start_game(self):
        """Start the game phase and reset scores."""
        log.debug("Starting game.")
        self.game_active = True
        self.game_start_time = time.time()
        
        self.p1.score = 0
        self.p2.score = 0
        self.p1.locked = None
        self.p2.locked = None
        self.p1.lock_start_time = None
        self.p2.lock_start_time = None
        self.round_result = ""

    def reset_locks(self):
        """
        Reset player locks after processing a round.
        
        Args:
            game_state: Current game state object
        """
        self.p1.locked = None
        self.p2.locked = None
        self.p1.lock_start_time = None
        self.p2.lock_start_time = None

    def check_and_lock(self,current_p1, current_p2):
        """
        Check if both players have locked their gestures.
        
        Args:
            current_p1: Current sign for player 1
            current_p2: Current sign for player 2
            game_state: Current game state object
        
        Returns:
            bool: True if both players have locked for the required duration
        """
        p1 = self.p1
        p2 = self.p2

        if current_p1 == p1.locked and \
        current_p2 == p2.locked and \
        current_p1 is not None and current_p2 is not None:
            if p1.lock_start_time is None:
                p1.lock_start_time = time.time()
                p2.lock_start_time = time.time()
                log.info(f"Positions locked: P1={current_p1}, P2={current_p2}")
            
            elapsed = time.time() - p1.lock_start_time
            if elapsed >= self.lock_duration:
                return True
        else:
            # Reset lock if signs changed
            p1.locked = current_p1
            p2.locked = current_p2
            p1.lock_start_time = None
            p2.lock_start_time = None
        
        return False

class Player():
    """Class to represent a player in the RPS game."""

    def __init__(self):
        self.id = None
        self.sign = None
        self.last_seen = None
        self.ready = False
        self.score = 0
        self.locked = None
        self.lock_start_time = None
        log.debug("Initialized new Player.")
    
    def __str__(self):
        return f"Player(id={self.id}, sign={self.sign}, last_seen={self.last_seen}, ready={self.ready}, score={self.score}, locked={self.locked}, lock_start_time={self.lock_start_time})"
    def __repr__(self):
        return self.__str__()
