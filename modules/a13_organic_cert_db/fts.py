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
        CREATE VIRTUAL TABLE IF NOT EXISTS a13_organic_fts USING fts5(
            registry_id UNINDEXED,
            material_name,
            category_type,
            period_year,
            tokenize='unicode61'
        );
    """)
    
    cursor.execute("DELETE FROM a13_organic_fts")
    
    cursor.execute("""
        INSERT INTO a13_organic_fts (registry_id, material_name, category_type, period_year)
        SELECT registry_id, material_name, category_type, period_year
        FROM a13_organic_materials_registry
    """)
    
    cnt = cursor.rowcount
    conn.commit()
    conn.close()
    return {"indexed_records": cnt}
