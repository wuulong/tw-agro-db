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
    
    concepts_inserted = 0
    labels_inserted = 0
    hierarchy_inserted = 0
    
    for item in raw_data:
        uri = item.get("uri", "").strip()
        cid = item.get("concept_id", "").strip()
        cat = item.get("category", "GENERAL").strip()
        
        if not uri or not cid:
            continue
            
        attr = {
            "_v": "1.0.0",
            "available_languages": ["en", "zh-TW", "zh-CN"],
            "domain_category": cat
        }
        
        # 1. 寫入 concept
        cursor.execute("""
            INSERT OR REPLACE INTO a50_agrovoc_concepts (concept_uri, concept_id, attributes_json)
            VALUES (?, ?, ?)
        """, (uri, cid, json.dumps(attr, ensure_ascii=False)))
        concepts_inserted += 1
        
        # 2. 寫入多語標籤 (en, zh-TW, zh-CN, altLabels)
        labels = []
        if item.get("prefLabel_en"):
            labels.append((uri, "en", item["prefLabel_en"], "prefLabel"))
        if item.get("prefLabel_zh_tw"):
            labels.append((uri, "zh-TW", item["prefLabel_zh_tw"], "prefLabel"))
        if item.get("prefLabel_zh_cn"):
            labels.append((uri, "zh-CN", item["prefLabel_zh_cn"], "prefLabel"))
            
        for alt in item.get("altLabels", []):
            labels.append((uri, "zh-TW", alt, "altLabel"))
            
        cursor.executemany("""
            INSERT INTO a50_agrovoc_labels (concept_uri, lang_code, label_text, label_type)
            VALUES (?, ?, ?, ?)
        """, labels)
        labels_inserted += len(labels)
        
        # 3. 寫入 broader 階層關係
        b_uri = item.get("broader_uri")
        if b_uri:
            cursor.execute("""
                INSERT OR REPLACE INTO a50_agrovoc_hierarchy (subject_uri, predicate, object_uri)
                VALUES (?, 'broader', ?)
            """, (uri, b_uri))
            hierarchy_inserted += 1
            
    conn.commit()
    conn.close()
    
    return {
        "concepts_inserted": concepts_inserted,
        "labels_inserted": labels_inserted,
        "hierarchy_inserted": hierarchy_inserted
    }
