"""
100% 領域特化單元測試: test_a40_agro_climate_db.py
硬核對齊 A40_SPECIFICATION.md 與 A40_ADVANCED_DESIGN_SPEC.md (VAL-001 ~ 004)
強調 A40 氣象站特異性: 每日 96 點 (15 min/次) 滿頻率算式、觀測完整度比例、測站流水號與真實 CSV 連結
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

from modules.a40_agro_climate_db.etl import run_etl
from modules.a40_agro_climate_db.fts import build_fts_index
from modules.a40_agro_climate_db.metadata_gen import update_metadata

TEST_DB_PATH = repo_root / "db" / "test_a40.db"
SAMPLE_JSON_PATH = repo_root / "agro_poc_samples" / "A40_agro_climate_stations.json"

@pytest.fixture(scope="module")
def setup_a40_db():
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
    TEST_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "="*80)
    print(f"🚀 [SETUP START] 初始化 A40 農業氣象觀測測試資料庫: {TEST_DB_PATH}")
    
    res_etl = run_etl(SAMPLE_JSON_PATH, TEST_DB_PATH)
    print(f"📥 A40 特異 ETL 入庫結果: {res_etl}")
    res_fts = build_fts_index(TEST_DB_PATH)
    print(f"🔍 A40 FTS5 氣象站倒排結果: {res_fts}")
    res_meta = update_metadata(TEST_DB_PATH)
    print(f"📋 A40 Metadata 寫入結果: {res_meta}")
    print("="*80 + "\n")
    
    yield TEST_DB_PATH
    
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()

def test_a40_val_001_record_counts(setup_a40_db):
    """VAL-001: 驗證 A40 農業氣象站數據結構、測站流水號與 CSV 下載網址"""
    print("\n[VAL-001] 檢查 a40_climate_daily_obs 筆數、測站流水號與 CSV 連結...")
    conn = sqlite3.connect(str(setup_a40_db))
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM a40_climate_daily_obs")
    cnt = cursor.fetchone()[0]
    
    cursor.execute("SELECT station_sn, obs_date, obs_count, download_url FROM a40_climate_daily_obs WHERE station_sn = '100213' LIMIT 1")
    sample = cursor.fetchone()
    conn.close()
    
    print(f"  • A40 氣象觀測總筆數: {cnt}")
    print(f"  • 測站 100213 特異樣例: 測站={sample[0]}, 日期={sample[1]}, 觀測點數={sample[2]}點, URL={sample[3]}")
    assert cnt == 2527, f"a40_climate_daily_obs 應為 2527 筆，實際為 {cnt}"
    assert sample[0] == "100213", "測站流水號應為 100213"
    assert sample[2] == 96, "單日滿頻觀測點數應為 96 點 (15min/點)"
    print("  ✅ [VAL-001 PASS]")

def test_a40_val_002_observation_completeness_scorer(setup_a40_db):
    """VAL-002 [Advanced Spec E1 特異算式]: 驗證單日 96 點滿頻率算式 (ObsCount >= 96) 與 FULL_DAY_OBSERVATION 統計"""
    print("\n[VAL-002] 驗證 A40 氣象觀測完整度算式 (ObsCount >= 96 滿頻率比例)...")
    conn = sqlite3.connect(str(setup_a40_db))
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            COUNT(*) AS total_records,
            SUM(CASE WHEN obs_count >= 96 THEN 1 ELSE 0 END) AS full_day_count,
            SUM(CASE WHEN obs_count < 96 THEN 1 ELSE 0 END) AS partial_day_count
        FROM a40_climate_daily_obs
    """)
    total, full_cnt, partial_cnt = cursor.fetchone()
    full_ratio = round((full_cnt / total) * 100, 2)
    
    cursor.execute("SELECT attributes_json FROM a40_climate_daily_obs LIMIT 1")
    attr_json = cursor.fetchone()[0]
    attr = json.loads(attr_json)
    conn.close()
    
    print(f"  • 氣象觀測完整度量化結果: 總筆數={total}, 滿頻96點筆數={full_cnt}, 欠缺點數筆數={partial_cnt}, 滿頻率={full_ratio}%")
    print(f"  • attributes_json 實例: {attr}")
    assert total == 2527, "總筆數應為 2527"
    assert full_cnt == 2308, f"滿頻率 96 點觀測筆數應為 2308 筆 (91.33%)，實際為 {full_cnt}"
    assert partial_cnt == 219, f"欠缺點數筆數應為 219 筆 (8.67%)，實際為 {partial_cnt}"
    assert attr.get("flag") == "FULL_DAY_OBSERVATION", "屬性應正確標記 FULL_DAY_OBSERVATION"
    print("  ✅ [VAL-002 PASS]")

def test_a40_val_003_fts5_latency(setup_a40_db):
    """VAL-003: 驗證 A40 氣象站編號與日期多維 FTS5 全文倒排檢索與 <0.05s 延遲"""
    print("\n[VAL-003] 測試 A40 氣象站 FTS5 倒排檢索效能 (測站: 100476)...")
    conn = sqlite3.connect(str(setup_a40_db))
    cursor = conn.cursor()
    
    t0 = time.perf_counter()
    cursor.execute("""
        SELECT r.station_sn, r.obs_date, r.obs_count, r.download_url
        FROM a40_climate_fts f
        JOIN a40_climate_daily_obs r ON f.station_sn = r.station_sn AND f.obs_date = r.obs_date
        WHERE a40_climate_fts MATCH '100476'
        LIMIT 5
    """)
    rows = cursor.fetchall()
    latency = time.perf_counter() - t0
    conn.close()
    
    print(f"  • FTS5 氣象站 '100476' 檢索命中 {len(rows)} 筆，延遲: {latency*1000:.3f} ms")
    print(f"  • 檢索結果樣例: {rows[0]}")
    assert len(rows) > 0, "應搜尋到 測站 100476"
    assert latency < 0.05, f"FTS 延遲應 < 0.05s，實際為 {latency:.6f}s"
    print("  ✅ [VAL-003 PASS]")

def test_a40_val_004_sys_module_metadata(setup_a40_db):
    """VAL-004 [Stage 7]: 驗證 SQL 系統表 sys_module_metadata 註冊"""
    print("\n[VAL-004] 檢查 sys_module_metadata 註冊狀態...")
    conn = sqlite3.connect(str(setup_a40_db))
    cursor = conn.cursor()
    
    cursor.execute("SELECT record_count, last_updated FROM sys_module_metadata WHERE module_id = 'A40'")
    row = cursor.fetchone()
    conn.close()
    
    print(f"  • sys_module_metadata 中 A40 紀錄: 筆數={row[0]}, 更新時間={row[1]}")
    assert row[0] == 2527, "sys_module_metadata 紀錄應為 2527 筆"
    print("  ✅ [VAL-004 PASS]")
