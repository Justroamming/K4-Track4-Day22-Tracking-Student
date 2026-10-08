# Tóm tắt hoàn thành bài Lab Tracking

## 1. Kiểm tra dữ liệu
- ✅ Tất cả 5 video có ảnh .jpg trong thư mục `img1/`
- ✅ `video_1` có nhãn ground truth (`gt/gt.txt`)
- ✅ `video_2`–`video_5` không có nhãn (đúng như yêu cầu)

| Video | Số frame | Đặc điểm |
|-------|----------|----------|
| video_1 | 600 | Quảng trường, camera tĩnh, ban ngày, mật độ vừa |
| video_2 | 1050 | Phố, camera tĩnh trên cao, ban đêm, rất đông |
| video_3 | 837 | Camera di chuyển, ảnh nhỏ, ít FPS |
| video_4 | 900 | Trong nhà, camera tiến tới, phản chiếu kính |
| video_5 | 750 | Trên xe bus, giao lộ đông, rung lắc |

## 2. Thí nghiệm Baseline (150 frame, conf=0.3, iou=0.5)
Tất cả 5 tracker chạy thành công trên 5 video:

| Tracker | Loại | Video_1 FPS | Video_2 FPS | Video_3 FPS | Video_4 FPS | Video_5 FPS |
|---------|------|-------------|-------------|-------------|-------------|-------------|
| bytetrack | Motion | 6.9 | 6.7 | 7.6 | 6.8 | 6.7 |
| ocsort | Motion | 6.9 | 6.6 | 7.6 | 6.7 | 6.6 |
| botsort | Re-ID | 4.9 | 3.1 | 7.5 | 4.7 | 3.7 |
| strongsort | Re-ID | 4.8 | 2.8 | 7.4 | 4.7 | 3.8 |
| deepocsort | Re-ID | 4.3 | 2.3 | 7.2 | 4.3 | 3.3 |

## 3. Tinh chỉnh tham số cho Video_1 (có nhãn)
Chạy strongsort với các giá trị conf/iou khác nhau:

| Cấu hình | HOTA | MOTA | IDF1 | IDSW | Dets | IDs |
|----------|------|------|------|------|------|-----|
| conf=0.15, iou=0.5 | **11.639** | **5.640** | **10.314** | 12 | 1218 | 39 |
| conf=0.25, iou=0.5 | 8.258 | 3.111 | 6.143 | 10 | 662 | 22 |
| conf=0.3, iou=0.5 | 7.044 | 2.470 | 4.930 | 5 | 528 | 17 |
| conf=0.5, iou=0.5 | 2.968 | 0.797 | 1.558 | 2 | 160 | 9 |
| conf=0.15, iou=0.4 | 11.637 | 5.635 | 10.314 | 12 | 1217 | 39 |
| conf=0.15, iou=0.7 | 10.763 | 5.581 | 9.873 | 13 | 1230 | 43 |

**Cấu hình tốt nhất cho video_1:** `strongsort --conf 0.15 --iou 0.5`

## 4. Cấu hình nộp bài cho 5 video

| Video | Tracker | conf | iou | Lý do chọn |
|-------|---------|------|-----|------------|
| video_1 (quảng trường) | **strongsort** | **0.15** | **0.5** | Re-ID giúp giữ ID tốt, conf thấp phát hiện nhiều người hơn, HOTA cao nhất (11.64) |
| video_2 (phố đêm đông) | **botsort** | **0.25** | **0.5** | Re-ID cần thiết cho cảnh đông, conf thấp hơn 0.3 để bắt người tối |
| video_3 (camera di động) | **ocsort** | **0.3** | **0.5** | Motion-based tốt cho camera chuyển động, nhanh, không phụ thuộc Re-ID |
| video_4 (trong nhà, kính) | **strongsort** | **0.3** | **0.5** | Re-ID giúp phân biệt người qua phản chiếu kính |
| video_5 (xe bus, rung lắc) | **bytetrack** | **0.3** | **0.5** | Motion-based nhanh, ổn định với rung lắc, không cần Re-ID |

## 5. File nộp bài (`runs/nop_bai/`)
- ✅ `video_1.txt` - 63,194 bytes, 1218 detections
- ✅ `video_2.txt` - 193,995 bytes, 3,794 detections  
- ✅ `video_3.txt` - 2,084 bytes, 41 detections
- ✅ `video_4.txt` - 79,726 bytes, 1,533 detections
- ✅ `video_5.txt` - 22,194 bytes, 435 detections

Tất cả 5 file `.txt` và 5 video preview `.mp4` đã sẵn sàng.

## 6. Kết quả chấm video_1 (HOTA / MOTA / IDF1)
```
HOTA:  11.639
MOTA:  5.640
IDF1:  10.314
IDSW:  12
```

## 7. Phân tích nhanh

**Video_1 (quảng trường, tĩnh, ban ngày):** StrongSort với Re-ID cho HOTA cao nhất. Conf=0.15 giúp phát hiện nhiều người nhỏ/xa hơn, bù đắp việc detector YOLO nano bỏ sót.

**Video_2 (phố đêm, rất đông):** BotSort dùng Re-ID + CMC (camera motion compensation) phù hợp camera tĩnh trên cao. Conf=0.25 cân bằng giữa phát hiện người tối và giảm false positive.

**Video_3 (camera di động, ít FPS):** OCSort dựa trên chuyển động (Kalman + observe) hoạt động tốt khi camera di chuyển, không cần Re-ID (chậm hơn).

**Video_4 (trong nhà, phản chiếu kính):** StrongSort với Re-ID giúp phân biệt người thật và phản chiếu, giữ ID ổn định khi người đi qua vùng kính.

**Video_5 (xe bus, rung lắc, giao lộ đông):** ByteTrack nhanh nhất, chỉ dùng motion, phù hợp rung lắc và mật độ cao. Low-level association bằng IoU đủ tốt cho cảnh này.

## 8. Các file đã tạo/sửa đổi
- `scripts/run_tracking.py` - Đã cập nhật tương thích boxmot v25+
- `scripts/run_experiments.py` - Script chạy thí nghiệm tự động
- `scripts/run_final_submission.py` - Script chạy full-frame nộp bài
- `data_lab21/data_lab21/video_1/eval_config.json` - Cấu hình TrackEval
- Patched TrackEval để tương thích NumPy 2.x (np.float → float, np.int → int)