"""
fts.py - aXX 全文檢索 FTS5 倒排索引建置範本 (Boilerplate)
"""

import sqlite3
from pathlib import Path
from typing import Union, Dict, Any

def build_fts_index(db_path: Union[str, Path]) -> Dict[str, Any]:
    db_p = Path(db_path)
    if not db_p.exists():
        raise FileNotFoundError(f"DB 檔案不存在: {db_p}")
        
    conn = sqlite3.connect(str(db_p))
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS aXX_entity_fts USING fts5(
            entity_id UNINDEXED,
            entity_name,
            category_name,
            tokenize='unicode61'
        );
    """)
    
    cursor.execute("DELETE FROM aXX_entity_fts")
    
    cursor.execute("""
        INSERT INTO aXX_entity_fts (entity_id, entity_name, category_name)
        SELECT entity_id, entity_name, category_name
        FROM aXX_entity_table
    """)
    
    cnt = cursor.rowcount
    conn.commit()
    conn.close()
    return {"indexed_records": cnt}
