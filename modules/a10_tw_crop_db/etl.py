import json
import sqlite3
from pathlib import Path
from typing import Union, Dict, Any, List

CATEGORY_MAP = {
    "N04": "蔬菜",
    "N05": "水果",
    "N06": "花卉",
    "N07": "其他"
}

def parse_taiwan_date(date_str: str) -> str:
    """轉換民國年 '115.08.19' 為 ISO 8601 '2026-08-19'"""
    try:
        parts = date_str.strip().split('.')
        if len(parts) == 3:
            year = int(parts[0]) + 1911
            month = int(parts[1])
            day = int(parts[2])
            return f"{year:04d}-{month:02d}-{day:02d}"
    except Exception:
        pass
    return date_str

def run_etl(json_path: Union[str, Path], db_path: Union[str, Path]) -> Dict[str, Any]:
    json_p = Path(json_path)
    db_p = Path(db_path)
    
    if not json_p.exists():
        raise FileNotFoundError(f"JSON 檔案不存在: {json_p}")
    
    db_p.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(str(db_p))
    cursor = conn.cursor()
    
    # 讀取並執行 schema
    schema_p = Path(__file__).parent / "schema.sql"
    if schema_p.exists():
        cursor.executescript(schema_p.read_text(encoding="utf-8"))
    
    with open(json_p, 'r', encoding='utf-8') as f:
        records = json.load(f)
    
    crop_dict: Dict[str, Dict[str, Any]] = {}
    trans_records: List[tuple] = []
    
    for r in records:
        crop_id = str(r.get("作物代號", "")).strip()
        crop_name = str(r.get("作物名稱", "")).strip()
        cat_code = str(r.get("種類代碼", "")).strip()
        cat_name = CATEGORY_MAP.get(cat_code, "未分類")
        
        if crop_id and crop_id != "rest" and crop_id not in crop_dict:
            attr_payload = {
                "_v": "1.0.0",
                "hs_code": f"08{crop_id.zfill(4)}.00" if crop_id.isdigit() else "0800.00.00",
                "english_name": crop_name
            }
            crop_dict[crop_id] = {
                "crop_id": crop_id,
                "crop_name": crop_name,
                "category_code": cat_code,
                "category_name": cat_name,
                "attributes_json": json.dumps(attr_payload, ensure_ascii=False)
            }
            
        trans_date = parse_taiwan_date(str(r.get("交易日期", "")))
        market_id = str(r.get("市場代號", "")).strip()
        market_name = str(r.get("市場名稱", "")).strip()
        
        price_high = float(r.get("上價", 0.0))
        price_mid = float(r.get("中價", 0.0))
        price_low = float(r.get("下價", 0.0))
        price_avg = float(r.get("平均價", 0.0))
        volume_kg = float(r.get("交易量", 0.0))
        
        is_rest = 1 if (crop_id == "rest" or volume_kg == 0.0) else 0
        attr_json = json.dumps({"_v": "1.0.0"}, ensure_ascii=False)
        
        if trans_date and crop_id and market_id:
            trans_records.append((
                trans_date, crop_id, market_id, market_name,
                price_high, price_mid, price_low, price_avg, volume_kg,
                is_rest, attr_json
            ))
            
    # 寫入 a10_crop_dictionary
    for c in crop_dict.values():
        cursor.execute("""
            INSERT OR REPLACE INTO a10_crop_dictionary (crop_id, crop_name, category_code, category_name, attributes_json)
            VALUES (?, ?, ?, ?, ?)
        """, (c["crop_id"], c["crop_name"], c["category_code"], c["category_name"], c["attributes_json"]))
        
    # 寫入 a10_crop_trans_daily
    cursor.executemany("""
        INSERT OR REPLACE INTO a10_crop_trans_daily 
        (trans_date, crop_id, market_id, market_name, price_high, price_mid, price_low, price_avg, volume_kg, is_rest, attributes_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, trans_records)
    
    conn.commit()
    conn.close()
    
    return {
        "crops_inserted": len(crop_dict),
        "trans_inserted": len(trans_records)
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 3:
        res = run_etl(sys.argv[1], sys.argv[2])
        print(f"ETL 完成: {res}")
