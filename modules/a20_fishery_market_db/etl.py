import json
import sqlite3
from pathlib import Path
from typing import Union, Dict, Any

def parse_fishery_description(desc_str: str) -> Dict[str, str]:
    """解析 '|產品名稱：秋刀魚|來源產地：臺灣|產品重量：500g|保存方式：零下-18℃' 格式"""
    res = {}
    if not desc_str:
        return res
        
    parts = desc_str.split("|")
    for p in parts:
        if "：" in p:
            k, v = p.split("：", 1)
            res[k.strip()] = v.strip()
    return res

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
        p_name = item.get("名稱", "").strip()
        desc = item.get("描述", "").strip()
        if not p_name:
            continue
            
        parsed_desc = parse_fishery_description(desc)
        origin = parsed_desc.get("來源產地", "臺灣").strip()
        weight = parsed_desc.get("產品重量", "").strip()
        storage = parsed_desc.get("保存方式", "").strip()
        
        attr = {"_v": "1.0.0", "raw_description": desc}
        if any(kw in origin for kw in ["臺灣", "宜蘭", "澎湖", "高雄", "基隆", "屏東"]):
            attr["flag"] = "LOCAL_TAIWAN_AQUACULTURE"
        else:
            attr["flag"] = "IMPORTED_AQUACULTURE"
            
        records.append((
            p_name,
            origin,
            weight,
            storage,
            json.dumps(attr, ensure_ascii=False)
        ))
        
    cursor.executemany("""
        INSERT INTO a20_fishery_products (
            product_name, origin_location, weight_spec, storage_method, attributes_json
        ) VALUES (?, ?, ?, ?, ?)
    """, records)
    
    conn.commit()
    conn.close()
    
    return {"records_inserted": len(records)}
