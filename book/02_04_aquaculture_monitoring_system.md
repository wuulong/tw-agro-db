# 📘 2.4 養殖漁業環境與微氣候寒害監測知識體系 (02_04_aquaculture_monitoring_system.md)

* **歸檔位置**：[events-2026Q3/agro-db-in/tw-agro-db/book/02_04_aquaculture_monitoring_system.md](file:///Users/wuulong/github/bmad-pa/events-2026Q3/agro-db-in/tw-agro-db/book/02_04_aquaculture_monitoring_system.md)
* **物理數據支撐**：`A20` (水產行情 DB)、`A21` (水質與寒害監測 DB)

---

## 🐟 2.4.1 水產養殖生態與 80% 臺灣在地屬性解構

養殖漁業產品資訊過去多填寫於管道符 `│` 描述欄位中。水產知識體系透過正則與字串解析器進行結構化拆解：

* **解構重點**：
  - 拆解 `|產品名稱：秋刀魚|來源產地：臺灣|產品重量：500g|保存方式：零下-18℃` 等混亂描述。
  - 量化臺灣在地養殖屬性標籤 (`LOCAL_TAIWAN_AQUACULTURE`)。
* **物理數據支撐 (`A20`)**：
  - [test_a20_fishery_market_db.py](file:///Users/wuulong/github/bmad-pa/events-2026Q3/agro-db-in/tw-agro-db/tests/test_a20_fishery_market_db.py) 驗證在地養殖產品佔比高達 80% (4/5 筆)。

---

## ❄️ 2.4.2 水溫 $<15^\circ\text{C}$ 寒害與溶氧 $<3\text{mg/L}$ 缺氧預警 Scorer 解構

沿海養殖池受冬季寒流與夏季悶熱影響極大。氣候與水質知識體系建立實時預警演算法：

* **解構重點**：
  - **寒害預警**：當實測水溫 $< 15^\circ\text{C}$ 且持續下降時，觸發 `FREEZING_ALERT` 防寒警報。
  - **缺氧預警**：當水體溶氧 $< 3\text{mg/L}$ 時，觸發 `ANOXIA_WARNING` 缺氧警報。
* **物理數據支撐 (`A21`)**：
  - `A21` 提供水質據點監測數據與 $13.08^\circ\text{C}$ 實測寒害標籤算式。
