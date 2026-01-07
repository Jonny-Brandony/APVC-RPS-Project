"""
Display utilities module.
Contains basic text rendering and window management functions.
"""
import cv2
import numpy as np
from config import TEXT_COLOR, TEXT_THICKNESS, BG_COLOR


def draw_text_with_transparent_bg(frame, text, org, font=cv2.FONT_HERSHEY_SIMPLEX,
                                   scale=0.7, color=TEXT_COLOR, thickness=TEXT_THICKNESS,
                                   bg_color=BG_COLOR, alpha=0.5):
    """
    Draw text with a transparent background overlay.
    
    Args:
        frame: Image frame to draw on
        text: Text string to display
        org: (x, y) position for text
        font: OpenCV font type
        scale: Font scale
        color: Text color (BGR)
        thickness: Text thickness
        bg_color: Background color (BGR)
        alpha: Background transparency (0.0 to 1.0)
    
    Returns:
        Modified frame
    """
    (text_width, text_height), baseline = cv2.getTextSize(text, font, scale, thickness)
    x, y = org
    
    # Create overlay for background
    overlay = frame.copy()
    cv2.rectangle(overlay, (x - 5, y - text_height - 5),
                  (x + text_width + 5, y + baseline + 5), bg_color, -1)
    
    # Blend overlay with frame
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
    
    # Draw text
    cv2.putText(frame, text, org, font, scale, color, thickness)
    return frame


def display_info(frame, text, position=(10, 30)):
    """
    Display text at a specific position.
    
    Args:
        frame: Image frame to draw on
        text: Text string to display
        position: (x, y) position tuple
    
    Returns:
        Modified frame
    """
    return draw_text_with_transparent_bg(frame, text, position)


def display_bottom_info(frame, text, position=(10, 30)):
    """
    Display text at the bottom of the frame.
    
    Args:
        frame: Image frame to draw on
        text: Text string to display
        position: (x, y) position tuple (y is offset from bottom)
    
    Returns:
        Modified frame
    """
    h, w = frame.shape[:2]
    return draw_text_with_transparent_bg(frame, text, (position[0], h - position[1]))


def display_centered_info(frame, text, height=30):
    """
    Display centered text at a specific height.
    
    Args:
        frame: Image frame to draw on
        text: Text string to display
        height: Y position from top
    
    Returns:
        Modified frame
    """
    h, w = frame.shape[:2]
    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
    text_width = text_size[0]
    x = int((w - text_width) / 2)
    return draw_text_with_transparent_bg(frame, text, (x, height))


def display_bottom_centered_info(frame, text, bottom_offset=30):
    """
    Display centered text at the bottom of the frame.
    
    Args:
        frame: Image frame to draw on
        text: Text string to display
        bottom_offset: Offset from bottom
    
    Returns:
        Modified frame
    """
    h, w = frame.shape[:2]
    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
    text_width = text_size[0]
    x = int((w - text_width) / 2)
    y = h - bottom_offset
    return draw_text_with_transparent_bg(frame, text, (x, y))


def resize_to_window(img, window_name, original_w, original_h):
    """
    Resize image to fit window while maintaining aspect ratio.
    
    Args:
        img: Image to resize
        window_name: OpenCV window name
        original_w: Original image width
        original_h: Original image height
    
    Returns:
        Resized image with padding if needed
    """
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
    
    return img

