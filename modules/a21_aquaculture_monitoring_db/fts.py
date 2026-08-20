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
        CREATE VIRTUAL TABLE IF NOT EXISTS a21_aquaculture_fts USING fts5(
            farm_id,
            county_name,
            town_name,
            aquaculture_species,
            tokenize='unicode61'
        );
    """)
    
    cursor.execute("DELETE FROM a21_aquaculture_fts")
    
    cursor.execute("""
        INSERT INTO a21_aquaculture_fts (farm_id, county_name, town_name, aquaculture_species)
        SELECT farm_id, county_name, town_name, aquaculture_species
        FROM a21_aquaculture_monitoring
    """)
    
    cnt = cursor.rowcount
    conn.commit()
    conn.close()
    return {"indexed_records": cnt}
