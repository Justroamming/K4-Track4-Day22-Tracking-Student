#!/usr/bin/env python
"""Chạy thí nghiệm toàn diện cho bài lab tracking.

Script này chạy tất cả 5 tracker trên 5 video với các tham số khác nhau
để tìm cấu hình tốt nhất cho từng video.
"""

from __future__ import annotations

import subprocess
import time
from pathlib import Path

# Cấu hình cố định
LAB_DATA = Path("data_lab21/data_lab21")
VIDEOS = ["video_1", "video_2", "video_3", "video_4", "video_5"]
TRACKERS = ["bytetrack", "ocsort", "botsort", "strongsort", "deepocsort"]

# Tracker dựa trên chuyển động vs có Re-ID
MOTION_TRACKERS = ["bytetrack", "ocsort"]
APPEARANCE_TRACKERS = ["botsort", "strongsort", "deepocsort"]

# Tham số detector để thử
CONF_VALUES = [0.15, 0.3, 0.5]
IOU_VALUES = [0.4, 0.5, 0.7]

# Tham số mặc định
DEFAULT_CONF = 0.3
DEFAULT_IOU = 0.5


def run_tracking(
    video_name: str,
    tracker: str,
    conf: float,
    iou: float,
    out_dir: Path,
    max_frames: int = 0,
    save_video: bool = False,
    device: str = "cpu",
) -> bool:
    """Chạy một lần tracking.

    Args:
        video_name: Tên video (video_1, video_2, ...)
        tracker: Tên tracker
        conf: Ngưỡng confidence detector
        iou: Ngưỡng IoU detector
        out_dir: Thư mục xuất kết quả
        max_frames: Giới hạn frame (0 = toàn bộ)
        save_video: Có xuất video preview không
        device: Thiết bị chạy

    Returns:
        True nếu thành công, False nếu lỗi.
    """
    source = LAB_DATA / video_name / "img1"
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
    ]
    if save_video:
        cmd.append("--save-video")
    if max_frames > 0:
        cmd.extend(["--max-frames", str(max_frames)])

    print(f"\n{'='*80}")
    print(f"Chạy: {video_name} | {tracker} | conf={conf} | iou={iou} | max_frames={max_frames or 'all'}")
    print(f"Thư mục xuất: {out_dir}")
    print(f"{'='*80}")

    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=3600,  # 1 hour timeout per run
        )
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"LỖI (exit code {e.returncode}):")
        print(e.stdout)
        print(e.stderr)
        return False
    except subprocess.TimeoutExpired:
        print("LỖI: Hết giờ (timeout 1h)")
        return False


def phase1_baseline_all():
    """Giai đoạn 1: Chạy baseline tất cả tracker trên tất cả video (150 frame)."""
    print("\n" + "="*80)
    print("GIAI ĐOẠN 1: BASELINE - Tất cả 5 tracker trên 5 video (150 frame)")
    print("="*80)

    out_dir = Path("runs/baseline_150")
    out_dir.mkdir(parents=True, exist_ok=True)

    results = {}
    for video in VIDEOS:
        results[video] = {}
        for tracker in TRACKERS:
            success = run_tracking(
                video_name=video,
                tracker=tracker,
                conf=DEFAULT_CONF,
                iou=DEFAULT_IOU,
                out_dir=out_dir,
                max_frames=150,
                save_video=True,
            )
            results[video][tracker] = success
            time.sleep(2)  # Nghỉ giữa các lần chạy

    # In tóm tắt
    print("\n" + "="*80)
    print("TÓM TẮT GIAI ĐOẠN 1")
    print("="*80)
    for video in VIDEOS:
        print(f"\n{video}:")
        for tracker in TRACKERS:
            status = "✓" if results[video][tracker] else "✗"
            print(f"  {tracker:12s} {status}")

    return results


def phase2_parameter_sweep():
    """Giai đoạn 2: Quét tham số cho các tracker được chọn."""
    print("\n" + "="*80)
    print("GIAI ĐOẠN 2: QUÉT THAM SỐ (conf/iou) - Chạy nhanh 150 frame")
    print("="*80)

    # Chỉ quét cho video_1 trước (có nhãn để kiểm tra)
    # Sau đó có thể mở rộng cho các video khác
    out_dir = Path("runs/param_sweep_150")
    out_dir.mkdir(parents=True, exist_ok=True)

    results = {}
    for video in VIDEOS:
        results[video] = {}
        # Chạy cả motion và appearance trackers
        for tracker in TRACKERS:
            results[video][tracker] = {}
            for conf in CONF_VALUES:
                for iou in IOU_VALUES:
                    key = f"conf{conf}_iou{iou}"
                    success = run_tracking(
                        video_name=video,
                        tracker=tracker,
                        conf=conf,
                        iou=iou,
                        out_dir=out_dir,
                        max_frames=150,
                        save_video=False,  # Không cần video khi quét tham số
                    )
                    results[video][tracker][key] = success
                    time.sleep(1)

    return results


def phase3_final_submission(selected_configs: dict):
    """Giai đoạn 3: Chạy full-frame cho các cấu hình đã chọn.

    Args:
        selected_configs: Dict {video_name: {"tracker": ..., "conf": ..., "iou": ...}}
    """
    print("\n" + "="*80)
    print("GIAI ĐOẠN 3: CHẠY FULL-FRAME CHO BÀI NỘP")
    print("="*80)

    out_dir = Path("runs/nop_bai")
    out_dir.mkdir(parents=True, exist_ok=True)

    results = {}
    for video in VIDEOS:
        if video not in selected_configs:
            print(f"Bỏ qua {video}: không có cấu hình được chọn")
            continue

        config = selected_configs[video]
        tracker = config["tracker"]
        conf = config["conf"]
        iou = config["iou"]

        print(f"\nChạy bài nộp cho {video}: {tracker} conf={conf} iou={iou}")
        success = run_tracking(
            video_name=video,
            tracker=tracker,
            conf=conf,
            iou=iou,
            out_dir=out_dir,
            max_frames=0,  # Full frames
            save_video=True,
        )
        results[video] = success
        time.sleep(3)

    # Kiểm tra file nộp
    print("\n" + "="*80)
    print("KIỂM TRA FILE NỘP BÀI")
    print("="*80)
    for video in VIDEOS:
        txt_file = out_dir / f"{video}.txt"
        if txt_file.exists():
            size = txt_file.stat().st_size
            lines = len(txt_file.read_text().strip().split("\n")) if size > 0 else 0
            print(f"  {video}.txt: {size} bytes, {lines} dòng - {'✓' if results.get(video) else '?'}")
        else:
            print(f"  {video}.txt: THIẾU - ✗")

    return results


def main():
    """Hàm chính."""
    import argparse

    parser = argparse.ArgumentParser(description="Chạy thí nghiệm tracking toàn diện")
    parser.add_argument("--phase", choices=["1", "2", "3", "all"], default="all",
                        help="Giai đoạn cần chạy (1=baseline, 2=param sweep, 3=final, all=tất cả)")
    parser.add_argument("--video", choices=VIDEOS + ["all"], default="all",
                        help="Video cần chạy (mặc định: all)")
    parser.add_argument("--device", default="cpu", help="Thiết bị (cpu, cuda:0)")
    args = parser.parse_args()

    # Cập nhật device global
    global DEVICE
    DEVICE = args.device

    if args.phase in ("1", "all"):
        phase1_baseline_all()

    if args.phase in ("2", "all"):
        phase2_parameter_sweep()

    if args.phase in ("3", "all"):
        # Cấu hình mẫu - cần điều chỉnh sau khi xem kết quả giai đoạn 1, 2
        selected = {
            "video_1": {"tracker": "strongsort", "conf": 0.3, "iou": 0.5},
            "video_2": {"tracker": "botsort", "conf": 0.25, "iou": 0.5},
            "video_3": {"tracker": "ocsort", "conf": 0.3, "iou": 0.5},
            "video_4": {"tracker": "strongsort", "conf": 0.3, "iou": 0.5},
            "video_5": {"tracker": "bytetrack", "conf": 0.3, "iou": 0.5},
        }
        # Lọc theo video được chọn
        if args.video != "all":
            selected = {args.video: selected[args.video]}
        phase3_final_submission(selected)


if __name__ == "__main__":
    main()