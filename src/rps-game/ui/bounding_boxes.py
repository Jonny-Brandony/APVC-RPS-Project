"""
Bounding box drawing module.
Handles drawing of detection boxes with lock state visualization.
"""
import cv2
import time
from config import CLASS_NAMES, CLASS_COLORS, BOX_COLOR, TEXT_FONT, THUMB_UP
from detection.hand_tracking import get_pending_hand_lock_state, get_lock_progress
from game_state import GamePhase, GameState


def get_lock_progress_for_track(track_id, class_name, game_state):
    """
    Get lock progress percentage for a tracked detection.
    Handles both detection and game phases uniformly.
    
    Args:
        track_id: Tracking ID of the detection
        class_name: Detected class name
        game_state: Current game state object
    
    Returns:
        float: Progress percentage (0.0 to 100.0)
    """
    if game_state.phase == GamePhase.DETECTION:
        if track_id in game_state.pending_hands:
            return get_lock_progress(track_id, game_state)
        return 100.0  # Not tracking, show 100%

    elif game_state.phase == GamePhase.GAME:
        # Check if this track_id belongs to a player and is currently locking
        if game_state.p1.id == track_id:
            if game_state.p1.locked == class_name and game_state.p1.lock_start_time:
                elapsed = time.time() - game_state.p1.lock_start_time
                progress = min(100, (elapsed / game_state.lock_duration) * 100)
                return progress
        elif game_state.p2.id == track_id:
            if game_state.p2.locked == class_name and game_state.p2.lock_start_time:
                elapsed = time.time() - game_state.p2.lock_start_time
                progress = min(100, (elapsed / game_state.lock_duration) * 100)
                return progress
        return 100.0  # Not locking, show 100%
    
    return 100.0


def draw_progress_bar(img, x, y, progress_percent, bar_length=12, 
                       font_scale=0.4, color=(255, 255, 255)):
    """
    Draw a progress bar with block characters at specified position.
    
    Args:
        img: Image to draw on
        x: X coordinate for progress bar
        y: Y coordinate for progress bar
        progress_percent: Progress percentage (0-100)
        bar_length: Number of block characters (default: 12)
        font_scale: Font scale for text (default: 0.4)
        color: Text color (BGR tuple, default: white)
    
    Returns:
        Modified image
    """
    # Calculate how many blocks should be filled
    filled_blocks = int((progress_percent / 100) * bar_length)
    
    # Build progress bar string
    progress_bar = ""
    for i in range(bar_length):
        if i < filled_blocks:
            progress_bar += "-"  # Filled portion
        else:
            progress_bar += "_"  # Unfilled portion
    
    # Draw the progress bar text
    font = cv2.FONT_HERSHEY_SIMPLEX
    thickness = 1
    
    cv2.putText(img, progress_bar, (int(x), int(y)), font, font_scale, color, thickness)
    
    return img


def draw_lock_progress_bar(img, x1, y2, progress_percent):
    """
    Draw a progress bar with block characters below the bounding box.
    
    Args:
        img: Image to draw on
        x1: Left x coordinate of bounding box
        y2: Bottom y coordinate of bounding box
        progress_percent: Progress percentage (0-100)
    
    Returns:
        Modified image
    """
    bar_y = int(y2) + 8
    bar_x = int(x1)
    return draw_progress_bar(img, bar_x, bar_y, progress_percent)


def get_box_color_and_thickness(track_id, class_name, game_state):
    """
    Determine box color and thickness based on phase and lock state.
    
    Args:
        track_id: Tracking ID of the detection
        class_name: Detected class name
        game_state: Current game state object
    
    Returns:
        tuple: (color, thickness)
    """
    color = CLASS_COLORS.get(class_name, BOX_COLOR)
    thickness = 1
    
    if game_state.phase == 'detection' and track_id in game_state.pending_hands:
        lock_state = get_pending_hand_lock_state(track_id, game_state)
        if lock_state == 'locking':
            color = (0, 255, 255)  # Yellow for locking
            thickness = 3
        elif lock_state == 'locked_ok':
            color = (0, 255, 0)  # Green for locked OK
            thickness = 4
        elif lock_state == 'locked_invalid':
            color = (0, 0, 255)  # Red for locked but not OK
            thickness = 2
        else:
            color = (128, 128, 128)  # Gray for no lock
            thickness = 1
    
    return color, thickness


def build_detection_label(class_name, conf, track_id, game_state: GameState):
    """
    Build label text for a detection box.
    
    Args:
        class_name: Detected class name
        conf: Confidence score
        track_id: Tracking ID
        game_state: Current game state object
    
    Returns:
        str: Label text
    """
    label = f"{class_name} {conf:.2f}"
    
    if track_id is not None:
        if game_state.p1.id == track_id:
            return f"P1 {label}"
        elif game_state.p2.id == track_id:
            return f"P2 {label}"
        else:
            return f"ID:{track_id} {label}"
    return label


def draw_custom_bounding_boxes(img, result, game_state : GameState, box_padding):
    """
    Draw custom bounding boxes with lock state visualization.
    
    Args:
        img: Image to draw on
        result: YOLO result object
        game_state: Current game state object
        box_padding: Padding to add to bounding boxes (pixels)
    
    Returns:
        Modified image
    """
    if not result or not result.boxes:
        return img
    
    for box in result.boxes:
        # Adjust bounding box if padding is set
        xyxy = box.xyxy[0].cpu().numpy().copy()
        if box_padding > 0:
            xyxy[0] = max(0, xyxy[0] - box_padding)  # x1
            xyxy[1] = max(0, xyxy[1] - box_padding)  # y1
            xyxy[2] = min(img.shape[1], xyxy[2] + box_padding)  # x2
            xyxy[3] = min(img.shape[0], xyxy[3] + box_padding)  # y2
        
        x1, y1, x2, y2 = xyxy
        conf = box.conf[0].cpu().numpy()
        class_id = int(box.cls[0].cpu().numpy())
        class_name = CLASS_NAMES[class_id]
        
        track_id = None
        if hasattr(box, 'id') and box.id is not None:
            track_id = int(box.id[0].cpu().numpy())
        

       #if game_state.phase == GamePhase.GAME and game_state.p1.id != track_id and game_state.p2.id != track_id:
       #    continue  # Skip drawing boxes not belonging to players

        # Get color and thickness
        color, thickness = get_box_color_and_thickness(track_id, class_name, game_state)
        
        # Draw box
        cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), color, thickness)
        
        # Build label
        label = build_detection_label(class_name, conf, track_id, game_state)
        # Draw label
        cv2.putText(img, label, (int(x1), int(y1) - 10),TEXT_FONT, 0.5, color, 1)
        
        # Draw unified lock progress bar (always shown, 100% if not locking)
        if track_id is not None:
            progress = get_lock_progress_for_track(track_id, class_name, game_state)
            draw_lock_progress_bar(img, x1, y2, progress)
            if track_id == game_state.p1.id:
                cv2.putText(img, f"SCORE {game_state.p1.score}", (int(x1), int(y2) - 10),  TEXT_FONT, 0.5, color, 1)
            if track_id == game_state.p2.id:
                cv2.putText(img, f"SCORE {game_state.p2.score}", (int(x1), int(y2) - 10),  TEXT_FONT, 0.5, color, 1)
    
    return img

