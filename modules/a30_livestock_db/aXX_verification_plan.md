# 📋 aXX_module_name 驗證計畫 (aXX_verification_plan.md)

本模組獨立單元測試應位於 `tests/test_aXX_[name].py`，對齊以下驗證 ID：

| 驗證 ID | 測試內容與對齊目標 | 預期 PASS 條件 |
| :--- | :--- | :--- |
| **`VAL-001`** | **主鍵與資料筆數完整性** | 全量真實數據 100% 入庫，主鍵無衝突。 |
| **`VAL-002`** | **日期/欄位格式轉換防呆** | 日期 100% 成功轉為 ISO 8601。 |
| **`VAL-003`** | **專屬 FTS5 檢索延遲** | 全文倒排檢索耗時 $< 0.05$ 秒。 |
| **`VAL-004`** | **雙軌 Metadata 系統表與 JSON 註冊** | `sys_module_metadata` 與 `metadata.json` 成功紀錄。 |
| **`VAL-005`** | **動態 Delta 增量與休市閉環** | 模擬新增、修改、休市閉環 100% 反應至 DB。 |
