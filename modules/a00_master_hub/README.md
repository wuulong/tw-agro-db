# 👑 a00_master_hub (母大腦與全域索引中心)

`a00_master_hub` 是 `tw-agro-db` (台灣農業開放大數據引擎) 的母大腦總控制庫。
負責維護全專案 5 大 Pillar 的解耦視圖織連、全域 FTS5 倒排索引 (`fts_agro_global`) 與母大腦延伸分析指標表 (`a00_master_cross_market_index`)。

## 📁 檔案結構

* `schema.sql`: 定義全域 FTS5 倒排表與全台跨市場價格離散指標表。
* `etl.py`: 母大腦 ETL 邏輯，觸發視圖織連與延伸分析計算。
* `fts.py`: 建立全域 FTS5 倒排總表。
* `metadata_gen.py`: 維護母大腦 Manifest 狀態與資料筆數。
* `metadata.json`: 模組 Master Manifest 檔。
