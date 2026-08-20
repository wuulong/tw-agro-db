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
        CREATE VIRTUAL TABLE IF NOT EXISTS a11_pesticide_fts USING fts5(
            pesticide_lic_id UNINDEXED,
            pesticide_name,
            pesticide_en_name,
            brand_name,
            vendor_name,
            tokenize='unicode61'
        );
    """)
    
    cursor.execute("DELETE FROM a11_pesticide_fts")
    
    cursor.execute("""
        INSERT INTO a11_pesticide_fts (pesticide_lic_id, pesticide_name, pesticide_en_name, brand_name, vendor_name)
        SELECT pesticide_lic_id, pesticide_name, pesticide_en_name, brand_name, vendor_name
        FROM a11_pesticide_licenses
    """)
    
    cnt = cursor.rowcount
    conn.commit()
    conn.close()
    return {"indexed_records": cnt}
