# 📋 a00_master_hub 驗證計畫 (a00_verification_plan.md)

本模組測試位於 `tests/test_a00_master_hub.py`，對齊以下驗證 ID：

| 驗證 ID | 測試內容與對齊目標 | 預期 PASS 條件 |
| :--- | :--- | :--- |
| **`VAL-A00-001`** | **母大腦視圖織連測試** | `v_master_crop_market` 正確連網 A10，筆數 $\ge 6000$。 |
| **`VAL-A00-002`** | **全域 FTS5 倒排延遲** | `fts_agro_global` 檢索延遲 $< 0.05$ 秒。 |
| **`VAL-A00-003`** | **延伸分析 $CV$ 演算法** | `a00_master_cross_market_index` 正確計算全台均價與 $CV$。 |
| **`VAL-A00-004`** | **Master Manifest 完整性** | `metadata.json` 包含全母大腦表與啟用子模組對應。 |
