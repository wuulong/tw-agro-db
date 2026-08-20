# 📘 2.7 聯合國 FAO AGROVOC 國際農學多語體系 (02_07_fao_agrovoc_lod_system.md)

* **歸檔位置**：[events-2026Q3/agro-db-in/tw-agro-db/book/02_07_fao_agrovoc_lod_system.md](file:///Users/wuulong/github/bmad-pa/events-2026Q3/agro-db-in/tw-agro-db/book/02_07_fao_agrovoc_lod_system.md)
* **物理數據支撐**：`A50` (FAO AGROVOC 國際農學詞庫 DB)

---

## 🌐 2.7 聯合國 FAO AGROVOC 國際農學多語 LOD 體系解構

台灣在地農學名詞（如椰子、釋迦、毛豬部位）長期面臨跨國貿易、國際學術交流與跨語言 Agent 檢索時的「語意斷層」困境。各國對同一作物的稱呼不一，使得台灣農業數據難以直接融入全球開放資料 Linked Open Data (LOD) 網絡。

為突破此一障礙，A50 模組建立了**聯合國糧農組織 FAO AGROVOC 國際農學多語本體體系**，作為在地台規數據與國際標準間的橋樑：

### 1. SKOS 多語階層拓撲與概念模型
- **40,097 概念與 82,954 標籤**：完整收錄 FAO AGROVOC 核心的概念 URI（如 `http://aims.fao.org/aos/agrovoc/c_1784`），涵蓋繁體中文、英文、法文、西班牙文、日文等數十種語言標籤。
- **SKOS 拓撲貫通**：解析 `skos:broader` 與 `skos:narrower` 上下位階層關係（例如：`椰子` 的上位概念為 `棕櫚科植物`，下位概念包含 `椰子油`）。

### 2. 實測物理數據對合 (A50)
- 在 [test_a50_fao_agrovoc_db.py](file:///Users/wuulong/github/bmad-pa/events-2026Q3/agro-db-in/tw-agro-db/tests/test_a50_fao_agrovoc_db.py) (VAL-001 ~ 004) 實測中：
  - 成功入庫 **40,097 筆** 核心概念與 **82,954 筆** 多語標籤。
  - FTS5 多語倒排檢索 `coconut` 命中 8 筆紀錄，延遲僅 51.7 ms。
  - 成功將台灣在地作物「椰子」與 FAO 國際概念 `c_1784` 完成 1.0 得分的精確語意對合，並連結至 A00 母大腦的 Master View `v_master_agrovoc_semantic`。
