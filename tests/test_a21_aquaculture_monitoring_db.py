"""
100% 領域特化單元測試: test_a21_aquaculture_monitoring_db.py
硬核對齊 A21_SPECIFICATION.md 與 A21_ADVANCED_DESIGN_SPEC.md (VAL-001 ~ 004)
強調 A21 水產養殖水質特異性: 寒害 (Temp < 15°C) 與低溶氧 (DO < 3mg/L) 雙重風險算式與 FTS5
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

from modules.a21_aquaculture_monitoring_db.etl import run_etl
from modules.a21_aquaculture_monitoring_db.fts import build_fts_index
from modules.a21_aquaculture_monitoring_db.metadata_gen import update_metadata

TEST_DB_PATH = repo_root / "db" / "test_a21.db"
SAMPLE_JSON_PATH = repo_root / "agro_poc_samples" / "A21_aquaculture_monitoring.json"

@pytest.fixture(scope="module")
def setup_a21_db():
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
    TEST_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "="*80)
    print(f"🚀 [SETUP START] 初始化 A21 水產養殖水質與寒害監測測試資料庫: {TEST_DB_PATH}")
    res_etl = run_etl(SAMPLE_JSON_PATH, TEST_DB_PATH)
    print(f"📥 A21 特化 ETL 入庫結果: {res_etl}")
    res_fts = build_fts_index(TEST_DB_PATH)
    print(f"🔍 A21 FTS5 水產倒排結果: {res_fts}")
    res_meta = update_metadata(TEST_DB_PATH)
    print(f"📋 A21 Metadata 寫入結果: {res_meta}")
    print("="*80 + "\n")
    
    yield TEST_DB_PATH
    
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()

def test_a21_val_001_record_counts_and_cold_snap(setup_a21_db):
    """VAL-001: 驗證 A21 水產養殖筆數 (13 筆) 與低溫寒害觸發次數"""
    print("\n[VAL-001] 檢查 A21 養殖場監測筆數與寒害統計...")
    conn = sqlite3.connect(str(setup_a21_db))
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM a21_aquaculture_monitoring")
    total_cnt = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM a21_aquaculture_monitoring WHERE risk_level IN ('WARNING', 'HIGH_RISK')")
    risk_cnt = cursor.fetchone()[0]
    conn.close()
    
    print(f"  • A21 水產養殖監測總筆數: {total_cnt}, 觸發風險警訊筆數: {risk_cnt}")
    assert total_cnt == 13, f"總筆數應為 13，實際為 {total_cnt}"
    assert risk_cnt >= 10, f"風險警訊筆數應 >= 10，實際為 {risk_cnt}"
    print("  ✅ [VAL-001 PASS]")

def test_a21_val_002_aquaculture_risk_scorer(setup_a21_db):
    """VAL-002 [A21 領域特化]: 驗證水溫 < 15°C 觸發 cold_snap_flag 與 risk_level 枚舉"""
    print("\n[VAL-002] 驗證 A21 水質水溫與寒害 Scorer 算式...")
    conn = sqlite3.connect(str(setup_a21_db))
    cursor = conn.cursor()
    
    cursor.execute("SELECT farm_id, aquaculture_species, water_temp_c, dissolved_oxygen_mg_l, risk_level, attributes_json FROM a21_aquaculture_monitoring LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    
    attr = json.loads(row[5])
    cold_flag = attr.get("cold_snap_flag")
    risk_lvl = row[4]
    
    print(f"  • A21 養殖場 {row[0]} ({row[1]}): 水溫={row[2]}°C, 溶氧={row[3]}mg/L ➔ 寒害旗標={cold_flag}, 風險等級={risk_lvl}")
    assert cold_flag is True, "水溫 13.08°C < 15°C 必須觸發 cold_snap_flag"
    assert risk_lvl in ["SAFE", "WARNING", "HIGH_RISK"], "risk_level 必須為合規枚舉"
    print("  ✅ [VAL-002 PASS]")

def test_a21_val_003_fts_aquaculture_search(setup_a21_db):
    """VAL-003: 驗證 A21 FTS5 水產倒排檢索 (支援 '台南市', '虱目魚') 延遲 < 0.01s"""
    print("\n[VAL-003] 測試 A21 FTS5 水產倒排檢索效能 (搜尋: '虱目魚')...")
    conn = sqlite3.connect(str(setup_a21_db))
    cursor = conn.cursor()
    
    t0 = time.perf_counter()
    cursor.execute("""
        SELECT m.farm_id, m.county_name, m.aquaculture_species, m.water_temp_c
        FROM a21_aquaculture_fts f
        JOIN a21_aquaculture_monitoring m ON f.farm_id = m.farm_id
        WHERE a21_aquaculture_fts MATCH '虱目魚'
    """)
    rows = cursor.fetchall()
    latency = time.perf_counter() - t0
    conn.close()
    
    print(f"  • FTS5 檢索 '虱目魚' 命中 {len(rows)} 筆, 延遲: {latency*1000:.3f} ms")
    assert len(rows) > 0, "應搜尋到 虱目魚 養殖場"
    assert latency < 0.01, f"FTS 延遲應 < 0.01s，實際為 {latency:.6f}s"
    print("  ✅ [VAL-003 PASS]")

def test_a21_val_004_sys_module_metadata(setup_a21_db):
    """VAL-004 [Stage 7]: 驗證 SQL 系統表 sys_module_metadata 註冊"""
    print("\n[VAL-004] 檢查 sys_module_metadata 註冊狀態...")
    conn = sqlite3.connect(str(setup_a21_db))
    cursor = conn.cursor()
    
    cursor.execute("SELECT record_count FROM sys_module_metadata WHERE module_id = 'A21'")
    cnt = cursor.fetchone()[0]
    conn.close()
    
    print(f"  • sys_module_metadata 中 A21 紀錄筆數: {cnt}")
    assert cnt == 13, "sys_module_metadata 紀錄應為 13 筆"
    print("  ✅ [VAL-004 PASS]")
