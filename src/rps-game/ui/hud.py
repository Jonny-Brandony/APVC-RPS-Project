"""
HUD (Heads-Up Display) module.
Handles drawing of game information overlay.
"""
import time
import cv2
from config import (HEADING1_HEIGHT, HEADING2_HEIGHT, HEADING3_HEIGHT,
                   HEADING4_HEIGHT)
from ui.display import (display_info, display_centered_info,
                       display_bottom_info, display_bottom_centered_info)
from ui.bounding_boxes import draw_progress_bar
from game_state import GamePhase, GameState

def draw_help_ui(img, game_state: GameState):
    """
    Draw help UI overlay.
    
    Args:
        img: Image to draw on
    
    Returns:
        Modified image
    """
    if not game_state.help_ui_visible:
        return display_bottom_info(img, "Press 'H' for Help", (10, HEADING2_HEIGHT))
    
    h_img, w_img = img.shape[:2]
    help_texts = [
        "Press 'Q' to quit the game."
        "Press 'R' to restart the game."
    ]
    
    y_offset = HEADING2_HEIGHT
    for text in help_texts:
        img = display_bottom_info(img, text, (10, y_offset))
        y_offset += 30
    
    return img

def draw_detection_phase_hud(img, game_state):
    """
    Draw HUD for detection phase.
    
    Args:
        img: Image to draw on
        game_state: Current game state object
    
    Returns:
        Modified image
    """
    players = game_state.players
    pending_hands = game_state.pending_hands
    
    img = display_centered_info(img, "Player Detection Phase - Lock to Register",
                               HEADING1_HEIGHT)
    
    # Show assigned players
    y_offset = HEADING2_HEIGHT
   
    # Show pending hands
    y_offset += 10
    img = display_info(img, "Pending Hands:", (10, y_offset))
    y_offset += 30
    
    for track_id, hand_data in pending_hands.items():
        sign = hand_data['sign']
        status = f"ID:{track_id} - {sign}"
        img = display_info(img, status, (10, y_offset))
        y_offset += 25
    
    # Instructions
    img = display_bottom_centered_info(img, "Show OK and hold position to register", HEADING1_HEIGHT)
    
    return img


def draw_timeout_timer(img, timeout_manager):
    """
    Draw timeout timer in center bottom of screen.
    
    Args:
        img: Image to draw on
        timeout_manager: PlayerTimeoutManager instance
    
    Returns:
        Modified image
    """
    if not timeout_manager.is_active():
        return img
    
    h_img, w_img = img.shape[:2]
    remaining_time = timeout_manager.get_remaining_time()
    progress = timeout_manager.get_progress_percent()
    
    # Position: center bottom
    bar_length = 20
    bar_y = h_img - HEADING2_HEIGHT
    bar_x = (w_img - bar_length * 8) // 2  # Approximate width of progress bar
    
    # Draw progress bar
    img = draw_progress_bar(img, bar_x, bar_y, progress, bar_length=bar_length,
                            font_scale=0.5, color=(0, 0, 255))  # Red color for warning
    
    # Draw time remaining text
    time_text = f"Player not visible: {remaining_time:.1f}s"
    if timeout_manager.should_show_warning():
        time_text = f"WARNING: Resetting in {remaining_time:.1f}s"
    
    img = display_bottom_centered_info(img, time_text, HEADING1_HEIGHT)
    
    return img


def draw_game_phase_hud(img, game_state: GameState, timeout_manager):
    """
    Draw HUD for game phase.
    
    Args:
        img: Image to draw on
        game_state: Current game state object
        timeout_manager: PlayerTimeoutManager instance
    
    Returns:
        Modified image
    """
    h_img, w_img = img.shape[:2]
    p1 = game_state.p1
    p2 = game_state.p2
    
    if not game_state.game_active:
        img = display_centered_info(img, "Game Ready - Show OK to begin",
                                   HEADING1_HEIGHT)
    else:
        elapsed_time = int(time.time() - game_state.game_start_time)
        if p1.id is not None:
            img = display_info(img, f"Player 1 ID: {p1.id}: {p1.score}", (10, HEADING1_HEIGHT))
        if p2.id is not None:
            img = display_info(img, f"Player 2 ID: {p2.id}: {p2.score}", (10, HEADING3_HEIGHT))
        
        img = display_info(img, f"Time: {elapsed_time}s", (w_img//2 - 100, HEADING2_HEIGHT))
        
        # Display lock timer when players are locking
        if p1.lock_start_time is not None:
            elapsed = time.time() - p1.lock_start_time
            remaining = max(0, game_state.lock_duration - elapsed)
            img = display_centered_info(img, f"Round: {remaining:.1f}s", HEADING3_HEIGHT)
        
        if game_state.round_result:
            img = display_centered_info(img, game_state.round_result, HEADING4_HEIGHT)
    
    # Draw timeout timer if active
    img = draw_timeout_timer(img, timeout_manager)
    
    return img


def draw_hud(img, game_state, timeout_manager=None):
    """
    Draw the main HUD based on current game phase.
    
    Args:
        img: Image to draw on
        game_state: Current game state object
        timeout_manager: PlayerTimeoutManager instance (optional)
    
    Returns:
        Modified image
    """

    img = draw_help_ui(img, game_state)

    if game_state.phase == GamePhase.DETECTION:
        return draw_detection_phase_hud(img, game_state)
    else:
        return draw_game_phase_hud(img, game_state, timeout_manager)

