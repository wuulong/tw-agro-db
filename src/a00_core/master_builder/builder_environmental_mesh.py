"""
src/a00_core/master_builder/builder_environmental_mesh.py
A00 ↔ A41 母大腦區域農地環境安全網與產地重金屬風險建置器
計算全台各縣市鄉鎮之農地重金屬超標密度、最高超標比率 MaxPollutionRatio 與環境風險等級
並寫入 a00_regional_environmental_safety_mesh 事前融合分析表與 GraphRAG 三元組
"""

import sqlite3
import json
from pathlib import Path
from typing import Union, Dict, Any

def build_environmental_mesh(db_path: Union[str, Path]) -> Dict[str, Any]:
    db_p = Path(db_path)
    if not db_p.exists():
        raise FileNotFoundError(f"DB 檔案不存在: {db_p}")
        
    conn = sqlite3.connect(str(db_p))
    cursor = conn.cursor()
    
    # 確保 schema 存在
    schema_p = Path(__file__).resolve().parents[3] / "modules" / "a00_master_hub" / "schema.sql"
    if schema_p.exists():
        cursor.executescript(schema_p.read_text(encoding="utf-8"))
        
    cursor.execute("DELETE FROM a00_regional_environmental_safety_mesh")
    
    cursor.execute("""
        SELECT 
            county_name,
            town_name,
            COUNT(*) AS total_cnt,
            SUM(is_polluted) AS polluted_cnt,
            pollutant_type,
            MAX(concentration_ppm / regulatory_limit_ppm) AS max_ratio
        FROM a41_soil_water_monitoring
        GROUP BY county_name, town_name;
    """)
    rows = cursor.fetchall()
    
    mesh_inserted = 0
    for r in rows:
        county, town, tot_cnt, pol_cnt, primary_pollutant, max_ratio = r[0], r[1], r[2], r[3], r[4], round(r[5], 4)
        
        risk_lvl = "HIGH_RISK" if pol_cnt > 0 or max_ratio >= 1.0 else ("WARNING" if max_ratio >= 0.7 else "SAFE")
        attr = {
            "_v": "1.0.0",
            "polluted_rate": round(pol_cnt / tot_cnt, 4) if tot_cnt > 0 else 0.0,
            "soil_quality_flag": "CONTAMINATED" if pol_cnt > 0 else "CLEAN"
        }
        
        cursor.execute("""
            INSERT OR REPLACE INTO a00_regional_environmental_safety_mesh (
                county_name, town_name, total_sites_count, polluted_sites_count,
                max_pollution_ratio, primary_pollutant, environmental_risk_level, attributes_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (county, town, tot_cnt, pol_cnt, max_ratio, primary_pollutant, risk_lvl, json.dumps(attr, ensure_ascii=False)))
        mesh_inserted += 1
        
        # 同步寫入 GraphRAG 三元組 (town -has_pollution_risk-> risk_lvl)
        cursor.execute("""
            INSERT INTO a00_graph_triples (subject_uri, predicate, object_uri, domain_code)
            VALUES (?, 'has_environmental_risk', ?, 'A41_ENV');
        """, (county + town, risk_lvl))
        
    conn.commit()
    conn.close()
    
    return {"environmental_mesh_records_inserted": mesh_inserted}
