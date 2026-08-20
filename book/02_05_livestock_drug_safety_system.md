# 📘 2.5 畜牧毛豬交易與獸藥殘留食安防衛體系 (02_05_livestock_drug_safety_system.md)

* **歸檔位置**：[events-2026Q3/agro-db-in/tw-agro-db/book/02_05_livestock_drug_safety_system.md](file:///Users/wuulong/github/bmad-pa/events-2026Q3/agro-db-in/tw-agro-db/book/02_05_livestock_drug_safety_system.md)
* **物理資料支撐**：`A30` (毛豬行情 DB)、`A31` (動物用藥殘留 DB)

---

## 🐖 2.5.1 毛豬批發市場拍賣與 ISO 無槓民國年轉碼解構

全台 23 處毛豬批發拍賣市場每日產出巨量交易資料，但原始日期多採用無槓民國年格式 (如 `1150819`)：

* **解構重點**：
  - 實作無槓民國年轉碼算式 (`1150819 ➔ 2026-08-19`)，達成 ISO 8601 標準對照整合。
  - 追蹤各大拍賣市場之成交頭數、平均重量與均價。
* **物理資料支撐 (`A30`)**：
  - [test_a30_livestock_db.py](file:///Users/wuulong/github/bmad-pa/events-2026Q3/agro-db-in/tw-agro-db/tests/test_a30_livestock_db.py) 驗證花蓮縣市場 291 頭、均價 105.19 元/kg 之轉碼資料。

---

## 💉 2.5.2 動物用藥殘留與禁藥 ($MRL == 0.0\text{ ppm}$) 零容忍食安網解構

肉品食安容不得半點死角。獸藥殘留知識體系建立嚴格的禁藥攔截模型：

* **解構重點**：
  - 判定殘留容許量 $MRL == 0.0\text{ ppm}$ 之品項為國定禁藥（如氯黴素）。
  - 自動標註 `PROHIBITED` 禁藥警告標籤，避免違規肉品流入消費市場。
* **物理資料支撐 (`A31`)**：
  - `A31` 提供畜產品殘留監測資料與 0.0ppm 禁藥判定。
