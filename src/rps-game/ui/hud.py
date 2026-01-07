"""
HUD (Heads-Up Display) module.
Handles drawing of game information overlay.
"""
import time
from config import (HEADING1_HEIGHT, HEADING2_HEIGHT, HEADING3_HEIGHT,
                   HEADING4_HEIGHT)
from ui.display import (display_info, display_centered_info,
                       display_bottom_info, display_bottom_centered_info)


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
    img = display_info(img, "Assigned Players:", (10, y_offset))
    y_offset += 25
    
    for player_key, player_data in players.items():
        if player_data.id is not None:
            status = f"🟢 {player_key.upper()}: ID {player_data.id} - {player_data.sign} ✓"
            img = display_info(img, status, (10, y_offset))
        else:
            status = f"⏳ {player_key.upper()}: Waiting..."
            img = display_info(img, status, (10, y_offset))
        y_offset += 25
    
    # Show pending hands
    y_offset += 10
    img = display_info(img, "Pending Hands:", (10, y_offset))
    y_offset += 25
    
    for track_id, hand_data in pending_hands.items():
        sign = hand_data['sign']
        status = f"ID:{track_id} - {sign}"
        img = display_info(img, status, (10, y_offset))
        y_offset += 25
    
    # Instructions
    img = display_centered_info(img, "Show OK and hold position to register",
                               HEADING4_HEIGHT)
    
    return img


def draw_game_phase_hud(img, game_state):
    """
    Draw HUD for game phase.
    
    Args:
        img: Image to draw on
        game_state: Current game state object
    
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
        img = display_info(img, f"Player 1: {p1.score}",
                          (10, HEADING1_HEIGHT))
        img = display_info(img, f"Player 2: {p2.score}",
                          (w_img - 200, HEADING1_HEIGHT))
        
        img = display_info(img, f"Time: {elapsed_time}s",
                          (w_img//2 - 100, HEADING2_HEIGHT))
        
        img = display_info(img, "Player 1", (10, h_img - HEADING3_HEIGHT))
        img = display_info(img, "Player 2", (w_img - 150, h_img - HEADING3_HEIGHT))
        
        # Display player IDs
        if p1.id is not None:
            img = display_info(img, f"ID: {p1.id}",
                              (10, h_img - HEADING2_HEIGHT))
        if p2.id is not None:
            img = display_info(img, f"ID: {p2.id}",
                              (w_img - 150, h_img - HEADING2_HEIGHT))
        
        if game_state.round_result:
            img = display_centered_info(img, game_state.round_result,
                                       HEADING4_HEIGHT)
    
    return img


def draw_hud(img, game_state):
    """
    Draw the main HUD based on current game phase.
    
    Args:
        img: Image to draw on
        game_state: Current game state object
    
    Returns:
        Modified image
    """
    if game_state.phase == 'detection':
        return draw_detection_phase_hud(img, game_state)
    else:
        return draw_game_phase_hud(img, game_state)

