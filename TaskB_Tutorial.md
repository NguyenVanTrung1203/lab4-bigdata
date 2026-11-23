# Task B Tutorial — Lab 4: Historical Baseline (T1)

## 0. Chuẩn bị

| Thành phần | Yêu cầu / nguồn |
|---|---|
| Python | >= 3.11 (đã chạy T1 trên Windows Python 3.14.4) |
| Starter | `Lab4-Student-Starter.zip` do giảng viên cung cấp |
| Code Task B | [GitHub — branch `trungnguyen-taskB`](https://github.com/NguyenVanTrung1203/lab4-bigdata/tree/trungnguyen-taskB) |
| Spark / Docker / Kubernetes | **Không cần khởi động** để chạy T1 |

Starter cung cấp `tools/`, `schemas/`, `manifests/`, `data/`. GitHub cung cấp code `fit_baseline()` và test Task B. **Không chỉ clone GitHub rồi chạy lệnh:** repository bàn giao không chứa toàn bộ Starter.

## 1. Tải code và chuẩn bị workspace (PowerShell)

### 1.1. Giải nén Starter

Ví dụ đặt ZIP trong Downloads; giải nén ở thư mục riêng:

```powershell
$base = Join-Path $HOME 'lab4-taskb'
New-Item -ItemType Directory -Force -Path $base | Out-Null
Expand-Archive -LiteralPath (Join-Path $HOME 'Downloads\Lab4-Student-Starter.zip') -DestinationPath (Join-Path $base 'starter')
```

Tìm **project root thực tế** (thư mục chứa đồng thời `tools/`, `templates/`, `data/`), rồi chuyển vào đó:

```powershell
Get-ChildItem (Join-Path $base 'starter')
# Đổi đường dẫn dưới đây nếu ZIP có thêm thư mục con:
$project = Join-Path $base 'starter\Lab4-Student-Starter'
cd $project
Test-Path .\tools\run_lab.py
Test-Path .\schemas\decision_contract.json
Test-Path .\data\upstream\silver_lab3.jsonl
```

Nếu một trong các lệnh `Test-Path` trả `False`, kiểm tra lại cấu trúc giải nén và sửa `$project` thành thư mục gốc đúng trước khi tiếp tục.

### 1.2. Lấy code Task B từ GitHub

```powershell
cd $base
git clone --branch trungnguyen-taskB --single-branch https://github.com/NguyenVanTrung1203/lab4-bigdata.git taskb-git
Test-Path .\taskb-git\templates\decision_impl.py
Test-Path .\taskb-git\tests\test_task_b_baseline.py
```

**Chỉ khi vừa giải nén Starter mới, chưa có thay đổi của C/D:**

```powershell
Copy-Item "$base\taskb-git\templates\decision_impl.py" "$project\templates\decision_impl.py"
Copy-Item "$base\taskb-git\tests\test_task_b_baseline.py" "$project\tests\test_task_b_baseline.py"
cd $project
```

Nếu đang dùng workspace chung mà C/D đã sửa `decision_impl.py`, **không chạy lệnh Copy-Item thứ nhất**: chỉ tích hợp phần `fit_baseline()` từ branch B, giữ nguyên `score_event()`, `evaluate()`, `make_action_key()` của C/D.

## 2. Chạy Preflight

Tại project root:

```powershell
python --version
python tools/run_lab.py preflight --trusted-manifest manifests/inputs_convenience.json
Get-Content .\work\input_check.json
Get-Content .\work\handoff.json
```

**PASS kỳ vọng:** 15/15 checksum hợp lệ. `inputs_convenience.json` chỉ xác minh tính nhất quán nội bộ Starter, **không thay thế trusted manifest độc lập của TA** (nếu TA yêu cầu).

## 3. Chạy test riêng Task B

```powershell
python -m unittest discover -s tests -p 'test_task_b_baseline.py' -v
```

**PASS kỳ vọng:** 9/9 test T1.

Bộ public tests toàn nhóm:

```powershell
python -m unittest discover -s tests -p 'test_public.py' -v
```

**Tại thời điểm B bàn giao:** 0/8 public tests PASS vì các hàm của C/D chưa triển khai. Sau khi C/D hoàn thiện, chạy lại và yêu cầu 8/8 PASS; không sửa phần của họ chỉ để ép kết quả.

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

Quy tắc: dùng `Decimal`; `median = median(temperature)`, `MAD = median(|temperature - median|)`, `scale = max(1.4826 × MAD, 0.50)`. Chỉ làm tròn khi xuất chuỗi (`ROUND_HALF_UP`: median/MAD 2 chữ số; scale 6 chữ số). Gặp `record_id` trùng, một trong hai timestamp >= `2026-02-09T00:00:00Z`, hoặc nhiệt độ NaN/Inf/ngoài `[-30,60]` thì `raise ValueError`. Không loại cảm biến có `n < 30` ở T1.

## 5. Kiểm tra Gold

```powershell
Get-Content .\data\upstream\gold_lab3.json
```

Đối chiếu 20 nhóm (4 site × 5 ngày). Trung bình site phải tính có trọng số:

```text
site_mean = sum(sum_temperature_c) / sum(n_observations)
```

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
| `tools/run_lab.py` không tồn tại | Đang ở thư mục GitHub thay vì **Starter project root**, hoặc `$project` sai |
| Không thấy `work/input_check.json` | Chạy preflight trước; kiểm tra CLI có PASS không |
| Không thấy `work/baseline.json` | Chạy baseline sau khi đã tích hợp code B |
| Test `fit_baseline` lỗi | Kiểm tra việc copy/tích hợp code, contract và dữ liệu Starter |
| Public tests C/D lỗi | Chờ C/D hoàn thành; không tự sửa các hàm của họ |
| Checksum FAIL | Dùng đúng Starter/manifest; không chỉnh dữ liệu/hash để ép PASS |
| Đã có code C/D trong `decision_impl.py` | Không copy đè; chỉ merge phần `fit_baseline()` |

## 8. Checklist

- [ ] Có Starter đầy đủ và đã lấy code từ branch `trungnguyen-taskB`.
- [ ] Đang ở đúng project root; `python >= 3.11`.
- [ ] Preflight PASS (15/15 checksum), có `work/input_check.json`.
- [ ] Test T1 PASS (9/9).
- [ ] CLI baseline PASS, có `work/baseline.json` với 20 cảm biến, tổng `n=9710`.
- [ ] S01 `n=486`, giữ 220 dòng late hợp lệ.
- [ ] Đối chiếu Gold bằng weighted mean; bàn giao artifact cho C.

**Kết quả ghi nhận của B:** `TASK_B = PASS`, `READY_FOR_MEMBER_C = YES` với bộ Starter đã kiểm chứng.
