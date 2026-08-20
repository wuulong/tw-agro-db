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
    
    records_inserted = 0
    polluted_count = 0
    
    for item in raw_data:
        site_id = str(item.get("site_id", "")).strip()
        county = str(item.get("county", "")).strip()
        town = str(item.get("township", "")).strip()
        s_date = str(item.get("anno_date", "")).strip()
        pollutant = str(item.get("pollutant", "")).strip()
        
        if not site_id or not county:
            continue
            
        conc = float(item.get("concentration_ppm", 150.0 if "銅" in pollutant else 5.0))
        limit_val = float(item.get("regulatory_limit_ppm", 200.0 if "銅" in pollutant else 5.0))
        
        # 特化算式：PollutionRatio = conc / limit_val
        ratio = round(conc / limit_val, 4) if limit_val > 0 else 1.0
        is_polluted = 1 if "公告控制場址" in item.get("controltype", "") or conc >= limit_val else 0
        if is_polluted:
            polluted_count += 1
            
        safety_lvl = "HIGH_RISK" if is_polluted else ("WARNING" if ratio >= 0.7 else "SAFE")
        
        attr = {
            "_v": "1.0.0",
            "pollution_ratio": ratio,
            "safety_level": safety_lvl,
            "site_name": item.get("site_name", ""),
            "controltype": item.get("controltype", "")
        }
        
        cursor.execute("""
            INSERT OR REPLACE INTO a41_soil_water_monitoring (
                site_id, county_name, town_name, sample_date, pollutant_type,
                concentration_ppm, regulatory_limit_ppm, is_polluted, attributes_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (site_id, county, town, s_date, pollutant, conc, limit_val, is_polluted, json.dumps(attr, ensure_ascii=False)))
        records_inserted += 1
        
    conn.commit()
    conn.close()
    
    return {
        "records_inserted": records_inserted,
        "polluted_count": polluted_count
    }
