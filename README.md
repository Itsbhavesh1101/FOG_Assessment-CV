# BowlVision: Automated Bowling Scoreboard Extraction

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/Tests-21%20Passed-brightgreen.svg)]()
[![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-orange.svg)](https://opencv.org/)
[![RapidOCR](https://img.shields.io/badge/OCR-ONNX%20Runtime-blueviolet.svg)](https://github.com/RapidAI/RapidOCR)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success.svg)]()

**BowlVision** is a robust computer-vision and temporal OCR analytics pipeline engineered to extract structured, machine-readable bowling game data from unstructured sports broadcast footage. Live electronic bowling scoreboards present numerous real-world computer vision challenges: camera angle cutaways to bowlers and pin decks, motion blur during pan/zoom transitions, LED matrix glare, small segmented fonts, and merged multi-digit bounding boxes.

This repository was developed for the **FOG Technologies Computer Vision Engineer Assessment**.

---

## 👤 Candidate & Project Information

| Field | Details |
| :--- | :--- |
| **Candidate Name** | **Bhavesh Barmashe** |
| **Institute** | Sagar Institute of Research and Technology (SIRT), Bhopal |
| **Target Role / Assessment** | FOG Technologies — Computer Vision Engineer Assessment |
| **Project Name** | BowlVision: Automated Bowling Scoreboard Extraction Pipeline |
| **Domain** | Computer Vision, Deep Learning OCR, Sports Broadcast Analytics |
| **GitHub Repository** | [https://github.com/Itsbhavesh1101/FOG_Assessment-CV.git](https://github.com/Itsbhavesh1101/FOG_Assessment-CV.git) |
| **Demo Video (Google Drive)** | [Watch Full Demo Video](https://drive.google.com/file/d/1SJZFywSiwqI_nj15JVHj_ni1_6zE9jrP/view?usp=sharing) |
| **Documentation Report (Drive)** | [Open Full Project Documentation (PDF)](https://drive.google.com/file/d/1WcimorSQORHNKZK4A8BovWxFIwXFzlSb/view?usp=sharing) |
| **Submission Date** | August 31, 2026 |

---

## 🔗 Key Links & Deliverables

* **GitHub Repository:** [https://github.com/Itsbhavesh1101/FOG_Assessment-CV.git](https://github.com/Itsbhavesh1101/FOG_Assessment-CV.git)
* **Demo Video (Google Drive):** [https://drive.google.com/file/d/1SJZFywSiwqI_nj15JVHj_ni1_6zE9jrP/view?usp=sharing](https://drive.google.com/file/d/1SJZFywSiwqI_nj15JVHj_ni1_6zE9jrP/view?usp=sharing)
* **Technical Documentation PDF (Google Drive):** [https://drive.google.com/file/d/1WcimorSQORHNKZK4A8BovWxFIwXFzlSb/view?usp=sharing](https://drive.google.com/file/d/1WcimorSQORHNKZK4A8BovWxFIwXFzlSb/view?usp=sharing)
* **Local Technical Documentation PDF:** [`docs/BowlVision_Project_Documentation_Bhavesh_Barmashe.pdf`](docs/BowlVision_Project_Documentation_Bhavesh_Barmashe.pdf)

---

## 📄 Submission Documentation

The complete, publication-grade technical report is available online on Google Drive and locally in the repository:

* **Google Drive Link:** [https://drive.google.com/file/d/1WcimorSQORHNKZK4A8BovWxFIwXFzlSb/view?usp=sharing](https://drive.google.com/file/d/1WcimorSQORHNKZK4A8BovWxFIwXFzlSb/view?usp=sharing)
* **Local File:** `docs/BowlVision_Project_Documentation_Bhavesh_Barmashe.pdf`

The document includes:
* **Embedded Screenshot Evidence & Explanations:**
  * ● Raw input broadcast frame capture (`1080p @ 30 FPS`)
  * ● Terminal execution & automated unit tests (**21/21 passing in 0.15s**)
  * ● Scoreboard detection with calibrated spatial grid mapping overlay
  * ● Final extracted scorecard data and JSON/CSV output deliverables
* **Vector Architecture & State Machine Diagrams**
* **Image Preprocessing & CLAHE Enhancement Analysis**
* **Proportional Character Slicing Mathematical Formulation**
* **Ten-Pin Bowling Scoring Invariants & Temporal Consensus Validation**
* **Comprehensive Benchmarks & Ground Truth Verification**

To re-generate the PDF report at any time:
```bash
python scripts/build_submission_pdf.py
```

---

## 🏆 Final Validated Match Scoreboard

The pipeline extracts and verifies the following final scoreboard from `assets/bowling_scoreboard.mp4` (57.83s duration):

| Player | Frame 1 | Frame 2 | Frame 3 | Frame 4 | Frame 5 | Final TTL |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **JAGDISH** | `X` → 15 | `5-` → 20 | `-7` → 27 | `4-` → 31 | *Unplayed* | **31** |
| **VISHAL** | `8-` → 8 | `3-` → 11 | `8-` → 19 | `9-` → 28 | `9-` → 37 | **37** |
| **P (Player 3)** | `X` → 20 | `4/` → 39 | `9-` → 48 | `6-` → 54 | *Unplayed* | **54** |
| **TARUN** | `1-/6-` → 6 | `1/` → 25 | `8-` → 33 | `34` → 40 | *Unplayed* | **40** |

> **Note:** Unplayed frames (Frames 5–10 for Jagdish, Player 3, and Tarun, and Frames 6–10 for Vishal) are strictly preserved as `null` in JSON and `unplayed` in CSV without any hallucinated or noisy numbers.

---

## 📐 System Architecture & Flow Diagrams

### 1. End-to-End System Pipeline Flowchart
```mermaid
flowchart TD
    A[Input Video MP4 Stream] --> B[VideoStream Decoded Frames]
    B --> C[Temporal Sampler ~5 FPS Stride]
    C --> D{CutawayDetector}
    D -->|Scoreboard Visible| E[Crop Scoreboard ROI]
    D -->|Cutaway Detected| F[Freeze Confirmed State]
    E --> G[ImageEnhancer CLAHE & Bilateral]
    G --> H[OCRManager RapidOCR / ONNX]
    H --> I[Normalized OCRItem Tokens]
    I --> J[SpatialGridMapper Cell Routing]
    J --> K[FrameObservation Candidates]
    F --> L[TemporalScoreboardTracker]
    K --> L
    L --> M[BowlingRules Validation Engine]
    M --> N[Confirmed PlayerScorecards]
    N --> O1[JSON Exporter]
    N --> O2[CSV Exporter]
    N --> O3[Timeline History CSV]
    N --> O4[Video Annotator HUD]
```

---

### 2. Scoreboard Visibility & Cutaway State Machine
```mermaid
stateDiagram-v2
    [*] --> IngestFrame: VideoStream Sample (~5 FPS)
    IngestFrame --> FeatureExtraction: Extract Scoreboard ROI
    FeatureExtraction --> ScoreboardVisible: Edge Density >= 0.035 AND Header Luminance >= 110
    FeatureExtraction --> CutawayDetected: Edge Density < 0.035 OR Header Luminance < 110
    ScoreboardVisible --> CropAndEnhance: CLAHE Contrast & Bilateral Denoising
    CropAndEnhance --> OCRManager: Extract OCRItem Tokens
    OCRManager --> SpatialGridMapper: Map Tokens to Player & Frame Cells
    CutawayDetected --> FreezeState: Retain Last Confirmed Game State
    SpatialGridMapper --> TemporalVote: Update Candidate Observation History
    FreezeState --> TemporalVote: Maintain Steady State
    TemporalVote --> CommitState: Bowling Invariants Verified
    CommitState --> [*]: Export Final Scorecards
```

---

### 3. Spatial Grid Mapping & Proportional Token Slicing
When OCR merges multi-digit numbers across columns into a single token (e.g. `"394854"`), character centers are calculated proportionally rather than dropping the detection:

$$X_i = X_{\min} + (i + 0.5) \cdot \frac{X_{\max} - X_{\min}}{L}$$

```mermaid
flowchart LR
    A["Raw Merged OCR Token '394854'"] --> B["Compute Proportional Centers"]
    B --> C["X_0, X_1: '39' &rarr; Frame 2"]
    B --> D["X_2, X_3: '48' &rarr; Frame 3"]
    B --> E["X_4, X_5: '54' &rarr; Frame 4"]
    C --> F["Temporal Consensus & Rules Engine"]
    D --> F
    E --> F
    F --> G["Confirmed Scorecard Output"]
```

---

### 4. Object-Oriented Domain Model
```mermaid
classDiagram
    class PipelineConfig {
        +video_path: Path
        +output_dir: Path
        +sample_fps: float
        +roi: tuple
        +ocr_engine: str
    }
    class PlayerScorecard {
        +row_index: int
        +name: str
        +frames: dict[int, FrameCell]
        +total_score: int
    }
    class FrameCell {
        +frame_number: int
        +rolls: list[str]
        +cumulative_score: Optional[int]
    }
    class OCRItem {
        +text: str
        +confidence: float
        +bbox: BoundingBox
    }
    class BoundingBox {
        +x1: float
        +y1: float
        +x2: float
        +y2: float
        +center_x: float
        +center_y: float
    }
    PlayerScorecard "1" *-- "10" FrameCell
    FrameCell --> OCRItem
    OCRItem --> BoundingBox
    PipelineConfig --> PlayerScorecard
```

---

### 5. Runtime Data Flow Sequence Diagram
```mermaid
sequenceDiagram
    participant CLI as CLI / Main
    participant P as BowlVisionPipeline
    participant VS as VideoStream
    participant CD as CutawayDetector
    participant OCR as OCRManager
    participant SG as SpatialGridMapper
    participant TT as TemporalScoreboardTracker
    participant EX as Exporters

    CLI->>P: run(config)
    P->>VS: open(video_path) & read metadata
    loop Every Sampled Frame (~5 FPS)
        VS->>P: VideoFrameSample
        P->>CD: evaluate_visibility(frame)
        alt Scoreboard Visible
            P->>OCR: enhanced_roi_image
            OCR->>P: list[OCRItem]
            P->>SG: map_tokens_to_cells(tokens)
            SG->>P: FrameObservation
            P->>TT: add_observation(obs)
        else Cutaway / Angle Switch
            P->>TT: add_cutaway_marker()
        end
        TT->>TT: consensus_vote() & apply_bowling_rules()
    end
    P->>EX: export_all(confirmed_state)
    EX->>CLI: final_scoreboard.json / .csv / timeline / video
```

---

## 📁 Repository Structure

```text
FOG-Assessment/
├── bowlvision/                           # Core BowlVision package
│   ├── analytics/                        # Scoring & temporal rules
│   │   ├── __init__.py
│   │   ├── bowling_rules.py              # Ten-pin bowling rules & monotonic checks
│   │   └── temporal_aggregator.py        # Sliding-window consensus tracker
│   ├── core/                             # Foundational models & configuration
│   │   ├── __init__.py
│   │   ├── config.py                     # PipelineConfig & default ROI constants
│   │   ├── models.py                     # PlayerScorecard, FrameScore, GameState
│   │   └── types.py                      # Typed geometry & OCR token data classes
│   ├── export/                           # Exporters & visualizers
│   │   ├── __init__.py
│   │   ├── csv_exporter.py               # Tabular CSV scorecard generation
│   │   ├── json_exporter.py              # Standardized JSON output builder
│   │   ├── video_annotator.py            # MP4 HUD scoreboard video renderer
│   │   └── visualizer.py                 # Debug & analysis visualization helpers
│   ├── ocr/                              # Multi-backend OCR engine abstraction
│   │   ├── __init__.py
│   │   ├── base.py                       # BaseOCREngine abstract interface
│   │   ├── ocr_manager.py                # Engine registry & OCRItem normalization
│   │   ├── paddle_engine.py              # PaddleOCR fallback engine
│   │   ├── rapid_engine.py               # RapidOCR ONNX primary engine
│   │   └── tesseract_engine.py           # PyTesseract fallback engine
│   ├── spatial/                          # Coordinate mapping & token slicing
│   │   ├── __init__.py
│   │   ├── cell_mapper.py                # Grid cell coordinate assignment
│   │   ├── grid_layout.py                # Scoreboard ROI & player row partitioning
│   │   └── player_tracker.py             # Active bowler row & indicator tracker
│   ├── vision/                           # Video ingestion & image processing
│   │   ├── __init__.py
│   │   ├── cutaway_detector.py           # Canny edge & luminance cutaway detector
│   │   ├── image_enhancer.py             # CLAHE & bilateral contrast preprocessing
│   │   └── video_stream.py               # OpenCV VideoCapture temporal sampler
│   ├── __init__.py
│   ├── __main__.py                       # Package entrypoint for python -m bowlvision
│   ├── cli.py                            # Full-featured argument parser & CLI
│   └── pipeline.py                       # BowlVisionPipeline orchestrator
│
├── dataset_video/                        # Input broadcast video dataset
│   └── bowling_scoreboard.mp4            # Full HD 1080p broadcast video
│
├── docs/                                 # Documentation deliverables
│   ├── BowlVision_Project_Documentation_Bhavesh_Barmashe.pdf # Full technical report
│   └── FOG_Assessment_Video.mp4          # Video demonstration
│
├── output/                               # Final pipeline deliverables
│   ├── annotated_bowling_scoreboard.mp4  # Visual HUD video tracking broadcast match
│   ├── final_scoreboard.csv              # Tabular scorecard output
│   ├── final_scoreboard.json             # Structured JSON scorecard
│   └── timeline_history.csv              # Timestamped frame-by-frame observation history
│
├── scripts/                              # Verification & utility scripts
│   ├── __init__.py
│   ├── build_submission_doc.py           # Word report generator
│   ├── build_submission_pdf.py           # Playwright PDF documentation generator
│   ├── generate_all_figures.py           # Standalone vector figure builder
│   ├── generate_demo_video.py            # Annotated video clip generator
│   ├── inspect_frame.py                  # Frame-level ROI diagnostic script
│   └── live_demo.py                      # Live GUI demonstration viewer
│
├── tests/                                # Automated unit test suite (21 tests)
│   ├── __init__.py
│   ├── test_bowling_rules.py             # Strike/spare & monotonic score tests
│   ├── test_config.py                    # Configuration parsing tests
│   ├── test_exporters.py                 # JSON/CSV serialization tests
│   ├── test_ocr_sanitizer.py             # OCR character normalization tests
│   ├── test_spatial_grid.py              # Spatial mapping & token slicing tests
│   ├── test_temporal_tracker.py          # Sliding-window consensus tests
│   └── test_vision_enhancer.py           # CLAHE & cutaway detector tests
│
├── .gitattributes                        # Git repository attributes
├── .gitignore                            # Git ignore rules
├── live_demo.py                          # Root live demonstration entrypoint
├── live_web_player.py                    # Lightweight web live player
├── main.py                               # Canonical root CLI entry point
├── pyproject.toml                        # Standard PEP 518/621 packaging metadata
├── README.md                             # Comprehensive project documentation
├── requirements.txt                      # Project dependency specification
└── run_pipeline.py                       # Convenience pipeline execution script
```

---

## ⚡ Installation & Quickstart

### 1. Environment Setup
```bash
# Clone the repository and navigate into the folder
cd FOG-Assessment

# Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate # Linux / macOS
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

*(Optional) Install BowlVision in editable development mode:*
```bash
pip install -e .
```

---

## 🚀 Execution Commands

### 1. Run the End-to-End Pipeline
```bash
# Canonical package invocation
python -m bowlvision --video assets/bowling_scoreboard.mp4

# Or through the root wrapper
python main.py --video assets/bowling_scoreboard.mp4
```

### 2. Run Pipeline with Annotated HUD Video
```bash
# Render and save annotated video to output/annotated_bowling_scoreboard.mp4
python main.py --video assets/bowling_scoreboard.mp4 --render-video
```

### 3. Run Pipeline with Live Interactive Desktop Viewer
```bash
# Process frames and display the live tracking HUD on screen
python main.py --video assets/bowling_scoreboard.mp4 --render-video --live

# Or launch via the live demo shortcut
python live_demo.py
```

### 4. Run Automated Unit Tests
```bash
python -m unittest discover -s tests -p "test_*.py"
```

### 5. Rebuild the Technical Documentation PDF
```bash
python scripts/build_submission_pdf.py
```

### 6. Inspect a Specific Video Timestamp
```bash
python scripts/inspect_frame.py --video assets/bowling_scoreboard.mp4 --time 52.2
```

---

## ⚙️ CLI Options Reference

| Option | Default | Description |
| :--- | :--- | :--- |
| `--video` | `assets/bowling_scoreboard.mp4` | Path to the input bowling broadcast video |
| `--output-dir` / `--output_dir` | `output` | Directory for JSON, CSV, and video deliverables |
| `--debug-dir` / `--debug_dir` | `debug` | Directory for debug frame crops |
| `--sample-fps` / `--sample_fps` | `5.0` | Frame sampling rate for temporal OCR analysis |
| `--roi` | `0.18 0.92 0.08 0.92` | Normalized scoreboard ROI crop (`YMIN YMAX XMIN XMAX`) |
| `--ocr-engine` | `auto` | OCR backend: `auto`, `rapidocr`, `paddleocr`, or `pytesseract` |
| `--render-video` / `--render_video` | `off` | Renders annotated MP4 video with real-time scoreboard HUD |
| `--save-crops` / `--save_crops` | `off` | Saves preprocessed OCR crops to debug folder |

---

## 🧪 Verification & Test Results

The test suite validates every pipeline component against edge cases, noisy OCR tokens, cutaways, and bowling rules:

```bash
> python -m unittest discover -s tests -p "test_*.py"
.....................
----------------------------------------------------------------------
Ran 21 tests in 0.150s

OK (exit code: 0)
```

---

## 📦 Output Artifacts & Deliverables

All deliverables are exported to the `output/` directory:

1. **`output/final_scoreboard.json`**:
   Nested JSON structure containing player names, total scores (TTL), roll marks, cumulative frame scores, and explicit `null` values for unplayed frames.
2. **`output/final_scoreboard.csv`**:
   Clean tabular scorecard containing rows for every player and frame (`player`, `frame`, `rolls`, `cumulative`, `ttl`).
3. **`output/timeline_history.csv`**:
   Timestamped observation log recording every sampled frame throughout the broadcast.
4. **`output/annotated_bowling_scoreboard.mp4`**:
   Broadcast demonstration video with synchronized real-time HUD scorecard overlay.
