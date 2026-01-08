"""
Main entry point for the RPS game.
Handles the main game loop and coordinates all modules.
"""
import cv2
from config import log, WINDOW_NAME
from game_state import GamePhase, GameState
from detection.yolo_handler import initialize_model_and_capture, process_detections
from detection.hand_tracking import update_player_detection
from game.phases import update_game_phase
from game.player_timeout import PlayerTimeoutManager
from ui.bounding_boxes import draw_custom_bounding_boxes
from ui.hud import draw_hud
from ui.display import resize_to_window


def handle_keyboard_input(key, game_state, timeout_manager):
    """
    Handle keyboard input and perform corresponding actions.
    
    Args:
        key: Key code from cv2.waitKey()
        game_state: Current game state object
        timeout_manager: PlayerTimeoutManager instance
    
    Returns:
        bool: True if the application should continue, False if it should quit
    """
    key_char = key & 0xFF
    
    if key_char == ord('q'):
        log.info("Quit key pressed. Exiting application.")
        return False
    elif key_char == ord('r'):
        log.info("Reset key pressed. Resetting game state.")
        game_state.reset_game_state()
        timeout_manager.reset()
    elif key_char == ord('h'):
        log.info("Help key pressed. Toggling help UI.")
        game_state.help_ui_visible = not game_state.help_ui_visible

    return True


def main():
    """Main game loop."""
    # Initialize model and capture
    model, w, h = initialize_model_and_capture()
    game_state = GameState()
    timeout_manager = PlayerTimeoutManager()
    
    # Configuration
    box_padding = 0  # Adjust this to change bounding box size (pixels to expand)
    
    # Open webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        log.error("Failed to open webcam for tracking.")
        return
    
    log.info("Starting tracking loop with manual frame capture.")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                log.warning("Failed to read frame from webcam.")
                break
            
            # Run YOLO tracking
            results = model.track(frame, persist=True, verbose=False)
            img = frame.copy()
            
            # Process each result
            for result in results:
                # Draw bounding boxes
                img = draw_custom_bounding_boxes(img, result, game_state, box_padding)
                
                # Process detections
                signs_by_id = process_detections(result, img.shape[1])
                
                # Update game state based on phase
                if game_state.phase == GamePhase.DETECTION:
                    update_player_detection(signs_by_id, game_state)
                else:
                    update_game_phase(signs_by_id, game_state, timeout_manager)
                
                # Draw HUD
                img = draw_hud(img, game_state, timeout_manager)
                
                # Display image
                display_img = resize_to_window(img, WINDOW_NAME, w, h)
                cv2.imshow(WINDOW_NAME, display_img)
                
                # Handle keyboard input
                key = cv2.waitKey(1)
                if key != -1:  # Only process if a key was pressed
                    if not handle_keyboard_input(key, game_state, timeout_manager):
                        return
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        log.info("Tracking loop ended.")


if __name__ == "__main__":
    main()

