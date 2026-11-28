#!/usr/bin/env python3
"""Giải nén Lab4-Student-Starter.zip thẳng vào thư mục dự án.

- Bỏ thư mục cấp 1 trong zip (Lab4-Student-Starter/) để tools/, data/, ... nằm ngay root dự án.
- KHÔNG ghi đè file đã tồn tại (vd. templates/decision_impl.py của nhóm).
Chạy được trên PowerShell và WSL:  python setup_starter.py   (WSL: python3 setup_starter.py)
"""
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ZIP = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "Lab4-Student-Starter.zip"

if not ZIP.is_file():
    sys.exit(f"Không thấy {ZIP}. Hãy đặt Lab4-Student-Starter.zip vào thư mục dự án.")

written, skipped = 0, []
with zipfile.ZipFile(ZIP) as zf:
    for info in zf.infolist():
        parts = Path(info.filename).parts
        if info.is_dir() or not parts or parts[0] == "__MACOSX":
            continue
        rel = Path(*parts[1:]) if len(parts) > 1 else Path(parts[0])
        target = (ROOT / rel).resolve()
        if ROOT not in target.parents:  # chặn zip-slip
            continue
        if target.exists():
            skipped.append(str(rel))
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(zf.read(info))
        written += 1

print(f"Đã giải nén {written} file vào {ROOT}")
if skipped:
    print(f"Giữ nguyên {len(skipped)} file đã có (không ghi đè):")
    for s in skipped:
        print("  -", s)
