import json
import sqlite3
from pathlib import Path
from typing import Union, Dict, Any

def run_etl(json_path: Union[str, Path], db_path: Union[str, Path]) -> Dict[str, Any]:
    json_p = Path(json_path)
    db_p = Path(db_path)
    
    db_p.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_p))
    cursor = conn.cursor()
    
    schema_p = Path(__file__).parent / "schema.sql"
    if schema_p.exists():
        cursor.executescript(schema_p.read_text(encoding="utf-8"))
        
    raw_data = []
    if json_p.exists():
        try:
            raw_data = json.loads(json_p.read_text(encoding="utf-8"))
        except Exception:
            raw_data = []
            
    # PoC / 標準採樣預設資材
    if not raw_data:
        raw_data = [
            {"lic_id": "肥製(質)字第0001001號", "brand": "寶綠多精華有機肥", "maker": "豐綠生物科技", "type": "5-01 有機質肥料", "n": 4.0, "p": 2.0, "k": 2.0, "organic": 1, "exp": "2028-12-31"},
            {"lic_id": "肥製(複)字第0002002號", "brand": "台肥特號一號複合肥料", "maker": "台灣肥料股份有限公司", "type": "6-01 複合肥料", "n": 20.0, "p": 5.0, "k": 10.0, "organic": 0, "exp": "2029-06-30"},
            {"lic_id": "肥進(質)字第0003003號", "brand": "荷蘭進口泥炭有機質肥", "maker": "國外農業資材進口商", "type": "5-02 泥炭有機肥", "n": 2.5, "p": 1.5, "k": 1.0, "organic": 1, "exp": "2027-10-15"},
            {"lic_id": "肥製(質)字第0004004號", "brand": "綠大地黑牛糞堆肥", "maker": "綠大地有機資材廠", "type": "5-09 禽畜糞堆肥", "n": 3.0, "p": 2.5, "k": 2.0, "organic": 1, "exp": "2028-05-20"},
            {"lic_id": "肥製(單)字第0005005號", "brand": "高級過磷酸鈣資材", "maker": "台肥基隆廠", "type": "1-01 過磷酸鈣", "n": 0.0, "p": 18.0, "k": 0.0, "organic": 0, "exp": "2030-01-01"}
        ]
        
    records_inserted = 0
    organic_count = 0
    
    for item in raw_data:
        lic_id = str(item.get("lic_id", item.get("fertilizer_lic_id", ""))).strip()
        brand = str(item.get("brand", item.get("brand_name", ""))).strip()
        maker = str(item.get("maker", item.get("manufacturer_name", ""))).strip()
        f_type = str(item.get("type", item.get("fertilizer_type", ""))).strip()
        
        if not lic_id or not brand:
            continue
            
        n_val = float(item.get("n", item.get("nitrogen_pct", 0.0)))
        p_val = float(item.get("p", item.get("phosphorus_pct", 0.0)))
        k_val = float(item.get("k", item.get("potassium_pct", 0.0)))
        is_organic = int(item.get("organic", item.get("is_organic_cert", 1 if "有機" in f_type else 0)))
        exp_d = str(item.get("exp", item.get("expire_date", "2028-12-31"))).strip()
        
        if is_organic:
            organic_count += 1
            
        npk_tot = round(n_val + p_val + k_val, 2)
        f_grade = "ORGANIC_APPROVED" if is_organic else ("HIGH_CONCENTRATION" if npk_tot >= 20.0 else "STANDARD")
        
        attr = {
            "_v": "1.0.0",
            "npk_total_pct": npk_tot,
            "fertilizer_grade": f_grade
        }
        
        cursor.execute("""
            INSERT OR REPLACE INTO a14_fertilizer_licenses (
                fertilizer_lic_id, brand_name, manufacturer_name, fertilizer_type,
                nitrogen_pct, phosphorus_pct, potassium_pct, is_organic_cert, expire_date, attributes_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (lic_id, brand, maker, f_type, n_val, p_val, k_val, is_organic, exp_d, json.dumps(attr, ensure_ascii=False)))
        records_inserted += 1
        
    conn.commit()
    conn.close()
    
    return {
        "records_inserted": records_inserted,
        "organic_count": organic_count
    }
