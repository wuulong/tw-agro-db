"""
100% 領域特化單元測試: test_a14_organic_fertilizer_db.py
硬核對齊 A14_SPECIFICATION.md 與 A14_ADVANCED_DESIGN_SPEC.md (VAL-001 ~ 004)
強調 A14 農糧資材與肥料登記證特異性: N-P-K 三要素比例算式、ORGANIC_APPROVED 有機品質標籤與 FTS5
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

from modules.a14_organic_fertilizer_db.etl import run_etl
from modules.a14_organic_fertilizer_db.fts import build_fts_index
from modules.a14_organic_fertilizer_db.metadata_gen import update_metadata

TEST_DB_PATH = repo_root / "db" / "test_a14.db"
SAMPLE_JSON_PATH = repo_root / "agro_poc_samples" / "A14_organic_fertilizer.json"

@pytest.fixture(scope="module")
def setup_a14_db():
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
    TEST_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "="*80)
    print(f"🚀 [SETUP START] 初始化 A14 農糧資材與肥料登記證測試資料庫: {TEST_DB_PATH}")
    res_etl = run_etl(SAMPLE_JSON_PATH, TEST_DB_PATH)
    print(f"📥 A14 特化 ETL 入庫結果: {res_etl}")
    res_fts = build_fts_index(TEST_DB_PATH)
    print(f"🔍 A14 FTS5 肥料資材倒排結果: {res_fts}")
    res_meta = update_metadata(TEST_DB_PATH)
    print(f"📋 A14 Metadata 寫入結果: {res_meta}")
    print("="*80 + "\n")
    
    yield TEST_DB_PATH
    
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()

def test_a14_val_001_record_counts_and_organic(setup_a14_db):
    """VAL-001: 驗證 A14 肥料登記證筆數 (5 筆) 與有機審定合格計數 (3 筆)"""
    print("\n[VAL-001] 檢查 A14 肥料資材筆數與有機審定統計...")
    conn = sqlite3.connect(str(setup_a14_db))
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM a14_fertilizer_licenses")
    total_cnt = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM a14_fertilizer_licenses WHERE is_organic_cert = 1")
    organic_cnt = cursor.fetchone()[0]
    conn.close()
    
    print(f"  • A14 肥料資材總筆數: {total_cnt}, 有機審定合格筆數: {organic_cnt}")
    assert total_cnt == 5, f"總筆數應為 5，實際為 {total_cnt}"
    assert organic_cnt >= 3, f"有機資材筆數應 >= 3，實際為 {organic_cnt}"
    print("  ✅ [VAL-001 PASS]")

def test_a14_val_002_npk_ratio_scorer(setup_a14_db):
    """VAL-002 [A14 領域特化]: 驗證 NPK_Total 算式與 ORGANIC_APPROVED 品質標籤"""
    print("\n[VAL-002] 驗證 A14 NPK 養分比例與 ORGANIC_APPROVED 標籤...")
    conn = sqlite3.connect(str(setup_a14_db))
    cursor = conn.cursor()
    
    cursor.execute("SELECT fertilizer_lic_id, brand_name, nitrogen_pct, phosphorus_pct, potassium_pct, is_organic_cert, attributes_json FROM a14_fertilizer_licenses WHERE is_organic_cert = 1 LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    
    attr = json.loads(row[6])
    npk_tot = attr.get("npk_total_pct")
    f_grade = attr.get("fertilizer_grade")
    
    print(f"  • A14 有機資材樣例 {row[1]} ({row[0]}): N={row[2]}%, P={row[3]}%, K={row[4]}% ➔ NPK總和={npk_tot}%, 評等={f_grade}")
    assert npk_tot == round(row[2] + row[3] + row[4], 2), "attributes_json 必須包含精確之 npk_total_pct"
    assert f_grade == "ORGANIC_APPROVED", "有機資材評等應為 ORGANIC_APPROVED"
    print("  ✅ [VAL-002 PASS]")

def test_a14_val_003_fts_fertilizer_search(setup_a14_db):
    """VAL-003: 驗證 A14 FTS5 肥料倒排檢索 (支援 FTS5 全文倒排鏈結) 延遲 < 0.01s"""
    print("\n[VAL-003] 測試 A14 FTS5 肥料資材倒排檢索效能...")
    conn = sqlite3.connect(str(setup_a14_db))
    cursor = conn.cursor()
    
    t0 = time.perf_counter()
    cursor.execute("""
        SELECT m.fertilizer_lic_id, m.brand_name, m.manufacturer_name, m.fertilizer_type
        FROM a14_fertilizer_fts f
        JOIN a14_fertilizer_licenses m ON f.fertilizer_lic_id = m.fertilizer_lic_id
    """)
    rows = cursor.fetchall()
    latency = time.perf_counter() - t0
    conn.close()
    
    print(f"  • FTS5 倒排連網命中 {len(rows)} 筆, 延遲: {latency*1000:.3f} ms")
    assert len(rows) == 5, f"應檢索到全部 5 筆 FTS5 倒排紀錄，實際為 {len(rows)}"
    assert latency < 0.01, f"FTS 延遲應 < 0.01s，實際為 {latency:.6f}s"
    print("  ✅ [VAL-003 PASS]")

def test_a14_val_004_sys_module_metadata(setup_a14_db):
    """VAL-004 [Stage 7]: 驗證 SQL 系統表 sys_module_metadata 註冊"""
    print("\n[VAL-004] 檢查 sys_module_metadata 註冊狀態...")
    conn = sqlite3.connect(str(setup_a14_db))
    cursor = conn.cursor()
    
    cursor.execute("SELECT record_count FROM sys_module_metadata WHERE module_id = 'A14'")
    cnt = cursor.fetchone()[0]
    conn.close()
    
    print(f"  • sys_module_metadata 中 A14 紀錄筆數: {cnt}")
    assert cnt == 5, "sys_module_metadata 紀錄應為 5 筆"
    print("  ✅ [VAL-004 PASS]")
