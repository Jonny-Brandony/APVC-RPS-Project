# Rock-Paper-Scissors Game

A computer vision-based Rock-Paper-Scissors game that uses YOLO object detection to track hand gestures in real-time. Players register by showing a "Thumb Up" gesture and then play rounds by showing Rock, Paper, or Scissors gestures.

## Project Structure

The project is organized into several modules:

- **Root modules**: Main entry point, configuration, and game state management
- **[detection/](detection/README.md)**: Hand tracking and YOLO model handling
- **[game/](game/README.md)**: Game logic, phases, rules, and timeout management
- **[ui/](ui/README.md)**: User interface components including HUD, bounding boxes, and display utilities

## How It Works

The game operates in two main phases:

1. **Detection Phase**: Players register by showing a "Thumb Up" gesture and holding it for a specified duration. Once both players are registered, the game transitions to the game phase.

2. **Game Phase**: Players show Rock, Paper, or Scissors gestures. When both players lock their gestures for a specified duration, the round is evaluated and scores are updated.

The game uses YOLO object detection with tracking to maintain consistent player identification across frames. Each detected hand is assigned a unique tracking ID that persists as long as the hand remains visible.

## Controls

- **Q**: Quit the game
- **R**: Reset the game state
- **H**: Toggle help UI

## Requirements

- OpenCV for video capture and display
- Ultralytics YOLO for object detection
- A trained YOLO model for hand gesture recognition
- Webcam access

## Root-Level Modules

### main.py

The main entry point for the Rock-Paper-Scissors game application. This module orchestrates the entire game loop, coordinating all other modules to create a cohesive gameplay experience.

**Responsibilities:**

- Initialization of the YOLO model and webcam capture
- Main game loop that processes video frames
- Coordination between detection, game logic, and UI modules
- Keyboard input handling for game controls
- Frame-by-frame processing of detections and game state updates

**Game Loop Flow:**

The main game loop follows this sequence:

1. Capture a frame from the webcam
2. Run YOLO tracking on the frame to detect and track hand gestures
3. Process detections to extract signs by tracking ID
4. Update game state based on current phase (detection or game)
5. Draw bounding boxes around detected hands
6. Render the HUD overlay with game information
7. Display the processed frame
8. Handle keyboard input

**Phase Management:**

The module coordinates between two distinct phases:

- **Detection Phase**: Handles player registration through hand tracking and gesture locking
- **Game Phase**: Manages actual gameplay rounds, scoring, and round evaluation

The transition between phases is automatic when both players successfully register during the detection phase.

**Keyboard Controls:**

The module processes keyboard input to allow user interaction:

- Quit command to exit the application
- Reset command to restart the game from the beginning
- Help toggle to show or hide help information

**Integration Points:**

This module integrates with:

- YOLO handler for model initialization and detection processing
- Hand tracking module for player detection and registration
- Game phases module for gameplay logic
- UI modules for visual feedback and information display
- Game state for maintaining current game status
- Timeout manager for handling player disconnection scenarios

### config.py

Central configuration module that defines all constants, settings, and shared resources used throughout the application.

**Purpose:**

This module serves as a single source of truth for:

- Hand gesture class names and categories
- Color schemes for visual feedback
- Display positioning constants
- Logging configuration
- Model and window settings

**Hand Gesture Classes:**

The module defines several hand gesture classes that the YOLO model can detect:

- **Playable Signs**: Rock, Paper, Scissor (used during gameplay)
- **Control Signs**: Thumb Up (for player registration), Thumb Down (for game control)
- **Other Signs**: Gun (detected but not used in gameplay)

**Color Coding:**

Each gesture class is assigned a specific color for bounding box visualization:

- Rock: Orange
- Paper: Green
- Scissor: Blue
- Thumb Up: Yellow
- Thumb Down: Red
- Gun: Magenta

These colors help players quickly identify what gesture is being detected.

**Display Constants:**

The module defines vertical positioning constants for UI elements, allowing consistent placement of text and information overlays across different screen resolutions.

**Logging:**

Comprehensive logging is configured to output to both console and file, with detailed formatting that includes timestamps, logger names, log levels, and messages. This helps with debugging and monitoring game behavior.

**Model Configuration:**

The module specifies the path to the trained YOLO model weights file and the window name for the OpenCV display window.

### game_state.py

Manages the complete state of the Rock-Paper-Scissors game, including player information, game phases, timing, and round results.

**Core Components:**

**GamePhase Enum:**

Defines the two main phases of the game:

- **DETECTION**: Phase where players register by showing and locking the Thumb Up gesture
- **GAME**: Phase where actual gameplay occurs with Rock-Paper-Scissors rounds

**GameState Class:**

The central state container that maintains:

- Current game phase
- Player objects (p1 and p2) with their individual states
- Pending hands dictionary for tracking unassigned detections during registration
- Timing information for lock durations and game start time
- Round results and game activity status
- Help UI visibility flag

**Player Class:**

Represents an individual player with:

- Tracking ID assigned during registration
- Current detected sign
- Last seen timestamp for disconnection detection
- Ready status indicating successful registration
- Score accumulated during gameplay
- Lock state for gesture locking mechanism
- Lock start time for timing lock duration

**State Management:**

The module provides methods for:

- Initializing a fresh game state
- Resetting the game to initial conditions
- Starting the game phase and resetting scores
- Checking and managing gesture locks
- Resetting locks after round processing

**Lock Mechanism:**

The game uses a locking system to ensure players hold their gestures for a minimum duration before actions are processed. This prevents accidental triggers and ensures intentional gameplay. The lock duration is configurable and applies to both player registration and gameplay rounds.

**Disconnection Handling:**

The game state tracks when players were last seen. If a player's tracking ID is not detected for a specified timeout period, the game can handle disconnection scenarios, potentially resetting to the detection phase if needed.

### video-predict.py

A standalone, monolithic version of the Rock-Paper-Scissors game that contains all functionality in a single file. This appears to be a legacy version of the game before it was modularized into separate components.

**Purpose:**

This module serves as a self-contained implementation of the game, including all detection, game logic, UI rendering, and state management in one file. It may be used for testing, reference, or as a backup implementation.

**Differences from Modular Version:**

Unlike the modular version that separates concerns into different modules, this file contains:

- Inline configuration and constants
- Integrated YOLO model handling
- Combined detection and game logic
- All UI rendering functions
- Complete game state management

**Functionality:**

The module implements the same core functionality as the modular version:

- YOLO-based hand gesture detection
- Player registration through gesture locking
- Rock-Paper-Scissors gameplay
- Score tracking and round evaluation
- Visual feedback through bounding boxes and HUD

**Usage Note:**

This appears to be a legacy file. The main game entry point is `main.py`, which uses the modular architecture. This file may be kept for reference or compatibility purposes.

## Navigation

- [Detection Module](detection/README.md) - Hand tracking and YOLO model handling
- [Game Module](game/README.md) - Game logic, phases, rules, and timeout management
- [UI Module](ui/README.md) - User interface components
