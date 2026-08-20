# 📘 2.2 病蟲害防治與農藥安全採收期知識體系 (02_02_pesticide_safety_system.md)

* **歸檔位置**：[events-2026Q3/agro-db-in/tw-agro-db/book/02_02_pesticide_safety_system.md](file:///Users/wuulong/github/bmad-pa/events-2026Q3/agro-db-in/tw-agro-db/book/02_02_pesticide_safety_system.md)
* **物理資料支撐**：`A11` (農藥許可證 DB)、`A12` (MRL食安抽驗 DB)

---

## 🐛 2.2 病蟲害防治與農藥安全採收期 (PHI) 避險知識解構

當病蟲害爆發時，農民需要精確知道用藥品項與採收前的安全等待天數 (Pre-Harvest Interval, PHI)，防止農藥殘留違規：

* **解構重點**：
  - 收錄全台 9,993 筆農藥許可證，處理包含 Unicode 特殊字元（如「滅」）的複雜成分。
  - 將抽驗檢驗紀錄與衛福部 MRL 容許量對照整合，自動標註 `OVER_LIMIT` (超標違規) 與 `HIGH_RISK` (採收等待期 $\ge 7$ 天)。
* **物理資料支撐 (`A11`, `A12`)**：
  - `A11` 提供 9,993 筆藥證與 FTS5 倒排索引。
  - `A12` 實現殘留抽驗與 MRL 標準對照整合。
