import sqlite3
from pathlib import Path
from typing import Union, Dict, Any

def build_fts_index(db_path: Union[str, Path]) -> Dict[str, Any]:
    db_p = Path(db_path)
    if not db_p.exists():
        raise FileNotFoundError(f"DB 檔案不存在: {db_p}")
        
    conn = sqlite3.connect(str(db_p))
    cursor = conn.cursor()
    
    # 清空現有 FTS 索引
    cursor.execute("DELETE FROM a10_crop_fts")
    
    # 從 字典 與 View / Trans 關聯寫入 FTS
    cursor.execute("""
        INSERT INTO a10_crop_fts (crop_id, crop_name, market_name, category_name)
        SELECT DISTINCT d.crop_id, d.crop_name, t.market_name, d.category_name
        FROM a10_crop_dictionary d
        JOIN a10_crop_trans_daily t ON d.crop_id = t.crop_id
    """)
    
    indexed_count = cursor.rowcount
    conn.commit()
    conn.close()
    
    return {"indexed_records": indexed_count}

if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 2:
        res = build_fts_index(sys.argv[1])
        print(f"FTS 建立完成: {res}")
