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
        CREATE VIRTUAL TABLE IF NOT EXISTS a14_fertilizer_fts USING fts5(
            fertilizer_lic_id UNINDEXED,
            brand_name,
            manufacturer_name,
            fertilizer_type,
            tokenize='unicode61'
        );
    """)
    
    cursor.execute("DELETE FROM a14_fertilizer_fts")
    
    cursor.execute("""
        INSERT INTO a14_fertilizer_fts (fertilizer_lic_id, brand_name, manufacturer_name, fertilizer_type)
        SELECT fertilizer_lic_id, brand_name, manufacturer_name, fertilizer_type
        FROM a14_fertilizer_licenses
    """)
    
    cnt = cursor.rowcount
    conn.commit()
    conn.close()
    return {"indexed_records": cnt}
