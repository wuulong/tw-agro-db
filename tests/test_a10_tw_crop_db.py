"""
100% 領域特化單元測試: test_a10_tw_crop_db.py
特化驗證: 作物行情全台均價、休市過濾標記、離散波幅 CV (變異係數) 計算
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

from modules.a10_tw_crop_db.etl import run_etl
from modules.a10_tw_crop_db.fts import build_fts_index
from modules.a10_tw_crop_db.metadata_gen import update_metadata

TEST_DB_PATH = repo_root / "db" / "test_a10.db"
SAMPLE_JSON_PATH = repo_root / "agro_poc_samples" / "A10_crop_farm_trans.json"

@pytest.fixture(scope="module")
def setup_a10_db():
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
    TEST_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "="*80)
    print(f"🚀 [SETUP START] 初始化 A10 農糧行情特化測試資料庫: {TEST_DB_PATH}")
    res_etl = run_etl(SAMPLE_JSON_PATH, TEST_DB_PATH)
    print(f"📥 A10 特化 ETL 入庫結果: {res_etl}")
    res_fts = build_fts_index(TEST_DB_PATH)
    print(f"🔍 A10 FTS5 倒排結果: {res_fts}")
    res_meta = update_metadata(TEST_DB_PATH)
    print(f"📋 A10 Metadata 寫入結果: {res_meta}")
    print("="*80 + "\n")
    
    yield TEST_DB_PATH
    
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()

def test_a10_val_001_record_counts_and_dict(setup_a10_db):
    """VAL-001: 驗證 A10 作物字典與每日行情紀錄入庫數量"""
    print("\n[VAL-001] 檢查 A10 作物字典與每日行情...")
    conn = sqlite3.connect(str(setup_a10_db))
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM a10_crop_dictionary")
    dict_cnt = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM a10_crop_trans_daily")
    trans_cnt = cursor.fetchone()[0]
    cursor.execute("SELECT crop_id, crop_name, category_name FROM a10_crop_dictionary WHERE crop_name = '椰子'")
    sample = cursor.fetchone()
    conn.close()
    
    print(f"  • A10 作物字典數: {dict_cnt}, 交易紀錄數: {trans_cnt}")
    print(f"  • 作物 '椰子' 特例: {sample}")
    assert dict_cnt == 1001, f"字典數應為 1001，實際為 {dict_cnt}"
    assert sample[1] == "椰子", "作物名稱應為 椰子"
    print("  ✅ [VAL-001 PASS]")

def test_a10_val_002_cv_price_volatility(setup_a10_db):
    """VAL-002 [A10 領域特化算式]: 驗證全台作物均價與價格離散波幅 CV (變異係數) 特化演算法"""
    print("\n[VAL-002] 驗證 A10 作物價格離散波幅 CV 特化算式 (椰子)...")
    conn = sqlite3.connect(str(setup_a10_db))
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT crop_id, price_avg, volume_kg
        FROM a10_crop_trans_daily
        WHERE crop_id = '11' AND price_avg > 0
    """)
    rows = cursor.fetchall()
    prices = [r[1] for r in rows]
    avg_price = round(sum(prices) / len(prices), 2)
    
    # 計算 CV (標準差 / 平均值)
    import math
    variance = sum((x - avg_price) ** 2 for x in prices) / len(prices)
    std_dev = math.sqrt(variance)
    cv = round(std_dev / avg_price, 4)
    conn.close()
    
    print(f"  • 椰子全台平均價: {avg_price} 元/kg, 離散標準差: {std_dev:.4f}, 價格變異係數 (CV): {cv}")
    assert avg_price == 16.91, f"椰子全台均價應為 16.91 元/kg，實際為 {avg_price}"
    assert cv == 0.232, f"椰子價格波動 CV 應為 0.232，實際為 {cv}"
    print("  ✅ [VAL-002 PASS]")

def test_a10_val_003_fts5_search(setup_a10_db):
    """VAL-003: 驗證 A10 FTS5 作物關鍵字檢索"""
    print("\n[VAL-003] 測試 A10 FTS5 倒排檢索 (椰子)...")
    conn = sqlite3.connect(str(setup_a10_db))
    cursor = conn.cursor()
    
    t0 = time.perf_counter()
    cursor.execute("""
        SELECT d.crop_id, d.crop_name, t.price_avg
        FROM a10_crop_fts f
        JOIN a10_crop_dictionary d ON f.crop_id = d.crop_id
        LEFT JOIN a10_crop_trans_daily t ON d.crop_id = t.crop_id
        WHERE a10_crop_fts MATCH '椰子'
        LIMIT 5
    """)
    rows = cursor.fetchall()
    latency = time.perf_counter() - t0
    conn.close()
    
    print(f"  • A10 FTS 命中 {len(rows)} 筆，延遲: {latency*1000:.3f} ms")
    assert len(rows) > 0, "應檢索到 椰子"
    print("  ✅ [VAL-003 PASS]")
