"""
Configuration module for RPS game.
Contains constants, class names, colors, and logging configuration.
"""
import logging
import logging.config
import cv2

# Logging configuration
LOGGING_CONFIG = {
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
            'filename': 'log/video-predict.log',
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

logging.config.dictConfig(LOGGING_CONFIG)
log = logging.getLogger('myapp')

# Hand sign constants
GUN = "Gun"
PAPER = "Paper"
RESTART = "Restart"
ROCK = "Rock"
SCISSOR = "Scissor"
START = "Start"
THUMB_DOWN = "THUMB_DOWN"
THUMB_UP = "Thumb_up"

# Class names from classes.txt (adjust indices if needed)
CLASS_NAMES = [GUN, PAPER, ROCK, SCISSOR, THUMB_DOWN, THUMB_UP]
PLAYABLE_SIGNS = [ROCK, PAPER, SCISSOR]

# Display position constants
HEADING1_HEIGHT = 30
HEADING2_HEIGHT = 60
HEADING3_HEIGHT = 90
HEADING4_HEIGHT = 110
HEADING5_HEIGHT = 140
HEADING6_HEIGHT = 170

# Text display constants
TEXT_THICKNESS = 1
TEXT_SCALE = 0.5
TEXT_COLOR = (255, 255, 255)
TEXT_FONT = cv2.FONT_HERSHEY_SIMPLEX
BG_COLOR = (0, 0, 0)
BOX_COLOR = (40, 196, 212)

# Class colors for bounding boxes
CLASS_COLORS = {
    GUN: (255, 0, 255),     # Magenta
    PAPER: (0, 255, 0),     # Green
    ROCK: (0, 165, 255),    # Orange
    SCISSOR: (255, 160, 0),   # Blue
    THUMB_DOWN: (0, 0, 255),      # Red
    THUMB_UP: (0, 255, 255),      # Yellow
}

# Model configuration
MODEL_PATH = "../../model_backup/modelv7/weights/best.pt"
WINDOW_NAME = 'YOLO Predictions'

