"""
Player timeout management module.
Handles timeout logic when both players become invisible during game phase.
"""
import time
from config import log


class PlayerTimeoutManager:
    """Manages timeout when both players are not visible."""
    
    TIMEOUT_DURATION = 60.0  # 1 minute in seconds
    WARNING_THRESHOLD = 5.0  # Show warning when 5 seconds remaining
    
    def __init__(self):
        """Initialize the timeout manager."""
        self.timeout_start_time = None
        self.warning_shown = False
        log.debug("Initialized PlayerTimeoutManager.")
    
    def update_visibility(self, p1_visible, p2_visible):
        """
        Update player visibility status and manage timeout.
        
        Args:
            p1_visible: True if player 1 is visible
            p2_visible: True if player 2 is visible
        
        Returns:
            bool: True if timeout has been reached and reset is needed
        """
        both_invisible = not p1_visible and not p2_visible
        
        if both_invisible:
            if self.timeout_start_time is None:
                self.timeout_start_time = time.time()
                self.warning_shown = False
                log.info("Both players invisible. Starting timeout timer.")
        else:
            # At least one player is visible, reset timer
            if self.timeout_start_time is not None:
                log.info("At least one player visible. Resetting timeout timer.")
                self.timeout_start_time = None
                self.warning_shown = False
        
        # Check if timeout has been reached
        if self.timeout_start_time is not None:
            elapsed = time.time() - self.timeout_start_time
            if elapsed >= self.TIMEOUT_DURATION:
                log.warning("Timeout reached. Game will be reset.")
                self.reset()
                return True
        
        return False
    
    def is_active(self):
        """
        Check if timeout timer is currently active.
        
        Returns:
            bool: True if timer is active
        """
        return self.timeout_start_time is not None
    
    def get_remaining_time(self):
        """
        Get remaining time until timeout.
        
        Returns:
            float: Remaining time in seconds, or 0 if timer not active
        """
        if self.timeout_start_time is None:
            return 0.0
        
        elapsed = time.time() - self.timeout_start_time
        remaining = max(0, self.TIMEOUT_DURATION - elapsed)
        return remaining
    
    def get_progress_percent(self):
        """
        Get timeout progress as percentage (0-100).
        
        Returns:
            float: Progress percentage (0.0 to 100.0)
        """
        if self.timeout_start_time is None:
            return 0.0
        
        elapsed = time.time() - self.timeout_start_time
        progress = min(100, (elapsed / self.TIMEOUT_DURATION) * 100)
        return progress
    
    def should_show_warning(self):
        """
        Check if warning should be shown.
        
        Returns:
            bool: True if warning should be displayed
        """
        if not self.is_active():
            return False
        
        remaining = self.get_remaining_time()
        return remaining <= self.WARNING_THRESHOLD
    
    def reset(self):
        """Reset the timeout manager to initial state."""
        self.timeout_start_time = None
        self.warning_shown = False
        log.debug("PlayerTimeoutManager reset.")

