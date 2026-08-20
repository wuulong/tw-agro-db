"""
etl.py - aXX 新模組 ETL 洗牌與增量數據入庫範本 (Boilerplate)
"""

import json
import sqlite3
from pathlib import Path
from typing import Union, Dict, Any

def run_etl(json_path: Union[str, Path], db_path: Union[str, Path]) -> Dict[str, Any]:
    json_p = Path(json_path)
    db_p = Path(db_path)
    
    if not json_p.exists():
        raise FileNotFoundError(f"來源 JSON 檔案不存在: {json_p}")
        
    db_p.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_p))
    cursor = conn.cursor()
    
    # 1. 執行實體 Schema 腳本
    schema_p = Path(__file__).parent / "schema.sql"
    if schema_p.exists():
        cursor.executescript(schema_p.read_text(encoding="utf-8"))
        
    # 2. 讀取並解析 JSON 數據
    raw_data = json.loads(json_p.read_text(encoding="utf-8"))
    insert_records = []
    
    for item in raw_data:
        entity_id = item.get("id") or item.get("代碼") or ""
        entity_name = item.get("name") or item.get("名稱") or ""
        if not entity_id:
            continue
            
        attr = {"_v": "1.0.0"}
        insert_records.append((
            str(entity_id),
            str(entity_name),
            item.get("category", ""),
            json.dumps(attr, ensure_ascii=False)
        ))
        
    # 3. 增量寫入 (INSERT OR REPLACE)
    cursor.executemany("""
        INSERT OR REPLACE INTO aXX_entity_table (
            entity_id, entity_name, category_name, attributes_json
        ) VALUES (?, ?, ?, ?)
    """, insert_records)
    
    conn.commit()
    conn.close()
    
    return {"records_inserted": len(insert_records)}
