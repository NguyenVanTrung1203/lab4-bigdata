# Task B Tutorial — Lab 4: Historical Baseline (T1)

> Mọi lệnh chạy bằng **PowerShell, tại thư mục gốc dự án**.

## 0. Chuẩn bị

| Thành phần | Yêu cầu / nguồn |
|---|---|
| Python | >= 3.11 (đã chạy T1 trên Windows Python 3.12.10 và 3.14.4) |
| Starter | `Lab4-Student-Starter.zip` do giảng viên cung cấp |
| Code Task B | [GitHub — branch `trungnguyen-taskB`](https://github.com/NguyenVanTrung1203/lab4-bigdata/tree/trungnguyen-taskB) |
| Spark / Docker / Kubernetes | **Không cần khởi động** để chạy T1 |

Starter cung cấp `tools/`, `schemas/`, `manifests/`, `data/`. GitHub cung cấp code `fit_baseline()` và test Task B. **Không chỉ clone GitHub rồi chạy lệnh:** repository bàn giao không chứa toàn bộ Starter.

## 1. Tải code và chuẩn bị workspace

### 1.1. Đưa Starter vào dự án và giải nén

Dự án chính là repo GitHub của branch Task B (đã có `templates/decision_impl.py`, `tests/test_task_b_baseline.py`). Chưa có repo thì clone, rồi đứng trong thư mục đó:

```powershell
git clone --branch trungnguyen-taskB --single-branch https://github.com/NguyenVanTrung1203/lab4-bigdata.git
cd lab4-bigdata
```

Copy `Lab4-Student-Starter.zip` vào thư mục gốc dự án (cùng cấp `setup_starter.py`), rồi giải nén ngay tại đó:

```powershell
python setup_starter.py
```

Script bỏ thư mục cấp 1 của ZIP nên `tools/`, `schemas/`, `manifests/`, `data/` nằm ngay root dự án, và **không ghi đè** file đã có (vd. `templates/decision_impl.py`). `.gitignore` đã loại ZIP, các thư mục Starter và `work/` khỏi git nên không bị push.

Kiểm tra root dự án:

```powershell
Test-Path .\tools\run_lab.py
Test-Path .\schemas\decision_contract.json
Test-Path .\data\upstream\silver_lab3.jsonl
```

Nếu một trong các lệnh `Test-Path` trả `False`, kiểm tra lại ZIP đã nằm đúng root và `setup_starter.py` đã chạy chưa.

### 1.2. Code Task B

Code Task B (`fit_baseline()` và test) đã nằm sẵn trong repo, **không cần Copy-Item**. Nếu workspace chung mà C/D đã sửa `decision_impl.py`: `setup_starter.py` không đè file này; chỉ tích hợp phần `fit_baseline()` từ branch B, giữ nguyên `score_event()`, `evaluate()`, `make_action_key()` của C/D.

## 2. Chạy Preflight

Tại project root:

```powershell
python --version
python tools/run_lab.py preflight --trusted-manifest manifests/inputs_convenience.json
Get-Content .\work\input_check.json
Get-Content .\work\handoff.json
```

**PASS kỳ vọng:** 15/15 checksum hợp lệ. `inputs_convenience.json` chỉ xác minh tính nhất quán nội bộ Starter, **không thay thế trusted manifest độc lập của TA** (nếu TA yêu cầu).

**Output thực tế đã kiểm chứng:**

```text
Python 3.12.10            <- chỉ cần >= 3.11
Inputs verified.
```

`work/input_check.json` (rút gọn):

| Trường | Giá trị kỳ vọng |
|---|---|
| `verified` | danh sách đủ **15** file (`data/event_sources/*`, `data/events/*`, `data/labels/*`, `data/upstream/*`, `schemas/*`) |
| `trusted_manifest_sha256` | `1a4a8475166bea72626ea3b4fc4fdf84b1681dac18f7fa58844b7e60b7fc806e` |
| `handoff_mode` | `course-fallback` |
| `silver_rows` | `9710` |
| `gold_rows` | `20` |
| `history_max_event` | `2026-02-06T01:40:00Z` (phải < `2026-02-09T00:00:00Z`) |
| `history_max_ingest` | `2026-02-06T01:41:00Z` (phải < `2026-02-09T00:00:00Z`) |

`work/handoff.json`: `mode = course-fallback`; `silver_rows = 9710`; `gold_rows = 20`; `fit_cutoff_utc = 2026-02-09T00:00:00Z`; `silver_delta_version` và `gold_delta_version` đều `null`. `course-fallback` là bản xuất logic từ Lab 3 TA Reference, **không phải** snapshot Delta thật. Đây là trạng thái bình thường của bộ Starter, không phải lỗi.

## 3. Chạy test riêng Task B

```powershell
python -m unittest discover -s tests -p 'test_task_b_baseline.py' -v
```

**PASS kỳ vọng:** 9/9 test T1.

**Output thực tế đã kiểm chứng:** 9 dòng `... ok` (`test_contract_values`, `test_cutoff_each_timestamp_and_timezone`, `test_duplicate`, `test_even_median_and_mad`, `test_floor_and_small_sensor`, `test_half_up_without_early_rounding`, `test_invalid_temperatures`, `test_limits_and_late_kept`, `test_odd_median_and_mad`), kết thúc bằng:

```text
Ran 9 tests in 0.006s

OK
```

Bộ public tests toàn nhóm:

```powershell
python -m unittest discover -s tests -p 'test_public.py' -v
```

**Tại thời điểm B bàn giao:** 0/8 public tests PASS vì các hàm của C/D chưa triển khai. **Kết quả 0/8 này ĐÚNG KỲ VỌNG, không phải lỗi.** Sau khi C/D hoàn thiện, chạy lại và yêu cầu 8/8 PASS; không sửa phần của họ chỉ để ép kết quả.

**Output thực tế đã kiểm chứng lúc bàn giao (đây là kết quả BÌNH THƯỜNG, không phải lỗi của B):**

```text
Ran 8 tests in 0.008s

FAILED (errors=8)
```

Cả 8 test (`test_below`, `test_denominators`, `test_key_policy`, `test_key_repeat`, `test_label_mismatch`, `test_late`, `test_missing_baseline`, `test_threshold_equality`) báo `ERROR` với `NotImplementedError`:

| Lỗi | Thuộc về | Số test |
|---|---|---:|
| `T2: implement score_event` | C | 4 (`test_below`, `test_late`, `test_missing_baseline`, `test_threshold_equality`) |
| `T2: implement evaluate` | C | 2 (`test_denominators`, `test_label_mismatch`) |
| `T3: implement make_action_key` | D | 2 (`test_key_policy`, `test_key_repeat`) |

## 4. Tạo lại Baseline

```powershell
python tools/run_lab.py baseline --trusted-manifest manifests/inputs_convenience.json
Get-Content .\work\baseline.json
```

Đối chiếu với **kết quả đã kiểm chứng của cùng bộ Starter**:

| Chỉ tiêu | Kỳ vọng |
|---|---:|
| Silver | 9.710 bản ghi |
| Baseline | 20/20 cảm biến S01–S20 |
| Tổng `n` | 9.710 |
| Bản ghi `is_late` hợp lệ được giữ | 220 |
| S01 `n` | 486 |
| S01 `median_c` | `22.10` |
| S01 `mad_c` | `2.00` |
| S01 `scale_c` | `2.965200` |

**Output thực tế đã kiểm chứng:** CLI in `Baseline written.`, rồi `work/baseline.json` có đúng 20 mục. Mọi cảm biến đều có `mad_c = "2.00"` và `scale_c = "2.965200"`; chỉ `n` và `median_c` khác nhau:

| Cảm biến | `n` | `median_c` | Cảm biến | `n` | `median_c` |
|---|---:|---|---|---:|---|
| S01 | 486 | `22.10` | S11 | 485 | `23.10` |
| S02 | 486 | `22.20` | S12 | 485 | `23.20` |
| S03 | 486 | `22.30` | S13 | 485 | `23.30` |
| S04 | 486 | `22.40` | S14 | 485 | `23.40` |
| S05 | 486 | `22.50` | S15 | 485 | `23.50` |
| S06 | 486 | `22.60` | S16 | 485 | `23.60` |
| S07 | 486 | `22.70` | S17 | 485 | `23.70` |
| S08 | 486 | `22.80` | S18 | 485 | `23.80` |
| S09 | 486 | `22.90` | S19 | 485 | `23.90` |
| S10 | 486 | `23.00` | S20 | 485 | `22.00` |

Kiểm tra tổng: 10 × 486 + 10 × 485 = **9.710**.

> Lưu ý: ví dụ trong đề bài ghi S01 `n = 485`. Số thực tế của S01 là **486**; 485 chỉ là số minh họa trong đề. Dùng 486 để đối chiếu.

Quy tắc: dùng `Decimal`; `median = median(temperature)`, `MAD = median(|temperature - median|)`, `scale = max(1.4826 × MAD, 0.50)`. Chỉ làm tròn khi xuất chuỗi (`ROUND_HALF_UP`: median/MAD 2 chữ số; scale 6 chữ số). Gặp `record_id` trùng, một trong hai timestamp >= `2026-02-09T00:00:00Z`, hoặc nhiệt độ NaN/Inf/ngoài `[-30,60]` thì `raise ValueError`. Không loại cảm biến có `n < 30` ở T1.

## 5. Kiểm tra Gold

```powershell
Get-Content .\data\upstream\gold_lab3.json
```

Đối chiếu 20 nhóm (4 site × 5 ngày). Trung bình site phải tính có trọng số:

```text
site_mean = sum(sum_temperature_c) / sum(n_observations)
```

**Kết quả thực tế đã kiểm chứng:** 20/20 nhóm (site × ngày) khớp Silver cả `n_observations` lẫn `sum_temperature_c`. Trung bình site có trọng số:

| Site | `sum(n_observations)` | `sum(sum_temperature_c)` | `site_mean` |
|---|---:|---:|---:|
| zone-1 | 2430 | 54219.00 | 22.312346 |
| zone-2 | 2430 | 55437.00 | 22.813580 |
| zone-3 | 2425 | 56534.50 | 23.313196 |
| zone-4 | 2425 | 56740.00 | 23.397938 |

Không lấy trung bình đơn giản của các trung bình theo ngày. Lần chạy của B đã kiểm chứng Gold khớp Silver trên 20/20 nhóm; người chạy lại cần đối chiếu trên dữ liệu thực tế, không coi ghi chú này là bằng chứng thay thế.

## 6. File kết quả và bàn giao cho C

| File | Nguồn / cách có được |
|---|---|
| `templates/decision_impl.py` | Lấy từ branch Task B, tích hợp `fit_baseline()` |
| `tests/test_task_b_baseline.py` | Lấy từ branch Task B |
| `work/input_check.json`, `work/handoff.json` | **Tự sinh** sau `preflight` |
| `work/baseline.json` | **Tự sinh** sau `baseline`; Member C dùng cho T2 |

Các file `work/*.json` **không nhất thiết có trên GitHub**. Không cần thư mục `TASK_B_HANDOFF/` để chạy lại. Member C tiếp tục `score_event()`, `evaluate()` và calibrate trên Validation. **Chưa chạy `init_sandbox.py`** cho đến khi cả bốn hàm của `decision_impl.py` hoàn thiện, public tests PASS và calibrate hoàn tất.

## 7. Lỗi thường gặp

| Lỗi | Cách xử lý |
|---|---|
| `tools/run_lab.py` không tồn tại | Chưa chạy `setup_starter.py` (ZIP phải nằm ở root dự án), hoặc đang đứng sai thư mục |
| Không thấy `work/input_check.json` | Chạy preflight trước; kiểm tra CLI có PASS không |
| Không thấy `work/baseline.json` | Chạy baseline sau khi đã tích hợp code B |
| Test `fit_baseline` lỗi | Kiểm tra việc tích hợp code, contract và dữ liệu Starter |
| Public tests C/D lỗi | Chờ C/D hoàn thành; không tự sửa các hàm của họ |
| Checksum FAIL | Dùng đúng Starter/manifest; không chỉnh dữ liệu/hash để ép PASS |
| Đã có code C/D trong `decision_impl.py` | Không copy đè; chỉ merge phần `fit_baseline()` |

## 8. Checklist

- [ ] ZIP Starter nằm ở root dự án, đã chạy `setup_starter.py`; code lấy từ branch `trungnguyen-taskB`.
- [ ] Đang ở đúng project root; `python >= 3.11`.
- [ ] Preflight PASS (15/15 checksum), có `work/input_check.json`.
- [ ] Test T1 PASS (9/9). `test_public.py` lúc này **0/8 PASS (`FAILED (errors=8)`) là ĐÚNG KỲ VỌNG** (chờ C/D).
- [ ] CLI baseline PASS, có `work/baseline.json` với 20 cảm biến, tổng `n=9710`.
- [ ] S01 `n=486`, giữ 220 dòng late hợp lệ.
- [ ] Đối chiếu Gold bằng weighted mean; bàn giao artifact cho C.

**Kết quả ghi nhận của B:** `TASK_B = PASS`, `READY_FOR_MEMBER_C = YES` với bộ Starter đã kiểm chứng.
