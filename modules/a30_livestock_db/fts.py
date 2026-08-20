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
        CREATE VIRTUAL TABLE IF NOT EXISTS a30_pork_fts USING fts5(
            trans_date UNINDEXED,
            market_name,
            tokenize='unicode61'
        );
    """)
    
    cursor.execute("DELETE FROM a30_pork_fts")
    
    cursor.execute("""
        INSERT INTO a30_pork_fts (trans_date, market_name)
        SELECT trans_date, market_name
        FROM a30_pork_trans_daily
    """)
    
    cnt = cursor.rowcount
    conn.commit()
    conn.close()
    return {"indexed_records": cnt}
