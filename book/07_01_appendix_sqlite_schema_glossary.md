# 📘 附錄 A：`schema.sql` 全庫資料表索引與導覽 (07_01_appendix_sqlite_schema_glossary.md)

* **歸檔位置**：[events-2026Q3/agro-db-in/tw-agro-db/book/07_01_appendix_sqlite_schema_glossary.md](file:///Users/wuulong/github/bmad-pa/events-2026Q3/agro-db-in/tw-agro-db/book/07_01_appendix_sqlite_schema_glossary.md)
* **物理 DDL 權威檔案**：[schema.sql](file:///Users/wuulong/github/bmad-pa/events-2026Q3/agro-db-in/tw-agro-db/schema.sql)

---

## 🏛️ A.1 全庫 12 大垂直 DB 與 A00 核心資料表索引速查

`tw-agro-db` 的物理資料庫 `agro.db` 包含 12 個垂直子模組主表、FTS5 全文倒排表與 A00 Master Hub 圖譜表。完整的 SQL `CREATE TABLE` 與備註說明已封裝於權威檔案 [`schema.sql`](file:///Users/wuulong/github/bmad-pa/events-2026Q3/agro-db-in/tw-agro-db/schema.sql) 中。

下表提供全庫資料表與 Views 之極簡速查索引：

| 垂直 DB 代號 | 主資料表名稱 (Main Table) | 全文倒排表 / View 名稱 | 核心主鍵 (Primary Key) | 關鍵領域欄位與說明 |
| :--- | :--- | :--- | :--- | :--- |
| **`A10`** | `a10_crop_farm_trans` | `v_master_crop_market` | `trans_id` | `crop_name`, `avg_price_ntd`, `attributes_json` (CV 離散) |
| **`A11`** | `a11_pesticide_licenses` | `a11_pesticide_fts` | `pesticide_lic_id` | `pesticide_name` (滅), `attributes_json` (PHI 採收期) |
| **`A12`** | `a12_pest_mrl_alert` | `v_master_pest_mrl` | `alert_id` | `detected_ppm`, `mrl_limit_ppm`, `is_over_limit` |
| **`A13`** | `a13_organic_farm_list` | `v_master_organic_cert` | `farm_id` | `farm_name`, `cert_number`, `applied_quantity_ton` |
| **`A14`** | `a14_fertilizer_licenses` | `v_master_fertilizer` | `fertilizer_lic_id` | `brand_name`, `nitrogen_pct`, `is_organic_cert` |
| **`A20`** | `a20_fishery_products` | `v_master_fishery_product` | `product_id` | `product_name`, `origin_location` (80% 臺灣在地標籤) |
| **`A21`** | `a21_aquaculture_monitoring`| `v_master_aquaculture` | `station_id` | `water_temp_c` ($15^\circ\text{C}$ 寒害), `dissolved_oxygen_mg_l` |
| **`A30`** | `a30_pork_trans_daily` | `v_master_livestock_pork` | `trans_id` | `trans_date` (無槓民國年轉 ISO), `total_heads`, `avg_price_ntd` |
| **`A31`** | `a31_vet_drug_residue` | `v_master_vet_drug` | `residue_id` | `drug_name` (氯黴素), `mrl_ppm` (0.0ppm 禁藥), `is_prohibited` |
| **`A40`** | `a40_agro_climate_stations` | `v_master_agro_climate` | `station_id` | `obs_date`, `temp_c`, `vapour_pressure_hpa` |
| **`A41`** | `a41_soil_water_pollution` | `v_master_soil_water` | `point_id` | `heavy_metal_name`, `concentration_ppm`, `regulatory_limit_ppm` |
| **`A50`** | `a50_agrovoc_concepts` | `a50_agrovoc_fts` | `concept_uri` | `pref_label_zh` (椰子), `pref_label_en`, FAO `c_1784` |
| **`A00`** | `a00_graph_triples` | `fts_agro_global` | `triple_id` | `subject_uri`, `predicate`, `object_uri` (GraphRAG 三元組) |

---

> **💡 查閱完整 DDL**：請直接點擊閱讀專案中的物理權威檔案 [schema.sql](file:///Users/wuulong/github/bmad-pa/events-2026Q3/agro-db-in/tw-agro-db/schema.sql)。
