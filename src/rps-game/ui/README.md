# UI Module

Handles all user interface components, including heads-up display (HUD), bounding box visualization, and display utilities.

## Overview

The UI module provides comprehensive visual feedback to players, displaying game information, detection status, and visual indicators that help players understand the current game state and what actions they should take.

## Visual Feedback

The UI provides comprehensive visual feedback:

- Color-coded bounding boxes that change based on lock state
- Progress bars showing lock progress
- Text overlays with game information
- Phase-specific displays for detection and gameplay
- Timeout warnings when players are not visible

## Display Features

- Transparent text backgrounds for readability
- Centered and positioned text overlays
- Window resizing with aspect ratio preservation
- Real-time updates reflecting current game state

## Modules

### hud.py

Renders the heads-up display overlay that provides game information and status updates to players.

**Purpose:**

The HUD module displays contextual information based on the current game phase, helping players understand game state, their status, and what actions they should take.

**Phase-Specific Displays:**

**Detection Phase HUD:**

During player registration, the HUD displays:

- Phase title indicating detection is in progress
- List of assigned players with their tracking IDs and status
- List of pending hands being tracked
- Instructions for players on how to register
- Lock progress for hands attempting to register

**Game Phase HUD:**

During active gameplay, the HUD displays:

- Player scores for both players
- Elapsed game time
- Round results when a round completes
- Lock status when players are locking gestures
- Timeout warnings if players become invisible
- Current gestures being shown by each player

**Help UI:**

The module includes a help system that can be toggled with keyboard input, displaying available controls and game instructions.

**Timeout Display:**

When the timeout manager is active, the HUD displays:

- Remaining time until game reset
- Progress bar visualization
- Warning messages when timeout threshold is approaching

**Visual Design:**

The HUD uses:

- Transparent backgrounds for text overlays to maintain visibility
- Positioned text at various screen locations (top, bottom, center)
- Color-coded information for quick recognition
- Real-time updates reflecting current game state

**Integration:**

The HUD module integrates with:

- Game state for current phase and player information
- Timeout manager for visibility warnings
- Display utilities for text rendering
- Bounding boxes module for progress bar visualization

### bounding_boxes.py

Handles drawing of visual indicators around detected hands, with dynamic styling based on lock state and game phase.

**Purpose:**

This module provides visual feedback by drawing bounding boxes around detected hand gestures, with color coding and progress indicators that help players understand the current state of detection and gameplay.

**Visual Features:**

**Color Coding:**

Bounding boxes change color based on context:

- **Default colors**: Each gesture class has its own color (Rock=Orange, Paper=Green, etc.)
- **Detection phase**: Boxes change to yellow when locking, green when successfully locked with Thumb Up, red when locked with wrong gesture, gray when not locking
- **Game phase**: Uses default class colors with additional visual indicators

**Box Styling:**

Box thickness varies to indicate importance:

- Thicker boxes for successfully locked hands
- Medium thickness for locking in progress
- Standard thickness for normal detections

**Labels:**

Each bounding box displays:

- Player identification (P1 or P2) if assigned
- Tracking ID
- Detected gesture class name
- Confidence score
- Lock status and remaining time (when applicable)
- Player score (for assigned players)

**Progress Bars:**

The module draws progress bars below bounding boxes to show:

- Lock progress during detection phase registration
- Lock progress during gameplay when players are locking gestures
- Visual feedback using block characters to represent progress percentage

**Lock State Visualization:**

The module provides unified lock progress tracking that works for both:

- Pending hands during detection phase
- Assigned players during game phase

This creates a consistent visual experience across both phases.

**Box Padding:**

Supports configurable padding to expand bounding boxes, which can help with visibility or accommodate detection inaccuracies.

**Integration:**

The module integrates with:

- Hand tracking module for lock state information
- Game state for player assignments and lock status
- Display utilities for text rendering
- Configuration for colors and styling constants

### display.py

Provides basic text rendering utilities and window management functions for the game interface.

**Purpose:**

This module offers a set of utility functions for drawing text overlays and managing the display window, ensuring consistent text rendering across the application.

**Text Rendering:**

**Transparent Background Text:**

The core function draws text with a semi-transparent background overlay, ensuring text remains readable regardless of the underlying video content. The background uses alpha blending to maintain visibility of the video feed while providing contrast for text.

**Text Positioning Functions:**

The module provides several convenience functions for common text placement scenarios:

- **Top positioning**: Display text at specific coordinates from the top
- **Bottom positioning**: Display text at the bottom with offset from bottom edge
- **Centered positioning**: Center text horizontally at a specific height
- **Bottom centered**: Center text horizontally at the bottom with offset

**Window Management:**

**Window Resizing:**

The resize function handles proper display of video frames:

- Maintains aspect ratio when resizing
- Centers the video in the window if window size differs from video size
- Adds black padding if needed to fill the window
- Handles window size queries and updates

**Configuration:**

Text rendering uses configurable constants for:

- Font type and scale
- Text color and thickness
- Background color and transparency level

These can be adjusted in the configuration module to change the appearance of all text overlays.

**Usage:**

All display functions return the modified image/frame, allowing for function chaining and easy integration into the rendering pipeline. This makes it simple to add multiple text overlays to a single frame.

## Integration Points

The UI module integrates with:

- **Game State**: For current phase, player information, and game status
- **Detection Module**: For lock state information and tracking IDs
- **Game Module**: For timeout manager and round results
- **Configuration**: For colors, fonts, and display constants

## Navigation

- [Main README](../README.md) - Project overview and root-level modules
- [Detection Module](../detection/README.md) - Hand tracking and YOLO model handling
- [Game Module](../game/README.md) - Game logic, phases, rules, and timeout management
