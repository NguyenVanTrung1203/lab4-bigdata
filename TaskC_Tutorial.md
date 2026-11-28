# Task C Tutorial — Lab 4: Event Scoring, Evaluation & Threshold Selection (T2)

> Mọi lệnh chạy bằng **PowerShell, tại thư mục gốc dự án**.

## 0. Chuẩn bị

| Thành phần | Yêu cầu / nguồn |
|---|---|
| Python | >= 3.11 |
| Task B | Chạy lại ở mục 1 (Starter đã giải nén, `fit_baseline()` đã nằm trong `templates/decision_impl.py`) |
| Code Task C | `score_event()` và `evaluate()` trong cùng file `templates/decision_impl.py` |
| Spark / Docker / Kubernetes | **Không cần khởi động** để chạy T2 |

Task C chỉ sửa **hai hàm**: `score_event` và `evaluate`. **Không sửa** `fit_baseline()` (Member B) và `make_action_key()` (Member D).

## 1. Chạy lại Task B trước khi thực hiện Task C

Task C dựa trên kết quả của Task B (`calibrate` gọi `fit_baseline()` của B). Chạy lại Task B theo `TaskB_Tutorial.md` (mục 1.1 đến 4):

```powershell
python setup_starter.py
python tools/run_lab.py preflight --trusted-manifest manifests/inputs_convenience.json
python -m unittest discover -s tests -p 'test_task_b_baseline.py' -v
python tools/run_lab.py baseline --trusted-manifest manifests/inputs_convenience.json
```

(`setup_starter.py` an toàn khi chạy lại: không ghi đè file đã có. Bỏ qua nếu Starter đã giải nén.)

**Kết quả kỳ vọng** (chi tiết ở `TaskB_Tutorial.md`):

```text
Inputs verified.                  <- preflight, 15/15 checksum
Ran 9 tests ... OK                <- test Task B, 9/9
Baseline written.                 <- 20 cảm biến, tổng n = 9710, S01 n = 486

=> PASS
```

Chỉ sang mục 2 khi cả ba bước trên PASS.

Trước khi viết code, đọc `schemas/decision_contract.json` (read-only). Các hằng số C dùng: `min_baseline_rows = 30`, `late_limit_seconds = 900`, `score_decimal_places = 6`, khoảng nhiệt độ `[-30, 60]`, 5 ngưỡng `1.50 / 2.00 / 2.50 / 3.00 / 3.50`, trọng số cost (`false_negative = 50`, `false_positive = 10`, `alert_review = 2`, `hold_review = 10`, chia hiển thị cho `10`).

Nếu workspace chung đã có code của thành viên khác trong `decision_impl.py`: **không copy đè**. Chỉ thay phần thân của `score_event` và `evaluate`.

## 2. Task C làm gì

Hai hàm và một lệnh:

| Thành phần | Việc |
|---|---|
| `score_event(event, baseline, threshold, contract)` | Chấm điểm bất thường cho một quan sát và định tuyến ALERT / NORMAL / HOLD |
| `evaluate(predictions, labels, contract)` | Tính 17 chỉ số: ma trận nhầm lẫn, hai loại recall, cost |
| `calibrate` (CLI có sẵn) | Thử 5 ngưỡng + 2 phương án so sánh trên 600 dòng validation, chọn ngưỡng có `cost_units` nhỏ nhất |

### 2.1. `score_event` — thứ tự ưu tiên (dừng ở bước đầu tiên thỏa)

| Bước | Điều kiện | route / reason | `score` |
|---|---|---|---|
| 1 | Không có cảm biến trong baseline, hoặc `n < 30` | HOLD / `INSUFFICIENT_BASELINE` | `None` |
| 2 | Nhiệt độ không đọc được, NaN/Inf, hoặc ngoài `[-30, 60]` | HOLD / `INVALID_VALUE` | `None` |
| 3 | Tính `score = round_half_up(\|temp − median_c\| / scale_c, 6)` | | chuỗi 6 chữ số thập phân |
| 4 | `ingest_time_utc − event_time_utc > 900` giây | HOLD / `LATE_FOR_ACTION` | **giữ lại score** |
| 5 | Đúng hạn và `score >= threshold` | ALERT / `THRESHOLD` | score |
| 6 | Đúng hạn và `score < threshold` | NORMAL / `BELOW_THRESHOLD` | score |

Điểm dễ sai: dùng `Decimal` (không dùng `float`); làm tròn half-up xuống 6 chữ số **trước** khi so với ngưỡng; điểm đúng bằng ngưỡng vẫn là ALERT; `threshold` có thể là `"3"` nên dùng `Decimal(str(threshold))`; trễ đúng 900 giây vẫn là đúng hạn, 901 giây mới là HOLD.

### 2.2. `evaluate` — kiểm tra đầu vào và công thức

`raise ValueError` nếu: `record_id` trong predictions bị trùng; tập `record_id` không khớp 1-1 với key của `labels`; có nhãn ngoài `{0, 1}`.

`tp / fp / tn / fn` chỉ đếm trên dòng đủ điều kiện (ALERT và NORMAL), **không đếm HOLD**.

```text
precision = tp / (tp + fp)        recall = tp / (tp + fn)       f1 = 2·tp / (2·tp + fp + fn)
coverage  = eligible / n          end_to_end_recall = tp / positive_total
cost_units = 50·fn + 10·fp + 2·alerts + 10·hold          cost = cost_units / 10
```

`positive_total` gồm cả `held_positive` (dòng dương bị HOLD). Mẫu số bằng 0 thì trả `None`. Kết quả có đủ **17 khóa**: `n, eligible, hold, tp, fp, tn, fn, alerts, positive_total, held_positive, precision, recall, f1, coverage, end_to_end_recall, cost_units, cost`.

## 3. Chạy test riêng Task C

Sáu public test liên quan đến C (`-k` lọc theo tên test):

```powershell
python -m unittest discover -s tests -p 'test_public.py' -k threshold -k below -k late -k missing_baseline -k denominators -k label_mismatch -v
```

**PASS kỳ vọng:** 6/6 test C.

**Output thực tế đã kiểm chứng:** 6 dòng `... ok` (`test_below`, `test_denominators`, `test_label_mismatch`, `test_late`, `test_missing_baseline`, `test_threshold_equality`), kết thúc bằng:

```text
Ran 6 tests in 0.002s

OK

=> PASS (6/6)
```

Nếu chạy cả file `test_public.py` (`python -m unittest discover -s tests -p 'test_public.py' -v`), kết quả lúc C bàn giao là 6/8. **Kết quả này ĐÚNG KỲ VỌNG của phạm vi C:**

```text
Ran 8 tests in 0.008s

FAILED (errors=2)

=> PASS (phạm vi C: 6/6 test của C; 2 test còn lại thuộc hàm ngoài phạm vi C)
```

Hai test lỗi là `test_key_policy` và `test_key_repeat` (`NotImplementedError: T3: implement make_action_key`). Đây là hàm thuộc phạm vi của member khác, C không sửa.

## 4. Chạy Calibrate

```powershell
python tools/run_lab.py calibrate --trusted-manifest manifests/inputs_convenience.json --team team-01
Get-Content .\work\validation_report.json
```

`calibrate` đánh giá 5 ngưỡng + 2 phương án so sánh (`never_alert`, `temperature_ge_30`, cùng quy tắc HOLD), chọn `cost_units` nhỏ nhất (hòa: `fn` thấp hơn → `fp` thấp hơn → ngưỡng cao hơn), rồi ghi `work/validation_report.json`, `work/validation_predictions.json`, `work/candidate_policy.json` (và tạo lại `work/baseline.json`).

**Output thực tế đã kiểm chứng:**

```text
Validation complete (selected threshold = 1.50). Freeze templates/decision_impl.py and run python tools/init_sandbox.py.

=> PASS
```

(Phần "Freeze ... init_sandbox.py" là câu nhắc cố định của CLI, nằm ngoài phạm vi C.)

Đối chiếu 5 ngưỡng (600 dòng validation, 90 dòng dương, 20 dòng HOLD ở mọi ngưỡng):

| Ngưỡng | alerts | tp | fp | tn | fn | held_positive | precision | recall | end_to_end_recall | `cost_units` |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **1.50 (chọn)** | 117 | 85 | 32 | 462 | 1 | 4 | 0.7265 | 0.9884 | 0.9444 | **804** |
| 2.00 | 105 | 82 | 23 | 471 | 4 | 4 | 0.7810 | 0.9535 | 0.9111 | 840 |
| 2.50 | 77 | 61 | 16 | 478 | 25 | 4 | 0.7922 | 0.7093 | 0.6778 | 1764 |
| 3.00 | 57 | 47 | 10 | 484 | 39 | 4 | 0.8246 | 0.5465 | 0.5222 | 2364 |
| 3.50 | 31 | 27 | 4 | 490 | 59 | 4 | 0.8710 | 0.3140 | 0.3000 | 3252 |

Hai phương án so sánh:

| Phương án | tp | fp | fn | alerts | hold | `cost_units` |
|---|---:|---:|---:|---:|---:|---:|
| `never_alert` | 0 | 0 | 86 | 0 | 20 | 4500 |
| `temperature_ge_30` | 38 | 12 | 48 | 50 | 20 | 2820 |

Ngưỡng được chọn (1.50) có 17 chỉ số: `n = 600`, `eligible = 580`, `hold = 20`, `coverage = 0.9667`, `f1 = 0.8374`, `cost = 80.4`.

**=> PASS** nếu: có đủ 5 ngưỡng + 2 phương án, mỗi mục 17 chỉ số, ngưỡng chọn là 1.50 với `cost_units = 804`, và cost của quy tắc đã chọn thấp hơn cả hai phương án so sánh.

## 5. Tự kiểm tra bằng tay

Kiểm tra `cost_units` của ngưỡng 1.50: `50·1 + 10·32 + 2·117 + 10·20 = 50 + 320 + 234 + 200 = 804` ✓.

Kiểm tra tính nhất quán:

| Phép kiểm | Kỳ vọng |
|---|---|
| `tp + fn` | 86 = `positive_total` (90) − `held_positive` (4) |
| `eligible` | 580 = `tp + fp + tn + fn` = 600 − 20 HOLD |
| `alerts` | 117 = `tp + fp` |
| `work/validation_predictions.json` | 600 dòng; route: 463 NORMAL, 117 ALERT, 20 HOLD (cả 20 HOLD đều `LATE_FOR_ACTION`) |

## 6. File kết quả

| File | Nguồn / cách có được |
|---|---|
| `templates/decision_impl.py` | Có `score_event()` và `evaluate()` của C |
| `work/validation_report.json` | **Tự sinh** sau `calibrate` (5 ngưỡng + 2 phương án, 17 chỉ số mỗi mục) |
| `work/validation_predictions.json` | **Tự sinh** sau `calibrate` (600 dự đoán của ngưỡng được chọn) |
| `work/candidate_policy.json` | **Tự sinh** sau `calibrate` (ngưỡng chọn + hash code/baseline/contract) |

Các file `work/*.json` bị gitignore, không có trên GitHub.

## 7. Bàn giao

C bàn giao:

| Hạng mục | Nội dung |
|---|---|
| Code | `templates/decision_impl.py` có `score_event()` và `evaluate()` |
| Kết quả chọn ngưỡng | ngưỡng **1.50**, `cost_units = 804` |
| Bằng chứng T2 | `work/validation_report.json`, `work/validation_predictions.json`, `work/candidate_policy.json` |

Phạm vi C kết thúc ở đây.

## 8. Câu hỏi bảo vệ của Member C

**"Eligible Recall có thể tăng trong khi End-to-End Recall giảm bằng cách nào?"**

- `recall = tp / (tp + fn)` chỉ tính trên dòng đủ điều kiện (ALERT/NORMAL). Dòng dương bị HOLD biến mất khỏi mẫu số này.
- `end_to_end_recall = tp / positive_total`, mẫu số gồm cả dòng dương bị HOLD (`held_positive`). Dòng HOLD không bao giờ là `tp`.
- Ví dụ: 10 dòng dương, ban đầu `tp = 8`, `fn = 2`: recall = 0.80, end-to-end = 0.80. Sau đó 2 dòng `fn` và 1 dòng `tp` bị chuyển sang HOLD (trễ): `tp = 7`, `fn = 0`, `held_positive = 3`. Recall = 7/7 = **1.00 (tăng)**, end-to-end = 7/10 = **0.70 (giảm)**.
- Dữ liệu thật: ngưỡng 1.50 có `held_positive = 4`, recall = 0.9884 nhưng end-to-end recall = 0.9444.
- Bài học: HOLD làm recall "đẹp" lên nhưng thực tế vẫn bỏ sót các sự cố đã bị giữ lại, nên phải báo cáo cả hai.

Câu hỏi phụ có thể gặp: vì sao `cost_units` chọn ngưỡng thấp nhất (1.50) dù precision thấp hơn? Vì một `fn` tốn 50 đơn vị, một `fp` chỉ tốn 10; bỏ sót sự cố đắt hơn báo nhầm 5 lần.

## 9. Lỗi thường gặp

| Lỗi | Cách xử lý |
|---|---|
| `NotImplementedError: T2: implement score_event` / `evaluate` | Chưa viết hàm hoặc đang chạy nhầm bản `decision_impl.py` cũ |
| `NotImplementedError: T3: implement make_action_key` ở 2 test | Ngoài phạm vi C; không phải lỗi của C |
| `tools/run_lab.py` không tồn tại | Chưa chạy lại Task B (mục 1) hoặc đang đứng sai thư mục |
| `FileNotFoundError` khi chạy `calibrate` | Chưa chạy lại Task B (mục 1); kiểm tra có `data/events/validation.csv` |
| Điểm lệch 0.000001 so với kỳ vọng | Đang dùng `float` hoặc làm tròn sớm; dùng `Decimal` + `ROUND_HALF_UP` |
| Điểm bằng ngưỡng mà route là NORMAL | So sánh `>` thay vì `>=`, hoặc so sánh trước khi làm tròn |
| Dòng trễ mất `score` | Bước 4 phải giữ chuỗi score, chỉ đổi route sang HOLD |
| `ValueError` ở `evaluate` khi chạy `calibrate` | `record_id` trùng, lệch nhãn, hoặc nhãn ngoài {0, 1}; kiểm tra dữ liệu, không chỉnh nhãn để ép PASS |
| Đã có code B/D trong `decision_impl.py` | Không copy đè; chỉ sửa thân `score_event` và `evaluate` |

## 10. Checklist

- [ ] Đã chạy lại Task B (mục 1): preflight PASS (15/15), test B 9/9, baseline 20 cảm biến.
- [ ] `score_event()` đúng 6 bước ưu tiên; `evaluate()` trả đủ 17 khóa và `ValueError` đúng chỗ.
- [ ] 6/6 test C PASS. Chạy cả `test_public.py` thì **6/8 PASS (`FAILED (errors=2)`) là ĐÚNG KỲ VỌNG** của phạm vi C.
- [ ] `calibrate` in `selected threshold = 1.50`; `work/validation_report.json` có 5 ngưỡng + 2 phương án, mỗi mục 17 chỉ số.
- [ ] Ngưỡng 1.50: `cost_units = 804`, thấp hơn `never_alert` (4500) và `temperature_ge_30` (2820).
- [ ] Bàn giao `decision_impl.py` và các file `work/validation_*.json`, `work/candidate_policy.json` (mục 7).
- [ ] Chuẩn bị câu trả lời cho câu hỏi bảo vệ của C (Eligible Recall vs End-to-End Recall).

**Kết quả ghi nhận của C:** `TASK_C = PASS` với bộ Starter đã kiểm chứng.
