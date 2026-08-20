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
        m_name = item.get("肥料別", "").strip()
        if not m_name:
            continue
            
        try:
            qty = float(item.get("數量", 0))
        except (ValueError, TypeError):
            qty = 0.0
            
        try:
            val = float(item.get("價值", 0))
        except (ValueError, TypeError):
            val = 0.0
            
        attr = {"_v": "1.0.0"}
        if qty > 0:
            unit_val = round((val * 1000) / qty, 2)
            attr["unit_val_ntd_per_ton"] = unit_val
            
        records.append((
            str(item.get("年度", "2025")).strip(),
            m_name,
            item.get("產銷類別", "").strip(),
            qty,
            val,
            json.dumps(attr, ensure_ascii=False)
        ))
        
    cursor.executemany("""
        INSERT INTO a13_organic_materials_registry (
            period_year, material_name, category_type, quantity_tons, value_thousand_ntd, attributes_json
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, records)
    
    conn.commit()
    conn.close()
    
    return {"records_inserted": len(records)}
