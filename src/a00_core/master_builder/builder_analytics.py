import sqlite3
import math
import json
from pathlib import Path
from typing import Union, Dict, Any

def build_analytics(db_path: Union[str, Path]) -> Dict[str, Any]:
    db_p = Path(db_path)
    if not db_p.exists():
        raise FileNotFoundError(f"DB 檔案不存在: {db_p}")
        
    conn = sqlite3.connect(str(db_p))
    cursor = conn.cursor()
    
    # 確保 Table 存在
    schema_p = Path(__file__).resolve().parents[3] / "modules" / "a00_master_hub" / "schema.sql"
    if schema_p.exists():
        cursor.executescript(schema_p.read_text(encoding="utf-8"))
        
    cursor.execute("""
        SELECT trans_date, crop_id, crop_name, market_name, price_avg, volume_kg
        FROM v_master_crop_market
        WHERE is_rest = 0
    """)
    rows = cursor.fetchall()
    
    # 群組計算: (trans_date, crop_id)
    groups: Dict[tuple, list] = {}
    for r in rows:
        key = (r[0], r[1])
        if key not in groups:
            groups[key] = []
        groups[key].append(r)
        
    insert_records = []
    for (t_date, c_id), items in groups.items():
        c_name = items[0][2]
        m_count = len(items)
        tot_vol = sum(i[5] for i in items)
        
        # 加權平均
        if tot_vol > 0:
            nat_avg = sum(i[4] * i[5] for i in items) / tot_vol
        else:
            nat_avg = sum(i[4] for i in items) / m_count
            
        prices = [i[4] for i in items]
        min_p_item = min(items, key=lambda x: x[4])
        max_p_item = max(items, key=lambda x: x[4])
        
        # 計算 CV (離散係數)
        if nat_avg > 0 and len(prices) > 1:
            variance = sum((p - nat_avg)**2 for p in prices) / len(prices)
            std_dev = math.sqrt(variance)
            cv = round(std_dev / nat_avg, 4)
        else:
            cv = 0.0
            
        attr = {"_v": "1.0.0"}
        if cv > 0.35:
            attr["flag"] = "HIGH_REGIONAL_DISPARITY"
            
        insert_records.append((
            t_date, c_id, c_name, m_count, round(nat_avg, 2), round(tot_vol, 2),
            min_p_item[3], max_p_item[3], cv, json.dumps(attr, ensure_ascii=False)
        ))
        
    cursor.executemany("""
        INSERT OR REPLACE INTO a00_master_cross_market_index
        (trans_date, crop_id, crop_name, market_count, national_avg_price, national_total_volume, min_price_market, max_price_market, price_cv, attributes_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, insert_records)
    
    conn.commit()
    conn.close()
    return {"analytics_records_inserted": len(insert_records)}
