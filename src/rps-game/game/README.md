# Game Module

Contains all game logic, rules, phase management, and timeout handling for the Rock-Paper-Scissors gameplay.

## Overview

The game module manages the active gameplay phase after players have been registered. It handles round processing, winner determination, score tracking, and timeout scenarios when players become invisible.

## Gameplay Flow

During the game phase:

1. Player signs are continuously updated from detections
2. When both players show gestures, the lock mechanism begins
3. If both players hold their gestures for the lock duration, the round is processed
4. Winner is determined using game rules
5. Scores are updated accordingly
6. Locks are reset for the next round

## Special Gestures

- **Thumb Down**: When both players show Thumb Down simultaneously, the game resets to detection phase
- **Rock, Paper, Scissors**: Standard gameplay gestures that trigger round evaluation

## Modules

### phases.py

Manages the game phase logic, handling player sign updates, gesture locking, round processing, and integration with timeout management.

**Responsibilities:**

This module handles all logic that occurs during the active game phase, after players have been registered. It coordinates between player detection updates, lock checking, and round evaluation.

**Player Sign Updates:**

Continuously updates player signs from current detections:

- Checks if each player's tracking ID is present in current detections
- Updates the player's sign and last seen timestamp
- Monitors for disconnections by checking if players haven't been seen within the timeout period
- Returns current signs for both players or None if disconnection occurred

**Lock Mechanism:**

The module uses the game state's lock checking functionality:

- Monitors when both players show gestures
- Tracks if players hold their gestures consistently
- Measures lock duration to ensure intentional gameplay
- Triggers round processing when lock duration is met

**Round Processing:**

When both players successfully lock their gestures:

- Checks if both players showed Thumb Down (triggers game reset)
- If both showed playable signs (Rock, Paper, Scissors), determines the winner
- Updates player scores based on round outcome
- Records round result for display
- Resets locks to prepare for the next round

**Timeout Integration:**

The module integrates with the timeout manager to handle scenarios where both players become invisible:

- Checks player visibility status each frame
- Updates the timeout manager with visibility information
- Resets game state if timeout is reached
- Prevents gameplay from continuing when players are not visible

**Disconnection Handling:**

If a player's tracking ID is not detected for longer than the disconnect timeout:

- Logs the disconnection event
- Resets the game state back to detection phase
- Allows players to re-register

This ensures the game can recover from temporary tracking failures or when players leave the camera view.

### rules.py

Implements the core Rock-Paper-Scissors game rules and winner determination logic.

**Purpose:**

This module contains the fundamental game logic that determines the outcome of each round based on the gestures shown by both players.

**Game Rules:**

The module implements the classic Rock-Paper-Scissors rules:

- **Rock beats Scissors**: Rock wins when played against Scissors
- **Paper beats Rock**: Paper wins when played against Rock
- **Scissors beats Paper**: Scissors wins when played against Paper
- **Tie**: When both players show the same gesture, the round is a tie

**Winner Determination:**

The function takes two signs as input and returns one of three possible outcomes:

- **Tie**: Both players showed the same gesture
- **Player 1 Wins**: Player 1's gesture beats Player 2's gesture
- **Player 2 Wins**: Player 2's gesture beats Player 1's gesture

The logic checks for ties first, then evaluates the three winning combinations for Player 1. If none of these conditions are met, Player 2 wins by default.

**Integration:**

This module is used by the phases module during round processing to determine round outcomes and update player scores accordingly.

### player_timeout.py

Manages timeout scenarios when both players become invisible during the game phase, providing automatic game reset functionality.

**Purpose:**

This module prevents the game from getting stuck in an unplayable state when both players leave the camera view or become undetectable. It provides a safety mechanism that resets the game after a timeout period.

**Timeout Behavior:**

The timeout manager:

- Monitors visibility status of both players
- Starts a timer when both players become invisible
- Resets the timer if at least one player becomes visible again
- Triggers game reset if the timeout duration is exceeded

**Configuration:**

The module defines configurable constants:

- **Timeout Duration**: The maximum time (in seconds) both players can be invisible before reset
- **Warning Threshold**: The time remaining when warnings should be displayed

**State Management:**

The timeout manager maintains:

- Start time of the current timeout period
- Warning display status
- Methods to query timeout state and remaining time

**Progress Tracking:**

The module provides methods to:

- Check if timeout is currently active
- Get remaining time until timeout
- Calculate timeout progress as a percentage
- Determine if warning should be shown

**Integration:**

The timeout manager is updated each frame during the game phase with current player visibility status. If timeout is reached, it signals the phases module to reset the game state, returning players to the detection phase where they can re-register.

**User Feedback:**

The timeout system provides visual feedback through the HUD, showing remaining time and warnings when the timeout threshold is approaching. This helps players understand when they need to return to the camera view.

## Integration Points

The game module integrates with:

- **Game State**: For player information, lock states, and phase management
- **Detection Module**: For receiving current player signs and tracking IDs
- **UI Module**: For displaying game information, scores, and timeout warnings
- **Rules Module**: For determining round winners

## Navigation

- [Main README](../README.md) - Project overview and root-level modules
- [Detection Module](../detection/README.md) - Hand tracking and YOLO model handling
- [UI Module](../ui/README.md) - User interface components
