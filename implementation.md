# Implementation Plan for APVC-RPS-Project

This plan outlines a step-by-step guide for implementing the Rock-Paper-Scissors hand sign detection game using YOLO and real-time webcam processing. It is based on the project overview in README.md, assuming Python as the primary language, YOLO (via Ultralytics) for object detection, and OpenCV for webcam handling. The plan is modular, with validation steps at each stage. Total estimated time: 4-6 weeks, depending on dataset size and hardware.

## Phase 1: Dataset Preparation and Enhancement (1-2 weeks)
**Objective**: Generate and label a high-quality dataset with bounding boxes for all hand signs, including custom ones.

**Note**: Assumed completed based on current project state. Hand signs include: rock, paper, scissors, gun, ok, not ok, start (7 classes total).

1. **Review and Modify Dataset Generation Code**:
   - Examine the existing Kaggle dataset and the owner's code (referenced in README).
   - Update `src/dataset-generation/generate-dataset.py` to generate images with bounding boxes (YOLO format: class_id x_center y_center width height).
   - Introduce variations: Random backgrounds, lighting, angles, distances, and hand poses. Ensure diversity (e.g., different skin tones, ages).
   - Generate images for the 7 hand signs.
   - Avoid invalid images: Filter out those without clear ground truth.

2. **Data Collection and Labeling**:
   - Use webcam capture to collect additional real-world images (store in `data/captured/`).
   - Label using Label Studio or similar (integrate with `data_labelling.md` notes; reference the YouTube video for labeling process).
   - Output to `data/labeled/custom_data/` in YOLO format (images/ and labels/ folders).
   - Split data: Use `src/dataset-generation/train_val_split.py` to create train/val/test sets (e.g., 70/20/10 split) in `data/labeled/custom_data/split/`.

3. **Validation**:
   - Check dataset balance (equal samples per class).
   - Run basic stats: Total images, bounding box distributions.
   - Test loading with YOLO tools to ensure format correctness.

## Phase 2: Model Training and Optimization (1-2 weeks)
**Objective**: Train and fine-tune a YOLO model for accurate, real-time hand sign detection.

1. **Setup Environment**:
   - Install dependencies from `requirements.txt` (add Ultralytics, OpenCV, etc., if missing).
   - Configure YOLO (e.g., YOLOv8) in `src/dataset-generation/Train_YOLO_Models.ipynb`.

2. **Train Models**:
   - Start with YOLOv8 small (yolo11s.pt as base).
   - Train on custom dataset using the notebook/script.
   - Experiment with variants: Nano, medium, large—compare precision/recall and inference speed.
   - Hyperparameters: Epochs (50-100), batch size, learning rate; enable data augmentation.

3. **Evaluate and Iterate**:
   - Test on validation set: Measure mAP, precision, recall.
   - Address overfitting: Adjust dataset variations or regularization.
   - Save best weights to `model/weights_backup/best.pt`.

4. **Validation**:
   - Run inference on test set; log results (e.g., confusion matrix).
   - Benchmark real-time performance (FPS on sample video).

## Phase 3: Real-Time Detection Implementation (1 week)
**Objective**: Build the core detection system for live webcam feed.

1. **Develop Detection Script**:
   - Create/update `src/rps-game/video-predict.py` to:
     - Capture webcam feed using OpenCV.
     - Load trained YOLO model.
     - Process frames: Detect signs, draw bounding boxes.
     - Differentiate players: Left half = Player 1, right half = Player 2.

2. **Integrate Custom Signs**:
   - Map detections to game actions (e.g., rock/paper/scissors for moves, custom signs for start/restart).

3. **Validation**:
   - Test on live feed: Ensure detections are accurate and fast (target >10 FPS).
   - Handle edge cases: Multiple hands, occlusions.

## Phase 4: Game Logic and Immersion Features (1 week)
**Objective**: Add game mechanics and HUD for full immersion. Focus on timing-based winner detection and OpenCV-based HUD.

1. **Implement Game Logic**:
   - In `src/rps-game/video-predict.py` or a new script:
     - Track player signs per frame/round using timing rules: Monitor if both players hold the same positions for a set duration (e.g., 2-3 seconds) to lock positions as final.
     - Determine winners: Standard RPS rules (rock beats scissors, paper beats rock, scissors beat paper; handle ties). Also handle custom signs (e.g., "start" to begin round, "gun" or others as special moves if applicable).
     - Accumulate scores; detect game start/end via custom signs (e.g., "start" to initiate).
     - Differentiate players: Left half = Player 1, right half = Player 2.

2. **Add HUD Overlay**:
   - Use OpenCV to overlay text/images: Scores for each player, game time/timer, player labels ("Player 1" on left, "Player 2" on right).
   - Ensure immersion: Semi-transparent HUD, clear positioning.

3. **Validation**:
   - Simulate games: Test win/loss logic with timing, HUD updates.
   - User testing: Verify real-time feel and accuracy.

## Phase 5: Testing, Evaluation, and Reporting (0.5-1 week)
**Objective**: Validate the full system and document results.

1. **Comprehensive Testing**:
   - End-to-end: Live gameplay with two players.
   - Metrics: Precision/recall on test data, FPS, latency.
   - Edge cases: Poor lighting, fast movements.

2. **Optimize and Debug**:
   - Fix issues (e.g., false positives); retrain if needed.

3. **Report Preparation**:
   - Document: Dataset challenges, model results (compare YOLO variants), real-time performance.
   - Include visuals: Confusion matrices, sample detections.

4. **Final Validation**:
   - Demo the project; ensure all README goals are met.

## Tools and Dependencies
- Python 3.x, OpenCV, Ultralytics YOLO.
- Hardware: Webcam, GPU for training (if available).
- Version control: Git for tracking changes.

## Risks and Contingencies
- Dataset quality: If labeling is slow, use data augmentation tools.
- Performance: If FPS is low, switch to lighter YOLO models.
- Scope creep: Stick to two-player logic; expand custom signs only if time allows.

This plan is actionable and modular—start with Phase 1 and iterate. Refer to README.md for project context and update this document as implementation progresses.