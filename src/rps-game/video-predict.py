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
        # Log detection info
        log.info(f"draw_custom_bounding_boxes Result={result}")
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
            center_x = (x1 + x2) / 2
            player = 1 if center_x < img.shape[1] / 2 else 2
            locked_gesture = game_state[f'locked_p{player}']
            color = CLASS_COLORS.get(class_name, BOX_COLOR)
            label = f"{class_name} {conf:.2f}"
            if track_id is not None:
                label = f"ID:{track_id} {label}"
            if locked_gesture == class_name and game_state['lock_start_time']:
                elapsed = time.time() - game_state['lock_start_time']
                remaining = max(0, game_state['lock_duration'] - elapsed)
                label += f" Lock:{remaining:.1f}s"
            # Draw box
            cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), color, TEXT_THICKNESS)
            # Draw label
            cv2.putText(img, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, TEXT_THICKNESS)
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
        return None, None
    detections = result.boxes
    p1_signs = []
    p2_signs = []
    for box in detections:
        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
        center_x = (x1 + x2) / 2
        class_id = int(box.cls[0].cpu().numpy())
        class_name = CLASS_NAMES[class_id]
        if center_x < w_img / 2:
            p1_signs.append(class_name)
        else:
            p2_signs.append(class_name)
    current_p1 = p1_signs[0] if p1_signs else None
    current_p2 = p2_signs[0] if p2_signs else None
    return current_p1, current_p2


def reset_game_state(game_state) -> None:
    game_state['score_p1'] = 0
    game_state['score_p2'] = 0
    game_state['game_start_time'] = time.time()
    game_state['locked_p1'] = None
    game_state['locked_p2'] = None
    game_state['lock_start_time'] = None
    game_state['lock_duration'] = 2.0
    game_state['round_result'] = ""
    game_state['game_active'] = False


def start_game(game_state) -> None:
    reset_game_state(game_state)
    game_state['game_active'] = True


def check_and_lock(current_p1, current_p2, game_state):
    if current_p1 == game_state['locked_p1'] and current_p2 == game_state['locked_p2'] and \
       current_p1 is not None and current_p2 is not None:
        if game_state['lock_start_time'] is None:
            game_state['lock_start_time'] = time.time()
            log.info(f"Positions locked: P1={current_p1}, P2={current_p2}")
        if time.time() - game_state['lock_start_time'] >= game_state['lock_duration']:
            return True
    else:
        game_state['locked_p1'] = current_p1
        game_state['locked_p2'] = current_p2
        game_state['lock_start_time'] = None
    return False


def update_game_state(current_p1, current_p2, game_state):
    locked = check_and_lock(current_p1, current_p2, game_state)
    if locked:
        if game_state['game_active']:
            if game_state['locked_p1'] == STOP and game_state['locked_p2'] == STOP:
                reset_game_state(game_state)
                log.info("Game stopped by both players showing STOP.")
            elif game_state['locked_p1'] in PLAYABLE_SIGNS and game_state['locked_p2'] in PLAYABLE_SIGNS:
                winner = get_rps_winner(
                    game_state['locked_p1'], game_state['locked_p2'])
                if winner == 'Player 1 Wins':
                    game_state['score_p1'] += 1
                elif winner == 'Player 2 Wins':
                    game_state['score_p2'] += 1
                game_state['round_result'] = f"{game_state['locked_p1']} vs {game_state['locked_p2']} - {winner}"
                log.info(f"Round result: {winner}")
        else:
            if game_state['locked_p1'] == OK and game_state['locked_p2'] == OK:
                start_game(game_state)
                log.info("Game started by both players showing OK.")
        # Reset locked after processing
        game_state['locked_p1'] = None
        game_state['locked_p2'] = None
        game_state['lock_start_time'] = None
    log.debug(f"Current Game State: {game_state}")


def draw_hud(img, game_state):
    h_img, w_img = img.shape[:2]
    if not game_state['game_active']:
        img = display_centered_info(
            img, f"Show '{OK}' to begin", HEADING1_HEIGHT)
    else:
        elapsed_time = int(time.time() - game_state['game_start_time'])
        img = display_info(
            img, f"Player 1: {game_state['score_p1']}", (10, HEADING1_HEIGHT))
        img = display_info(
            img, f"Player 2: {game_state['score_p2']}", (w_img - 200, HEADING1_HEIGHT))

        img = display_info(
            img, f"Time: {elapsed_time}s", (w_img//2 - 100, HEADING2_HEIGHT))

        img = display_info(img, "Player 1", (10, h_img - HEADING3_HEIGHT))
        img = display_info(
            img, "Player 2", (w_img - 150, h_img - HEADING3_HEIGHT))

        if game_state['round_result']:
            img = display_centered_info(
                img, game_state['round_result'], HEADING4_HEIGHT)
    if game_state['lock_start_time']:
        elapsed = time.time() - game_state['lock_start_time']
        remaining = max(0, game_state['lock_duration'] - elapsed)
        lock_info = f"Locking: ({remaining:.1f}s)"
        img = display_bottom_centered_info(img, lock_info, HEADING2_HEIGHT)
    if game_state['locked_p1']:
        img = display_bottom_info(img, game_state['locked_p1'], (10, HEADING1_HEIGHT))
    if game_state['locked_p2']:
        img = display_bottom_info(
            img, game_state['locked_p2'], (w_img - 150, HEADING1_HEIGHT))
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
                current_p1, current_p2 = process_detections(result if results else None, img.shape[1])
                update_game_state(current_p1, current_p2, game_state)
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
