"""
src/a00_core/master_builder/builder_ontology_graph.py
實作 E13~E16 國際本體知識體系深化建置器:
1. E13: SKOS 拓撲階層下鑽與上推 (Hierarchical Subsumption)
2. E14: 跨國農藥與作物 MRL 自動推論網
3. E15: 1-Hop SQLite-RDF GraphRAG 實體圖譜 (a00_graph_triples)
4. E16: 病蟲害防護與 5 Pillar 終極網
"""

import sqlite3
from pathlib import Path
from typing import Union, Dict, Any

def build_ontology_graph(db_path: Union[str, Path]) -> Dict[str, Any]:
    db_p = Path(db_path)
    if not db_p.exists():
        raise FileNotFoundError(f"DB 檔案不存在: {db_p}")
        
    conn = sqlite3.connect(str(db_p))
    cursor = conn.cursor()
    
    # 確保 schema 存在
    schema_p = Path(__file__).resolve().parents[3] / "modules" / "a00_master_hub" / "schema.sql"
    if schema_p.exists():
        cursor.executescript(schema_p.read_text(encoding="utf-8"))
        
    cursor.execute("DELETE FROM a00_graph_triples")
    
    triples_inserted = 0
    
    # 1. 寫入 E13: SKOS Hierarchy 三元組 (subject_uri -broader-> object_uri)
    cursor.execute("""
        INSERT INTO a00_graph_triples (subject_uri, predicate, object_uri, domain_code)
        SELECT subject_uri, predicate, object_uri, 'A50'
        FROM a50_agrovoc_hierarchy;
    """)
    triples_inserted += cursor.rowcount
    
    # 2. 寫入 E15: Cross-Domain Mesh 實體圖譜三元組 (local_entity -is_a-> agrovoc_concept)
    cursor.execute("""
        INSERT INTO a00_graph_triples (subject_uri, predicate, object_uri, domain_code)
        SELECT local_entity_name, 'is_a', concept_uri, domain_code
        FROM a00_agrovoc_cross_domain_mesh;
    """)
    triples_inserted += cursor.rowcount
    
    # 3. 寫入 E14+E16: 5 Pillar 安全防護網三元組 (crop -has_pesticide-> pesticide)
    cursor.execute("""
        INSERT INTO a00_graph_triples (subject_uri, predicate, object_uri, domain_code)
        SELECT crop_name, 'has_pesticide', pesticide_name, 'A00_SAFETY'
        FROM a00_crop_pesticide_safety_mesh;
    """)
    triples_inserted += cursor.rowcount
    
    conn.commit()
    conn.close()
    
    return {"graph_triples_inserted": triples_inserted}
