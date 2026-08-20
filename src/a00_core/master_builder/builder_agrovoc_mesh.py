"""
src/a00_core/master_builder/builder_agrovoc_mesh.py
A00 母大腦 AGROVOC 跨領域本體知識網建置器 (Cross-Domain Semantic Ontology Mesh Builder)
將全庫 A10~A40 所有在地實體名稱 (農糧、農藥、水產、毛豬、氣象)
透過 A50 AGROVOC 多語主題詞庫，自動綁定至統一的國際 Concept URI 知識網絡表 a00_agrovoc_cross_domain_mesh
"""

import sqlite3
from pathlib import Path
from typing import Union, Dict, Any

def build_agrovoc_mesh(db_path: Union[str, Path]) -> Dict[str, Any]:
    db_p = Path(db_path)
    if not db_p.exists():
        raise FileNotFoundError(f"DB 檔案不存在: {db_p}")
        
    conn = sqlite3.connect(str(db_p))
    cursor = conn.cursor()
    
    # 確保 schema 存在
    schema_p = Path(__file__).resolve().parents[3] / "modules" / "a00_master_hub" / "schema.sql"
    if schema_p.exists():
        cursor.executescript(schema_p.read_text(encoding="utf-8"))
        
    cursor.execute("DELETE FROM a00_agrovoc_cross_domain_mesh")
    
    mesh_inserted = 0
    
    # 1. 碰撞 A10 作物 (crop_name ↔ A50 label_text)
    cursor.execute("""
        INSERT OR IGNORE INTO a00_agrovoc_cross_domain_mesh (concept_uri, concept_id, domain_code, local_entity_id, local_entity_name, semantic_match_score)
        SELECT 
            s.concept_uri,
            SUBSTR(s.concept_uri, INSTR(s.concept_uri, 'c_')),
            'A10',
            c.crop_id,
            c.crop_name,
            CASE WHEN s.label_type = 'prefLabel' THEN 1.0 ELSE 0.8 END
        FROM a10_crop_dictionary c
        JOIN a50_agrovoc_labels s ON c.crop_name LIKE '%' || s.label_text || '%'
        WHERE length(s.label_text) >= 2;
    """)
    mesh_inserted += cursor.rowcount
    
    # 2. 碰撞 A11 農藥 (pesticide_name / brand_name ↔ A50 label_text)
    cursor.execute("""
        INSERT OR IGNORE INTO a00_agrovoc_cross_domain_mesh (concept_uri, concept_id, domain_code, local_entity_id, local_entity_name, semantic_match_score)
        SELECT 
            s.concept_uri,
            SUBSTR(s.concept_uri, INSTR(s.concept_uri, 'c_')),
            'A11',
            p.pesticide_lic_id,
            p.pesticide_name,
            CASE WHEN s.label_type = 'prefLabel' THEN 1.0 ELSE 0.8 END
        FROM a11_pesticide_licenses p
        JOIN a50_agrovoc_labels s ON p.pesticide_name LIKE '%' || s.label_text || '%'
        WHERE length(s.label_text) >= 2;
    """)
    mesh_inserted += cursor.rowcount
    
    # 3. 碰撞 A20 水產 (product_name ↔ A50 label_text)
    cursor.execute("""
        INSERT OR IGNORE INTO a00_agrovoc_cross_domain_mesh (concept_uri, concept_id, domain_code, local_entity_id, local_entity_name, semantic_match_score)
        SELECT 
            s.concept_uri,
            SUBSTR(s.concept_uri, INSTR(s.concept_uri, 'c_')),
            'A20',
            CAST(p.product_id AS TEXT),
            p.product_name,
            CASE WHEN s.label_type = 'prefLabel' THEN 1.0 ELSE 0.8 END
        FROM a20_fishery_products p
        JOIN a50_agrovoc_labels s ON p.product_name LIKE '%' || s.label_text || '%'
        WHERE length(s.label_text) >= 2;
    """)
    mesh_inserted += cursor.rowcount
    
    conn.commit()
    conn.close()
    
    return {"mesh_records_inserted": mesh_inserted}
