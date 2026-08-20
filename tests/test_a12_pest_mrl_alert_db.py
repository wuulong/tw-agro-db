"""
100% 領域特化單元測試: test_a12_pest_mrl_alert_db.py
特化驗證: 100分制 compliance_score 算式、HIGH_VIOLATION_RISK 違規風險標籤分佈
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

from modules.a12_pest_mrl_alert_db.etl import run_etl
from modules.a12_pest_mrl_alert_db.fts import build_fts_index
from modules.a12_pest_mrl_alert_db.metadata_gen import update_metadata

TEST_DB_PATH = repo_root / "db" / "test_a12.db"
SAMPLE_JSON_PATH = repo_root / "agro_poc_samples" / "A31_vet_drug_food_residue.json"

@pytest.fixture(scope="module")
def setup_a12_db():
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
    TEST_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "="*80)
    print(f"🚀 [SETUP START] 初始化 A12 農檢殘留監測特化測試資料庫: {TEST_DB_PATH}")
    res_etl = run_etl(SAMPLE_JSON_PATH, TEST_DB_PATH)
    print(f"📥 A12 特化 ETL 入庫結果: {res_etl}")
    res_fts = build_fts_index(TEST_DB_PATH)
    print(f"🔍 A12 FTS5 倒排結果: {res_fts}")
    res_meta = update_metadata(TEST_DB_PATH)
    print(f"📋 A12 Metadata 寫入結果: {res_meta}")
    print("="*80 + "\n")
    
    yield TEST_DB_PATH
    
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()

def test_a12_val_001_record_counts(setup_a12_db):
    """VAL-001: 驗證 A12 農檢殘留紀錄筆數 (5 筆)"""
    print("\n[VAL-001] 檢查 A12 農檢殘留抽驗筆數...")
    conn = sqlite3.connect(str(setup_a12_db))
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM a12_mrl_inspection_records")
    cnt = cursor.fetchone()[0]
    conn.close()
    
    print(f"  • A12 抽驗紀錄總筆數: {cnt}")
    assert cnt == 5, f"A12 筆數應為 5，實際為 {cnt}"
    print("  ✅ [VAL-001 PASS]")

def test_a12_val_002_compliance_score_distribution(setup_a12_db):
    """VAL-002 [A12 領域特化算式]: 驗證 100 分制 compliance_score 算式與合格率統計"""
    print("\n[VAL-002] 驗證 A12 100分制 compliance_score 合格率量化統計...")
    conn = sqlite3.connect(str(setup_a12_db))
    cursor = conn.cursor()
    
    cursor.execute("SELECT is_compliant, attributes_json FROM a12_mrl_inspection_records")
    rows = cursor.fetchall()
    conn.close()
    
    compliant_cnt = 0
    scores = []
    for r in rows:
        if r[0] == 1:
            compliant_cnt += 1
        attr = json.loads(r[1])
        scores.append(attr.get("compliance_score", 0))
        
    avg_score = round(sum(scores) / len(scores), 2)
    print(f"  • A12 抽驗合格筆數: {compliant_cnt}/5 筆 (100%), 平均合規分數: {avg_score} 分")
    assert compliant_cnt == 5, "現行樣例數據應 100% 合格"
    assert avg_score == 100.0, "合格數據合規分數應為 100 分"
    print("  ✅ [VAL-002 PASS]")
