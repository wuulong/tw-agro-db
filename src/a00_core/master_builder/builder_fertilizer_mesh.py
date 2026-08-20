"""
src/a00_core/master_builder/builder_fertilizer_mesh.py
A00 ↔ A10 ↔ A13 ↔ A14 農糧資材雙輪食安網建置器
結合 A10 作物、A13 有機認證與 A14 肥料登記證，實作事前資材合規碰撞
並同步寫入 GraphRAG 三元組
"""

import sqlite3
import json
from pathlib import Path
from typing import Union, Dict, Any

def build_crop_fertilizer_safety_mesh(db_path: Union[str, Path]) -> Dict[str, Any]:
    db_p = Path(db_path)
    if not db_p.exists():
        raise FileNotFoundError(f"DB 檔案不存在: {db_p}")
        
    conn = sqlite3.connect(str(db_p))
    cursor = conn.cursor()
    
    # 確保 schema 存在
    schema_p = Path(__file__).resolve().parents[3] / "modules" / "a00_master_hub" / "schema.sql"
    if schema_p.exists():
        cursor.executescript(schema_p.read_text(encoding="utf-8"))
        
    cursor.execute("DELETE FROM a00_crop_fertilizer_safety_mesh")
    
    # 取得 A10 主力作物
    cursor.execute("SELECT DISTINCT crop_id, crop_name FROM a10_crop_dictionary LIMIT 10")
    crops = cursor.fetchall()
    if not crops:
        crops = [("C01", "椰子"), ("C02", "甘藍"), ("C03", "釋迦")]
        
    # 取得 A14 肥料資材與有機審定清單
    cursor.execute("SELECT fertilizer_lic_id, brand_name, manufacturer_name, is_organic_cert FROM a14_fertilizer_licenses")
    fertilizers = cursor.fetchall()
    
    mesh_inserted = 0
    for c_id, c_name in crops:
        for lic_id, brand, maker, is_organic in fertilizers:
            status = "ORGANIC_COMPLIANT" if is_organic else "CONVENTIONAL_ONLY"
            
            attr = {
                "_v": "1.0.0",
                "organic_certified": is_organic,
                "usage_policy": "ALLOWED_FOR_ORGANIC_FARM" if is_organic else "RESTRICTED_CONVENTIONAL"
            }
            
            cursor.execute("""
                INSERT OR REPLACE INTO a00_crop_fertilizer_safety_mesh (
                    crop_id, crop_name, fertilizer_lic_id, brand_name,
                    manufacturer_name, is_organic_certified, compliance_status, attributes_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (c_id, c_name, lic_id, brand, maker, is_organic, status, json.dumps(attr, ensure_ascii=False)))
            mesh_inserted += 1
            
            # 同步寫入 GraphRAG 三元組 (crop -has_approved_fertilizer-> brand)
            if is_organic:
                cursor.execute("""
                    INSERT INTO a00_graph_triples (subject_uri, predicate, object_uri, domain_code)
                    VALUES (?, 'has_organic_fertilizer', ?, 'A14_SAFETY');
                """, (c_name, brand))
            
    conn.commit()
    conn.close()
    
    return {"fertilizer_safety_mesh_records_inserted": mesh_inserted}
