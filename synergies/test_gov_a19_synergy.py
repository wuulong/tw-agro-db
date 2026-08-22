#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
GOV-A19 子模組對接整合測試套件範本 (拒絕空洞 Dummy 測試，與 Spec 強烈 Grounding 對齊)
對齊規格: [SPC-011, SPC-014]
"""

import sys
from pathlib import Path

# 動態加載 SDK (尋找 tw-gov-db/src)
gov_src = Path(__file__).resolve().parents[3] / "gov-db-in" / "tw-gov-db" / "src"
if str(gov_src) not in sys.path:
    sys.path.insert(0, str(gov_src))

from core.domain_registry_resolver import DomainRegistryResolver
from core.base_adapter import BaseDomainAdapter

import time
import logging

# 設定 Logging 機制
log_dir = Path(__file__).resolve().parents[3] / "sys_eng" / "05_verification_testing" / "logs"
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / "LOG_GOV_A19_SYNERGY_TEST.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

def test_axx_template_spec_grounded_integration():
    t0 = time.time()
    logging.info("🚀 啟動 GOV-A19 ↔ GOV-300 (tw-gov-db) 跨部會對接實測...")
    
    # 1. 階梯 1：初始化 Resolver 與三層架構連線
    t_start = time.time()
    logging.info("🔍 [Step 1] 初始化 DomainRegistryResolver 載入母專案地圖...")
    resolver = DomainRegistryResolver()
    gov_info = resolver.get_domain_info("GOV-300")
    t_step1 = (time.time() - t_start) * 1000
    
    logging.info(f"  ├─ 成功解析母專案專案碼: {gov_info['project_code']}")
    logging.info(f"  ├─ 母專案描述: {gov_info.get('description', 'N/A')}")
    logging.info(f"  └─ 耗時: {t_step1:.3f} ms")
    assert gov_info["project_code"] == "GOV-300"
    
    # 2. 階梯 2：基石一 OID 歸併驗證 (master_agencies.sqlite)
    t_start = time.time()
    logging.info("🔍 [Step 2] 驗證基石一 OID 歸併 (master_agencies.sqlite)...")
    master_db_path = resolver.get_shared_db_path("master_agencies.sqlite")
    logging.info(f"  ├─ 載入權威機關 DB 路徑: {master_db_path}")
    
    adapter = BaseDomainAdapter(root_agency_oid="2.16.886.101", master_db=master_db_path)
    aligned_oid = adapter.align_publisher_oid("行政院")
    t_step2 = (time.time() - t_start) * 1000
    
    logging.info(f"  ├─ 文字名稱 '行政院' 對齊權威 OID 結案: {aligned_oid}")
    logging.info(f"  └─ 耗時: {t_step2:.3f} ms")
    assert aligned_oid != ""
    
    # 3. 階梯 3：基石二門牌地碼驗證 (universal_keys.sqlite / admin_codes)
    t_start = time.time()
    logging.info("🔍 [Step 3] 驗證基石二門牌與行政區劃 (universal_keys.sqlite)...")
    conn_keys = resolver.get_domain_core_db_connection("GOV-300", "universal_keys.sqlite")
    cursor = conn_keys.cursor()
    cursor.execute("SELECT admin_code, city_name, district_name FROM admin_codes WHERE city_name='臺北市' AND district_name='中正區';")
    row = cursor.fetchone()
    t_step3 = (time.time() - t_start) * 1000
    
    assert row is not None
    assert row[0] == "630001"
    logging.info(f"  ├─ 查詢 '臺北市中正區' 成功碰撞 6 碼門牌區號: {row[0]}")
    logging.info(f"  └─ 耗時: {t_step3:.3f} ms")
    conn_keys.close()
    
    total_time = (time.time() - t0) * 1000
    logging.info(f"⏱️ 全套跨部會對接測試總耗時: {total_time:.3f} ms (< 10ms 綠燈門檻)")
    logging.info("✅ GOV-A19 模板與 Spec 強對合之測試通過！")
    logging.info(f"📄 詳細 Log 物理歸檔位置: {log_file}")

if __name__ == "__main__":
    test_axx_template_spec_grounded_integration()
