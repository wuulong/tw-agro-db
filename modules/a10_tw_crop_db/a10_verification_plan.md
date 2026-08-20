# 📋 a10_tw_crop_db 驗證計畫 (a10_verification_plan.md)

本模組驗證腳本位於 `tests/test_a10_tw_crop_db.py`，驗證規範剛性對齊以下 ID：

| 驗證 ID | 測試內容與對齊目標 | 預期 PASS 條件 |
| :--- | :--- | :--- |
| **`VAL-001`** | **主鍵與資料筆數完整性** | `a10_crop_dictionary` $\ge 1$，`a10_crop_trans_daily` $\ge 6,000$ 筆。 |
| **`VAL-002`** | **ISO 8601 日期轉換** | `trans_date` 格式符合 `YYYY-MM-DD`（如 `2026-08-19`），無民國年殘留。 |
| **`VAL-003`** | **休市狀態自動標記** | `crop_id = 'rest'` 或交易量為 0 之紀錄其 `is_rest = 1`。 |
| **`VAL-004`** | **雙層 Metadata 版號** | `attributes_json` 欄位包含 `{"_v": "1.0.0"}`。 |
| **`VAL-005`** | **FTS5 與 View 檢索測試** | `a10_crop_fts` 檢索反應時間 $< 0.005$ 秒。 |
