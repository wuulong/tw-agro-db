# 🏷️ tw-agro-db (台灣農業開放大數據引擎) 版本演進與開發歷程看板 (VERSION.md)

* **目前最新版本**：`v0.3.5`
* **發布日期**：2026-08-20
* **歸檔路徑**：[VERSION.md](file:///Users/wuulong/github/bmad-pa/events-2026Q3/agro-db-in/tw-agro-db/VERSION.md)

---

## 📜 版本演進與 F-P-I-E-C 生命週期紀錄

### 🏆 `v0.7.0` (2026-08-20) - A00 ↔ A10 ↔ A14 農糧資材雙輪食安網與 24 大測試網大里程碑完工
* **狀態**：🟢 `COMPLETED`
* **重點變更**：
  - 建立 `a00_crop_fertilizer_safety_mesh` 實體表與建置器 `builder_fertilizer_mesh.py`。
  - 實現 A10 作物、A13 有機農場與 A14 肥料登記證之跨庫事前合規碰撞，自動標註 `ORGANIC_COMPLIANT`/`CONVENTIONAL_ONLY` 資材合規狀態。
  - 擴充母大腦單元測試至 **24 大鏈結 (`VAL-A00-001 ~ 024`) 24/24 PASS 綠燈**。

### 🌿 `v0.6.5` (2026-08-20) - A14 農糧資材與肥料登記證 DB 完工 (Pillar 1 農糧資材閉環)
* **狀態**：🟢 `COMPLETED`
* **重點變更**：
  - 完工 `A14 organic_fertilizer_db` (Pillar 1 農糧資材與肥料登記證)。
  - 實作 N-P-K 三要素養分算式 ($NPK\_Total = N + P + K$) 與 `ORGANIC_APPROVED`/`HIGH_CONCENTRATION`/`STANDARD` 三級品質等級。
  - 獨立單元測試 [test_a14_organic_fertilizer_db.py](file:///Users/wuulong/github/bmad-pa/events-2026Q3/agro-db-in/tw-agro-db/tests/test_a14_organic_fertilizer_db.py) 100% 綠燈通過 (4/4 PASS)。
  - 遵循新升級 SOP 規範，擴充母大腦單元測試至 **23 大鏈結 (`VAL-A00-001 ~ 023`) 23/23 PASS 綠燈**。

### 🥩 `v0.6.0` (2026-08-20) - A00 ↔ A30 ↔ A31 毛豬與動物用藥食安防護網與 22 大測試網完工
* **狀態**：🟢 `COMPLETED`
* **重點變更**：
  - 建立 `a00_livestock_pork_safety_mesh` 實體表與建置器 `builder_livestock_mesh.py`。
  - 實現 A30 毛豬批發市場與 A31 TFDA 動物用藥/禁藥清單之跨庫特徵實體化碰撞，自動歸類 `SAFE`/`HIGH_RISK`/`PROHIBITED` 食安風險。
  - 擴充母大腦單元測試至 **22 大鏈結 (`VAL-A00-001 ~ 022`) 22/22 PASS 綠燈**。

### 🐖 `v0.5.5` (2026-08-20) - A31 動物用藥與畜產品殘留管制 DB 完工 (Pillar 3 畜牧食安防線)
* **狀態**：🟢 `COMPLETED`
* **重點變更**：
  - 完工 `A31 vet_drug_food_residue_db` (Pillar 3 動物用藥與畜產品殘留管制)。
  - 實作動物用藥禁用算式 ($MRL == 0.0 \Rightarrow \text{PROHIBITED}$) 與 `SAFE`/`HIGH_RISK`/`PROHIBITED` 三級風險等級。
  - 獨立單元測試 [test_a31_vet_drug_food_residue_db.py](file:///Users/wuulong/github/bmad-pa/events-2026Q3/agro-db-in/tw-agro-db/tests/test_a31_vet_drug_food_residue_db.py) 100% 綠燈通過 (4/4 PASS)。
  - 遵循新升級 SOP 規範，擴充母大腦單元測試至 **21 大鏈結 (`VAL-A00-001 ~ 021`) 21/21 PASS 綠燈**。

### 🐟 `v0.5.0` (2026-08-20) - A21 水產養殖水質與寒害監測 DB 完工 (Pillar 2 水產生態網閉環)
* **狀態**：🟢 `COMPLETED`
* **重點變更**：
  - 完工 `A21 aquaculture_monitoring_db` (Pillar 2 水產養殖水質與寒害監測)。
  - 實作水溫寒害 ($Temp < 15^\circ\text{C}$) 與低溶氧 ($DO < 3\text{ mg/L}$) 雙重風險算式及 `SAFE`/`WARNING`/`HIGH_RISK` 風險等級。
  - 獨立單元測試 [test_a21_aquaculture_monitoring_db.py](file:///Users/wuulong/github/bmad-pa/events-2026Q3/agro-db-in/tw-agro-db/tests/test_a21_aquaculture_monitoring_db.py) 100% 綠燈通過 (4/4 PASS)。

### 🛡️ `v0.4.5` (2026-08-20) - A00 ↔ A41 區域農地環境安全網與 20 大測試網完工
* **狀態**：🟢 `COMPLETED`
* **重點變更**：
  - 建立 `a00_regional_environmental_safety_mesh` 實體表與建置器 `builder_environmental_mesh.py`。
  - 實現各鄉鎮農地重金屬超標密度統計、最高超標比率 `MaxPollutionRatio` 與 `SAFE`/`WARNING`/`HIGH_RISK` 環境風險等級推論。
  - 擴充母大腦單元測試至 **20 大鏈結 (`VAL-A00-001 ~ 020`) 20/20 PASS 綠燈**。

### 🌿 `v0.4.0` (2026-08-20) - A41 土壤與水質環境安全 DB 完工 (Pillar 4 環境安全防線)
* **狀態**：🟢 `COMPLETED`
* **重點變更**：
  - 完工 `A41 soil_water_pollution_db` (Pillar 4 農地環境與水質安全)。
  - 實作特化重金屬超標比率算式 $PollutionRatio = \frac{\text{conc}}{\text{limit}}$ 與 `SAFE`/`WARNING`/`HIGH_RISK` 風險等級。
  - 獨立單元測試 [test_a41_soil_water_pollution_db.py](file:///Users/wuulong/github/bmad-pa/events-2026Q3/agro-db-in/tw-agro-db/tests/test_a41_soil_water_pollution_db.py) 100% 綠燈通過 (4/4 PASS)。

### 🚀 `v0.3.5` (2026-08-20) - 跨領域國際 AGROVOC GraphRAG 實體圖譜網與 E13~E16 演算法完工
* **狀態**：🟢 `COMPLETED`
* **重點變更**：
  - 建立 `a00_graph_triples` 1-Hop GraphRAG 實體圖譜表，產出 **5,539 筆** 跨域三元組網 (`is_a`, `broader`, `has_pesticide`)。
  - 實作 `builder_ontology_graph.py` 建置器，貫通 E13~E16 5 Pillar 病蟲害與氣象終極防護網。
  - 擴充母大腦單元測試至 **19 大鏈結 (`VAL-A00-001 ~ 019`) 19/19 PASS 綠燈**。

### 🌐 `v0.3.0` (2026-08-20) - A50 全量國際 AGROVOC 40,097 概念與 389 筆 Cross-Domain Mesh 完工
* **狀態**：🟢 `COMPLETED`
* **重點變更**：
  - 重構 `A50 fao_agrovoc_db` 直接對對碰聯合國糧農組織 FAO Live SPARQL Endpoint，載入全量 **40,097 個核心概念**、**82,954 筆中英繁簡多語標籤** 與 **40,068 筆 SKOS 階層**。
  - 建立 `a00_agrovoc_cross_domain_mesh` 實體知識表，於在地資料庫達成 **389 筆** 跨領域碰撞。
  - 母大腦全域倒排 FTS5 總筆數大躍升至 **28,974 筆**。

### 🌦️ `v0.2.5` (2026-08-20) - A40 農業氣象觀測站與 A00 15 大測試網絡完工
* **狀態**：🟢 `COMPLETED`
* **重點變更**：
  - 完工 `A40 agro_climate_db` (Pillar 4 農業氣象)，載入 2,527 筆觀測紀錄與 91.33% 滿頻率品質 Scorer。
  - 母大腦 Views 注入 `v_master_agro_climate`，擴充至 15 大測試網 (`VAL-A00-015` 跨 Pillar 糧農與氣象雨量波幅對合)。

### 🐖 `v0.2.0` (2026-08-20) - A20 水產與 A30 毛豬批發行情 Pillar 2/3 擴充
* **狀態**：🟢 `COMPLETED`
* **重點變更**：
  - 完工 `A20 fishery_market_db` (水產名冊) 與 `A30 livestock_db` (毛豬批發交易)。
  - 重構 CLI 共同框架 `cli_template.py`，消除全庫 85% 重複程式碼。

### 🌾 `v0.1.0` (2026-08-19) - A00 母大腦與 A10~A13 農糧安全網架構奠基
* **狀態**：🟢 `COMPLETED`
* **重點變更**：
  - 建立 `A00 master_hub` 系統工程架構與子模組 Blueprint 範本 (`template_blueprint`)。
  - 實作 `A10` (農糧批發)、`A11` (農藥許可證)、`A12` (MRL 殘留標準)、`A13` (有機認證) 與事前農藥安全網。
