# Kiểm chứng Task B

Preflight chính thức PASS; work/input_check.json xác nhận 15/15 object. Starter convenience manifest xác minh nhất quán byte, không tự chứng minh authenticity độc lập. Silver 9.710 dòng, 220 late hợp lệ; Gold 20 nhóm, 4 site × 5 ngày. CLI baseline chạy thành công. Không tạo sandbox hoặc chạy calibrate.

Test riêng T1 9/9 PASS (`T1_TESTS.log`). Suite đầy đủ 17 tests: 9 PASS, 8 ERROR do score_event/evaluate/make_action_key chưa triển khai; public 0/8 PASS, không phải lỗi đã sửa của T1.

Baseline CLI `work/baseline.json` được so từng sensor với oracle độc lập dùng statistics.median và Decimal: 20/20 khớp.

| Sensor | n | Median | MAD | Scale | Status |
|---|---:|---:|---:|---:|---|
| S01 | 486 | 22.10 | 2.00 | 2.965200 | PASS |
| S02 | 486 | 22.20 | 2.00 | 2.965200 | PASS |
| S03 | 486 | 22.30 | 2.00 | 2.965200 | PASS |
| S04 | 486 | 22.40 | 2.00 | 2.965200 | PASS |
| S05 | 486 | 22.50 | 2.00 | 2.965200 | PASS |
| S06 | 486 | 22.60 | 2.00 | 2.965200 | PASS |
| S07 | 486 | 22.70 | 2.00 | 2.965200 | PASS |
| S08 | 486 | 22.80 | 2.00 | 2.965200 | PASS |
| S09 | 486 | 22.90 | 2.00 | 2.965200 | PASS |
| S10 | 486 | 23.00 | 2.00 | 2.965200 | PASS |
| S11 | 485 | 23.10 | 2.00 | 2.965200 | PASS |
| S12 | 485 | 23.20 | 2.00 | 2.965200 | PASS |
| S13 | 485 | 23.30 | 2.00 | 2.965200 | PASS |
| S14 | 485 | 23.40 | 2.00 | 2.965200 | PASS |
| S15 | 485 | 23.50 | 2.00 | 2.965200 | PASS |
| S16 | 485 | 23.60 | 2.00 | 2.965200 | PASS |
| S17 | 485 | 23.70 | 2.00 | 2.965200 | PASS |
| S18 | 485 | 23.80 | 2.00 | 2.965200 | PASS |
| S19 | 485 | 23.90 | 2.00 | 2.965200 | PASS |
| S20 | 485 | 22.00 | 2.00 | 2.965200 | PASS |

Gold count/sum đối chiếu độc lập với Silver 20/20 nhóm; weighted mean theo tổng/count:

| Site | n | Sum | Weighted mean |
|---|---:|---:|---:|
| zone-1 | 2430 | 54219.00 | 22.31234567901234567901234568 |
| zone-2 | 2430 | 55437.00 | 22.81358024691358024691358025 |
| zone-3 | 2425 | 56534.50 | 23.31319587628865979381443299 |
| zone-4 | 2425 | 56740.00 | 23.39793814432989690721649485 |
