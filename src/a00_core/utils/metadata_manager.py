import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Union, Dict, Any, List

def write_dual_metadata(
    db_path: Union[str, Path],
    module_id: str,
    module_name: str,
    table_name: str,
    agency_name: str,
    dataset_name: str,
    source_url: str,
    local_sample_path: str,
    tables: List[str],
    views: List[str],
    json_output_path: Union[str, Path]
) -> Dict[str, Any]:
    """
    通用雙軌 Metadata 寫入器
    同時更新 SQL 實體系統表 sys_module_metadata 與子模組本地 metadata.json
    """
    db_p = Path(db_path)
    if not db_p.exists():
        raise FileNotFoundError(f"DB 檔案不存在: {db_p}")
        
    conn = sqlite3.connect(str(db_p))
    cursor = conn.cursor()
    
    # 計算來源採樣 Hash
    from src.a00_core.utils.sync_guard import compute_file_sha256
    file_hash = compute_file_sha256(local_sample_path)
    
    # 1. 查詢目標表數據筆數
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    rec_count = cursor.fetchone()[0]
    
    # 2. 更新 SQL 系統表 sys_module_metadata
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sys_module_metadata (
            module_id TEXT PRIMARY KEY,
            module_name TEXT NOT NULL,
            table_name TEXT NOT NULL,
            record_count INTEGER DEFAULT 0,
            schema_version TEXT DEFAULT '1.0.0',
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    cursor.execute("""
        INSERT INTO sys_module_metadata (module_id, module_name, table_name, record_count, schema_version, last_updated)
        VALUES (?, ?, ?, ?, '1.0.0', CURRENT_TIMESTAMP)
        ON CONFLICT(module_id) DO UPDATE SET
            record_count=excluded.record_count,
            last_updated=CURRENT_TIMESTAMP;
    """, (module_id.upper(), module_name, table_name, rec_count))
    conn.commit()
    conn.close()
    
    # 3. 寫入 JSON metadata
    now_str = datetime.now().astimezone().isoformat()
    meta = {
        "module_id": module_name,
        "name": dataset_name,
        "version": "1.0.0",
        "data_source": {
            "agency": agency_name,
            "dataset_name": dataset_name,
            "source_url": source_url,
            "download_method": "opendata_cli / curl",
            "local_sample_path": str(local_sample_path),
            "sha256_hash": file_hash,
            "last_updated": now_str
        },
        "tables": tables,
        "views": views,
        "record_counts": {
            table_name: rec_count
        },
        "status": "ACTIVE"
    }
    
    json_out = Path(json_output_path)
    json_out.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return meta
