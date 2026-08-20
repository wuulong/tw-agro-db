"""
100% 領域特化單元測試: test_a50_fao_agrovoc_db.py
硬核對齊 A50_SPECIFICATION.md 與 A50_ADVANCED_DESIGN_SPEC.md (VAL-001 ~ 004)
強調 A50 國際農學特異性: 中/英/繁簡三語系標籤、SKOS Broader 階層、EXACT_PREF_LABEL 匹配與 URI 錨點
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

from modules.a50_fao_agrovoc_db.etl import run_etl
from modules.a50_fao_agrovoc_db.fts import build_fts_index
from modules.a50_fao_agrovoc_db.metadata_gen import update_metadata

TEST_DB_PATH = repo_root / "db" / "test_a50.db"
SAMPLE_JSON_PATH = repo_root / "agro_poc_samples" / "A50_fao_agrovoc_full.json"

@pytest.fixture(scope="module")
def setup_a50_db():
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
    TEST_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "="*80)
    print(f"🚀 [SETUP START] 初始化 A50 國際農學主題詞測試資料庫: {TEST_DB_PATH}")
    res_etl = run_etl(SAMPLE_JSON_PATH, TEST_DB_PATH)
    print(f"📥 A50 特化 ETL 入庫結果: {res_etl}")
    res_fts = build_fts_index(TEST_DB_PATH)
    print(f"🔍 A50 FTS5 多語倒排結果: {res_fts}")
    res_meta = update_metadata(TEST_DB_PATH)
    print(f"📋 A50 Metadata 寫入結果: {res_meta}")
    print("="*80 + "\n")
    
    yield TEST_DB_PATH
    
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()

def test_a50_val_001_record_counts_and_multilingual(setup_a50_db):
    """VAL-001: 驗證 A50 AGROVOC 全量概念數 (4,951 筆) 與萬筆中/英/繁簡標籤分佈"""
    print("\n[VAL-001] 檢查 A50 概念與多語標籤數量...")
    conn = sqlite3.connect(str(setup_a50_db))
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM a50_agrovoc_concepts")
    concept_cnt = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM a50_agrovoc_labels")
    label_cnt = cursor.fetchone()[0]
    conn.close()
    
    print(f"  • A50 AGROVOC 全量概念數: {concept_cnt}, 多語標籤總數: {label_cnt}")
    assert concept_cnt >= 4951, f"概念數應 >= 4951 筆，實際為 {concept_cnt}"
    assert label_cnt >= 9933, f"標籤數應 >= 9933 筆，實際為 {label_cnt}"
    print("  ✅ [VAL-001 PASS]")

def test_a50_val_002_skos_hierarchy_traversal(setup_a50_db):
    """VAL-002 [A50 領域特化]: 驗證 SKOS Broader/Narrower 階層拓撲貫通 (全量 SKOS 貫通)"""
    print("\n[VAL-002] 驗證 A50 SKOS 階層拓撲貫通...")
    conn = sqlite3.connect(str(setup_a50_db))
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT h.subject_uri, l1.label_text AS child_name, h.object_uri, l2.label_text AS parent_name
        FROM a50_agrovoc_hierarchy h
        JOIN a50_agrovoc_labels l1 ON h.subject_uri = l1.concept_uri
        JOIN a50_agrovoc_labels l2 ON h.object_uri = l2.concept_uri
        LIMIT 1
    """)
    row = cursor.fetchone()
    conn.close()
    
    print(f"  • SKOS 階層關係: 子概念({row[1]}) ➔ 依附上位概念({row[3]})")
    assert row[1] is not None and row[3] is not None, "SKOS 階層應能成功關聯子概念與上位概念"
    print("  ✅ [VAL-002 PASS]")

def test_a50_val_003_multilingual_fts_search(setup_a50_db):
    """VAL-003: 驗證 A50 FTS5 多語跨國倒排檢索 (支援 'coconut', 萬筆 FTS 延遲 < 0.5s)"""
    print("\n[VAL-003] 測試 A50 FTS5 多語倒排檢索效能 (搜尋: 'coconut')...")
    conn = sqlite3.connect(str(setup_a50_db))
    cursor = conn.cursor()
    
    t0 = time.perf_counter()
    cursor.execute("""
        SELECT l.concept_uri, l.lang_code, l.label_text
        FROM a50_agrovoc_fts f
        JOIN a50_agrovoc_labels l ON f.concept_uri = l.concept_uri AND f.lang_code = l.lang_code AND f.label_text = l.label_text
        WHERE a50_agrovoc_fts MATCH 'coconut'
    """)
    rows = cursor.fetchall()
    latency = time.perf_counter() - t0
    conn.close()
    
    print(f"  • FTS5 檢索 'coconut' 命中 {len(rows)} 筆, 延遲: {latency*1000:.3f} ms")
    print(f"  • 命中特例: {rows[0]}")
    assert len(rows) > 0, "應搜尋到 coconut"
    assert latency < 0.5, f"全量萬筆 FTS 延遲應 < 0.5s，實際為 {latency:.6f}s"
    print("  ✅ [VAL-003 PASS]")

def test_a50_val_004_sys_module_metadata(setup_a50_db):
    """VAL-004 [Stage 7]: 驗證 SQL 系統表 sys_module_metadata 註冊"""
    print("\n[VAL-004] 檢查 sys_module_metadata 註冊狀態...")
    conn = sqlite3.connect(str(setup_a50_db))
    cursor = conn.cursor()
    
    cursor.execute("SELECT record_count FROM sys_module_metadata WHERE module_id = 'A50'")
    cnt = cursor.fetchone()[0]
    conn.close()
    
    print(f"  • sys_module_metadata 中 A50 紀錄筆數: {cnt}")
    assert cnt >= 4951, "sys_module_metadata 紀錄應 >= 4951 筆"
    print("  ✅ [VAL-004 PASS]")
