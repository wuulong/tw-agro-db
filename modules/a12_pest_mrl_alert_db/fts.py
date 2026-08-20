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
        CREATE VIRTUAL TABLE IF NOT EXISTS a12_mrl_fts USING fts5(
            record_id UNINDEXED,
            sample_name,
            vendor_name,
            inspection_agency,
            test_result,
            tokenize='unicode61'
        );
    """)
    
    cursor.execute("DELETE FROM a12_mrl_fts")
    
    cursor.execute("""
        INSERT INTO a12_mrl_fts (record_id, sample_name, vendor_name, inspection_agency, test_result)
        SELECT record_id, sample_name, vendor_name, inspection_agency, test_result
        FROM a12_mrl_inspection_records
    """)
    
    cnt = cursor.rowcount
    conn.commit()
    conn.close()
    return {"indexed_records": cnt}
