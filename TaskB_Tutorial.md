# Task B Tutorial — Lab 4: Historical Baseline (T1)

## 0. Chuẩn bị

### 0.1. Môi trường

| Thành phần | Yêu cầu | Đã chạy thành công |
|---|---|---|
| Hệ điều hành | Windows hoặc Linux/WSL | Windows |
| Python | >= 3.11 | 3.14.4 |
| Thư viện cho hàm T1 | Python standard library (`decimal`, `json`, `hashlib`) | PASS |
| Spark / Docker / Kubernetes | Không bắt buộc để chạy T1 | Không cần khởi động |

### 0.2. Dữ liệu và file cần có

- `Lab4-Student-Starter.zip` (gói starter của giảng viên).
- `schemas/decision_contract.json` — quy tắc tính và kiểm tra.
- `manifests/inputs_convenience.json` — manifest đi kèm starter; dùng cho self-simulation, **không phải trusted manifest độc lập của TA**.
- `data/upstream/silver_lab3.jsonl` — 9.710 dòng lịch sử.
- `data/upstream/gold_lab3.json` — 20 nhóm tổng hợp.
- `templates/decision_impl.py` — cần có phiên bản đã triển khai `fit_baseline()` của Member B.
- `tests/test_task_b_baseline.py` — 9 bài test riêng T1 đã bổ sung.

---

## 1. Mở workspace và kiểm tra file

Từ project root đã chuẩn bị bằng starter và code Task B:

```powershell
python --version
Test-Path .\tools\run_lab.py
Test-Path .\templates\decision_impl.py
Test-Path .\data\upstream\silver_lab3.jsonl
Test-Path .\data\upstream\gold_lab3.json
```

Repository này chỉ bàn giao code/test/tài liệu Task B; nhận starter từ LMS, đưa các file Task B vào bản starter riêng rồi `cd` vào đúng **project root** (nơi có `tools/`, `templates/`, `data/`). **Starter nguyên bản chưa chứa code T1 đã hoàn thiện:** cần nhận `decision_impl.py` và test của Member B trước khi chạy lại. Không ghi đè công việc C/D nếu file chung đã được sửa.

---

## 2. Kiểm tra đầu vào — Preflight

Chạy từ project root:

```powershell
python tools/run_lab.py preflight --trusted-manifest manifests/inputs_convenience.json
```

**PASS kỳ vọng:** xác minh **15/15 checksum**; kiểm tra đầu vào hợp lệ. Xem bằng chứng:

```powershell
Get-Content .\work\input_check.json
Get-Content .\work\handoff.json
```

Lưu ý: đây là kiểm tra nhất quán với **convenience manifest**, không xác thực nguồn phát hành độc lập. Nếu TA cấp trusted manifest riêng, dùng manifest đó theo chỉ dẫn của TA.

---

## 3. Chạy unit test Task B

Chạy riêng các test T1:

```powershell
python -m unittest discover -s tests -p 'test_task_b_baseline.py' -v
```

**PASS kỳ vọng:** **9/9** test T1. Test kiểm tra median/MAD/scale, `Decimal`, cutoff hai timestamp, ID trùng, nhiệt độ lỗi và các trường hợp biên.

Có thể kiểm tra public suite:

```powershell
python -m unittest discover -s tests -p 'test_public.py' -v
```

**Trạng thái ở thời điểm bàn giao:** public suite **0/8 PASS**, do `score_event`, `evaluate`, `make_action_key` (phần C/D) chưa triển khai. Không sửa các hàm của C/D để ép test PASS; khi nhóm hoàn thành cần chạy lại **8/8**.

---

## 4. Tạo lại baseline — CLI chính thức

```powershell
python tools/run_lab.py baseline --trusted-manifest manifests/inputs_convenience.json
```

Mở artifact:

```powershell
Get-Content .\work\baseline.json
```

**Kết quả đã kiểm chứng trên bộ starter này:**

| Chỉ tiêu | Giá trị |
|---|---:|
| Silver rows | 9.710 |
| Cảm biến | S01–S20 (20/20) |
| Tổng `n` của 20 cảm biến | 9.710 |
| Dòng `is_late` hợp lệ được giữ | 220 |
| S01 `n` | 486 |
| S01 `median_c` | `22.10` |
| S01 `mad_c` | `2.00` |
| S01 `scale_c` | `2.965200` |

**Quy tắc thuật toán:**

```text
median = median(temperature_c)
MAD    = median(abs(temperature_c - median))
scale  = max(1.4826 * MAD, 0.50)
```

- Dùng `Decimal`, `ROUND_HALF_UP`; median/MAD xuất chuỗi **2** chữ số, scale xuất chuỗi **6** chữ số thập phân.
- Có ID trùng, `event_time_utc` **hoặc** `ingest_time_utc` không trước `2026-02-09T00:00:00Z`, nhiệt độ không hữu hạn hoặc ngoài `[-30, 60]` thì `raise ValueError`.
- Không loại cảm biến ít hơn 30 dòng trong `fit_baseline()`; việc `HOLD` thuộc Task C.

---

## 5. Kiểm tra Gold và evidence

Gold có **20 nhóm (4 site × 5 ngày)**. Trung bình site phải tính có trọng số:

```text
site_mean = sum(sum_temperature_c) / sum(n_observations)
```

Không tính trung bình đơn giản của các daily mean. Kết quả đối chiếu đã thực hiện: **20/20 nhóm Gold khớp số dòng và tổng nhiệt độ với Silver**.

Đọc báo cáo đã bàn giao để xem bảng đầy đủ 20 cảm biến và weighted site means:

```powershell
Get-Content .\TASK_B_HANDOFF\TASK_B_VALIDATION_REPORT.md
Get-Content .\TASK_B_HANDOFF\TASK_B_IMPLEMENTATION_REPORT.md
```

---

## 6. Bàn giao cho Member C

| File | Mục đích |
|---|---|
| `templates/decision_impl.py` | Hàm `fit_baseline()` đã hoàn thiện; **file chung B/C/D** |
| `tests/test_task_b_baseline.py` | Kiểm thử T1 |
| `work/baseline.json` | Đầu vào baseline cho T2 |
| `work/input_check.json`, `work/handoff.json` | Evidence preflight |
| `TASK_B_HANDOFF/TASK_B_VALIDATION_REPORT.md` | Kết quả T1 và Gold |
| `TASK_B_HANDOFF/TASK_B_HANDOFF_TO_C.md` | Ghi chú tích hợp T2 |

**Member C tiếp tục:** triển khai `score_event()` và `evaluate()`, chạy calibrate Validation. **Chưa chạy `init_sandbox.py`** đến khi cả 4 hàm trong `decision_impl.py` hoàn thiện, public tests đạt và calibrate xong. Không chỉnh ngưỡng theo Test.

---

## 7. Lỗi thường gặp

| Triệu chứng | Xử lý |
|---|---|
| `No such file` / `FileNotFoundError` | `cd` đúng project root, kiểm tra thư mục ZIP giải nén |
| `ModuleNotFoundError` | Kiểm tra Python và môi trường; T1 dùng standard library |
| Preflight checksum FAIL | Kiểm tra đúng starter/manifest; không sửa dữ liệu hoặc hash để ép PASS |
| `ValueError` trong baseline | Kiểm tra ID trùng, hai timestamp, nhiệt độ theo contract |
| Baseline không đủ 20 cảm biến | Kiểm tra đúng `silver_lab3.jsonl`; không lọc late hợp lệ |
| Public test của C/D FAIL | Chờ hoàn thành các hàm khác; không coi đó là lỗi của T1 nếu 9/9 T1 PASS |
| Hash code không khớp sau lock | Không sửa `decision_impl.py` sau `init_sandbox.py`; nếu bắt buộc sửa, nhóm phải calibrate và reset lock theo đề |

---

## 8. Checklist chạy lại

- [ ] Mở đúng project root, có code `fit_baseline()` đã bàn giao.
- [ ] Preflight PASS, 15/15 checksum.
- [ ] Unit test riêng Task B: 9/9 PASS.
- [ ] CLI baseline chạy thành công.
- [ ] `baseline.json`: 20 cảm biến, tổng 9.710 dòng; S01 `n=486`.
- [ ] Giữ 220 dòng late hợp lệ.
- [ ] Đối chiếu Gold theo weighted mean.
- [ ] Bàn giao artifact cho C; chưa khóa policy.

**Kết quả gốc của Member B:** `TASK B = PASS`, `READY FOR MEMBER C = YES`. Các chỉ số trên là tham chiếu cho đúng bộ dữ liệu Starter đã kiểm tra, không thay cho việc chạy kiểm chứng trên máy nhận bàn giao.
