"""
100% 領域特化單元測試: test_a31_vet_drug_food_residue_db.py
硬核對齊 A31_SPECIFICATION.md 與 A31_ADVANCED_DESIGN_SPEC.md (VAL-001 ~ 004)
強調 A31 動物用藥與畜產品殘留特異性: MRL 容許標準、禁用藥 (is_prohibited) 判定與 FTS5
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

from modules.a31_vet_drug_food_residue_db.etl import run_etl
from modules.a31_vet_drug_food_residue_db.fts import build_fts_index
from modules.a31_vet_drug_food_residue_db.metadata_gen import update_metadata

TEST_DB_PATH = repo_root / "db" / "test_a31.db"
SAMPLE_JSON_PATH = repo_root / "agro_poc_samples" / "A31_vet_drug_food_residue.json"

@pytest.fixture(scope="module")
def setup_a31_db():
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
    TEST_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "="*80)
    print(f"🚀 [SETUP START] 初始化 A31 動物用藥與畜產品殘留測試資料庫: {TEST_DB_PATH}")
    res_etl = run_etl(SAMPLE_JSON_PATH, TEST_DB_PATH)
    print(f"📥 A31 特化 ETL 入庫結果: {res_etl}")
    res_fts = build_fts_index(TEST_DB_PATH)
    print(f"🔍 A31 FTS5 動物用藥倒排結果: {res_fts}")
    res_meta = update_metadata(TEST_DB_PATH)
    print(f"📋 A31 Metadata 寫入結果: {res_meta}")
    print("="*80 + "\n")
    
    yield TEST_DB_PATH
    
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()

def test_a31_val_001_record_counts_and_prohibited(setup_a31_db):
    """VAL-001: 驗證 A31 動物用藥殘留筆數 (5 筆) 與禁用用藥計數 (2 筆)"""
    print("\n[VAL-001] 檢查 A31 用藥筆數與禁藥統計...")
    conn = sqlite3.connect(str(setup_a31_db))
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM a31_vet_drug_residue")
    total_cnt = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM a31_vet_drug_residue WHERE is_prohibited = 1")
    prohibited_cnt = cursor.fetchone()[0]
    conn.close()
    
    print(f"  • A31 動物用藥監測總筆數: {total_cnt}, 禁用/不合格用藥筆數: {prohibited_cnt}")
    assert total_cnt == 5, f"總筆數應為 5，實際為 {total_cnt}"
    assert prohibited_cnt >= 2, f"禁藥筆數應 >= 2，實際為 {prohibited_cnt}"
    print("  ✅ [VAL-001 PASS]")

def test_a31_val_002_vet_drug_safety_scorer(setup_a31_db):
    """VAL-002 [A31 領域特化]: 驗證禁藥 mrl_ppm == 0.0 與 PROHIBITED 風險等級枚舉"""
    print("\n[VAL-002] 驗證 A31 禁藥 Scorer 算式與 PROHIBITED 標籤...")
    conn = sqlite3.connect(str(setup_a31_db))
    cursor = conn.cursor()
    
    cursor.execute("SELECT drug_name, target_livestock, mrl_ppm, is_prohibited, attributes_json FROM a31_vet_drug_residue WHERE is_prohibited = 1 LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    
    attr = json.loads(row[4])
    risk_lvl = attr.get("risk_level")
    
    print(f"  • A31 禁藥樣例 {row[0]} ({row[1]}): MRL={row[2]} ppm ➔ 禁藥旗標={row[3]}, 風險等級={risk_lvl}")
    assert row[2] == 0.0, "禁藥殘留容許標準 MRL 應為 0.0 ppm"
    assert risk_lvl == "PROHIBITED", "attributes_json 必須標註 PROHIBITED 風險等級"
    print("  ✅ [VAL-002 PASS]")

def test_a31_val_003_fts_vet_drug_search(setup_a31_db):
    """VAL-003: 驗證 A31 FTS5 動物用藥倒排檢索 (支援 '氯黴素', '雞肉') 延遲 < 0.01s"""
    print("\n[VAL-003] 測試 A31 FTS5 動物用藥倒排檢索效能 (搜尋: '氯黴素')...")
    conn = sqlite3.connect(str(setup_a31_db))
    cursor = conn.cursor()
    
    t0 = time.perf_counter()
    cursor.execute("""
        SELECT m.residue_id, m.drug_name, m.target_livestock, m.mrl_ppm
        FROM a31_vet_drug_fts f
        JOIN a31_vet_drug_residue m ON f.rowid = m.residue_id
        WHERE a31_vet_drug_fts MATCH '氯黴素'
    """)
    rows = cursor.fetchall()
    latency = time.perf_counter() - t0
    conn.close()
    
    print(f"  • FTS5 檢索 '氯黴素' 命中 {len(rows)} 筆, 延遲: {latency*1000:.3f} ms")
    assert len(rows) > 0, "應搜尋到 氯黴素 紀錄"
    assert latency < 0.01, f"FTS 延遲應 < 0.01s，實際為 {latency:.6f}s"
    print("  ✅ [VAL-003 PASS]")

def test_a31_val_004_sys_module_metadata(setup_a31_db):
    """VAL-004 [Stage 7]: 驗證 SQL 系統表 sys_module_metadata 註冊"""
    print("\n[VAL-004] 檢查 sys_module_metadata 註冊狀態...")
    conn = sqlite3.connect(str(setup_a31_db))
    cursor = conn.cursor()
    
    cursor.execute("SELECT record_count FROM sys_module_metadata WHERE module_id = 'A31'")
    cnt = cursor.fetchone()[0]
    conn.close()
    
    print(f"  • sys_module_metadata 中 A31 紀錄筆數: {cnt}")
    assert cnt == 5, "sys_module_metadata 紀錄應為 5 筆"
    print("  ✅ [VAL-004 PASS]")
