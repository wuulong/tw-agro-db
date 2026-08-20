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
        CREATE VIRTUAL TABLE IF NOT EXISTS a20_fishery_fts USING fts5(
            product_id UNINDEXED,
            product_name,
            origin_location,
            tokenize='unicode61'
        );
    """)
    
    cursor.execute("DELETE FROM a20_fishery_fts")
    
    cursor.execute("""
        INSERT INTO a20_fishery_fts (product_id, product_name, origin_location)
        SELECT product_id, product_name, origin_location
        FROM a20_fishery_products
    """)
    
    cnt = cursor.rowcount
    conn.commit()
    conn.close()
    return {"indexed_records": cnt}
