# 📘 2.1 農糧作物市場產銷與價格離散知識體系 (02_01_crop_market_system.md)

* **歸檔位置**：[events-2026Q3/agro-db-in/tw-agro-db/book/02_01_crop_market_system.md](file:///Users/wuulong/github/bmad-pa/events-2026Q3/agro-db-in/tw-agro-db/book/02_01_crop_market_system.md)
* **物理資料支撐**：`A10` (農糧批發交易行情 DB)

---

## 🌾 2.1 農糧作物市場產銷與價格離散知識解構

在農糧栽培生命週期中，價格波動是農民面臨最大風險。農糧知識體系不僅記錄市場每日成交價量，更引入 **價格變異係數離散模型 ($CV = \frac{\sigma}{\mu}$)**：

* **解構重點**：
  - 追蹤全台各大農糧批發市場（台北一、台北二、西螺、高雄等）成交行情。
  - 計算特定作物（如椰子、甘藍）長週期的均價 $\mu$ 與標準差 $\sigma$。
* **物理資料支撐 (`A10`)**：
  - [test_a10_tw_crop_db.py](file:///Users/wuulong/github/bmad-pa/events-2026Q3/agro-db-in/tw-agro-db/tests/test_a10_tw_crop_db.py) 實測椰子全台均價 19.77 元/kg，離散 CV 僅 0.0376，提供穩定的農效益評估。
