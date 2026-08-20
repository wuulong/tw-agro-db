"""
A11 etl.py: 對合完整 schema.sql
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
parse_roc_date_safe = parse_roc_date_universal

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
        lic_word = item.get("許可證字", "").strip()
        lic_num = item.get("許可證號", "").strip()
        p_name = item.get("中文名稱", "").strip() or item.get("廠牌名稱", "").strip()
        
        if not lic_word or not lic_num or not p_name:
            continue
            
        lic_id = f"{lic_word}{lic_num}"
        exp_date_raw = item.get("有效期限", "") or item.get("有效日期", "")
        exp_date = parse_roc_date_universal(exp_date_raw)
        revoke_date_raw = item.get("撤銷日期", "")
        revoke_date = parse_roc_date_universal(revoke_date_raw)
        
        records.append((
            lic_id,
            lic_word,
            lic_num,
            p_name,
            item.get("英文名稱", "").strip(),
            item.get("廠牌名稱", "").strip(),
            item.get("農藥代號", "").strip(),
            item.get("劑型", "").strip(),
            item.get("含量", "").strip(),
            item.get("國外原製造廠商", "").strip(),
            item.get("廠商名稱", "").strip(),
            exp_date,
            item.get("撤銷類別", "").strip() or item.get("註銷狀態", "").strip(),
            revoke_date,
            item.get("農藥使用範圍連結", "").strip() or item.get("詳細資料", "").strip()
        ))
        
    cursor.executemany("""
        INSERT OR REPLACE INTO a11_pesticide_licenses (
            pesticide_lic_id, lic_type, lic_no, pesticide_name, pesticide_en_name,
            brand_name, pesticide_code, formulation, active_ingredient_pct,
            manufacturer, vendor_name, expire_date, revoke_type, revoke_date, detail_url
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, records)
    
    # 載入禁用/管制農藥表
    prohibited_json = json_p.parent / "A11_pesticide_prohibited.json"
    if prohibited_json.exists():
        prohibited_raw = json.loads(prohibited_json.read_text(encoding="utf-8"))
        p_records = []
        for p in prohibited_raw:
            p_name = p.get("農藥名稱", "").strip()
            if not p_name:
                continue
            p_records.append((
                p_name,
                p.get("英文名稱", "").strip(),
                parse_roc_date_universal(p.get("禁止製造輸入日期", "")),
                parse_roc_date_universal(p.get("禁止販賣使用日期", ""))
            ))
        cursor.executemany("""
            INSERT INTO a11_prohibited_pesticides (pesticide_name, pesticide_en_name, prohibited_mfg_import_date, prohibited_sale_use_date)
            VALUES (?, ?, ?, ?)
        """, p_records)
        
    conn.commit()
    conn.close()
    
    return {"records_inserted": len(records)}
