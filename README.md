# APVC-RPS-Project

This is a repository for the final project of the APVC currecular unit in ISCTE.

The project consists of a Convolutional neural network that makes predictions on every frame captured by the computer's webcam.


## Overview

The predictions aim to find hand signs of the popular game Rock, Paper, Sccisors.
Since this project is focused on joining AI with elements of gamification we aim to include an immersion first approach.
By also training our model to find special hand signs designed by the team members


Besides the model we will also program game logic around the main loop to store who wins each round of Rock paper scissors and who is winning overall.
With this we can display a HUD over the webcam image creating a higher sense of immersion for the players.

## The Game
We built a live game where the webcam is always predicting your hand sign and checks for two players in the viewing frame.
It will store your relative scores according to the Rock paper scissors gun game

[Main readme for the Game](src\rps-game\README.md)

## Dataset

Found this dataset but it lacks bouding boxes for each image
Luckily the owner of the dataset shared his code on how he generated the dataset.
Which we intend to modify to also include the bounding boxes of each hand sign and this way we generate our own dataset.

https://www.kaggle.com/datasets/alexandredj/rock-paper-scissors-dataset/data

With this method we are allowed to generate datasets for other hand signs and for other hand games.
For example the game of zero or one (zerinho ou um), or even signs to start, stop and restart the game.


## Methodology / Approach

1. Modify the code found from the dataset owner to be able to generate a proper dataset with bounding boxes.
2. Train our own custom Object detection model with our generated dataset.
3. Code an initial form of the project that can detect the hand signs with the live webcam feed.
4. Program the game logic around ur initial PoC to detect who wins each round and how many point each side holds
   1. The algorithm will only be focused on two player games, each player being differentiated by being on the left half or the right half of the webcam feed.



https://www.youtube.com/watch?v=mjglZWtWQCg

Notas tiradas na meeting com profs: 

ter cuidado a gerar o dataset 

introduzir muita variaçao nas imagens

ter imagens sem ground truth -> n vale mt a pena

tracking das mãos com o yolo e treinar o yolo


Gestos:
pedra papel tesoura, começar, restart, etc

Relatorio:
* explicar dificuldades na captura do dataset
* explicar resultados do yolo
* precision e recall
* modelos diferentes do yolo? - nano, small, medium
* tempo que demora pa classificar (real time considerations)
* Apresentar bem o problema, dificuldades, dataset, resultados com varios modelos.


## How we labbeled our data

https://www.youtube.com/watch?v=r0RspiLG260

## Notes:

Needed to follow this tutorial to get gpu training to work: https://www.digitalocean.com/community/tutorials/yolov8-for-gpu-accelerate-object-detection 


# Future notes:

### Future Improvements Notes: Multi-Phase RPS Game with Player Tracking

#### Overview
Implement a state machine with two main phases: **Player Detection Phase** (initial setup) and **Game Phase** (active play). Use YOLO tracking IDs to persistently identify players across frames. Add timers for player presence/absence to handle disconnections. This enhances robustness for real-time multiplayer scenarios.

#### Phase 1: Player Detection Phase
- **Purpose**: Detect and register players before starting the game. Ensure both players are present and recognized.
- **Mechanics**:
  - Run model.track() to assign unique IDs to detected hand signs.
  - Store player data: Map IDs to player slots (e.g., player1_id, player2_id) and their associated signs.
  - Require both players to show a "ready" sign (e.g., "OK" or "Start") simultaneously for a short duration (e.g., 2-3 seconds) to confirm presence.
  - Display HUD: "Waiting for Player 1" / "Waiting for Player 2" with detected signs/IDs.
  - Transition to Game Phase once both players are registered and ready.
- **Edge Cases**:
  - If a detected ID moves out of frame during detection, reset its slot after a short timeout (e.g., 10 seconds).
  - Limit to 2 players max; ignore additional detections.
- **Technical Notes**:
  - Use a dict: `players = {'p1': {'id': None, 'sign': None, 'last_seen': None}, 'p2': {...}}`
  - Update `last_seen` timestamp on each detection.
  - Add a new function: `update_player_detection(results, players)`

#### Phase 2: Game Phase
- **Purpose**: Run the standard RPS game logic with persistent player tracking.
- **Mechanics**:
  - Use stored IDs to validate detections (only accept signs from registered player IDs).
  - Continue existing game logic (locking, scoring, HUD).
  - Monitor player presence: Update `last_seen` for each registered ID on detection.
- **Automatic Stop Condition**:
  - If a registered player's ID is not detected for 2 minutes (120 seconds), trigger game stop.
  - On stop: Reset game state, clear player data, and transition back to Player Detection Phase.
  - Display message: "Player X disconnected. Returning to setup."
- **Technical Notes**:
  - In main loop, check `time.time() - players['p1']['last_seen'] > 120` for each player.
  - Add a new state variable: `game_phase = 'detection' or 'game'`
  - Modify `main()` to switch logic based on `game_phase`.
  - Ensure tracking persists across phases with `persist=True`.

#### General Implementation Tips
- **State Management**: Add `game_phase` to `game_state` dict. Use if/else in main loop for phase-specific logic.
- **Logging**: Log phase transitions, player registrations, and disconnections for debugging.
- **UI Updates**: Modify `draw_hud()` to show phase-specific info (e.g., player IDs in detection phase).
- **Testing**: Simulate disconnections by covering camera; verify ID persistence.
- **Potential Enhancements**: Add player re-entry during game (if ID reappears within timeout), or support for more players.
- **Code Structure**: Refactor main loop into `handle_detection_phase()` and `handle_game_phase()` functions for clarity.

This setup makes the game more interactive and fault-tolerant, focusing on reliable multiplayer tracking.

