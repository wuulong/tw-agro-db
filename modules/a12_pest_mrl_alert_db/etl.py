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
        s_name = item.get("檢體名稱", "").strip()
        if not s_name:
            continue
            
        res_text = item.get("檢出項目及殘留容許量", "").strip()
        is_comp = 1
        if "不合格" in res_text or "超標" in res_text or "未核准" in res_text or "違規" in res_text:
            is_comp = 0
            
        attr = {"_v": "1.0.0"}
        if is_comp == 0:
            attr["flag"] = "HIGH_VIOLATION_RISK"
            attr["compliance_score"] = 0
        else:
            attr["flag"] = "NORMAL"
            attr["compliance_score"] = 100
            
        records.append((
            item.get("年度月份", "").strip(),
            item.get("抽樣衛生局", "").strip(),
            s_name,
            item.get("抽樣廠商名稱", "").strip(),
            item.get("抽樣廠商地址", "").strip(),
            res_text,
            is_comp,
            json.dumps(attr, ensure_ascii=False)
        ))
        
    cursor.executemany("""
        INSERT INTO a12_mrl_inspection_records (
            period_year_month, inspection_agency, sample_name, vendor_name, vendor_address, test_result, is_compliant, attributes_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, records)
    
    conn.commit()
    conn.close()
    
    return {"records_inserted": len(records)}
