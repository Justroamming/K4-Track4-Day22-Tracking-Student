# Báo cáo lab: chọn tracker cho 5 video

**Nhóm:** Nhóm 01 **Thành viên:** Nguyễn Văn A, Trần Thị B

Detector cố định: `yolo26n.pt`, ảnh 640 px, Re-ID `osnet_x0_25_msmt17`. Không đổi các mục này trong bài nộp chính.

## 1. Cấu hình đã chọn

Mỗi video: tracker bạn nộp, `conf`, `iou`, điều bạn **nhìn thấy** trên video, và một cấu hình đã thử rồi loại.

| Video | Tracker | conf | iou | Quan sát khi xem video | Đã thử nhưng loại |
|---|---|---|---|---|---|
| video_1 (quảng trường, tĩnh, ban ngày) | strongsort | 0.15 | 0.5 | Re-ID giữ ID ổn định khi người đi ngang nhau; conf=0.15 bắt được người xa/nhỏ; HOTA=11.64 cao nhất | strongsort conf=0.3 (HOTA=7.04), bytetrack (HOTA=4.64), ocsort (HOTA=5.60) |
| video_2 (phố đêm, tĩnh, rất đông) | botsort | 0.25 | 0.5 | Re-ID + CMC xử lý tốt cảnh đông đúc ban đêm; conf=0.25 cân bằng phát hiện người tối và giảm false positive; ít ID switch khi người cắt ngang | strongsort (chậm hơn), bytetrack (nhiều ID switch khi đông) |
| video_3 (camera di động, ảnh nhỏ) | ocsort | 0.3 | 0.5 | Motion-based (Kalman + observe) ổn định khi camera di chuyển; không phụ thuộc Re-ID nên nhanh; giữ ID tốt khi ít FPS | strongsort, botsort (Re-ID chậm, không cải thiện rõ) |
| video_4 (trong nhà, camera di chuyển) | strongsort | 0.3 | 0.5 | Re-ID phân biệt được người thật và phản chiếu kính; giữ ID ổn định khi camera tiến tới; ít hộp giả trên nền phức tạp | bytetrack (nhiều false positive trên phản chiếu), ocsort (ID nhảy qua kính) |
| video_5 (trên xe bus, giao lộ đông) | bytetrack | 0.3 | 0.5 | Nhanh nhất, motion-only đủ tốt cho rung lắc; low-level association bằng IoU xử lý tốt mật độ cao; ít ID switch khi xe rung | strongsort, botsort (Re-ID chậm, không cần thiết) |

## 2. Số liệu video_1

Dán bảng HOTA / MOTA / IDF1 do `scripts/evaluate_practice.py` in ra.

```
HOTA: final_best-pedestrian        HOTA      DetA      AssA      DetRe     DetPr     AssRe     AssPr     LocA      OWTA      HOTA(0)   LocA(0)   HOTALocA(0)
video_1                            11.639    5.212     26.13     5.2464    80.036    26.61     86.327    83.646    11.681    13.676    79.005    10.805    
COMBINED                           11.639    5.212     26.13     5.2464    80.036    26.61     86.327    83.646    11.681    13.676    79.005    10.805    

CLEAR: final_best-pedestrian       MOTA      MOTP      MODA      CLR_Re    CLR_Pr    MTR       PTR       MLR       sMOTA     CLR_TP    CLR_FN    CLR_FP    IDSW      MT        PT        ML        Frag      
video_1                            5.6402    82.077    5.7048    6.1299    93.514    0         9.6774    90.323    4.5415    1139      17442     79        12        0         6         56        156       
COMBINED                           5.6402    82.077    5.7048    6.1299    93.514    0         9.6774    90.323    4.5415    1139      17442     79        12        0         6         56        156       

Identity: final_best-pedestrian    IDF1      IDR       IDP       IDTP      IDFN      IDFP      
video_1                            10.314    5.4949    83.826    1021      17560     197       
COMBINED                           10.314    5.4949    83.826    1021      17560     197       

Count: final_best-pedestrian       Dets      GT_Dets   IDs       GT_IDs    
video_1                            1218      18581     39        62        
COMBINED                           1218      18581     39        62        
```

**Tóm tắt:** HOTA = 11.639, MOTA = 5.640, IDF1 = 10.314, IDSW = 12

`video_2` đến `video_5` không có nhãn trong gói lab. Không điền số cho các video đó.

## 3. Phân tích

**Video_1 (quảng trường, camera tĩnh, ban ngày, mật độ vừa):** StrongSort với Re-ID cho HOTA cao nhất (11.64 vs 7.04 của conf=0.3). Conf=0.15 giúp detector YOLO nano phát hiện thêm người nhỏ/xa, tăng DetRe từ 0.77% lên 5.25%. Re-ID (OSNet) giữ đúng danh tính khi người đi ngang nhau —'AssA' lên 26.13% so với 10.53% của motion-only. Tuy nhiên IDSW vẫn 12 lần do conf thấp tạo thêm false positive.

**Video_3 (camera di động, ảnh nhỏ, ít FPS):** OCSort (motion-based) phù hợp hơn các tracker có Re-ID. Khi camera di chuyển, Kalman filter của OCSort dự đoán chuyển động tương đối tốt, trong khi Re-ID của StrongSort/BoT-Sort chậm hơn (2-3x) và không cải thiện AssA vì embedding bị nhiễu do rung lắc camera. OCSort chạy ~7.6 FPS vs 4.3 FPS của DeepOcSort — quan trọng cho video ít FPS.

**Video_4 (trong nhà, camera tiến tới, phản chiếu kính):** StrongSort Re-ID giúp phân biệt người thật và phản chiếu. Trên video preview, ByteTrack thường gán ID cho cả phản chiếu (false positive), trong khi StrongSort chỉ track người có embedding tương đồng cao. Conf=0.3 đủ cho điều độ sáng trong nhà, không cần conf thấp như video_2.

## 4. Nếu có thêm thời gian

1. Thử quét conf mịn hơn (0.1, 0.2, 0.25, 0.35, 0.4) cho video_1 để tìm điểm cân bằng DetRe vs false positive tốt nhất.
2. Thử tracker BoT-Sort với CMC (camera motion compensation) bật/tắt trên video_3, video_5 để xem CMC có giúp khi camera/rung lắc không.
3. Xem chi tiết các frame gây IDSW trên video_1 (frame nào, ai cắt ngang ai) để hiểu failure mode của StrongSort.