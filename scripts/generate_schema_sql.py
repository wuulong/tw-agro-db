#!/usr/bin/env python3
"""
[metadata]
script_name = generate_schema_sql.py
description = 從實體 SQLite 資料庫 Dump 原生 DDL，並結合 schema_comments.json 自動產生帶中文備註的權威 schema.sql
category = maintenance
version = 1.0.0
"""

import sqlite3
import json
import sys
from pathlib import Path

def generate_annotated_schema(db_path: str, config_path: str, output_path: str) -> None:
    """自動讀取 SQLite .schema 與 JSON 備註，編譯產生權威 schema.sql 檔"""
    db_file = Path(db_path)
    config_file = Path(config_path)
    out_file = Path(output_path)

    if not db_file.exists():
        raise FileNotFoundError(f"資料庫不存在: {db_path}")
    if not config_file.exists():
        raise FileNotFoundError(f"備註配置檔不存在: {config_path}")

    with open(config_file, "r", encoding="utf-8") as f:
        comments_config = json.load(f).get("tables", {})

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 取得 SQLite 中所有 CREATE TABLE / CREATE VIEW 語法
    cursor.execute("SELECT name, type, sql FROM sqlite_master WHERE sql IS NOT NULL AND name NOT LIKE 'sqlite_%' ORDER BY type, name")
    schema_objects = cursor.fetchall()
    conn.close()

    lines = [
        "-- ==============================================================================",
        "-- tw-agro-db (台灣農業開放大數據引擎) 大一統全庫 Schema 與 DDL 定義檔 (自動生成)",
        "-- 生成腳本: scripts/generate_schema_sql.py",
        "-- 備註來源: src/config/schema_comments.json",
        "-- ==============================================================================\n"
    ]

    for name, obj_type, raw_sql in schema_objects:
        tbl_info = comments_config.get(name, {})
        tbl_comment = tbl_info.get("table_comment", "")
        cols_comments = tbl_info.get("columns", {})

        if tbl_comment:
            lines.append(f"-- ------------------------------------------------------------------------------")
            lines.append(f"-- {name} ({tbl_comment})")
            lines.append(f"-- ------------------------------------------------------------------------------")
        
        # 逐欄位注入註解
        sql_lines = raw_sql.split("\n")
        annotated_sql_lines = []
        for line in sql_lines:
            stripped = line.strip()
            matched_col = None
            for col_name, col_desc in cols_comments.items():
                if stripped.startswith(col_name + " ") or stripped.startswith(f'"{col_name}" ') or stripped.startswith(f"`{col_name}` "):
                    matched_col = (col_name, col_desc)
                    break
            
            if matched_col and not line.strip().endswith(","):
                annotated_sql_lines.append(f"{line}  -- {matched_col[1]}")
            elif matched_col:
                # 處理帶逗號的欄位
                clean_line = line.rstrip()
                if clean_line.endswith(","):
                    annotated_sql_lines.append(f"{clean_line[:-1]}  -- {matched_col[1]},")
                else:
                    annotated_sql_lines.append(f"{line}  -- {matched_col[1]}")
            else:
                annotated_sql_lines.append(line)

        lines.append("\n".join(annotated_sql_lines) + ";\n")

    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"✅ 成功編譯帶有中文備註的權威 schema.sql 至: {output_path}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="編譯動態 schema.sql 工具")
    parser.add_argument("--db", default="db/agro.db", help="SQLite 資料庫路徑")
    parser.add_argument("--config", default="src/config/schema_comments.json", help="備註 JSON 配置檔")
    parser.add_argument("--out", default="schema.sql", help="輸出 schema.sql 路徑")
    args = parser.parse_args()

    try:
        generate_annotated_schema(args.db, args.config, args.out)
    except Exception as e:
        print(f"❌ 編譯失敗: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
