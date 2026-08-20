# 📘 2.6 農業氣象觀測與農地重金屬環境安全體系 (02_06_agro_climate_environment_system.md)

* **歸檔位置**：[events-2026Q3/agro-db-in/tw-agro-db/book/02_06_agro_climate_environment_system.md](file:///Users/wuulong/github/bmad-pa/events-2026Q3/agro-db-in/tw-agro-db/book/02_06_agro_climate_environment_system.md)
* **物理數據支撐**：`A40` (農業氣象 DB)、`A41` (土壤水質 DB)

---

## 🌤️ 2.6.1 微氣候觀測與農地重金屬 ($PollutionRatio$) 風險評等解構

氣象與農地環境直接決定了作物的健康與食用安全：

* **解構重點**：
  - **微氣候觀測**：收錄全台 2,527 點氣象觀測歷史，提供日照、降雨與氣溫序列。
  - **重金屬風險**：計算污染比率 $PollutionRatio = \frac{conc}{limit}$，精確標註 `HIGH_RISK`（污染比率 $\ge 1.0$）區域。
* **物理數據支撐 (`A40`, `A41`)**：
  - `A40` 提供 2,527 點氣象觀測。
  - `A41` 提供重金屬 Ratio 0.75 / 1.0 風險評等。
