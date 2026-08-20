#!/usr/bin/env python3
"""
[metadata]
script_name = sync_version.py
description = 檢查與一鍵同步 tw-agro-db 專案內所有專書、程式碼、元資料 JSON、VERSION.md 與 README.md 之版本號 (Target Version: 0.7.0)
category = maintenance
version = 1.0.0
"""

import sys
import re
import json
from pathlib import Path

TARGET_VERSION = "0.7.0"

def sync_versions(target_ver=TARGET_VERSION):
    base_dir = Path("events-2026Q3/agro-db-in/tw-agro-db")
    if not base_dir.exists():
        print(f"❌ 找不到專案目錄: {base_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"🚀 開始點檢並同步專案版本號至 `v{target_ver}`...\n")
    updated_files = 0

    # 1. 同步全量 metadata.json (根目錄 + 所有子模組)
    for meta_file in base_dir.glob("**/metadata.json"):
        try:
            with open(meta_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            if data.get("version") != target_ver:
                old_v = data.get("version", "N/A")
                data["version"] = target_ver
                with open(meta_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print(f"  [+] [JSON] 已更新 {meta_file.relative_to(base_dir)}: {old_v} ➔ {target_ver}")
                updated_files += 1
            else:
                print(f"  [✓] [JSON] 已對齊 {meta_file.relative_to(base_dir)}: v{target_ver}")
        except Exception as e:
            print(f"  [-] 無法處理 {meta_file}: {e}")

    # 2. 同步 VERSION.md 頂部目前最新版本
    ver_md = base_dir / "VERSION.md"
    if ver_md.exists():
        with open(ver_md, "r", encoding="utf-8") as f:
            content = f.read()
        
        new_content = re.sub(
            r"\* \*\*目前最新版本\*\*：`v[0-9]+\.[0-9]+\.[0-9]+`",
            f"* **目前最新版本**：`v{target_ver}`",
            content
        )
        if content != new_content:
            with open(ver_md, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"  [+] [MD] 已更新 VERSION.md 頂部版本標籤 ➔ v{target_ver}")
            updated_files += 1

    # 3. 同步專書 20 個章節之 * **當前版本**：`vX.Y.Z`
    book_dir = base_dir / "book"
    if book_dir.exists():
        for md_file in book_dir.glob("*.md"):
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            new_content = re.sub(
                r"\* \*\*當前版本\*\*：`v[0-9]+\.[0-9]+\.[0-9]+`",
                f"* **當前版本**：`v{target_ver}`",
                content
            )
            if content != new_content:
                with open(md_file, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print(f"  [+] [BOOK] 已更新 {md_file.name} 當前版本標籤 ➔ v{target_ver}")
                updated_files += 1

    # 4. 同步 sys_eng/05_verification_testing/SYSTEM_ENGINEERING_ALIGNMENT_AUDIT.md 版本
    audit_md = Path("events-2026Q3/agro-db-in/sys_eng/05_verification_testing/SYSTEM_ENGINEERING_ALIGNMENT_AUDIT.md")
    if audit_md.exists():
        with open(audit_md, "r", encoding="utf-8") as f:
            content = f.read()
        
        new_content = re.sub(
            r"\* \*\*目前版本\*\*：`v[0-9]+\.[0-9]+\.[0-9]+`",
            f"* **目前版本**：`v{target_ver}`",
            content
        )
        if content != new_content:
            with open(audit_md, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"  [+] [SYSENG] 已更新 SYSTEM_ENGINEERING_ALIGNMENT_AUDIT.md ➔ v{target_ver}")
            updated_files += 1

    print(f"\n🎉 版本同步點檢完畢！共更新 {updated_files} 個檔案的版本標籤至 `v{target_ver}`。")

if __name__ == "__main__":
    ver = sys.argv[1] if len(sys.argv) > 1 else TARGET_VERSION
    sync_versions(ver)
