import json
import sqlite3
from pathlib import Path
from typing import Union, Dict, Any

def update_metadata(db_path: Union[str, Path]) -> Dict[str, Any]:
    db_p = Path(db_path)
    if not db_p.exists():
        raise FileNotFoundError(f"DB 檔案不存在: {db_p}")
        
    conn = sqlite3.connect(str(db_p))
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM fts_agro_global")
    fts_cnt = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM a00_master_cross_market_index")
    ana_cnt = cursor.fetchone()[0]
    
    conn.close()
    
    meta_p = Path(__file__).parent / "metadata.json"
    meta = {}
    if meta_p.exists():
        meta = json.loads(meta_p.read_text(encoding="utf-8"))
        
    meta["record_counts"] = {
        "fts_agro_global": fts_cnt,
        "a00_master_cross_market_index": ana_cnt
    }
    meta["status"] = "ACTIVE"
    
    meta_p.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return meta

if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 2:
        res = update_metadata(sys.argv[1])
        print(f"A00 Metadata 更新完成: {res}")
