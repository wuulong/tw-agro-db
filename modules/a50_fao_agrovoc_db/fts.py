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
        CREATE VIRTUAL TABLE IF NOT EXISTS a50_agrovoc_fts USING fts5(
            concept_uri,
            lang_code,
            label_text,
            tokenize='unicode61'
        );
    """)
    
    cursor.execute("DELETE FROM a50_agrovoc_fts")
    
    cursor.execute("""
        INSERT INTO a50_agrovoc_fts (concept_uri, lang_code, label_text)
        SELECT concept_uri, lang_code, label_text
        FROM a50_agrovoc_labels
    """)
    
    cnt = cursor.rowcount
    conn.commit()
    conn.close()
    return {"indexed_records": cnt}
