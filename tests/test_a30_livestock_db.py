"""
100% 領域特化單元測試: test_a30_livestock_db.py
特化驗證: 無槓民國年日期轉碼 (1150819 -> 2026-08-19)、規格豬比率 SpecRatio 算式 (如 花蓮縣 85.91%)
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

from modules.a30_livestock_db.etl import run_etl
from modules.a30_livestock_db.fts import build_fts_index
from modules.a30_livestock_db.metadata_gen import update_metadata

TEST_DB_PATH = repo_root / "db" / "test_a30.db"
SAMPLE_JSON_PATH = repo_root / "agro_poc_samples" / "A30_livestock_pork_trans.json"

@pytest.fixture(scope="module")
def setup_a30_db():
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
    TEST_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "="*80)
    print(f"🚀 [SETUP START] 初始化 A30 毛豬批發行情特化測試資料庫: {TEST_DB_PATH}")
    res_etl = run_etl(SAMPLE_JSON_PATH, TEST_DB_PATH)
    print(f"📥 A30 特化 ETL 入庫結果: {res_etl}")
    res_fts = build_fts_index(TEST_DB_PATH)
    print(f"🔍 A30 FTS5 倒排結果: {res_fts}")
    res_meta = update_metadata(TEST_DB_PATH)
    print(f"📋 A30 Metadata 寫入結果: {res_meta}")
    print("="*80 + "\n")
    
    yield TEST_DB_PATH
    
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()

def test_a30_val_001_record_counts(setup_a30_db):
    """VAL-001: 驗證 A30 毛豬批發行情筆數 (5 筆) 與無槓民國年轉碼"""
    print("\n[VAL-001] 檢查 A30 毛豬批發行情筆數與日期轉碼...")
    conn = sqlite3.connect(str(setup_a30_db))
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM a30_pork_trans_daily")
    cnt = cursor.fetchone()[0]
    cursor.execute("SELECT trans_date, market_name, total_heads, avg_price_ntd FROM a30_pork_trans_daily WHERE market_name = '花蓮縣'")
    sample = cursor.fetchone()
    conn.close()
    
    print(f"  • A30 毛豬批發行情總筆數: {cnt}")
    print(f"  • 花蓮縣樣例: 日期={sample[0]} (ISO 8601), 市場={sample[1]}, 頭數={sample[2]}, 均價={sample[3]}元/kg")
    assert cnt == 5, f"A30 筆數應為 5，實際為 {cnt}"
    assert sample[0] == "2026-08-19", "無槓民國年 1150819 應正確轉換為 2026-08-19"
    print("  ✅ [VAL-001 PASS]")

def test_a30_val_002_spec_ratio_formula(setup_a30_db):
    """VAL-002 [A30 領域特化算式]: 驗證規格豬比率 SpecRatio (%) 算式與 attributes_json"""
    print("\n[VAL-002] 驗證 A30 規格豬比率 SpecRatio 算式 (花蓮縣)...")
    conn = sqlite3.connect(str(setup_a30_db))
    cursor = conn.cursor()
    cursor.execute("SELECT market_name, total_heads, spec_heads, attributes_json FROM a30_pork_trans_daily WHERE market_name = '花蓮縣'")
    m_name, total, spec, attr_json = cursor.fetchone()
    conn.close()
    
    spec_ratio = round((spec / total) * 100, 2)
    attr = json.loads(attr_json)
    print(f"  • 花蓮縣成交頭數: {total} 頭, 規格豬頭數: {spec} 頭 ➔ 規格豬比率 (SpecRatio): {spec_ratio}%")
    print(f"  • attributes_json 實例: {attr}")
    assert m_name == "花蓮縣", "市場應為 花蓮縣"
    assert spec_ratio == 98.97, f"規格豬比率應為 98.97%，實際為 {spec_ratio}%"
    assert attr.get("spec_ratio_pct") == 98.97, "attributes_json 應紀錄 spec_ratio_pct"
    print("  ✅ [VAL-002 PASS]")
