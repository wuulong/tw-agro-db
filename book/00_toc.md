# 📘 《台灣農漁畜開放數據全景圖鑑：從產地行情到食安防禦的資料體系》全書目錄 (00_toc.md)

* **專案名稱**：`tw-agro-db` (台灣農業開放大數據引擎)
* **當前版本**：`v0.7.0`
* **歸檔目錄**：[events-2026Q3/agro-db-in/tw-agro-db/book/00_toc.md](file:///Users/wuulong/github/bmad-pa/events-2026Q3/agro-db-in/tw-agro-db/book/00_toc.md)

---

## 📚 專書完整目錄地圖

* **[第 0 章：全書目錄與導覽](00_toc.md)** (本檔)
* **[第 1 章：專案願景與農業數位轉型使命](01_vision_and_mission.md)**
  - 1.1 台灣農漁畜產銷與食安防禦的 5 大現實困境
  - 1.2 建立大一統農業開放知識體系的開源價值 (`Fig 1.1`)
* **第 2 章：A00 母大腦全景架構與農業知識體系解構 (1-to-1 獨立檔案)**
  - [2.0 第 2 章總覽與 4 層技術堆疊](02_00_architecture_overview.md) (`Fig 2.0`, `Fig 2.0.1`)
  - [2.1 農糧作物市場產銷與價格離散知識體系](02_01_crop_market_system.md)
  - [2.2 病蟲害防治與農藥安全採收期知識體系](02_02_pesticide_safety_system.md)
  - [2.3 有機友善栽培與肥料資材合規知識體系](02_03_organic_fertilizer_system.md)
  - [2.4 養殖漁業環境與微氣候寒害監測知識體系](02_04_aquaculture_monitoring_system.md)
  - [2.5 畜牧毛豬交易與獸藥殘留食安防衛體系](02_05_livestock_drug_safety_system.md)
  - [2.6 農業氣象觀測與農地重金屬環境安全體系](02_06_agro_climate_environment_system.md)
  - [2.7 聯合國 FAO AGROVOC 國際農學多語體系](02_07_fao_agrovoc_lod_system.md)
  - [2.8 A00 母大腦：將農業知識凝練為 5 大事前融合防護網 (2.8.1 ~ 2.8.6)](02_08_a00_safety_meshes_and_graphrag.md) (`Fig 2.8`, `Fig 2.8.1`)
  - [2.9 4 大真實農業情境之知識流轉與 DB 串接接力](02_09_scenarios_knowledge_navigation.md) (`Fig 2.9`)
  - [2.10 摘要：如何透過 A00 完全掌握台灣農漁畜資料體系](02_10_summary_master_control.md)
* **第 3 章：12 大農業知識資產與 DB 百科圖鑑 (通用 7 大維度獨立檔案)**
  - [3.0 全章子模組撰寫規範與通用 7 大維度架構說明](03_00_structure_guide.md) (`Fig 3.0`)
  - [3.1 A10 台灣農糧批發交易行情知識庫](03_01_a10_tw_crop_db.md) (`Fig 3.1`)
  - [3.2 A11 農藥許可證與安全採收期知識庫](03_02_a11_pesticide_db.md) (`Fig 3.2`)
  - [3.3 A12 農檢 MRL 殘留抽驗預警知識庫](03_03_a12_pest_mrl_alert_db.md) (`Fig 3.3`)
  - [3.4 A13 有機友善農場認證名冊知識庫](03_04_a13_organic_cert_db.md) (`Fig 3.4`)
  - [3.5 A14 農糧資材與肥料登記證知識庫](03_05_a14_organic_fertilizer_db.md) (`Fig 3.5`)
  - [3.6 A20 水產產品與市場行情知識庫](03_06_a20_fishery_market_db.md) (`Fig 3.6`)
  - [3.7 A21 水產養殖水質與寒害監測知識庫](03_07_a21_aquaculture_monitoring_db.md) (`Fig 3.7`)
  - [3.8 A30 毛豬批發交易行情知識庫](03_08_a30_livestock_db.md) (`Fig 3.8`)
  - [3.9 A31 動物用藥與畜產品殘留管制知識庫](03_09_a31_vet_drug_food_residue_db.md) (`Fig 3.9`)
  - [3.10 A40 農業氣象站歷史觀測知識庫](03_10_a40_agro_climate_db.md) (`Fig 3.10`)
  - [3.11 A41 土壤與水質環境安全知識庫](03_11_a41_soil_water_pollution_db.md) (`Fig 3.11`)
  - [3.50 A50 FAO AGROVOC 國際農學詞庫知識庫](03_50_a50_fao_agrovoc_db.md) (`Fig 3.50`)
* **[第 4 章：4 大領域利害關係人實戰劇本 Playbook](04_stakeholder_playbooks.md)**
  - 4.1 農民與農會推廣人員：有機友善栽培與價格避險 Playbook
  - 4.2 食安稽查與團膳採購團隊：肉品農藥與禁藥即時攔截 Playbook
  - 4.3 AI 系統架構師與 Agent 開發者：GraphRAG 零幻覺 Grounding Playbook
  - 4.4 農業經濟與環境研究員：跨域 LOD 與重金屬生態 Playbook
  - 4.5 Python API 程式開發與架構設計指南 (API Development Guide)
* **[第 5 章：系統工程驗證、單元測試網與 QGIS 軟體定義地圖](05_system_engineering_and_sdm.md)**
  - 5.1 系統工程 100% 對合度與 Buildlogs 審計機制 (`Fig 5.1`)
  - 5.2 63/63 PASS 全網綠燈驗證矩陣
  - 5.3 軟體定義地圖 (SDM) 與 QGIS 空間可視化整合 (`Fig 5.2`)
  - 5.4 專案自動化維運、Just Command 與全庫重構管線
* **[第 6 章：結語與專案總結](06_conclusion.md)**
  - 6.1 結語：打破部門資料孤島的大一統里程碑
  - 6.2 賦能智慧農業與食安防護的長遠價值
* **附錄 (Appendix)**
  - [附錄 A：agro.db 大一統全庫 Schema 與 DDL 地圖](07_01_appendix_sqlite_schema_glossary.md)
  - [附錄 B：台灣在地實體與聯合國 FAO AGROVOC 對合總表](07_02_appendix_fao_agrovoc_mapping.md)
  - [附錄 C：tw-agro-cli 與各模組 CLI 參數指令速查手冊](07_03_appendix_cli_reference.md)
