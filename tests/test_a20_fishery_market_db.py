"""
100% 領域特化單元測試: test_a20_fishery_market_db.py
特化驗證: 管道分隔符 │ 描述解析器 parse_fishery_description(), LOCAL_TAIWAN_AQUACULTURE 在地養殖標籤分佈
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

from modules.a20_fishery_market_db.etl import run_etl, parse_fishery_description
from modules.a20_fishery_market_db.fts import build_fts_index
from modules.a20_fishery_market_db.metadata_gen import update_metadata

TEST_DB_PATH = repo_root / "db" / "test_a20.db"
SAMPLE_JSON_PATH = repo_root / "agro_poc_samples" / "A20_fishery_product_info.json"

@pytest.fixture(scope="module")
def setup_a20_db():
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
    TEST_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "="*80)
    print(f"🚀 [SETUP START] 初始化 A20 水產名冊特化測試資料庫: {TEST_DB_PATH}")
    res_etl = run_etl(SAMPLE_JSON_PATH, TEST_DB_PATH)
    print(f"📥 A20 特化 ETL 入庫結果: {res_etl}")
    res_fts = build_fts_index(TEST_DB_PATH)
    print(f"🔍 A20 FTS5 倒排結果: {res_fts}")
    res_meta = update_metadata(TEST_DB_PATH)
    print(f"📋 A20 Metadata 寫入結果: {res_meta}")
    print("="*80 + "\n")
    
    yield TEST_DB_PATH
    
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()

def test_a20_val_001_record_counts(setup_a20_db):
    """VAL-001: 驗證 A20 水產品名冊筆數 (5 筆)"""
    print("\n[VAL-001] 檢查 A20 水產品名冊筆數...")
    conn = sqlite3.connect(str(setup_a20_db))
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM a20_fishery_products")
    cnt = cursor.fetchone()[0]
    conn.close()
    
    print(f"  • A20 水產品名冊總筆數: {cnt}")
    assert cnt == 5, f"A20 筆數應為 5，實際為 {cnt}"
    print("  ✅ [VAL-001 PASS]")

def test_a20_val_002_pipe_parser_formula(setup_a20_db):
    """VAL-002 [A20 領域特化解析器]: 驗證管道分隔符 │ 描述解析器與產地/規格結構化拆解"""
    print("\n[VAL-002] 驗證 A20 管道分隔符 │ 描述解析器 (秋刀魚)...")
    raw_desc = "|產品名稱：秋刀魚|來源產地：臺灣|產品重量：500g|保存方式：零下-18℃"
    parsed = parse_fishery_description(raw_desc)
    
    print(f"  • Raw 描述: '{raw_desc}'")
    print(f"  • 特異解析結果: {parsed}")
    assert parsed.get('來源產地') == "臺灣", "來源產地應解析為 臺灣"
    assert parsed.get('產品重量') == "500g", "產品重量應解析為 500g"
    assert parsed.get('保存方式') == "零下-18℃", "保存方式應解析為 零下-18℃"
    print("  ✅ [VAL-002 PASS]")

def test_a20_val_003_origin_flag_distribution(setup_a20_db):
    """VAL-003 [A20 領域特化標籤]: 驗證在地養殖標籤 (LOCAL_TAIWAN_AQUACULTURE) 量化分佈"""
    print("\n[VAL-003] 驗證 A20 在地養殖屬性標籤量化統計...")
    conn = sqlite3.connect(str(setup_a20_db))
    cursor = conn.cursor()
    cursor.execute("SELECT origin_location, attributes_json FROM a20_fishery_products")
    rows = cursor.fetchall()
    conn.close()
    
    local_cnt = 0
    for r in rows:
        attr = json.loads(r[1])
        if attr.get("flag") == "LOCAL_TAIWAN_AQUACULTURE":
            local_cnt += 1
            
    print(f"  • A20 產地統計: 總筆數=5, 臺灣在地養殖={local_cnt}/5 筆 (80%)")
    assert local_cnt == 4, f"臺灣在地水產應為 4 筆 (80%)，實際為 {local_cnt}"
    print("  ✅ [VAL-003 PASS]")
