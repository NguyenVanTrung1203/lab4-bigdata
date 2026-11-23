# Bàn giao Member C

Baseline: `work/baseline.json` trong workspace. Mỗi sensor có `n` integer, `median_c` và `mad_c` string 2 chữ số, `scale_c` string 6 chữ số; input evidence `work/input_check.json`, `work/handoff.json`, `work/gold_context.json`. Dữ liệu course fallback, manifest đi kèm chưa xác thực độc lập.

C dùng score = |temperature - median_c| / scale_c bằng Decimal và ROUND_HALF_UP 6 chữ số; so sánh score đã làm tròn với threshold theo contract. Sensor thiếu hoặc n < 30 là HOLD ở score_event; không lọc trong fit_baseline. C cần thực hiện đầy đủ thứ tự ưu tiên invalid temperature, late, threshold theo contract/docstring. Không sửa input/contract; decision_impl.py dùng chung nên giữ hàm fit_baseline khi tích hợp. T2/calibrate và policy chưa chạy, public suite chưa pass do stub C/D.
