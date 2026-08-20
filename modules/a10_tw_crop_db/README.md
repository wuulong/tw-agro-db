# 🌾 a10_tw_crop_db (農作物與行情錨點庫)

`a10_tw_crop_db` 是 `tw-agro-db` (台灣農業開放大數據引擎) 的第一基石子模組。
負責儲存台灣農作物登記字典、別名對照與每日批發市場交易行情快照。

## 📁 檔案結構

* `schema.sql`: 定義實體資料表 `a10_crop_dictionary`, `a10_crop_trans_daily` 與 FTS5 全文檢索虛擬表 `a10_crop_fts`。
* `etl.py`: 負責清洗 MOA 農產品交易 Open Data (`A10_crop_farm_trans.json`)，將民國年轉換為 ISO 8601，並自動識別休市資料。
* `fts.py`: 建立專屬 FTS5 倒排索引。
* `metadata_gen.py`: 動態統計與維護模組中之資料筆數。
* `metadata.json`: 模組 Master Manifest 檔。
