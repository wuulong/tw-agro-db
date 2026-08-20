# 📌 AXX template_blueprint (子模組複製藍圖範本手冊)

> [!WARNING]
> **領域特化防護鏈 (Domain Specificity Guard Warning)**：
> 本藍圖僅提供 CLI 與通用的骨架控制流！在建立新子模組時：
> 1. **嚴禁塗改變數後直接生成通用套話**的 Impl Plan, Walkthrough 與測試 Log！
> 2. 必須針對該領域的 **「特異欄位、特化算式、特異情境與真實量化分佈」** 撰寫專屬測試與 Log 印出！

---

## 🛠️ 藍圖包含檔案說明

* `schema.sql`: 實體表、FTS5 倒排表與解耦 View 結構
* `etl.py`: ETL 數據入庫與 `attributes_json` 欄位寫入
* `fts.py`: FTS5 倒排建置
* `metadata_gen.py`: 呼叫核心 `write_dual_metadata()` 自動算 Hash 與更新系統表
* `commands_blueprint.py`: 呼叫核心 `cli_template` 框架提供 `build`, `search`, `doctor` CLI
