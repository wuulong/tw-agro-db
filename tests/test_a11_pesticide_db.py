"""
100% 領域特化單元測試: test_a11_pesticide_db.py
特化驗證: 農藥許可證 9,993 筆、Unicode 特殊字元 (滅) FTS5 倒排命中、禁用農藥 PROHIBITED_PESTICIDE 標籤
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

from modules.a11_pesticide_db.etl import run_etl
from modules.a11_pesticide_db.fts import build_fts_index
from modules.a11_pesticide_db.metadata_gen import update_metadata

TEST_DB_PATH = repo_root / "db" / "test_a11.db"
SAMPLE_JSON_PATH = repo_root / "agro_poc_samples" / "A11_pesticide_licenses.json"

@pytest.fixture(scope="module")
def setup_a11_db():
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
    TEST_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "="*80)
    print(f"🚀 [SETUP START] 初始化 A11 農藥許可證特化測試資料庫: {TEST_DB_PATH}")
    res_etl = run_etl(SAMPLE_JSON_PATH, TEST_DB_PATH)
    print(f"📥 A11 特化 ETL 入庫結果: {res_etl}")
    res_fts = build_fts_index(TEST_DB_PATH)
    print(f"🔍 A11 FTS5 倒排結果: {res_fts}")
    res_meta = update_metadata(TEST_DB_PATH)
    print(f"📋 A11 Metadata 寫入結果: {res_meta}")
    print("="*80 + "\n")
    
    yield TEST_DB_PATH
    
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()

def test_a11_val_001_record_counts(setup_a11_db):
    """VAL-001: 驗證 A11 許可證入庫筆數 (9993 筆)"""
    print("\n[VAL-001] 檢查 A11 農藥許可證數量...")
    conn = sqlite3.connect(str(setup_a11_db))
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM a11_pesticide_licenses")
    cnt = cursor.fetchone()[0]
    conn.close()
    
    print(f"  • A11 農藥許可證總筆數: {cnt}")
    assert cnt == 9993, f"A11 筆數應為 9993，實際為 {cnt}"
    print("  ✅ [VAL-001 PASS]")

def test_a11_val_002_unicode_special_char_fts(setup_a11_db):
    """VAL-002 [A11 領域特化]: 驗證 Unicode 特殊字元 (滅) FTS5 精準倒排命中與解析"""
    print("\n[VAL-002] 驗證 A11 Unicode 特殊字元 (滅) FTS5 倒排命中...")
    conn = sqlite3.connect(str(setup_a11_db))
    cursor = conn.cursor()
    
    t0 = time.perf_counter()
    cursor.execute("""
        SELECT r.pesticide_lic_id, r.pesticide_name, r.vendor_name
        FROM a11_pesticide_fts f
        JOIN a11_pesticide_licenses r ON f.pesticide_lic_id = r.pesticide_lic_id
        WHERE a11_pesticide_fts MATCH '滅'
    """)
    rows = cursor.fetchall()
    latency = time.perf_counter() - t0
    conn.close()
    
    print(f"  • FTS5 特殊字元 '滅' 命中: {len(rows)} 筆, 延遲: {latency*1000:.3f} ms")
    print(f"  • 命中樣例: {rows[0]}")
    assert len(rows) == 1, "特殊字元 '滅' 應精準命中 1 筆"
    assert "滅" in rows[0][1], "農藥名稱應包含 滅"
    print("  ✅ [VAL-002 PASS]")

def test_a11_val_003_prohibited_pesticide_flag(setup_a11_db):
    """VAL-003 [A11 領域特化標籤]: 驗證禁用農藥標籤 (PROHIBITED_PESTICIDE) 量化統計"""
    print("\n[VAL-003] 驗證 A11 禁用農藥屬性標籤量化統計...")
    conn = sqlite3.connect(str(setup_a11_db))
    cursor = conn.cursor()
    
    cursor.execute("SELECT attributes_json FROM a11_pesticide_licenses")
    rows = cursor.fetchall()
    conn.close()
    
    normal_cnt = 0
    prohibited_cnt = 0
    for r in rows:
        attr = json.loads(r[0])
        if attr.get("flag") == "PROHIBITED_PESTICIDE":
            prohibited_cnt += 1
        else:
            normal_cnt += 1
            
    print(f"  • A11 農藥許可證屬性統計: 正常許可={normal_cnt} 筆, 禁用農藥={prohibited_cnt} 筆")
    assert normal_cnt == 9993, "現行樣例數據應全數為正常登記許可證"
    print("  ✅ [VAL-003 PASS]")
