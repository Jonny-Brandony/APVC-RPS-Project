"""
YOLO model handler module.
Handles model initialization and detection processing.
"""
import cv2
from ultralytics import YOLO
from config import log, MODEL_PATH, WINDOW_NAME, CLASS_NAMES


def initialize_model_and_capture():
    """
    Initialize YOLO model and configure webcam capture.
    
    Returns:
        tuple: (model, width, height) of the webcam
    """
    log.info("Initializing YOLO model and webcam capture.")
    model = YOLO(MODEL_PATH)
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        log.error("Failed to open webcam.")
        raise RuntimeError("Webcam not available.")
    
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_NAME, w, h)
    
    return model, w, h


def process_detections(result, w_img):
    """
    Process YOLO detection results and extract signs by track ID.
    
    Args:
        result: YOLO result object
        w_img: Image width (unused, kept for compatibility)
    
    Returns:
        dict: Mapping of track_id -> class_name
    """
    if result is None or result.boxes is None:
        return {}
    
    signs_by_id = {}
    for box in result.boxes:
        class_id = int(box.cls[0].cpu().numpy())
        class_name = CLASS_NAMES[class_id]
        track_id = None
        
        if hasattr(box, 'id') and box.id is not None:
            track_id = int(box.id[0].cpu().numpy())
        
        if track_id is not None:
            signs_by_id[track_id] = class_name
    
    return signs_by_id

