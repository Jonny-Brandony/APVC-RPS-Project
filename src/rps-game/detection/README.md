# Detection Module

Handles all aspects of hand gesture detection and tracking using YOLO object detection. This module is responsible for processing video frames, detecting hand gestures, and maintaining tracking IDs for consistent player identification.

## Overview

The detection module processes video frames from the webcam, uses YOLO to detect and track hand gestures, and manages the player registration process during the detection phase. It maintains tracking IDs for detected hands and coordinates the assignment of these IDs to player slots.

## Detection Flow

1. YOLO model processes each video frame
2. Detections are extracted with tracking IDs
3. Signs are mapped to their respective tracking IDs
4. Hand tracking module processes these detections based on game phase
5. Player assignment occurs when hands successfully lock with Thumb Up gesture

## Tracking Persistence

The module relies on YOLO's built-in tracking capabilities to maintain consistent IDs for detected hands across frames. This allows the game to distinguish between different players and maintain their identity even when hands temporarily leave the frame.

## Modules

### yolo_handler.py

Handles initialization and processing of the YOLO object detection model for hand gesture recognition.

**Responsibilities:**

This module is responsible for:

- Loading the trained YOLO model from the configured path
- Setting up webcam capture and determining video dimensions
- Creating and configuring the OpenCV display window
- Processing YOLO detection results to extract tracking information
- Mapping detections to their corresponding gesture class names

**Model Initialization:**

The initialization process:

1. Loads the YOLO model from the specified weights file
2. Opens the webcam to determine video resolution
3. Creates a resizable OpenCV window for display
4. Returns the model and video dimensions for use by other modules

**Detection Processing:**

The detection processing function:

- Takes YOLO result objects containing detection boxes
- Extracts class IDs and maps them to gesture class names
- Extracts tracking IDs assigned by YOLO's tracking algorithm
- Returns a dictionary mapping tracking IDs to detected gesture classes

This processed format makes it easy for other modules to query what gesture each tracked hand is showing.

**Error Handling:**

The module includes error handling for webcam access failures, ensuring the application fails gracefully with clear error messages if the camera cannot be opened.

### hand_tracking.py

Manages the detection phase logic, including tracking of unassigned hands, lock state management, and player assignment.

**Purpose:**

This module handles the complex process of registering players during the detection phase. It tracks all detected hands, monitors their lock states, and assigns tracking IDs to player slots when registration conditions are met.

**Key Functions:**

**Lock State Management:**

Tracks the lock state of pending hands with four possible states:

- **none**: No lock in progress
- **locking**: Hand is holding a gesture but hasn't reached lock duration
- **locked_ok**: Hand has successfully locked with Thumb Up gesture
- **locked_invalid**: Hand has locked with a gesture other than Thumb Up

**Player Assignment Process:**

The module coordinates a multi-phase process:

1. **Update Assigned Players**: Updates already-assigned players with current detections and checks for disconnections
2. **Update Pending Hands**: Maintains tracking of unassigned hands, updates their lock states, and removes disconnected ones
3. **Add New Detections**: Identifies newly detected hands and adds them to the pending hands dictionary
4. **Assign Players**: Assigns tracking IDs from successfully locked hands to available player slots
5. **Check Transition**: Monitors when both players are assigned and triggers transition to game phase

**Lock Progress Tracking:**

The module calculates lock progress as a percentage, allowing the UI to display visual feedback showing how long a player needs to hold their gesture before registration completes.

**Disconnection Handling:**

The module monitors when hands are no longer detected. If a pending hand disappears for longer than the disconnect timeout, it is removed from tracking. If an assigned player disappears, their assignment is cleared.

**Registration Requirements:**

For a hand to be assigned to a player slot:

1. The hand must be detected and tracked (have a tracking ID)
2. The hand must show the Thumb Up gesture
3. The hand must hold the Thumb Up gesture continuously for the lock duration
4. A player slot must be available

Once both players successfully register, the game automatically transitions to the game phase.

## Integration Points

The detection module integrates with:

- **Game State**: For maintaining player assignments and phase transitions
- **UI Modules**: For displaying detection status and lock progress
- **Game Module**: For transitioning to gameplay after registration

## Navigation

- [Main README](../README.md) - Project overview and root-level modules
- [Game Module](../game/README.md) - Game logic, phases, rules, and timeout management
- [UI Module](../ui/README.md) - User interface components
