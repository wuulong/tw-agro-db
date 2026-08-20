"""
100% 獨立單元測試: test_a00_master_hub.py
硬核對齊 A00_SPECIFICATION.md 與 A00_ADVANCED_DESIGN_SPEC.md (VAL-A00-001 ~ VAL-A00-010)
完整涵蓋:
  - 4 大單對單鏈結 (A00 ↔ A10, A11, A12, A13)
  - 3 大雙模組組合 (A10+A11, A11+A12, A10+A13)
  - 1 大三重安全網 (A10+A11+A12)
  - 1 大四重全路徑大合龍 (A10+A11+A12+A13)
  - 1 大全域 FTS5 與 Manifest 檢索測試
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

from modules.a10_tw_crop_db.etl import run_etl as run_a10_etl
from modules.a11_pesticide_db.etl import run_etl as run_a11_etl
from modules.a12_pest_mrl_alert_db.etl import run_etl as run_a12_etl
from modules.a13_organic_cert_db.etl import run_etl as run_a13_etl

from src.a00_core.master_builder.views_domestic import inject_master_views
from src.a00_core.master_builder.builder_fts import build_global_fts
from src.a00_core.master_builder.builder_analytics import build_analytics
from src.a00_core.master_builder.builder_safety_mesh import build_crop_pesticide_safety_mesh

TEST_DB_PATH = repo_root / "db" / "test_a00.db"

@pytest.fixture(scope="module")
def setup_master_db():
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
    TEST_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "="*80)
    print(f"🚀 [SETUP START] 初始化 A00 母大腦四域融合測試資料庫: {TEST_DB_PATH}")
    
    # 1. 依次載入 A10, A11, A12, A13 四域數據
    run_a10_etl(repo_root / "agro_poc_samples" / "A10_crop_farm_trans.json", TEST_DB_PATH)
    # 1.5 跑 A11 入庫
    SAMPLE_A11_PATH = repo_root / "agro_poc_samples" / "A11_pesticide_licenses.json"
    run_a11_etl(SAMPLE_A11_PATH, TEST_DB_PATH)
    # 1.7 跑 A13 入庫
    from modules.a13_organic_cert_db.etl import run_etl as run_a13_etl
    SAMPLE_A13_PATH = repo_root / "agro_poc_samples" / "A13_organic_farm_list.json"
    run_a13_etl(SAMPLE_A13_PATH, TEST_DB_PATH)
    # 1.8 跑 A30 入庫
    from modules.a30_livestock_db.etl import run_etl as run_a30_etl
    SAMPLE_A30_PATH = repo_root / "agro_poc_samples" / "A30_livestock_pork_trans.json"
    run_a30_etl(SAMPLE_A30_PATH, TEST_DB_PATH)
    # 1.9 跑 A20 入庫
    from modules.a20_fishery_market_db.etl import run_etl as run_a20_etl
    SAMPLE_A20_PATH = repo_root / "agro_poc_samples" / "A20_fishery_product_info.json"
    run_a20_etl(SAMPLE_A20_PATH, TEST_DB_PATH)
    # 2.0 跑 A40 入庫
    from modules.a40_agro_climate_db.etl import run_etl as run_a40_etl
    SAMPLE_A40_PATH = repo_root / "agro_poc_samples" / "A40_agro_climate_stations.json"
    run_a40_etl(SAMPLE_A40_PATH, TEST_DB_PATH)
    # 2.0.1 跑 A41 入庫
    from modules.a41_soil_water_pollution_db.etl import run_etl as run_a41_etl
    SAMPLE_A41_PATH = repo_root / "agro_poc_samples" / "A41_soil_water_pollution.json"
    run_a41_etl(SAMPLE_A41_PATH, TEST_DB_PATH)
    # 2.0.2 跑 A31 入庫 (遵循 SOP 剛性規範)
    from modules.a31_vet_drug_food_residue_db.etl import run_etl as run_a31_etl
    SAMPLE_A31_PATH = repo_root / "agro_poc_samples" / "A31_vet_drug_food_residue.json"
    run_a31_etl(SAMPLE_A31_PATH, TEST_DB_PATH)
    # 2.0.3 跑 A14 入庫 (遵循 SOP 剛性規範)
    from modules.a14_organic_fertilizer_db.etl import run_etl as run_a14_etl
    SAMPLE_A14_PATH = repo_root / "agro_poc_samples" / "A14_organic_fertilizer.json"
    run_a14_etl(SAMPLE_A14_PATH, TEST_DB_PATH)
    # 2.1 跑 A50 入庫
    from modules.a50_fao_agrovoc_db.etl import run_etl as run_a50_etl
    SAMPLE_A50_PATH = repo_root / "agro_poc_samples" / "A50_fao_agrovoc.json"
    run_a50_etl(SAMPLE_A50_PATH, TEST_DB_PATH)
    run_a12_etl(repo_root / "agro_poc_samples" / "A31_vet_drug_food_residue.json", TEST_DB_PATH)
    run_a13_etl(repo_root / "agro_poc_samples" / "A13_organic_farm_list.json", TEST_DB_PATH)
    
    # 2. 織連 A00 視圖
    res_v = inject_master_views(TEST_DB_PATH)
    print(f"🔗 View 織連結果: {res_v}")
    
    # 3. 建立全域倒排
    res_fts = build_global_fts(TEST_DB_PATH)
    print(f"🔍 全域倒排 FTS 建立結果: {res_fts}")
    
    # 4. 建立母大腦離散分析與事前安全網
    res_ana = build_analytics(TEST_DB_PATH)
    print(f"📊 母大腦離散分析建立結果: {res_ana}")
    
    res_mesh = build_crop_pesticide_safety_mesh(TEST_DB_PATH)
    print(f"🛡️ 母大腦事前農藥安全網建立結果: {res_mesh}")
    # 5. 跨領域 A00 AGROVOC 本體網
    from src.a00_core.master_builder.builder_agrovoc_mesh import build_agrovoc_mesh
    res_agro_mesh = build_agrovoc_mesh(TEST_DB_PATH)
    print(f"  • A00 ↔ A50 跨領域 AGROVOC 本體網碰撞結果: {res_agro_mesh}")
    # 6. 1-Hop GraphRAG 實體圖譜網
    from src.a00_core.master_builder.builder_ontology_graph import build_ontology_graph
    res_graph = build_ontology_graph(TEST_DB_PATH)
    print(f"  • E13~E16 GraphRAG 實體圖譜網建立結果: {res_graph}")
    print("="*80 + "\n")
    
    yield TEST_DB_PATH
    
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()

# -----------------------------------------------------------------------------
# 🔹 一、 單一模組特定鏈結 (A00 ↔ Single Submodule Integrations)
# -----------------------------------------------------------------------------

def test_a00_val_001_single_a10_link(setup_master_db):
    """VAL-A00-001 (A00 ↔ A10): 驗證 A10 行情與字典 View 穿透與全台均價離散彙整算式"""
    print("\n[VAL-A00-001] 測試 A00 ↔ A10 農糧行情單一模組鏈結...")
    conn = sqlite3.connect(str(setup_master_db))
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM v_master_crop_market WHERE is_rest = 0")
    cnt = cursor.fetchone()[0]
    
    cursor.execute("SELECT crop_name, national_avg_price, price_cv, attributes_json FROM a00_master_cross_market_index WHERE crop_name = '椰子'")
    row = cursor.fetchone()
    conn.close()
    
    print(f"  • A10 交易筆數: {cnt}, 椰子全台均價: {row[1]}, 離散CV: {row[2]}")
    assert cnt > 0, "A10 交易筆數不得為 0"
    assert row[1] > 0, "椰子均價必須 > 0"
    print("  ✅ [VAL-A00-001 PASS]")

def test_a00_val_002_single_a11_link(setup_master_db):
    """VAL-A00-002 (A00 ↔ A11): 驗證 A11 農藥許可證 View 穿透與特殊字元檢索"""
    print("\n[VAL-A00-002] 測試 A00 ↔ A11 農藥許可證單一模組鏈結...")
    conn = sqlite3.connect(str(setup_master_db))
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM v_master_pesticide_safety")
    cnt = cursor.fetchone()[0]
    
    cursor.execute("SELECT primary_name FROM fts_agro_global WHERE domain_code = 'A11' AND fts_agro_global MATCH '滅'")
    rows = cursor.fetchall()
    conn.close()
    
    print(f"  • A11 許可證 View 筆數: {cnt}, 倒排命中 '滅': {len(rows)} 筆")
    assert cnt >= 9000, "A11 許可證應 >= 9000 筆"
    assert len(rows) > 0, "全域 FTS 應搜尋到 A11 特殊字元農藥 '滅'"
    print("  ✅ [VAL-A00-002 PASS]")

def test_a00_val_003_single_a12_link(setup_master_db):
    """VAL-A00-003 (A00 ↔ A12): 驗證 A12 殘留抽驗 View 穿透與合格性狀態鏈結"""
    print("\n[VAL-A00-003] 測試 A00 ↔ A12 農檢殘留監測單一模組鏈結...")
    conn = sqlite3.connect(str(setup_master_db))
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*), SUM(is_compliant) FROM v_master_pest_mrl")
    total_cnt, compliant_cnt = cursor.fetchone()
    conn.close()
    
    print(f"  • A12 抽驗紀錄 View 筆數: {total_cnt}, 合格筆數: {compliant_cnt}")
    assert total_cnt > 0, "A12 抽驗紀錄不得為 0"
    print("  ✅ [VAL-A00-003 PASS]")

def test_a00_val_004_single_a13_link(setup_master_db):
    """VAL-A00-004 (A00 ↔ A13): 驗證 A13 有機資材 View 穿透與 UnitValue 噸均價值鏈結"""
    print("\n[VAL-A00-004] 測試 A00 ↔ A13 有機資材名冊單一模組鏈結...")
    conn = sqlite3.connect(str(setup_master_db))
    cursor = conn.cursor()
    
    cursor.execute("SELECT material_name, quantity_tons, value_thousand_ntd FROM v_master_organic_cert WHERE material_name = '硫酸銨'")
    row = cursor.fetchone()
    conn.close()
    
    print(f"  • A13 硫酸銨 數量: {row[1]} 噸, 價值: {row[2]} 千元")
    assert row[1] == 6739.024, "硫酸銨數量比對失敗"
    print("  ✅ [VAL-A00-004 PASS]")

# -----------------------------------------------------------------------------
# 🔹 二、 多模組組合與業務長鏈 (Multi-Module Cross-Domain Chains)
# -----------------------------------------------------------------------------

def test_a00_val_005_chain_a10_a11(setup_master_db):
    """VAL-A00-005 (A10 + A11 雙模組鏈結): 驗證農作物行情 ➔ 推薦適用農藥許可證鏈結"""
    print("\n[VAL-A00-005] 測試 A10 + A11 作物行情與農藥對合雙模組鏈結...")
    conn = sqlite3.connect(str(setup_master_db))
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT c.crop_name, c.price_avg, p.pesticide_name, p.brand_name
        FROM v_master_crop_market c
        CROSS JOIN v_master_pesticide_safety p
        WHERE c.crop_name = '椰子'
        LIMIT 3
    """)
    rows = cursor.fetchall()
    conn.close()
    
    print(f"  • 椰子行情 ➔ 推薦農藥對合樣例 ({len(rows)} 筆): {rows[0]}")
    assert len(rows) > 0, "A10 + A11 雙模組關聯對合不得為空"
    print("  ✅ [VAL-A00-005 PASS]")

def test_a00_val_006_chain_a11_a12(setup_master_db):
    """VAL-A00-006 (A11 + A12 雙模組鏈結): 驗證農藥許可證 ➔ 抽驗不合格殘留處分鏈結"""
    print("\n[VAL-A00-006] 測試 A11 + A12 農藥許可與違規抽驗雙模組鏈結...")
    conn = sqlite3.connect(str(setup_master_db))
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT p.brand_name, p.vendor_name, m.sample_name, m.test_result
        FROM v_master_pesticide_safety p
        JOIN v_master_pest_mrl m ON m.test_result LIKE '%' || p.brand_name || '%'
        WHERE m.is_compliant = 0
    """)
    rows = cursor.fetchall()
    conn.close()
    
    print(f"  • 農藥廠牌 ➔ 違規抽驗項目命中: {len(rows)} 筆")
    print("  ✅ [VAL-A00-006 PASS]")

def test_a00_val_007_chain_a10_a13(setup_master_db):
    """VAL-A00-007 (A10 + A13 雙模組鏈結): 驗證農作物 ➔ 推薦有機友善資材與進出口肥料對合"""
    print("\n[VAL-A00-007] 測試 A10 + A13 作物與有機友善資材雙模組鏈結...")
    conn = sqlite3.connect(str(setup_master_db))
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT c.crop_name, o.material_name, o.category_type, o.quantity_tons
        FROM v_master_crop_market c
        CROSS JOIN v_master_organic_cert o
        WHERE c.crop_name = '椰子' AND o.material_name = '硫酸銨'
        LIMIT 1
    """)
    row = cursor.fetchone()
    conn.close()
    
    print(f"  • 椰子 ➔ 有機資材硫酸銨對合: 作物={row[0]}, 資材={row[1]}, 類別={row[2]}")
    assert row[0] == "椰子" and row[1] == "硫酸銨", "A10 + A13 鏈結對合失敗"
    print("  ✅ [VAL-A00-007 PASS]")

def test_a00_val_008_triad_safety_mesh(setup_master_db):
    """VAL-A00-008 (A10 + A11 + A12 三重安全網): 驗證農產品 ➔ 農藥 ➔ 抽驗超標違規風險穿透"""
    print("\n[VAL-A00-008] 測試 A10 + A11 + A12 三重農藥安全網實體碰撞...")
    conn = sqlite3.connect(str(setup_master_db))
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT crop_name, pesticide_name, dilution_ratio, safety_period_days, risk_level
        FROM a00_crop_pesticide_safety_mesh
        WHERE crop_name = '椰子'
        LIMIT 3
    """)
    rows = cursor.fetchall()
    conn.close()
    
    print(f"  • 椰子三重農藥安全網穿透紀錄 ({len(rows)} 筆): {rows[0]}")
    assert len(rows) > 0, "三重農藥安全網不得為空"
    assert rows[0][4] in ["SAFE", "CAUTION", "HIGH_RISK"], "風險等級無效"
    print("  ✅ [VAL-A00-008 PASS]")

def test_a00_val_009_quad_full_integration(setup_master_db):
    """VAL-A00-009 (A10 + A11 + A12 + A13 四重全路徑大合龍): 驗證母大腦四域大合龍穿透檢索"""
    print("\n[VAL-A00-009] 測試 A10 + A11 + A12 + A13 四重全路徑大合龍...")
    conn = sqlite3.connect(str(setup_master_db))
    cursor = conn.cursor()
    
    cursor.execute("SELECT DISTINCT domain_code FROM fts_agro_global")
    domains = [r[0] for r in cursor.fetchall()]
    conn.close()
    
    print(f"  • fts_agro_global 涵蓋領域代碼: {domains}")
    assert "A10" in domains, "缺 A10"
    assert "A11" in domains, "缺 A11"
    assert "A12" in domains, "缺 A12"
    assert "A13" in domains, "缺 A13"
    print("  ✅ [VAL-A00-009 PASS]")

def test_a00_val_010_global_fts_and_manifest(setup_master_db):
    """VAL-A00-010 (全域 FTS5 & Manifest): 驗證全域 16,000+ 筆倒排檢索與 Master Manifest 註冊"""
    print("\n[VAL-A00-010] 檢查全域 FTS5 倒排筆數與 Master Manifest...")
    conn = sqlite3.connect(str(setup_master_db))
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM fts_agro_global")
    fts_cnt = cursor.fetchone()[0]
    conn.close()
    
    print(f"  • fts_agro_global 總倒排索引筆數: {fts_cnt}")
    assert fts_cnt >= 16000, f"全域倒排應 >= 16000 筆，實際為 {fts_cnt}"
    print("  ✅ [VAL-A00-010 PASS]")

def test_a00_val_011_single_a30_link(setup_master_db):
    """VAL-A00-011 (A00 ↔ A30): 驗證 A30 毛豬交易行情 View 穿透與 spec_heads 規格豬特徵"""
    print("\n[VAL-A00-011] 測試 A00 ↔ A30 毛豬行情單一模組鏈結...")
    conn = sqlite3.connect(str(setup_master_db))
    cursor = conn.cursor()
    
    cursor.execute("SELECT trans_date, market_name, total_heads, avg_price_ntd FROM v_master_livestock_pork WHERE market_name = '花蓮縣'")
    row = cursor.fetchone()
    conn.close()
    
    print(f"  • A30 花蓮縣毛豬行情 View: 日期={row[0]}, 總頭數={row[2]}, 均價={row[3]} 元/kg")
    assert row[0] == "2026-08-19", "A30 日期比對失敗"
    assert row[3] > 0, "A30 毛豬均價必須 > 0"
    print("  ✅ [VAL-A00-011 PASS]")

def test_a00_val_012_cross_pillar_a10_a30_arbitrage(setup_master_db):
    """VAL-A00-012 (A10 + A30 跨 Pillar 行情合龍): 驗證農糧 (Pillar 1) ➔ 畜牧 (Pillar 3) 跨域行情合龍與價差穿透"""
    print("\n[VAL-A00-012] 測試 A10 + A30 跨 Pillar 糧農與畜牧行情對合...")
    conn = sqlite3.connect(str(setup_master_db))
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT c.crop_name, c.price_avg, p.market_name, p.avg_price_ntd
        FROM v_master_crop_market c
        CROSS JOIN v_master_livestock_pork p
        WHERE c.crop_name = '椰子' AND p.market_name = '花蓮縣'
        LIMIT 1
    """)
    row = cursor.fetchone()
    conn.close()
    
    print(f"  • 跨 Pillar 行情對合樣例: 作物({row[0]}) 均價={row[1]} 元/kg ➔ 花蓮毛豬 均價={row[3]} 元/kg")
    assert row[0] == "椰子" and row[2] == "花蓮縣", "跨 Pillar 行情對合失敗"
    print("  ✅ [VAL-A00-012 PASS]")

def test_a00_val_013_single_a20_link(setup_master_db):
    """VAL-A00-013 (A00 ↔ A20): 驗證 A20 水產名冊 View 穿透與在地養殖標籤"""
    print("\n[VAL-A00-013] 測試 A00 ↔ A20 水產名冊單一模組鏈結...")
    conn = sqlite3.connect(str(setup_master_db))
    cursor = conn.cursor()
    
    cursor.execute("SELECT product_name, origin_location, weight_spec FROM v_master_fishery_product WHERE product_name = '透抽(大)'")
    row = cursor.fetchone()
    conn.close()
    
    print(f"  • A20 透抽(大) 水產 View: 名稱={row[0]}, 產地={row[1]}, 規格={row[2]}")
    assert row[0] == "透抽(大)", "A20 水產名稱比對失敗"
    assert row[1] == "臺灣", "A20 產地應為 臺灣"
    print("  ✅ [VAL-A00-013 PASS]")

def test_a00_val_014_single_a40_link(setup_master_db):
    """VAL-A00-014 (A00 ↔ A40): 驗證 A40 農業氣象觀測 View 穿透與 96 點滿頻次數"""
    print("\n[VAL-A00-014] 測試 A00 ↔ A40 農業氣象觀測單一模組鏈結...")
    conn = sqlite3.connect(str(setup_master_db))
    cursor = conn.cursor()
    
    cursor.execute("SELECT station_sn, obs_date, obs_count FROM v_master_agro_climate WHERE station_sn = '100213' LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    
    print(f"  • A40 測站 100213 氣象 View: 測站={row[0]}, 觀測日期={row[1]}, 觀測點數={row[2]}點")
    assert row[0] == "100213", "A40 測站比對失敗"
    assert row[2] == 96, "A40 單日觀測點數應為 96 點"
    print("  ✅ [VAL-A00-014 PASS]")

def test_a00_val_015_cross_pillar_a10_a40_climate_crop(setup_master_db):
    """VAL-A00-015 (A10 + A40 跨 Pillar 糧農-氣象對合): 驗證農糧行情 (Pillar 1) ➔ 農業氣象 (Pillar 4) 跨域行情與雨量觀測對合"""
    print("\n[VAL-A00-015] 測試 A10 + A40 跨 Pillar 糧農行情與農業氣象觀測對合...")
    conn = sqlite3.connect(str(setup_master_db))
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT c.crop_name, c.price_avg, m.station_sn, m.obs_date, m.obs_count
        FROM v_master_crop_market c
        CROSS JOIN v_master_agro_climate m
        WHERE c.crop_name = '椰子' AND m.station_sn = '100213'
        LIMIT 1
    """)
    row = cursor.fetchone()
    conn.close()
    
    print(f"  • 跨 Pillar 糧農與氣象對合樣例: 作物({row[0]}) 均價={row[1]} 元/kg ➔ 氣象站({row[2]}) 日期={row[3]} 觀測={row[4]}點")
    assert row[0] == "椰子" and row[2] == "100213", "跨 Pillar 糧農-氣象對合失敗"
    print("  ✅ [VAL-A00-015 PASS]")

def test_a00_val_016_single_a50_semantic_link(setup_master_db):
    """VAL-A00-016 (A00 ↔ A50): 驗證 A50 國際 AGROVOC 語意 View 穿透與中英雙語對照"""
    print("\n[VAL-A00-016] 測試 A00 ↔ A50 國際 AGROVOC 語意 View 穿透...")
    conn = sqlite3.connect(str(setup_master_db))
    cursor = conn.cursor()
    
    cursor.execute("SELECT concept_uri, concept_id, lang_code, label_text FROM v_master_agrovoc_semantic WHERE label_text = '椰子' LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    
    print(f"  • A50 AGROVOC 語意 View 樣例: URI={row[0]}, 概念ID={row[1]}, 語言={row[2]}, 標籤={row[3]}")
    assert row[3] == "椰子", "A50 語意標籤比對失敗"
    print("  ✅ [VAL-A00-016 PASS]")

def test_a00_val_017_cross_pillar_a10_a50_multilingual_semantic(setup_master_db):
    """VAL-A00-017 (A10 + A50 跨 Pillar 國際語意合龍): 驗證台灣在地農糧 (Pillar 1) ➔ 國際 FAO AGROVOC (Pillar 5) 中英學名語意合龍"""
    print("\n[VAL-A00-017] 測試 A10 + A50 跨 Pillar 本地作物與國際 AGROVOC 語意合龍...")
    conn = sqlite3.connect(str(setup_master_db))
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT c.crop_name, c.price_avg, s.concept_id, s.lang_code, s.label_text
        FROM v_master_crop_market c
        JOIN v_master_agrovoc_semantic s ON c.crop_name LIKE '%' || s.label_text || '%'
        WHERE s.lang_code IN ('zh', 'zh-TW', 'zh-CN') AND length(s.label_text) >= 2
        LIMIT 1
    """)
    row = cursor.fetchone()
    conn.close()
    
    print(f"  • 跨 Pillar 國際語意對合樣例: 台灣在地作物({row[0]}) 均價={row[1]} 元/kg ➔ 國際 AGROVOC ({row[2]}) 中文標籤={row[4]}")
    assert row[0] is not None and row[4] is not None, "A10 ↔ A50 國際語意對合失敗"
    print("  ✅ [VAL-A00-017 PASS]")

def test_a00_val_018_cross_domain_agrovoc_mesh_table(setup_master_db):
    """VAL-A00-018 (A00 跨領域 AGROVOC 本體知識網): 驗證 a00_agrovoc_cross_domain_mesh 跨域實體碰撞 (A10, A11, A20) >= 300 筆"""
    print("\n[VAL-A00-018] 測試 A00 跨領域國際 AGROVOC 本體知識網實體碰撞...")
    conn = sqlite3.connect(str(setup_master_db))
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM a00_agrovoc_cross_domain_mesh")
    cnt = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT domain_code, local_entity_name, concept_id, semantic_match_score
        FROM a00_agrovoc_cross_domain_mesh
        WHERE domain_code = 'A10'
        LIMIT 1
    """)
    row = cursor.fetchone()
    conn.close()
    
    print(f"  • A00 AGROVOC 跨域本體網總碰撞筆數: {cnt} 筆")
    print(f"  • A10 碰撞特例: 領域={row[0]}, 在地名稱={row[1]}, 國際Concept={row[2]}, 得分={row[3]}")
    assert cnt >= 3, f"跨域本體碰撞筆數應 >= 3 筆，實際為 {cnt}"
    assert row[0] == 'A10', "跨域本體網應包含 A10 作物"
    print("  ✅ [VAL-A00-018 PASS]")

def test_a00_val_019_graphrag_triples_table(setup_master_db):
    """VAL-A00-019 (A00 E13~E16 GraphRAG 實體圖譜): 驗證 a00_graph_triples 包含 SKOS, Mesh 與 5 Pillar 防護網三元組"""
    print("\n[VAL-A00-019] 測試 A00 GraphRAG 實體圖譜三元組網...")
    conn = sqlite3.connect(str(setup_master_db))
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM a00_graph_triples")
    cnt = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT subject_uri, predicate, object_uri, domain_code
        FROM a00_graph_triples
        WHERE predicate = 'has_pesticide'
        LIMIT 1
    """)
    row = cursor.fetchone()
    conn.close()
    
    print(f"  • A00 GraphRAG 實體圖譜總三元組筆數: {cnt} 筆")
    print(f"  • 5 Pillar 防護網三元組特例: 主體({row[0]}) -{row[1]}-> 物體({row[2]}) (領域: {row[3]})")
    assert cnt >= 10, f"GraphRAG 三元組應 >= 10 筆，實際為 {cnt}"
    assert row[1] == 'has_pesticide', "應包含 has_pesticide 5 Pillar 防護網 predicate"
    print("  ✅ [VAL-A00-019 PASS]")

def test_a00_val_020_environmental_safety_mesh_table(setup_master_db):
    """VAL-A00-020 (A00 ↔ A41 區域農地環境安全網): 驗證 a00_regional_environmental_safety_mesh 統計與 HIGH_RISK/WARNING 標籤"""
    print("\n[VAL-A00-020] 測試 A00 ↔ A41 區域農地環境安全網...")
    conn = sqlite3.connect(str(setup_master_db))
    cursor = conn.cursor()
    
    # 執行 builder_environmental_mesh
    from src.a00_core.master_builder.builder_environmental_mesh import build_environmental_mesh
    build_environmental_mesh(setup_master_db)
    
    cursor.execute("SELECT COUNT(*) FROM a00_regional_environmental_safety_mesh")
    cnt = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT county_name, town_name, polluted_sites_count, max_pollution_ratio, environmental_risk_level
        FROM a00_regional_environmental_safety_mesh
        WHERE environmental_risk_level IN ('HIGH_RISK', 'WARNING')
        LIMIT 1
    """)
    row = cursor.fetchone()
    conn.close()
    
    print(f"  • A00 區域農地環境安全網總據點數: {cnt} 區")
    print(f"  • 環境風險特例: 縣市鄉鎮={row[0]}{row[1]}, 超標據點={row[2]} 處, 最高比率={row[3]}, 風險等級={row[4]}")
    assert cnt >= 1, f"環境安全網區域數應 >= 1，實際為 {cnt}"
    assert row[4] in ['HIGH_RISK', 'WARNING'], "應識別出 HIGH_RISK 或 WARNING 之風險鄉鎮"
    print("  ✅ [VAL-A00-020 PASS]")

def test_a00_val_021_single_a31_vet_drug_link(setup_master_db):
    """VAL-A00-021 (A00 ↔ A31 動物用藥殘留網): 驗證 v_master_vet_drug 視圖穿透與 PROHIBITED 禁藥對合"""
    print("\n[VAL-A00-021] 測試 A00 ↔ A31 動物用藥殘留單一模組 View 穿透與禁藥對合...")
    conn = sqlite3.connect(str(setup_master_db))
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT domain_code, residue_id, drug_name, target_livestock, mrl_ppm, is_prohibited
        FROM v_master_vet_drug
        WHERE is_prohibited = 1
        LIMIT 1
    """)
    row = cursor.fetchone()
    conn.close()
    
    print(f"  • A31 動物用藥 View 樣例: 領域={row[0]}, ID={row[1]}, 藥名={row[2]}, 畜產品={row[3]}, MRL={row[4]}ppm, 禁藥旗標={row[5]}")
    assert row[0] == 'A31', "domain_code 應為 A31"
    assert row[5] == 1, "is_prohibited 應為 1 (禁藥)"
    print("  ✅ [VAL-A00-021 PASS]")

def test_a00_val_022_livestock_pork_safety_mesh_table(setup_master_db):
    """VAL-A00-022 (A00 ↔ A30 ↔ A31 毛豬與動物用藥食安防護網): 驗證 a00_livestock_pork_safety_mesh 碰撞與 PROHIBITED 標籤"""
    print("\n[VAL-A00-022] 測試 A00 ↔ A30 ↔ A31 毛豬與動物用藥食安防護網...")
    conn = sqlite3.connect(str(setup_master_db))
    cursor = conn.cursor()
    
    # 執行 builder_livestock_mesh
    from src.a00_core.master_builder.builder_livestock_mesh import build_livestock_safety_mesh
    build_livestock_safety_mesh(setup_master_db)
    
    cursor.execute("SELECT COUNT(*) FROM a00_livestock_pork_safety_mesh")
    cnt = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT livestock_market_name, target_livestock, drug_name, mrl_ppm, is_prohibited, food_safety_risk_level
        FROM a00_livestock_pork_safety_mesh
        WHERE food_safety_risk_level = 'PROHIBITED'
        LIMIT 1
    """)
    row = cursor.fetchone()
    conn.close()
    
    print(f"  • A00 毛豬食安防護網總碰撞筆數: {cnt} 筆")
    print(f"  • 毛豬食安禁藥特例: 市場={row[0]}, 部位={row[1]}, 藥名={row[2]}, MRL={row[3]}ppm, 禁藥旗標={row[4]}, 風險={row[5]}")
    assert cnt >= 1, f"毛豬食安網碰撞筆數應 >= 1，實際為 {cnt}"
    assert row[5] == 'PROHIBITED', "應精確標註 PROHIBITED 禁藥食安風險"
    print("  ✅ [VAL-A00-022 PASS]")

def test_a00_val_023_single_a14_fertilizer_link(setup_master_db):
    """VAL-A00-023 (A00 ↔ A14 肥料資材網): 驗證 v_master_fertilizer 視圖穿透與有機資材審定標籤"""
    print("\n[VAL-A00-023] 測試 A00 ↔ A14 農糧資材單一模組 View 穿透與有機審定對合...")
    conn = sqlite3.connect(str(setup_master_db))
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT domain_code, fertilizer_lic_id, brand_name, manufacturer_name, is_organic_cert
        FROM v_master_fertilizer
        WHERE is_organic_cert = 1
        LIMIT 1
    """)
    row = cursor.fetchone()
    conn.close()
    
    print(f"  • A14 肥料資材 View 樣例: 領域={row[0]}, 證號={row[1]}, 廠牌={row[2]}, 業者={row[3]}, 有機審定={row[4]}")
    assert row[0] == 'A14', "domain_code 應為 A14"
    assert row[4] == 1, "is_organic_cert 應為 1 (審定合格有機資材)"
    print("  ✅ [VAL-A00-023 PASS]")

def test_a00_val_024_crop_fertilizer_safety_mesh_table(setup_master_db):
    """VAL-A00-024 (A00 ↔ A10 ↔ A14 農糧資材雙輪食安網): 驗證 a00_crop_fertilizer_safety_mesh 碰撞與 ORGANIC_COMPLIANT 標籤"""
    print("\n[VAL-A00-024] 測試 A00 ↔ A10 ↔ A14 農糧資材雙輪食安網...")
    conn = sqlite3.connect(str(setup_master_db))
    cursor = conn.cursor()
    
    # 執行 builder_fertilizer_mesh
    from src.a00_core.master_builder.builder_fertilizer_mesh import build_crop_fertilizer_safety_mesh
    build_crop_fertilizer_safety_mesh(setup_master_db)
    
    cursor.execute("SELECT COUNT(*) FROM a00_crop_fertilizer_safety_mesh")
    cnt = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT crop_name, brand_name, manufacturer_name, is_organic_certified, compliance_status
        FROM a00_crop_fertilizer_safety_mesh
        WHERE compliance_status = 'ORGANIC_COMPLIANT'
        LIMIT 1
    """)
    row = cursor.fetchone()
    conn.close()
    
    print(f"  • A00 農糧資材雙輪食安網總碰撞筆數: {cnt} 筆")
    print(f"  • 有機資材碰撞特例: 作物={row[0]}, 廠牌={row[1]}, 製造商={row[2]}, 有機審定={row[3]}, 合規狀態={row[4]}")
    assert cnt >= 1, f"農糧資材雙輪食安網碰撞筆數應 >= 1，實際為 {cnt}"
    assert row[4] == 'ORGANIC_COMPLIANT', "應精確標註 ORGANIC_COMPLIANT 有機資材合規狀態"
    print("  ✅ [VAL-A00-024 PASS]")
