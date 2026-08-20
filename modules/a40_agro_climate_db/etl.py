import json
import sqlite3
from pathlib import Path
from typing import Union, Dict, Any

def run_etl(json_path: Union[str, Path], db_path: Union[str, Path]) -> Dict[str, Any]:
    json_p = Path(json_path)
    db_p = Path(db_path)
    
    if not json_p.exists():
        raise FileNotFoundError(f"來源 JSON 檔案不存在: {json_p}")
        
    db_p.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_p))
    cursor = conn.cursor()
    
    schema_p = Path(__file__).parent / "schema.sql"
    if schema_p.exists():
        cursor.executescript(schema_p.read_text(encoding="utf-8"))
        
    raw_data = json.loads(json_p.read_text(encoding="utf-8"))
    records = []
    
    for item in raw_data:
        sn = str(item.get("sn", "")).strip()
        info1 = str(item.get("info1", "")).strip() # 日期
        info3 = int(item.get("info3", 0))          # 觀測筆數
        info2 = str(item.get("info2", "")).strip() # URL
        
        if not sn or not info1:
            continue
            
        attr = {"_v": "1.0.0", "data_format": "CSV"}
        if info3 >= 96:
            attr["flag"] = "FULL_DAY_OBSERVATION"
        else:
            attr["flag"] = "PARTIAL_OBSERVATION_WARNING"
            
        records.append((
            sn,
            info1,
            info3,
            info2,
            json.dumps(attr, ensure_ascii=False)
        ))
        
    cursor.executemany("""
        INSERT OR REPLACE INTO a40_climate_daily_obs (
            station_sn, obs_date, obs_count, download_url, attributes_json
        ) VALUES (?, ?, ?, ?, ?)
    """, records)
    
    conn.commit()
    conn.close()
    
    return {"records_inserted": len(records)}
