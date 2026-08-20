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
        CREATE VIRTUAL TABLE IF NOT EXISTS a41_soil_water_fts USING fts5(
            site_id,
            county_name,
            town_name,
            pollutant_type,
            tokenize='unicode61'
        );
    """)
    
    cursor.execute("DELETE FROM a41_soil_water_fts")
    
    cursor.execute("""
        INSERT INTO a41_soil_water_fts (site_id, county_name, town_name, pollutant_type)
        SELECT site_id, county_name, town_name, pollutant_type
        FROM a41_soil_water_monitoring
    """)
    
    cnt = cursor.rowcount
    conn.commit()
    conn.close()
    return {"indexed_records": cnt}
