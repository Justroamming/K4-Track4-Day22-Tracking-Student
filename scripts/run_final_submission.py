#!/usr/bin/env python
"""Chạy full-frame cho bài nộp cuối cùng."""

from __future__ import annotations

import subprocess
import time
from pathlib import Path

LAB_DATA = Path("data_lab21/data_lab21")
VIDEOS = ["video_1", "video_2", "video_3", "video_4", "video_5"]

# Cấu hình được chọn cho từng video (dựa trên baseline và quan sát)
# Mỗi video: (tracker, conf, iou)
SELECTED_CONFIGS = {
    "video_1": ("strongsort", 0.3, 0.5),   # Quảng trường, tĩnh, ban ngày - Re-ID giúp giữ ID
    "video_2": ("botsort", 0.25, 0.5),     # Phố đêm, rất đông - Re-ID + conf thấp hơn
    "video_3": ("ocsort", 0.3, 0.5),       # Camera di chuyển, ít FPS - Motion-based tốt hơn
    "video_4": ("strongsort", 0.3, 0.5),   # Trong nhà, camera tiến, phản chiếu - Re-ID xử lý phản chiếu
    "video_5": ("bytetrack", 0.3, 0.5),    # Xe bus, rung lắc, giao lộ đông - Motion-based nhanh
}


def run_full_frame(video_name: str, tracker: str, conf: float, iou: float, device: str = "cpu") -> bool:
    """Chạy full-frame cho một video."""
    source = LAB_DATA / video_name / "img1"
    out_dir = Path("runs/nop_bai")
    out_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        "python",
        "scripts/run_tracking.py",
        "--source",
        str(source),
        "--seq-name",
        video_name,
        "--tracker",
        tracker,
        "--conf",
        str(conf),
        "--iou",
        str(iou),
        "--out",
        str(out_dir),
        "--device",
        device,
        "--save-video",
    ]

    print(f"\n{'='*80}")
    print(f"CHẠY FULL-FRAME: {video_name} | {tracker} | conf={conf} | iou={iou}")
    print(f"{'='*80}")

    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=7200,  # 2 hours timeout per video
        )
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"LỖI (exit code {e.returncode}):")
        print(e.stdout)
        print(e.stderr)
        return False
    except subprocess.TimeoutExpired:
        print("LỖI: Hết giờ (timeout 2h)")
        return False


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Chạy full-frame cho bài nộp")
    parser.add_argument("--video", choices=VIDEOS + ["all"], default="all",
                        help="Video cần chạy")
    parser.add_argument("--device", default="cpu", help="Thiết bị")
    args = parser.parse_args()

    videos_to_run = VIDEOS if args.video == "all" else [args.video]

    print(f"Sẽ chạy full-frame cho: {', '.join(videos_to_run)}")
    print(f"Thiết bị: {args.device}")

    results = {}
    for video in videos_to_run:
        if video not in SELECTED_CONFIGS:
            print(f"Bỏ qua {video}: không có cấu hình")
            continue

        tracker, conf, iou = SELECTED_CONFIGS[video]
        success = run_full_frame(video, tracker, conf, iou, args.device)
        results[video] = success
        time.sleep(3)

    # Kiểm tra file nộp
    print("\n" + "="*80)
    print("KIỂM TRA FILE NỘP BÀI (runs/nop_bai/)")
    print("="*80)
    out_dir = Path("runs/nop_bai")
    for video in VIDEOS:
        txt_file = out_dir / f"{video}.txt"
        if txt_file.exists():
            size = txt_file.stat().st_size
            lines = len(txt_file.read_text().strip().split("\n")) if size > 0 else 0
            status = "✓" if results.get(video) else "?"
            print(f"  {video}.txt: {size:,} bytes, {lines:,} dòng - {status}")
        else:
            print(f"  {video}.txt: THIẾU - ✗")

    # Chấm video_1 nếu có
    if "video_1" in results and results["video_1"]:
        print("\n" + "="*80)
        print("CHẤM VIDEO_1 (chỉ video này có nhãn)")
        print("="*80)
        subprocess.run([
            "python", "scripts/evaluate_practice.py",
            "--trackeval-root", "H:/AITHUCCHIEN/K4-Track4-Day22-Tracking-Student/TrackEval",
            "--lab-data-root", "data_lab21/data_lab21",
            "--submission", "runs/nop_bai/video_1.txt",
            "--run-name", "final_submission"
        ], check=False)


if __name__ == "__main__":
    main()