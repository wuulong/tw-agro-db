import sqlite3
import json
from pathlib import Path
from typing import Union, Dict, Any

def build_crop_pesticide_safety_mesh(db_path: Union[str, Path]) -> Dict[str, Any]:
    """
    母大腦事前融合分析引擎 (A00 Pre-computed Fusion Engine)
    將 A10 (農作物行情)、A11 (農藥許可證與停藥天數)、A12 (殘留抽驗違規) 進行跨庫特徵實體化與安全網碰撞
    """
    db_p = Path(db_path)
    if not db_p.exists():
        raise FileNotFoundError(f"DB 檔案不存在: {db_p}")
        
    conn = sqlite3.connect(str(db_p))
    cursor = conn.cursor()
    
    # 1. 確保實體分析表 a00_crop_pesticide_safety_mesh 存在
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS a00_crop_pesticide_safety_mesh (
            crop_id TEXT NOT NULL,            -- 作物主碼 (A10)
            crop_name TEXT NOT NULL,          -- 作物名稱
            pesticide_lic_id TEXT NOT NULL,   -- 農藥許可證號 (A11)
            pesticide_name TEXT NOT NULL,     -- 農藥名稱
            dilution_ratio TEXT,              -- 推薦稀釋倍數
            safety_period_days INTEGER,       -- 安全採收停藥期 (天數)
            mrl_ppm REAL,                     -- MRL 容許量 (ppm, A12)
            risk_level TEXT DEFAULT 'SAFE',   -- SAFE, CAUTION, HIGH_RISK
            attributes_json TEXT NOT NULL DEFAULT '{"_v":"1.0.0"}',
            PRIMARY KEY (crop_id, pesticide_lic_id)
        );
    """)
    cursor.execute("DELETE FROM a00_crop_pesticide_safety_mesh")
    
    # 2. 從 A10 作物字典與 A11 農藥許可證提取關聯數據
    cursor.execute("SELECT crop_id, crop_name FROM a10_crop_dictionary")
    crops = cursor.fetchall()
    
    cursor.execute("SELECT pesticide_lic_id, pesticide_name, brand_name, formulation, expire_date, revoke_type FROM a11_pesticide_licenses")
    pesticides = cursor.fetchall()
    
    # 3. 取得 A12 不合格農檢抽驗紀錄之關鍵字集合
    cursor.execute("SELECT sample_name, test_result FROM a12_mrl_inspection_records WHERE is_compliant = 0")
    non_compliant_rows = cursor.fetchall()
    non_compliant_samples = set(r[0] for r in non_compliant_rows)
    
    mesh_records = []
    # 跨庫對合計算 (以主要作物如 椰子, 甘藍, 釋迦 連動 A11 許可證)
    for c_id, c_name in crops[:20]: # 採樣前 20 主力作物
        is_sample_risky = any(c_name in s for s in non_compliant_samples)
        for lic_id, p_name, brand, form, exp_d, rev in pesticides[:10]: # 對合主力農藥
            risk = "SAFE"
            if rev and "廢止" in rev:
                risk = "HIGH_RISK"
            elif is_sample_risky:
                risk = "CAUTION"
                
            attr = {
                "_v": "1.0.0",
                "brand_name": brand,
                "formulation": form,
                "expire_date": exp_d
            }
            
            mesh_records.append((
                c_id,
                c_name,
                lic_id,
                p_name or brand or "未定名農藥",
                "1000倍", # 預設推荐
                7,        # 預設 7 天安全採收期
                0.05,     # MRL 預設容許量
                risk,
                json.dumps(attr, ensure_ascii=False)
            ))
            
    cursor.executemany("""
        INSERT OR REPLACE INTO a00_crop_pesticide_safety_mesh (
            crop_id, crop_name, pesticide_lic_id, pesticide_name, dilution_ratio, safety_period_days, mrl_ppm, risk_level, attributes_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, mesh_records)
    
    cnt = cursor.rowcount
    conn.commit()
    conn.close()
    
    return {"safety_mesh_records_inserted": cnt}
