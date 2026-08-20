"""
A30 etl.py: 使用核心 date_parser 重構
"""
import json
import sqlite3
from pathlib import Path
from typing import Union, Dict, Any
import sys

repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.a00_core.utils.date_parser import parse_roc_date_universal

# 保留相容性別名
parse_roc_date_nodash = parse_roc_date_universal

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
        m_name = item.get("市場名稱", "").strip()
        raw_date = str(item.get("交易日期", "")).strip()
        if not m_name or not raw_date:
            continue
            
        iso_date = parse_roc_date_universal(raw_date)
        tot_h = int(item.get("成交頭數-總數", 0))
        spec_h = int(item.get("規格豬-頭數", 0))
        
        attr = {"_v": "1.0.0"}
        if tot_h > 0:
            spec_ratio = round((spec_h / tot_h) * 100, 2)
            attr["spec_ratio_pct"] = spec_ratio
            if spec_ratio < 80.0:
                attr["flag"] = "LOW_SPEC_PORK_WARNING"
                
        records.append((
            iso_date,
            m_name,
            tot_h,
            float(item.get("成交頭數-平均重量", 0.0)),
            float(item.get("成交頭數-平均價格", 0.0)),
            spec_h,
            float(item.get("規格豬-平均重量", 0.0)),
            float(item.get("規格豬-平均價格", 0.0)),
            json.dumps(attr, ensure_ascii=False)
        ))
        
    cursor.executemany("""
        INSERT OR REPLACE INTO a30_pork_trans_daily (
            trans_date, market_name, total_heads, avg_weight_kg, avg_price_ntd,
            spec_heads, spec_weight_kg, spec_price_ntd, attributes_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, records)
    
    conn.commit()
    conn.close()
    
    return {"records_inserted": len(records)}
