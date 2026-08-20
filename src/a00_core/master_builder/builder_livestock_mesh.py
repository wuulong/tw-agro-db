"""
src/a00_core/master_builder/builder_livestock_mesh.py
A00 ↔ A30 ↔ A31 毛豬交易與動物用藥食安防護網建置器
結合 A30 毛豬批發市場行情與 A31 TFDA 動物用藥殘留/禁藥清單
進行跨庫實體化碰撞，計算毛豬食安風險層級並同步寫入 GraphRAG 三元組
"""

import sqlite3
import json
from pathlib import Path
from typing import Union, Dict, Any

def build_livestock_safety_mesh(db_path: Union[str, Path]) -> Dict[str, Any]:
    db_p = Path(db_path)
    if not db_p.exists():
        raise FileNotFoundError(f"DB 檔案不存在: {db_p}")
        
    conn = sqlite3.connect(str(db_p))
    cursor = conn.cursor()
    
    # 確保 schema 存在
    schema_p = Path(__file__).resolve().parents[3] / "modules" / "a00_master_hub" / "schema.sql"
    if schema_p.exists():
        cursor.executescript(schema_p.read_text(encoding="utf-8"))
        
    cursor.execute("DELETE FROM a00_livestock_pork_safety_mesh")
    
    # 取得 A30 毛豬批發市場列表
    markets = []
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='a30_livestock_pork_transactions'")
    if cursor.fetchone():
        cursor.execute("SELECT DISTINCT market_name FROM a30_livestock_pork_transactions LIMIT 10")
        markets = [r[0] for r in cursor.fetchall()]
        
    if not markets:
        markets = ["彰化縣", "雲林縣", "新竹市"]
        
    # 取得 A31 動物用藥與 MRL 清單
    cursor.execute("SELECT drug_name, target_livestock, mrl_ppm, is_prohibited FROM a31_vet_drug_residue")
    drugs = cursor.fetchall()
    
    mesh_inserted = 0
    for m_name in markets:
        for d_name, t_livestock, mrl, is_prohibited in drugs:
            risk_lvl = "PROHIBITED" if is_prohibited else ("HIGH_RISK" if mrl <= 0.05 else "SAFE")
            
            attr = {
                "_v": "1.0.0",
                "mrl_ppm": mrl,
                "regulatory_status": "BANNED" if is_prohibited else "APPROVED"
            }
            
            cursor.execute("""
                INSERT OR REPLACE INTO a00_livestock_pork_safety_mesh (
                    livestock_market_name, target_livestock, drug_name, mrl_ppm,
                    is_prohibited, food_safety_risk_level, attributes_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (m_name, t_livestock, d_name, mrl, is_prohibited, risk_lvl, json.dumps(attr, ensure_ascii=False)))
            mesh_inserted += 1
            
            # 同步寫入 GraphRAG 三元組 (market/pork -has_vet_drug_restriction-> drug)
            cursor.execute("""
                INSERT INTO a00_graph_triples (subject_uri, predicate, object_uri, domain_code)
                VALUES (?, 'has_vet_drug_restriction', ?, 'A31_SAFETY');
            """, (m_name + "毛豬", d_name))
            
    conn.commit()
    conn.close()
    
    return {"livestock_safety_mesh_records_inserted": mesh_inserted}
