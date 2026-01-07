import cv2
import numpy as np
from ultralytics import YOLO
import time
import logging
import logging.config

config = {
    'version': 1,
    'formatters': {
        'detailed': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'detailed'
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'video-predict.log',
            'level': 'DEBUG',
            'formatter': 'detailed'
        }
    },
    'loggers': {
        'myapp': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True
        }
    }
}
logging.config.dictConfig(config)
log = logging.getLogger('myapp')


GUN = "Gun"
OK = "Ok"
PAPER = "Paper"
RESTART = "Restart"
ROCK = "Rock"
SCISSOR = "Scissor"
START = "Start"
STOP = "Stop"

# Class names from classes.txt (adjust indices if needed)
CLASS_NAMES = [GUN, OK, PAPER, RESTART,
               ROCK, SCISSOR, START, STOP]
PLAYABLE_SIGNS = [ROCK, PAPER, SCISSOR]
HEADING1_HEIGHT = 30
HEADING2_HEIGHT = 50
HEADING3_HEIGHT = 70
HEADING4_HEIGHT = 90
HEADING5_HEIGHT = 110
HEADING6_HEIGHT = 130

TEXT_THICKNESS = 1
TEXT_COLOR = (255, 255, 255)
BG_COLOR = (0, 0, 0)
BOX_COLOR = (40, 196, 212)

CLASS_COLORS = {
    ROCK: (0, 165, 255),    # Orange
    PAPER: (0, 255, 0),     # Green
    SCISSOR: (255, 0, 0),   # Blue
    OK: (0, 255, 255),      # Yellow
    GUN: (255, 0, 255),     # Magenta
    RESTART: (255, 255, 0), # Cyan
    START: (128, 128, 128), # Gray
    STOP: (0, 0, 255),      # Red
}


def draw_custom_bounding_boxes(img, result, game_state, box_padding):
    if result and result.boxes:
        for box in result.boxes:
            # Adjust bounding box if padding is set
            xyxy = box.xyxy[0]
            if box_padding > 0:
                xyxy[0] = max(0, xyxy[0] - box_padding)  # x1
                xyxy[1] = max(0, xyxy[1] - box_padding)  # y1
                xyxy[2] = min(img.shape[1], xyxy[2] + box_padding)  # x2
                xyxy[3] = min(img.shape[0], xyxy[3] + box_padding)  # y2
            x1, y1, x2, y2 = xyxy.cpu().numpy()
            conf = box.conf[0].cpu().numpy()
            class_id = int(box.cls[0].cpu().numpy())
            class_name = CLASS_NAMES[class_id]
            track_id = None
            if hasattr(box, 'id') and box.id is not None:
                track_id = int(box.id[0].cpu().numpy())
            
            # Determine box color and thickness based on phase and lock state
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
            
            # Build label
            label = f"{class_name} {conf:.2f}"
            if track_id is not None:
                label = f"ID:{track_id} {label}"
            
            # Add lock info for detection phase
            if game_state['phase'] == 'detection' and track_id in game_state['pending_hands']:
                lock_state = get_pending_hand_lock_state(track_id, game_state)
                progress = get_lock_progress(track_id, game_state)
                if lock_state == 'locking':
                    remaining = max(0, game_state['lock_duration'] - (progress / 100.0 * game_state['lock_duration']))
                    label += f" Lock:{remaining:.1f}s ⏱"
                elif lock_state == 'locked_ok':
                    label += " ✓ READY"
                elif lock_state == 'locked_invalid':
                    label += f" ({game_state['pending_hands'][track_id]['sign']})"
            # Add lock info for game phase
            elif game_state['phase'] == 'game':
                center_x = (x1 + x2) / 2
                player = None
                for p_key, p_data in game_state['players'].items():
                    if p_data['id'] == track_id:
                        player = 1 if p_key == 'p1' else 2
                        break
                if player:
                    locked_gesture = game_state['players'][f'p{player}']['locked']
                    if locked_gesture == class_name and game_state['players'][f'p{player}']['lock_start_time']:
                        elapsed = time.time() - game_state['players'][f'p{player}']['lock_start_time']
                        remaining = max(0, game_state['lock_duration'] - elapsed)
                        label += f" Lock:{remaining:.1f}s"
            
            # Draw box
            cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), color, thickness)
            # Draw label
            cv2.putText(img, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            
            # Draw progress bar for locking hands
            if game_state['phase'] == 'detection' and track_id in game_state['pending_hands']:
                lock_state = get_pending_hand_lock_state(track_id, game_state)
                if lock_state in ['locking', 'locked_ok']:
                    progress = get_lock_progress(track_id, game_state)
                    draw_lock_progress_bar(img, x1, y2, progress)
    
    return img

def draw_text_with_transparent_bg(frame, text, org, font=cv2.FONT_HERSHEY_SIMPLEX, scale=0.7, color=TEXT_COLOR, thickness=TEXT_THICKNESS, bg_color=BG_COLOR, alpha=0.5):
    (text_width, text_height), baseline = cv2.getTextSize(text, font, scale, thickness)
    x, y = org
    # Create overlay for background
    overlay = frame.copy()
    cv2.rectangle(overlay, (x - 5, y - text_height - 5), (x + text_width + 5, y + baseline + 5), bg_color, -1)
    # Blend overlay with frame
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
    # Draw text
    cv2.putText(frame, text, org, font, scale, color, thickness)
    return frame


def display_info(frame, text, position=(10, HEADING1_HEIGHT)):
    return draw_text_with_transparent_bg(frame, text, position)


def display_bottom_info(frame, text, position=(10, HEADING1_HEIGHT)):
    h, w = frame.shape[:2]
    return draw_text_with_transparent_bg(frame, text, (position[0], h - position[1]))


def display_centered_info(frame, text, height=HEADING1_HEIGHT):
    h, w = frame.shape[:2]
    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
    text_width = text_size[0]
    x = int((w - text_width) / 2)
    return draw_text_with_transparent_bg(frame, text, (x, height))


def display_bottom_centered_info(frame, text, bottom_offset=HEADING1_HEIGHT):
    h, w = frame.shape[:2]
    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
    text_width = text_size[0]
    x = int((w - text_width) / 2)
    y = h - bottom_offset
    return draw_text_with_transparent_bg(frame, text, (x, y))


def resize_to_window(img, window_name, original_w, original_h):
    rect = cv2.getWindowImageRect(window_name)
    win_w = rect[2]
    win_h = rect[3]
    if win_w > 0 and win_h > 0:
        scale = min(win_w / original_w, win_h / original_h)
        new_w = int(original_w * scale)
        new_h = int(original_h * scale)
        resized_img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
        canvas = np.zeros((win_h, win_w, 3), dtype=np.uint8)
        x_offset = (win_w - new_w) // 2
        y_offset = (win_h - new_h) // 2
        canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized_img
        return canvas
    else:
        return img


def initialize_model_and_capture():
    log.info("Initializing YOLO model and webcam capture.")
    # load the custom trained YOLO model
    model = YOLO("model/weights_backup/best.pt")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        log.error("Failed to open webcam.")
        raise RuntimeError("Webcam not available.")
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    cv2.namedWindow('YOLO Predictions', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('YOLO Predictions', w, h)
    return model, w, h


def process_detections(result, w_img):
    if result is None or result.boxes is None:
        return {}
    detections = result.boxes
    signs_by_id = {}
    for box in detections:
        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
        class_id = int(box.cls[0].cpu().numpy())
        class_name = CLASS_NAMES[class_id]
        track_id = None
        if hasattr(box, 'id') and box.id is not None:
            track_id = int(box.id[0].cpu().numpy())
        if track_id is not None:
            signs_by_id[track_id] = class_name
    return signs_by_id


def get_pending_hand_lock_state(track_id, game_state):
    """Determine the lock state of a pending hand."""
    if track_id not in game_state['pending_hands']:
        return 'none'
    
    hand = game_state['pending_hands'][track_id]
    sign = hand['sign']
    locked_sign = hand['locked']
    
    if locked_sign is None:
        return 'none'
    
    if sign != locked_sign:
        return 'none'
    
    if sign == OK:
        if hand['lock_start_time'] is not None:
            elapsed = time.time() - hand['lock_start_time']
            if elapsed >= game_state['lock_duration']:
                return 'locked_ok'
            else:
                return 'locking'
        return 'locking'
    else:
        return 'locked_invalid'


def get_lock_progress(track_id, game_state):
    """Get lock progress as percentage (0-100)."""
    if track_id not in game_state['pending_hands']:
        return 0.0
    
    hand = game_state['pending_hands'][track_id]
    if hand['lock_start_time'] is None:
        return 0.0
    
    elapsed = time.time() - hand['lock_start_time']
    progress = min(100, (elapsed / game_state['lock_duration']) * 100)
    return progress


def draw_lock_progress_bar(img, x1, y2, progress_percent):
    """Draw a progress bar below the bounding box."""
    bar_width = 100
    bar_height = 4
    bar_x = int(x1)
    bar_y = int(y2) + 2
    
    # Background (empty)
    cv2.rectangle(img, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (100, 100, 100), -1)
    
    # Filled portion
    filled_width = int((progress_percent / 100) * bar_width)
    if filled_width > 0:
        cv2.rectangle(img, (bar_x, bar_y), (bar_x + filled_width, bar_y + bar_height), (0, 255, 255), -1)
    
    return img


def update_pending_hand_lock(hand_data, current_sign, current_time, game_state):
    """Update lock state for a pending hand."""
    locked_sign = hand_data['locked']
    
    if current_sign == locked_sign and locked_sign is not None:
        # Continue locking
        if hand_data['lock_start_time'] is None:
            hand_data['lock_start_time'] = current_time
    else:
        # Sign changed, reset lock
        hand_data['locked'] = current_sign
        hand_data['lock_start_time'] = None


def reset_game_state(game_state) -> None:
    game_state['game_start_time'] = time.time()
    game_state['lock_duration'] = 2.0
    game_state['round_result'] = ""
    game_state['game_active'] = False
    game_state['phase'] = 'detection'  # 'detection' or 'game'
    game_state['players'] = {
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
    }
    game_state['pending_hands'] = {}  # Temporary tracking for unassigned hands
    game_state['ready_duration'] = 2.0  # Time to hold OK to lock
    game_state['disconnect_timeout'] = 120.0  # 2 minutes


def start_game(game_state) -> None:
    game_state['game_active'] = True
    game_state['game_start_time'] = time.time()
    game_state['players']['p1']['score'] = 0
    game_state['players']['p2']['score'] = 0
    game_state['players']['p1']['locked'] = None
    game_state['players']['p2']['locked'] = None
    game_state['players']['p1']['lock_start_time'] = None
    game_state['players']['p2']['lock_start_time'] = None
    game_state['round_result'] = ""





def update_player_detection(signs_by_id, game_state):
    """Handle detection phase with per-hand locking and ID assignment on OK lock."""
    players = game_state['players']
    pending_hands = game_state['pending_hands']
    current_time = time.time()
    
    # Phase A: Update pending hands and assigned players
    for player_key, player_data in players.items():
        if player_data['id'] is not None and player_data['id'] in signs_by_id:
            player_data['last_seen'] = current_time
            player_data['sign'] = signs_by_id[player_data['id']]
        elif player_data['id'] is not None:
            # Check for disconnection
            if current_time - player_data['last_seen'] > game_state['disconnect_timeout']:
                log.info(f"{player_key} disconnected during detection.")
                player_data['id'] = None
                player_data['sign'] = None
    
    # Phase B: Update pending hands - track/update unassigned detections
    hands_to_remove = []
    for track_id, hand_data in pending_hands.items():
        if track_id in signs_by_id:
            hand_data['last_seen'] = current_time
            hand_data['sign'] = signs_by_id[track_id]
            # Update lock state for this hand
            update_pending_hand_lock(hand_data, signs_by_id[track_id], current_time, game_state)
        else:
            # Hand not detected, check for timeout
            if current_time - hand_data['last_seen'] > game_state['disconnect_timeout']:
                hands_to_remove.append(track_id)
    
    # Remove disconnected hands
    for track_id in hands_to_remove:
        del pending_hands[track_id]
    
    # Phase C: Add new detections to pending hands
    for track_id, sign in signs_by_id.items():
        if track_id not in [p['id'] for p in players.values()] and track_id not in pending_hands:
            pending_hands[track_id] = {
                'sign': sign,
                'locked': None,
                'lock_start_time': None,
                'last_seen': current_time
            }
            log.info(f"Tracking new hand: ID {track_id}")
    
    # Phase D: Assign IDs from locked OK hands to available player slots
    available_slots = [k for k, v in players.items() if v['id'] is None]
    locked_ok_hands = [
        (track_id, hand) for track_id, hand in pending_hands.items()
        if get_pending_hand_lock_state(track_id, game_state) == 'locked_ok'
    ]
    
    for track_id, hand_data in locked_ok_hands:
        if available_slots:
            slot = available_slots.pop(0)
            players[slot]['id'] = track_id
            players[slot]['sign'] = hand_data['sign']
            players[slot]['last_seen'] = current_time
            players[slot]['ready'] = True
            del pending_hands[track_id]  # Remove from pending
            log.info(f"Assigned {slot} to ID {track_id} (locked with OK)")
    
    # Phase E: Check if both players are assigned, transition to game
    if all(p['id'] is not None for p in players.values()):
        game_state['phase'] = 'game'
        game_state['pending_hands'] = {}  # Clear pending hands
        log.info("Both players assigned. Starting game phase.")
        start_game(game_state)


def check_and_lock(current_p1, current_p2, game_state):
    players = game_state['players']
    if current_p1 == players['p1']['locked'] and current_p2 == players['p2']['locked'] and \
       current_p1 is not None and current_p2 is not None:
        if players['p1']['lock_start_time'] is None:
            players['p1']['lock_start_time'] = time.time()
            players['p2']['lock_start_time'] = time.time()
            log.info(f"Positions locked: P1={current_p1}, P2={current_p2}")
        if time.time() - players['p1']['lock_start_time'] >= game_state['lock_duration']:
            return True
    else:
        players['p1']['locked'] = current_p1
        players['p2']['locked'] = current_p2
        players['p1']['lock_start_time'] = None
        players['p2']['lock_start_time'] = None
    return False


def update_game_phase(signs_by_id, game_state):
    players = game_state['players']
    current_time = time.time()
    # Update signs and last_seen
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
                return
    # Now use the old logic with current_p1, current_p2
    locked = check_and_lock(current_p1, current_p2, game_state)
    if locked:
        if game_state['game_active']:
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
        # Reset locked after processing
        players['p1']['locked'] = None
        players['p2']['locked'] = None
        players['p1']['lock_start_time'] = None
        players['p2']['lock_start_time'] = None
    log.debug(f"Current Game State: {game_state}")


def draw_hud(img, game_state):
    h_img, w_img = img.shape[:2]
    players = game_state['players']
    pending_hands = game_state['pending_hands']
    
    if game_state['phase'] == 'detection':
        # Detection phase HUD
        img = display_centered_info(img, "Player Detection Phase - Lock to Register", HEADING1_HEIGHT)
        
        # Show assigned players
        y_offset = HEADING2_HEIGHT
        img = display_info(img, "Assigned Players:", (10, y_offset))
        y_offset += 25
        
        for player_key, player_data in players.items():
            if player_data['id'] is not None:
                status = f"🟢 {player_key.upper()}: ID {player_data['id']} - {player_data['sign']} ✓"
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
            lock_state = get_pending_hand_lock_state(track_id, game_state)
            progress = get_lock_progress(track_id, game_state)
            sign = hand_data['sign']
            
            if lock_state == 'locking':
                remaining = max(0, game_state['lock_duration'] - (progress / 100.0 * game_state['lock_duration']))
                status = f"🟡 ID:{track_id} - {sign} (Locking {remaining:.1f}s/2.0s)"
            elif lock_state == 'locked_ok':
                status = f"🟢 ID:{track_id} - {sign} (Ready to assign!)"
            elif lock_state == 'locked_invalid':
                status = f"🔴 ID:{track_id} - {sign} (Not OK - change sign)"
            else:
                status = f"⚪ ID:{track_id} - {sign}"
            
            img = display_info(img, status, (10, y_offset))
            y_offset += 25
        
        # Instructions
        img = display_centered_info(img, "Show OK and hold position to register", HEADING4_HEIGHT)
    
    else:  # game phase
        if not game_state['game_active']:
            img = display_centered_info(
                img, "Game Ready - Show OK to begin", HEADING1_HEIGHT)
        else:
            elapsed_time = int(time.time() - game_state['game_start_time'])
            img = display_info(
                img, f"Player 1: {players['p1']['score']}", (10, HEADING1_HEIGHT))
            img = display_info(
                img, f"Player 2: {players['p2']['score']}", (w_img - 200, HEADING1_HEIGHT))

            img = display_info(
                img, f"Time: {elapsed_time}s", (w_img//2 - 100, HEADING2_HEIGHT))

            img = display_info(img, "Player 1", (10, h_img - HEADING3_HEIGHT))
            img = display_info(
                img, "Player 2", (w_img - 150, h_img - HEADING3_HEIGHT))
            
            # Display player IDs
            if players['p1']['id'] is not None:
                img = display_info(img, f"ID: {players['p1']['id']}", (10, h_img - HEADING2_HEIGHT))
            if players['p2']['id'] is not None:
                img = display_info(img, f"ID: {players['p2']['id']}", (w_img - 150, h_img - HEADING2_HEIGHT))

            if game_state['round_result']:
                img = display_centered_info(
                    img, game_state['round_result'], HEADING4_HEIGHT)
        
        # Check if any player has lock_start_time active
        p1_lock_start = players['p1']['lock_start_time']
        p2_lock_start = players['p2']['lock_start_time']
        if p1_lock_start and p2_lock_start:
            elapsed = time.time() - p1_lock_start
            remaining = max(0, game_state['lock_duration'] - elapsed)
            lock_info = f"Locking: ({remaining:.1f}s)"
            img = display_bottom_centered_info(img, lock_info, HEADING2_HEIGHT)
        if players['p1']['locked']:
            img = display_bottom_info(img, players['p1']['locked'], (10, HEADING1_HEIGHT))
        if players['p2']['locked']:
            img = display_bottom_info(
                img, players['p2']['locked'], (w_img - 150, HEADING1_HEIGHT))
    
    return img


def get_rps_winner(sign1, sign2):
    if sign1 == sign2:
        return 'Tie'
    if (sign1 == ROCK and sign2 == SCISSOR) or \
       (sign1 == PAPER and sign2 == ROCK) or \
       (sign1 == SCISSOR and sign2 == PAPER):
        return 'Player 1 Wins'
    return 'Player 2 Wins'


def main():
    model, w, h = initialize_model_and_capture()
    game_state = {}
    reset_game_state(game_state)
    # Config for plotting detections
    plot_config = {'line_width': 2, 'font_size': 12}
    box_padding = 0  # Adjust this to change bounding box size (pixels to expand)
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
            results = model.track(frame, persist=True, verbose=False)
            img = frame.copy()  # Default to frame if no results
            for result in results:
                img = draw_custom_bounding_boxes(img, result, game_state, box_padding)
                signs_by_id = process_detections(result if results else None, img.shape[1])
                if game_state['phase'] == 'detection':
                    update_player_detection(signs_by_id, game_state)
                else:
                    update_game_phase(signs_by_id, game_state)
                img = draw_hud(img, game_state)
                display_img = resize_to_window(img, 'YOLO Predictions', w, h)
                cv2.imshow('YOLO Predictions', display_img)
                key = cv2.waitKey(1)
                if key & 0xFF == ord('q'):
                    return
    finally:
        cap.release()
        cv2.destroyAllWindows()
        log.info("Tracking loop ended.")


if __name__ == "__main__":
    main()
