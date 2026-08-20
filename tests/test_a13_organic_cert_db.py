"""
100% 領域特化單元測試: test_a13_organic_cert_db.py
特化驗證: 噸均價值 UnitValue (元/噸) 算式 (如 硫酸銨 7,060.67 元/噸)、HIGH_UNIT_VALUE_MATERIAL 標籤分佈
"""

import sys
import sqlite3
import json
import time
from pathlib import Path
import pytest

repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from modules.a13_organic_cert_db.etl import run_etl
from modules.a13_organic_cert_db.fts import build_fts_index
from modules.a13_organic_cert_db.metadata_gen import update_metadata

TEST_DB_PATH = repo_root / "db" / "test_a13.db"
SAMPLE_JSON_PATH = repo_root / "agro_poc_samples" / "A13_organic_farm_list.json"

@pytest.fixture(scope="module")
def setup_a13_db():
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
    TEST_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "="*80)
    print(f"🚀 [SETUP START] 初始化 A13 有機資材特化測試資料庫: {TEST_DB_PATH}")
    res_etl = run_etl(SAMPLE_JSON_PATH, TEST_DB_PATH)
    print(f"📥 A13 特化 ETL 入庫結果: {res_etl}")
    res_fts = build_fts_index(TEST_DB_PATH)
    print(f"🔍 A13 FTS5 倒排結果: {res_fts}")
    res_meta = update_metadata(TEST_DB_PATH)
    print(f"📋 A13 Metadata 寫入結果: {res_meta}")
    print("="*80 + "\n")
    
    yield TEST_DB_PATH
    
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()

def test_a13_val_001_record_counts(setup_a13_db):
    """VAL-001: 驗證 A13 有機資材名冊筆數 (5 筆)"""
    print("\n[VAL-001] 檢查 A13 有機資材名冊筆數...")
    conn = sqlite3.connect(str(setup_a13_db))
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM a13_organic_materials_registry")
    cnt = cursor.fetchone()[0]
    conn.close()
    
    print(f"  • A13 資材名冊總筆數: {cnt}")
    assert cnt == 5, f"A13 筆數應為 5，實際為 {cnt}"
    print("  ✅ [VAL-001 PASS]")

def test_a13_val_002_unit_value_formula(setup_a13_db):
    """VAL-002 [A13 領域特化算式]: 驗證噸均價值 UnitValue (元/噸) 特化演算法 (硫酸銨)"""
    print("\n[VAL-002] 驗證 A13 有機資材噸均價值 UnitValue 算式 (硫酸銨)...")
    conn = sqlite3.connect(str(setup_a13_db))
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT material_name, quantity_tons, value_thousand_ntd, attributes_json
        FROM a13_organic_materials_registry
        WHERE material_name = '硫酸銨'
    """)
    name, qty, val_k, attr_json = cursor.fetchone()
    conn.close()
    
    unit_val = round((val_k * 1000) / qty, 2)
    attr = json.loads(attr_json)
    print(f"  • A13 硫酸銨數量: {qty} 噸, 價值: {val_k} 千元 ➔ 噸均價值 (UnitValue): {unit_val} 元/噸")
    print(f"  • attributes_json 實例: {attr}")
    assert name == "硫酸銨", "資材名稱應為 硫酸銨"
    assert unit_val == 7060.67, f"噸均價值應為 7060.67 元/噸，實際為 {unit_val}"
    assert attr.get("unit_val_ntd_per_ton") == 7060.67, "attributes_json 應紀錄 unit_val_ntd_per_ton"
    print("  ✅ [VAL-002 PASS]")
