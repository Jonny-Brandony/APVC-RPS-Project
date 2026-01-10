# Project Structure

This document describes the modular structure of the RPS game project.

## Directory Structure

```
src/rps-game/
├── config.py                 # Configuration and constants
├── game_state.py             # Game state management
├── main.py                   # Main entry point
├── video-predict.py          # Original file (can be removed)
├── detection/
│   ├── __init__.py
│   ├── yolo_handler.py       # YOLO model initialization and detection processing
│   └── hand_tracking.py      # Hand tracking and detection phase logic
├── game/
│   ├── __init__.py
│   ├── rules.py              # RPS game rules
│   └── phases.py             # Game phase management
└── ui/
    ├── __init__.py
    ├── display.py            # Basic display utilities
    ├── hud.py                # HUD drawing
    └── bounding_boxes.py     # Bounding box drawing with lock visualization
```

## Module Responsibilities

### `config.py`
- Logging configuration
- Hand sign constants (ROCK, PAPER, SCISSOR, OK, etc.)
- Class names and colors
- Display position constants
- Model path and window configuration

### `game_state.py`
- `create_initial_state()` - Create new game state
- `reset_game_state()` - Reset game to initial state
- `start_game()` - Start game phase

### `detection/yolo_handler.py`
- `initialize_model_and_capture()` - Initialize YOLO model and webcam
- `process_detections()` - Extract signs by track ID from YOLO results

### `detection/hand_tracking.py`
- `get_pending_hand_lock_state()` - Determine lock state of pending hand
- `get_lock_progress()` - Get lock progress percentage
- `update_pending_hand_lock()` - Update hand lock state
- `update_player_detection()` - Main detection phase handler
- Helper functions for player assignment and tracking

### `game/rules.py`
- `get_rps_winner()` - Determine RPS round winner

### `game/phases.py`
- `check_and_lock()` - Check if both players have locked gestures
- `update_game_phase()` - Main game phase handler
- Helper functions for sign updates and round processing

### `ui/display.py`
- `draw_text_with_transparent_bg()` - Draw text with transparent background
- `display_info()` - Display text at position
- `display_centered_info()` - Display centered text
- `display_bottom_info()` - Display text at bottom
- `display_bottom_centered_info()` - Display centered text at bottom
- `resize_to_window()` - Resize image to fit window

### `ui/hud.py`
- `draw_hud()` - Main HUD drawing function
- `draw_detection_phase_hud()` - HUD for detection phase
- `draw_game_phase_hud()` - HUD for game phase

### `ui/bounding_boxes.py`
- `draw_custom_bounding_boxes()` - Draw bounding boxes with lock visualization
- `draw_lock_progress_bar()` - Draw progress bar for locking
- `get_box_color_and_thickness()` - Determine box styling
- `build_detection_label()` - Build label text for detections

### `main.py`
- `main()` - Main game loop
- Coordinates all modules
- Handles frame capture and display

## Benefits

1. **Maintainability**: Each module has a single, clear responsibility
2. **Testability**: Individual components can be unit tested easily
3. **Reusability**: Detection and UI logic can be reused in other projects
4. **Readability**: Smaller, focused files are easier to understand
5. **Scalability**: Easy to add new features (e.g., multi-player modes)
6. **Collaboration**: Multiple developers can work on different modules simultaneously

## Usage

Run the game with:
```bash
python main.py
```

The original `video-predict.py` file can be kept for reference or removed once you've verified the new structure works correctly.

