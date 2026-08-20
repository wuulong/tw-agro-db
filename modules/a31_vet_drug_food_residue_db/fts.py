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
        CREATE VIRTUAL TABLE IF NOT EXISTS a31_vet_drug_fts USING fts5(
            drug_name,
            target_livestock,
            tokenize='unicode61'
        );
    """)
    
    cursor.execute("DELETE FROM a31_vet_drug_fts")
    
    cursor.execute("""
        INSERT INTO a31_vet_drug_fts (rowid, drug_name, target_livestock)
        SELECT residue_id, drug_name, target_livestock
        FROM a31_vet_drug_residue
    """)
    
    cnt = cursor.rowcount
    conn.commit()
    conn.close()
    return {"indexed_records": cnt}
