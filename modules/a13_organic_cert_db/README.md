# 🌾 aXX_module_name (新模組名稱)

本模組為 `tw-agro-db` (台灣農業開放大數據引擎) 的子模組藍圖範本。

## 📁 檔案結構

* `schema.sql`: 定義子模組實體主表 `aXX_entity_table`、倒排表 `aXX_entity_fts` 與母大腦 View `v_master_aXX_name`。
* `etl.py`: ETL 洗牌管線與 `INSERT OR REPLACE` 增量寫入邏輯。
* `fts.py`: 建立子模組專屬 FTS5 全文檢索索引。
* `metadata_gen.py`: 雙軌 Metadata 更新 (寫入 SQL `sys_module_metadata` 與 `metadata.json`)。
* `commands_aXX_template.py`: 複製至 `src/cli/commands_aXX.py` 使用。
