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
        CREATE VIRTUAL TABLE IF NOT EXISTS a40_climate_fts USING fts5(
            station_sn,
            obs_date,
            tokenize='unicode61'
        );
    """)
    
    cursor.execute("DELETE FROM a40_climate_fts")
    
    cursor.execute("""
        INSERT INTO a40_climate_fts (station_sn, obs_date)
        SELECT station_sn, obs_date
        FROM a40_climate_daily_obs
    """)
    
    cnt = cursor.rowcount
    conn.commit()
    conn.close()
    return {"indexed_records": cnt}
