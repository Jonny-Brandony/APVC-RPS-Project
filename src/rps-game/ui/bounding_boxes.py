"""
Bounding box drawing module.
Handles drawing of detection boxes with lock state visualization.
"""
import cv2
import time
from config import CLASS_NAMES, CLASS_COLORS, BOX_COLOR, OK
from detection.hand_tracking import get_pending_hand_lock_state, get_lock_progress


def draw_lock_progress_bar(img, x1, y2, progress_percent):
    """
    Draw a progress bar below the bounding box.
    
    Args:
        img: Image to draw on
        x1: Left x coordinate of bounding box
        y2: Bottom y coordinate of bounding box
        progress_percent: Progress percentage (0-100)
    
    Returns:
        Modified image
    """
    bar_width = 100
    bar_height = 4
    bar_x = int(x1)
    bar_y = int(y2) + 2
    
    # Background (empty)
    cv2.rectangle(img, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height),
                  (100, 100, 100), -1)
    
    # Filled portion
    filled_width = int((progress_percent / 100) * bar_width)
    if filled_width > 0:
        cv2.rectangle(img, (bar_x, bar_y), (bar_x + filled_width, bar_y + bar_height),
                     (0, 255, 255), -1)
    
    return img


def get_box_color_and_thickness(track_id, class_name, game_state):
    """
    Determine box color and thickness based on phase and lock state.
    
    Args:
        track_id: Tracking ID of the detection
        class_name: Detected class name
        game_state: Current game state dictionary
    
    Returns:
        tuple: (color, thickness)
    """
    color = CLASS_COLORS.get(class_name, BOX_COLOR)
    thickness = 1
    
    if game_state['phase'] == 'detection' and track_id in game_state['pending_hands']:
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


def build_detection_label(class_name, conf, track_id, game_state):
    """
    Build label text for a detection box.
    
    Args:
        class_name: Detected class name
        conf: Confidence score
        track_id: Tracking ID
        game_state: Current game state dictionary
    
    Returns:
        str: Label text
    """
    label = f"{class_name} {conf:.2f}"
    
    if track_id is not None:
        label = f"ID:{track_id} {label}"
    
    # Add lock info for detection phase
    if game_state['phase'] == 'detection' and track_id in game_state['pending_hands']:
        lock_state = get_pending_hand_lock_state(track_id, game_state)
        progress = get_lock_progress(track_id, game_state)
        
        if lock_state == 'locking':
            remaining = max(0, game_state['lock_duration'] -
                          (progress / 100.0 * game_state['lock_duration']))
            label += f" Lock:{remaining:.1f}s ⏱"
        elif lock_state == 'locked_ok':
            label += " ✓ READY"
        elif lock_state == 'locked_invalid':
            label += f" ({game_state['pending_hands'][track_id]['sign']})"
    
    # Add lock info for game phase
    elif game_state['phase'] == 'game':
        players = game_state['players']
        for p_key, p_data in players.items():
            if p_data['id'] == track_id:
                locked_gesture = p_data['locked']
                if locked_gesture == class_name and p_data['lock_start_time']:
                    elapsed = time.time() - p_data['lock_start_time']
                    remaining = max(0, game_state['lock_duration'] - elapsed)
                    label += f" Lock:{remaining:.1f}s"
                break
    
    return label


def draw_custom_bounding_boxes(img, result, game_state, box_padding):
    """
    Draw custom bounding boxes with lock state visualization.
    
    Args:
        img: Image to draw on
        result: YOLO result object
        game_state: Current game state dictionary
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
        
        # Get color and thickness
        color, thickness = get_box_color_and_thickness(track_id, class_name, game_state)
        
        # Build label
        label = build_detection_label(class_name, conf, track_id, game_state)
        
        # Draw box
        cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), color, thickness)
        
        # Draw label
        cv2.putText(img, label, (int(x1), int(y1) - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        
        # Draw progress bar for locking hands
        if game_state['phase'] == 'detection' and track_id in game_state['pending_hands']:
            lock_state = get_pending_hand_lock_state(track_id, game_state)
            if lock_state in ['locking', 'locked_ok']:
                progress = get_lock_progress(track_id, game_state)
                draw_lock_progress_bar(img, x1, y2, progress)
    
    return img

