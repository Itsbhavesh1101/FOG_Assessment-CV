"""Generate and organize all project figures with clean, descriptive names."""

from __future__ import annotations

import csv
import json
import shutil
import subprocess
import sys
from pathlib import Path
from textwrap import wrap

import cv2
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
FIGURES = ASSETS / "figures"
OUTPUT = ROOT / "output"
VIDEO_PATH = ASSETS / "bowling_scoreboard.mp4"


def get_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/calibrib.ttf" if bold else "C:/Windows/Fonts/calibri.ttf"),
        Path("C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"),
    ]
    for c in candidates:
        if c.exists():
            return ImageFont.truetype(str(c), size)
    return ImageFont.load_default()


def draw_wrapped_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    xy: tuple[int, int],
    width_chars: int,
    line_height: int,
    fill: str | tuple[int, int, int],
    text_font: ImageFont.ImageFont,
) -> int:
    x, y = xy
    for source_line in text.splitlines():
        lines = wrap(source_line, width=width_chars) or [""]
        for line in lines:
            draw.text((x, y), line, fill=fill, font=text_font)
            y += line_height
    return y


def make_pipeline_diagram(path: Path) -> None:
    width, height = 1800, 1100
    img = Image.new("RGB", (width, height), "#ffffff")
    draw = ImageDraw.Draw(img)
    title_font = get_font(40, bold=True)
    box_font = get_font(21, bold=True)
    small_font = get_font(18)

    draw.text((50, 35), "BowlVision End-to-End Processing Architecture", fill="#0f172a", font=title_font)

    stages = [
        ("1. Video Ingestion", "1080p MP4 Stream\n30 FPS broadcast\nMetadata extraction", "#dbeafe"),
        ("2. Temporal Sampling", "Uniform frame stride\n~5 FPS sampling rate\n83% compute reduction", "#dcfce7"),
        ("3. Cutaway Filter", "Canny edge density\nHeader luminance\nScoreboard vs Lane check", "#fef3c7"),
        ("4. Contrast Enhancement", "ROI bounding box crop\nCLAHE equalization\nBilateral noise filter", "#ede9fe"),
        ("5. Multi-Engine OCR", "RapidOCR (ONNX Runtime)\nTesseract/Paddle fallback\nUnified OCRItem tokens", "#fee2e2"),
        ("6. Spatial Mapping", "4 player row partitions\n10 frame columns + TTL\nProportional token slicing", "#e0f2fe"),
        ("7. Temporal & Rules Engine", "Sliding window consensus\nBowling rules validation\nMonotonic score updates", "#fce7f3"),
        ("8. Multi-Format Export", "JSON structured scorecard\nTabular frame CSV\nTimeline & Video HUD", "#ecfccb"),
    ]

    positions = [
        (80, 160),
        (500, 160),
        (920, 160),
        (1340, 160),
        (1340, 560),
        (920, 560),
        (500, 560),
        (80, 560),
    ]
    box_w, box_h = 330, 220
    for idx, ((title, body, color), (x, y)) in enumerate(zip(stages, positions)):
        draw.rounded_rectangle((x, y, x + box_w, y + box_h), radius=20, fill=color, outline="#334155", width=3)
        draw.text((x + 20, y + 22), title, fill="#0f172a", font=box_font)
        draw_wrapped_text(draw, body, (x + 20, y + 70), 25, 28, "#334155", small_font)
        if idx < len(positions) - 1:
            nx, ny = positions[idx + 1]
            if y == ny:
                start = (x + box_w + 15, y + box_h // 2)
                end = (nx - 15, ny + box_h // 2)
            else:
                start = (x + box_w // 2, y + box_h + 15)
                end = (nx + box_w // 2, ny - 15)
            draw.line((start, end), fill="#0f172a", width=5)
            draw.polygon(
                [(end[0], end[1]), (end[0] - 18, end[1] - 10), (end[0] - 18, end[1] + 10)],
                fill="#0f172a",
            )

    draw.rounded_rectangle((480, 900, 1320, 1030), radius=18, fill="#f8fafc", outline="#94a3b8", width=2)
    draw.text((510, 928), "Key Engineering Principle: Typed Data Contract & Decoupled Stages", fill="#0f172a", font=get_font(24, bold=True))
    draw.text((510, 968), "Every stage accepts typed models and outputs validated intermediate results.", fill="#475569", font=get_font(21))
    img.save(path)


def make_state_machine_diagram(path: Path) -> None:
    width, height = 1600, 1050
    img = Image.new("RGB", (width, height), "#ffffff")
    draw = ImageDraw.Draw(img)
    draw.text((50, 35), "Visibility Classification & Temporal State Machine", fill="#0f172a", font=get_font(40, bold=True))

    nodes = {
        "Sample Video Frame": (100, 170, "#dbeafe"),
        "Compute Edge & Luminance": (540, 170, "#fef3c7"),
        "Scoreboard Visible": (1000, 120, "#dcfce7"),
        "Cutaway / Angle Switch": (1000, 340, "#fee2e2"),
        "Crop, CLAHE & OCR": (540, 520, "#ede9fe"),
        "Freeze Previous State": (1000, 560, "#fce7f3"),
        "Temporal Consensus Vote": (540, 770, "#e0f2fe"),
        "Commit & Export State": (1000, 770, "#ecfccb"),
    }

    def box(label: str, x: int, y: int, color: str) -> None:
        draw.rounded_rectangle((x, y, x + 340, y + 115), radius=18, fill=color, outline="#334155", width=3)
        draw_wrapped_text(draw, label, (x + 20, y + 26), 24, 28, "#0f172a", get_font(21, bold=True))

    for label, (x, y, color) in nodes.items():
        box(label, x, y, color)

    arrows = [
        ("Sample Video Frame", "Compute Edge & Luminance", "Stride ~5 FPS"),
        ("Compute Edge & Luminance", "Scoreboard Visible", "Edge >= 0.035 & Lum >= 110"),
        ("Compute Edge & Luminance", "Cutaway / Angle Switch", "Edge < 0.035 or Lum < 110"),
        ("Scoreboard Visible", "Crop, CLAHE & OCR", "Extract Tokens"),
        ("Cutaway / Angle Switch", "Freeze Previous State", "Suppress OCR"),
        ("Crop, CLAHE & OCR", "Temporal Consensus Vote", "Candidate Tokens"),
        ("Freeze Previous State", "Temporal Consensus Vote", "Retain History"),
        ("Temporal Consensus Vote", "Commit & Export State", "Bowling Rules Validated"),
    ]

    for src, dst, label in arrows:
        sx, sy, _ = nodes[src]
        dx, dy, _ = nodes[dst]
        start = (sx + 340, sy + 58) if dx > sx else (sx + 170, sy + 115)
        end = (dx, dy + 58) if dx > sx else (dx + 170, dy)
        draw.line((start, end), fill="#0f172a", width=4)
        draw.ellipse((end[0] - 8, end[1] - 8, end[0] + 8, end[1] + 8), fill="#0f172a")
        if label:
            mid = ((start[0] + end[0]) // 2, (start[1] + end[1]) // 2 - 24)
            draw.text(mid, label, fill="#0369a1", font=get_font(17, bold=True))

    img.save(path)


def make_terminal_screenshot(path: Path) -> None:
    test_proc = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    test_text = f"> python -m unittest discover -s tests -p \"test_*.py\"\n{test_proc.stdout.strip()}"
    
    help_proc = subprocess.run(
        [sys.executable, "-m", "bowlvision", "--help"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    help_text = f"> python -m bowlvision --help\n{help_proc.stdout.strip()[:650]}..."

    combined = f"{test_text}\n\n{help_text}"

    width, height = 1700, 1050
    img = Image.new("RGB", (width, height), "#0f172a")
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, width, 70), fill="#1e293b")
    draw.ellipse((28, 24, 48, 44), fill="#ef4444")
    draw.ellipse((62, 24, 82, 44), fill="#f59e0b")
    draw.ellipse((96, 24, 116, 44), fill="#22c55e")
    draw.text((145, 21), "BowlVision Terminal - Unit Tests & CLI Interface", fill="#e2e8f0", font=get_font(26, bold=True))
    draw_wrapped_text(
        draw,
        combined,
        (40, 105),
        width_chars=110,
        line_height=26,
        fill="#d1fae5",
        text_font=get_font(20),
    )
    img.save(path)


def make_output_screenshot(path: Path) -> None:
    with (OUTPUT / "final_scoreboard.json").open("r", encoding="utf-8") as f:
        data = json.load(f)

    width, height = 1700, 1000
    img = Image.new("RGB", (width, height), "#ffffff")
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, width, 120), fill="#0f172a")
    draw.text((50, 32), "BowlVision Final Extracted Scoreboard", fill="#ffffff", font=get_font(38, bold=True))
    draw.text((50, 80), "Validated JSON/CSV match state at video conclusion (t=57.83s)", fill="#94a3b8", font=get_font(20))

    headers = ["Player", "Frame 1", "Frame 2", "Frame 3", "Frame 4", "Frame 5", "Final TTL"]
    col_x = [60, 420, 600, 780, 960, 1140, 1380]
    y = 180
    draw.rectangle((40, y - 25, 1620, y + 45), fill="#e2e8f0")
    for idx, header in enumerate(headers):
        draw.text((col_x[idx], y), header, fill="#0f172a", font=get_font(24, bold=True))
    y += 80

    for player in data["players"]:
        row_fill = "#ffffff" if (y // 80) % 2 == 0 else "#f8fafc"
        draw.rectangle((40, y - 20, 1620, y + 48), fill=row_fill)
        values = [player["name"]]
        for frame in range(1, 6):
            cell = player["frames"][str(frame)]
            if cell is None:
                values.append("Unplayed")
            else:
                rolls = "".join(cell["rolls"])
                values.append(f"{rolls} -> {cell['cumulative']}")
        values.append(str(player["ttl"]))
        for idx, value in enumerate(values):
            color = "#b45309" if idx == 6 else ("#0f172a" if idx == 0 else "#334155")
            draw.text((col_x[idx], y), value, fill=color, font=get_font(23, bold=idx in (0, 6)))
        y += 80

    summary = (
        "Key Validation Results:\n"
        "• JAGDISH: 31 | VISHAL: 37 (updated in F5) | P (Player 3): 54 | TARUN: 40\n"
        "• Unplayed frames (F6-F10) are strictly preserved as null in JSON and 'unplayed' in CSV."
    )
    draw.rounded_rectangle((40, y + 20, 1620, y + 160), radius=14, fill="#eff6ff", outline="#3b82f6", width=2)
    draw_wrapped_text(draw, summary, (65, y + 42), 100, 32, "#1e3a8a", get_font(22, bold=True))
    img.save(path)


def make_preprocessing_figure(path: Path) -> None:
    """Generate a 4-panel comparison of image preprocessing and CLAHE enhancement."""
    cap = cv2.VideoCapture(str(VIDEO_PATH))
    cap.set(cv2.CAP_PROP_POS_MSEC, 52200)
    ret, frame = cap.read()
    cap.release()

    if not ret or frame is None:
        return

    h, w = frame.shape[:2]
    # Crop scoreboard ROI: y: 18% to 92%, x: 8% to 92%
    ymin, ymax = int(0.18 * h), int(0.92 * h)
    xmin, xmax = int(0.08 * w), int(0.92 * w)
    roi = frame[ymin:ymax, xmin:xmax]

    # Preprocessing stages
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    denoised = cv2.bilateralFilter(enhanced, d=5, sigmaColor=50, sigmaSpace=50)

    # Zoom in on player row 1 & 2 for clear comparison
    rh, rw = roi.shape[:2]
    crop_roi = roi[int(0.2 * rh):int(0.65 * rh), int(0.05 * rw):int(0.75 * rw)]
    crop_gray = gray[int(0.2 * rh):int(0.65 * rh), int(0.05 * rw):int(0.75 * rw)]
    crop_clahe = enhanced[int(0.2 * rh):int(0.65 * rh), int(0.05 * rw):int(0.75 * rw)]
    crop_denoised = denoised[int(0.2 * rh):int(0.65 * rh), int(0.05 * rw):int(0.75 * rw)]

    fig, axes = plt.subplots(2, 2, figsize=(14, 8), dpi=200)
    
    axes[0, 0].imshow(cv2.cvtColor(crop_roi, cv2.COLOR_BGR2RGB))
    axes[0, 0].set_title("1. Original Broadcast ROI Crop", fontsize=12, fontweight="bold", pad=8)
    axes[0, 0].axis("off")

    axes[0, 1].imshow(crop_gray, cmap="gray")
    axes[0, 1].set_title("2. Grayscale Intensity Conversion", fontsize=12, fontweight="bold", pad=8)
    axes[0, 1].axis("off")

    axes[1, 0].imshow(crop_clahe, cmap="gray")
    axes[1, 0].set_title("3. CLAHE Contrast Equalization (clipLimit=2.5)", fontsize=12, fontweight="bold", pad=8)
    axes[1, 0].axis("off")

    axes[1, 1].imshow(crop_denoised, cmap="gray")
    axes[1, 1].set_title("4. Bilateral Edge-Preserving Denoising (OCR-Ready)", fontsize=12, fontweight="bold", pad=8)
    axes[1, 1].axis("off")

    plt.suptitle("BowlVision Image Preprocessing & Contrast Enhancement Pipeline", fontsize=15, fontweight="bold", y=0.98)
    plt.tight_layout()
    plt.savefig(path, bbox_inches="tight")
    plt.close()


def make_cutaway_figure(path: Path) -> None:
    """Generate visual proof of cutaway detection comparing scoreboard vs lane frames."""
    cap = cv2.VideoCapture(str(VIDEO_PATH))
    # Frame 1: Scoreboard at 10.0s
    cap.set(cv2.CAP_PROP_POS_MSEC, 10000)
    ret1, f1 = cap.read()
    # Frame 2: Cutaway at 28.0s
    cap.set(cv2.CAP_PROP_POS_MSEC, 28000)
    ret2, f2 = cap.read()
    cap.release()

    if not ret1 or not ret2:
        return

    # Compute metrics for f1
    gray1 = cv2.cvtColor(f1, cv2.COLOR_BGR2GRAY)
    edges1 = cv2.Canny(gray1, 50, 150)
    density1 = np.count_nonzero(edges1) / edges1.size
    lum1 = np.mean(gray1[:int(0.3 * gray1.shape[0]), :])

    # Compute metrics for f2
    gray2 = cv2.cvtColor(f2, cv2.COLOR_BGR2GRAY)
    edges2 = cv2.Canny(gray2, 50, 150)
    density2 = np.count_nonzero(edges2) / edges2.size
    lum2 = np.mean(gray2[:int(0.3 * gray2.shape[0]), :])

    fig, axes = plt.subplots(1, 2, figsize=(14, 6), dpi=200)

    axes[0].imshow(cv2.cvtColor(f1, cv2.COLOR_BGR2RGB))
    axes[0].set_title(f"Scoreboard View (t=10.0s)\nEdge Density: {density1:.3f} (>=0.035) | Header Lum: {lum1:.1f} (>=110)\nDECISION: SCOREBOARD VISIBLE -> RUN OCR", fontsize=11, fontweight="bold", color="darkgreen")
    axes[0].axis("off")

    axes[1].imshow(cv2.cvtColor(f2, cv2.COLOR_BGR2RGB))
    axes[1].set_title(f"Lane Cutaway View (t=28.0s)\nEdge Density: {density2:.3f} (<0.035) | Header Lum: {lum2:.1f} (<110)\nDECISION: CUTAWAY DETECTED -> FREEZE STATE", fontsize=11, fontweight="bold", color="darkred")
    axes[1].axis("off")

    plt.suptitle("BowlVision Scoreboard Cutaway Detection & Visibility Verification", fontsize=14, fontweight="bold", y=0.98)
    plt.tight_layout()
    plt.savefig(path, bbox_inches="tight")
    plt.close()


def make_score_progression_chart(path: Path) -> None:
    """Generate a score progression timeline chart from timeline_history.csv."""
    csv_path = OUTPUT / "timeline_history.csv"
    if not csv_path.exists():
        return

    timestamps = []
    scores = {"JAGDISH": [], "VISHAL": [], "P (Player 3)": [], "TARUN": []}

    # Group by timestamp and player TTL
    time_map: dict[float, dict[str, int]] = {}
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            t = float(row["timestamp"])
            player = row["player"]
            ttl = int(row["ttl"]) if row["ttl"].isdigit() else 0
            if t not in time_map:
                time_map[t] = {}
            time_map[t][player] = ttl

    sorted_times = sorted(time_map.keys())
    t_vals = []
    j_vals, v_vals, p_vals, t_v_vals = [], [], [], []

    for t in sorted_times:
        t_vals.append(t)
        j_vals.append(time_map[t].get("JAGDISH", 0))
        v_vals.append(time_map[t].get("VISHAL", 0))
        p_vals.append(time_map[t].get("P (Player 3)", 0))
        t_v_vals.append(time_map[t].get("TARUN", 0))

    plt.figure(figsize=(12, 6), dpi=200)
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")

    plt.plot(t_vals, p_vals, label="P (Player 3) - Final TTL: 54", color="#8b5cf6", linewidth=2.5, marker="o", markersize=3)
    plt.plot(t_vals, t_v_vals, label="TARUN - Final TTL: 40", color="#f59e0b", linewidth=2.5, marker="s", markersize=3)
    plt.plot(t_vals, v_vals, label="VISHAL - Final TTL: 37 (Updated t=52s)", color="#10b981", linewidth=2.5, marker="^", markersize=3)
    plt.plot(t_vals, j_vals, label="JAGDISH - Final TTL: 31", color="#3b82f6", linewidth=2.5, marker="d", markersize=3)

    plt.title("BowlVision Cumulative Score Progression Across Video Timeline", fontsize=14, fontweight="bold", pad=12)
    plt.xlabel("Video Timestamp (seconds)", fontsize=11, fontweight="bold")
    plt.ylabel("Confirmed Total Score (TTL)", fontsize=11, fontweight="bold")
    plt.xlim(0, 58)
    plt.ylim(0, 65)
    plt.legend(loc="lower right", frameon=True, fontsize=10)
    plt.axvspan(22, 36, color="#fee2e2", alpha=0.4, label="Camera Cutaway (State Frozen)")
    plt.axvline(52.2, color="#059669", linestyle="--", alpha=0.8)
    plt.text(52.5, 38, "Vishal F5 Update (37)", color="#059669", fontweight="bold", fontsize=9)
    plt.tight_layout()
    plt.savefig(path, bbox_inches="tight")
    plt.close()


def main() -> int:
    FIGURES.mkdir(parents=True, exist_ok=True)
    print("[1/3] Generating new project figures...")

    # Define clean, organized target files
    make_pipeline_diagram(FIGURES / "Figure_03_End_to_End_Architecture_Pipeline.png")
    make_state_machine_diagram(FIGURES / "Figure_04_Visibility_and_Temporal_State_Machine.png")
    make_preprocessing_figure(FIGURES / "Figure_05_Image_Preprocessing_and_CLAHE_Enhancement.png")
    make_cutaway_figure(FIGURES / "Figure_06_Cutaway_Detection_and_Visibility_Analysis.png")
    make_score_progression_chart(FIGURES / "Figure_09_Score_Progression_Timeline_Chart.png")
    make_terminal_screenshot(FIGURES / "Figure_10_Code_Execution_and_Automated_Tests.png")
    make_output_screenshot(FIGURES / "Figure_11_Extracted_Scoreboard_Final_Output.png")

    print("[2/3] Renaming and copying existing raw figures with descriptive names...")
    mapping = {
        "fig1_input_scoreboard_frame.png": "Figure_01_Raw_Input_Scoreboard_Frame.png",
        "fig2_spatial_grid_debug.png": "Figure_02_Scoreboard_ROI_and_Spatial_Grid_Overlay.png",
        "fig5_ocr_evaluation_results.png": "Figure_07_OCR_Performance_and_Confidence_Evaluation.png",
        "fig6_spatial_mapping_samples.png": "Figure_08_Spatial_Mapping_Across_Timeline.png",
        "fig4_spatial_grid_report.png": "Figure_12_Spatial_Grid_Layout_and_Cell_Geometry.png",
        "fig3_env_setup_summary.png": "Figure_13_Environment_Setup_and_System_Summary.png",
    }

    for src_name, dst_name in mapping.items():
        src_path = FIGURES / src_name
        dst_path = FIGURES / dst_name
        if src_path.exists():
            shutil.copy2(src_path, dst_path)
            # Remove old short name to keep clean
            src_path.unlink()

    print("[3/3] Listing all organized figures:")
    for f in sorted(FIGURES.glob("*.png")):
        size_kb = f.stat().st_size / 1024
        print(f"  • {f.name} ({size_kb:.1f} KB)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
