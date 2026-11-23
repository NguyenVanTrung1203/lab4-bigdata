# Triển khai Task B

Workspace: `thư mục project Lab 4`; Python `3.14.4`.

Chỉ sửa `templates/decision_impl.py`, hàm `fit_baseline`; thêm `tests/test_task_b_baseline.py`. Không sửa score_event, evaluate, make_action_key, verify_audit. Median chẵn/lẻ và MAD tính Decimal chính xác, scale=max(contract mad_scale × MAD, scale_floor_c); chỉ quantize đầu ra ROUND_HALF_UP. Reject duplicate ID, timestamps không hợp lệ hoặc >= cutoff khi quy đổi UTC, nhiệt độ không hữu hạn/ngoài miền; không bỏ late hoặc sensor ít dòng.

Contract: cutoff 2026-02-09T00:00:00Z, nhiệt độ [-30,60], mad_scale=1.4826, floor=0.50, median/MAD 2 và scale 6 chữ số.
