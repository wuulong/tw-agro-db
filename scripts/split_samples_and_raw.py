#!/usr/bin/env python3
"""
[metadata]
script_name = split_samples_and_raw.py
description = 將過往龐大的 agro_poc_samples 分離為精簡微型 data/samples/ (限 20 筆) 與全量 data/raw/
category = maintenance
version = 1.0.0
"""

import json
from pathlib import Path

def process_data_split():
    base_dir = Path(".")
    poc_dir = base_dir / "agro_poc_samples"
    samples_dir = base_dir / "data" / "samples"
    raw_dir = base_dir / "data" / "raw"

    samples_dir.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)

    if not poc_dir.exists():
        print(f"⚠️ 找不到 {poc_dir}，跳過移轉。")
        return

    for json_file in poc_dir.glob("*.json"):
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 1. 搬移至全量 data/raw/
        raw_file = raw_dir / json_file.name
        with open(raw_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        # 2. 抽樣前 20 筆至 data/samples/
        sample_data = data
        if isinstance(data, list):
            sample_data = data[:20]
        elif isinstance(data, dict) and "data" in data and isinstance(data["data"], list):
            sample_data = dict(data)
            sample_data["data"] = data["data"][:20]

        sample_file = samples_dir / json_file.name
        with open(sample_file, "w", encoding="utf-8") as f:
            json.dump(sample_data, f, ensure_ascii=False, indent=2)

        print(f"📦 已處理 {json_file.name}: Raw({len(data) if isinstance(data, list) else 'dict'}) -> Samples(前 20 筆)")

    print("\n✅ 資料分離重構完成！")

if __name__ == "__main__":
    process_data_split()
