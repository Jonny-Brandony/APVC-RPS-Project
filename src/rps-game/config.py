"""
Configuration module for RPS game.
Contains constants, class names, colors, and logging configuration.
"""
import logging
import logging.config

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

logging.config.dictConfig(LOGGING_CONFIG)
log = logging.getLogger('myapp')

# Hand sign constants
GUN = "Gun"
OK = "Ok"
PAPER = "Paper"
RESTART = "Restart"
ROCK = "Rock"
SCISSOR = "Scissor"
START = "Start"
STOP = "Stop"

# Class names from classes.txt (adjust indices if needed)
CLASS_NAMES = [GUN, OK, PAPER, RESTART, ROCK, SCISSOR, START, STOP]
PLAYABLE_SIGNS = [ROCK, PAPER, SCISSOR]

# Display position constants
HEADING1_HEIGHT = 30
HEADING2_HEIGHT = 50
HEADING3_HEIGHT = 70
HEADING4_HEIGHT = 90
HEADING5_HEIGHT = 110
HEADING6_HEIGHT = 130

# Text display constants
TEXT_THICKNESS = 1
TEXT_COLOR = (255, 255, 255)
BG_COLOR = (0, 0, 0)
BOX_COLOR = (40, 196, 212)

# Class colors for bounding boxes
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

# Model configuration
MODEL_PATH = "model/weights_backup/best.pt"
WINDOW_NAME = 'YOLO Predictions'

