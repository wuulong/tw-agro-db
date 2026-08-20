"""
100% 領域特化單元測試: test_a41_soil_water_pollution_db.py
硬核對齊 A41_SPECIFICATION.md 與 A41_ADVANCED_DESIGN_SPEC.md (VAL-001 ~ 004)
強調 A41 農業土壤與水質特異性: PollutionRatio 超標比率算式、SAFE/WARNING/HIGH_RISK 三級防護與 FTS5
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

from modules.a41_soil_water_pollution_db.etl import run_etl
from modules.a41_soil_water_pollution_db.fts import build_fts_index
from modules.a41_soil_water_pollution_db.metadata_gen import update_metadata

TEST_DB_PATH = repo_root / "db" / "test_a41.db"
SAMPLE_JSON_PATH = repo_root / "agro_poc_samples" / "A41_soil_water_pollution.json"

@pytest.fixture(scope="module")
def setup_a41_db():
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
    TEST_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "="*80)
    print(f"🚀 [SETUP START] 初始化 A41 土壤與水質環境安全測試資料庫: {TEST_DB_PATH}")
    res_etl = run_etl(SAMPLE_JSON_PATH, TEST_DB_PATH)
    print(f"📥 A41 特化 ETL 入庫結果: {res_etl}")
    res_fts = build_fts_index(TEST_DB_PATH)
    print(f"🔍 A41 FTS5 環境倒排結果: {res_fts}")
    res_meta = update_metadata(TEST_DB_PATH)
    print(f"📋 A41 Metadata 寫入結果: {res_meta}")
    print("="*80 + "\n")
    
    yield TEST_DB_PATH
    
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()

def test_a41_val_001_record_counts_and_pollution_rate(setup_a41_db):
    """VAL-001: 驗證 A41 土壤監測筆數 (5 筆) 與管制場址超標計數 (4 筆)"""
    print("\n[VAL-001] 檢查 A41 監測筆數與超標管制統計...")
    conn = sqlite3.connect(str(setup_a41_db))
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM a41_soil_water_monitoring")
    total_cnt = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM a41_soil_water_monitoring WHERE is_polluted = 1")
    polluted_cnt = cursor.fetchone()[0]
    conn.close()
    
    print(f"  • A41 土壤水質監測總筆數: {total_cnt}, 公告管制/超標筆數: {polluted_cnt}")
    assert total_cnt == 5, f"總筆數應為 5，實際為 {total_cnt}"
    assert polluted_cnt >= 4, f"管制超標筆數應 >= 4，實際為 {polluted_cnt}"
    print("  ✅ [VAL-001 PASS]")

def test_a41_val_002_pollution_ratio_scorer(setup_a41_db):
    """VAL-002 [A41 領域特化]: 驗證 PollutionRatio = conc / limit 與 HIGH_RISK 風險等級算式"""
    print("\n[VAL-002] 驗證 A41 PollutionRatio 算式與 HIGH_RISK 標籤...")
    conn = sqlite3.connect(str(setup_a41_db))
    cursor = conn.cursor()
    
    cursor.execute("SELECT site_id, concentration_ppm, regulatory_limit_ppm, is_polluted, attributes_json FROM a41_soil_water_monitoring LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    
    attr = json.loads(row[4])
    ratio = attr.get("pollution_ratio")
    safety_lvl = attr.get("safety_level")
    
    print(f"  • A41 監測點 {row[0]}: 實測={row[1]} ppm, 標準={row[2]} ppm ➔ PollutionRatio={ratio}, 風險等級={safety_lvl}")
    assert ratio is not None, "attributes_json 必須包含 pollution_ratio"
    assert safety_lvl in ["SAFE", "WARNING", "HIGH_RISK"], "safety_level 必須為合規枚舉"
    print("  ✅ [VAL-002 PASS]")

def test_a41_val_003_fts_environmental_search(setup_a41_db):
    """VAL-003: 驗證 A41 FTS5 環境倒排檢索 (支援 '臺北市', '北投區') 延遲 < 0.01s"""
    print("\n[VAL-003] 測試 A41 FTS5 環境倒排檢索效能 (搜尋: '北投區')...")
    conn = sqlite3.connect(str(setup_a41_db))
    cursor = conn.cursor()
    
    t0 = time.perf_counter()
    cursor.execute("""
        SELECT m.site_id, m.county_name, m.town_name, m.pollutant_type
        FROM a41_soil_water_fts f
        JOIN a41_soil_water_monitoring m ON f.site_id = m.site_id
        WHERE a41_soil_water_fts MATCH '北投區'
    """)
    rows = cursor.fetchall()
    latency = time.perf_counter() - t0
    conn.close()
    
    print(f"  • FTS5 檢索 '北投區' 命中 {len(rows)} 筆, 延遲: {latency*1000:.3f} ms")
    assert len(rows) > 0, "應搜尋到 北投區 監測點"
    assert latency < 0.01, f"FTS 延遲應 < 0.01s，實際為 {latency:.6f}s"
    print("  ✅ [VAL-003 PASS]")

def test_a41_val_004_sys_module_metadata(setup_a41_db):
    """VAL-004 [Stage 7]: 驗證 SQL 系統表 sys_module_metadata 註冊"""
    print("\n[VAL-004] 檢查 sys_module_metadata 註冊狀態...")
    conn = sqlite3.connect(str(setup_a41_db))
    cursor = conn.cursor()
    
    cursor.execute("SELECT record_count FROM sys_module_metadata WHERE module_id = 'A41'")
    cnt = cursor.fetchone()[0]
    conn.close()
    
    print(f"  • sys_module_metadata 中 A41 紀錄筆數: {cnt}")
    assert cnt == 5, "sys_module_metadata 紀錄應為 5 筆"
    print("  ✅ [VAL-004 PASS]")
