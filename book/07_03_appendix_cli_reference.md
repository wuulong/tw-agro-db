# 📘 附錄 C：`tw-agro-cli` 與 12 大垂直模組特化 CLI 參數指令速查手冊 (07_03_appendix_cli_reference.md)

* **歸檔位置**：[events-2026Q3/agro-db-in/tw-agro-db/book/07_03_appendix_cli_reference.md](file:///Users/wuulong/github/bmad-pa/events-2026Q3/agro-db-in/tw-agro-db/book/07_03_appendix_cli_reference.md)

---

## 🛠️ C.1 A00 全域主程式 `tw-agro-cli` 指令速查

A00 母大腦命令列工具提供對全庫 12 大 DB 的總攬操控：

```bash
# 1. 全庫 12 DB 與 A00 母大腦神經網絡一鍵重新建置
tw-agro-cli build-all [--db PATH] [--force]

# 2. 全庫 18,725 筆 FTS5 倒排與 346 筆 GraphRAG 三元組跨域檢索
tw-agro-cli search <KEYWORD> [--json] [--db PATH]

# 3. 全庫 5 大 Safety Mesh 食安、寒害與重金屬診斷
tw-agro-cli doctor [--db PATH]
```

---

## 🌾 C.2 12 大垂直子模組領域特化 CLI 指令速查表

每個子模組除了具備基底 `build` 與 `search` 外，均針對其農業領域特化了專屬命令與篩選旗標：

### 1. `A10` 農糧行情 (`commands_a10.py`)
```bash
# 查詢作物批發行情並計算 CV 離散穩定度
python src/cli/commands_a10.py search "椰子" [--market "台北一"] [--cv-stability]
```

### 2. `A11` 農藥許可證 (`commands_a11.py`)
```bash
# 檢索農藥並篩選安全採收等待期 (PHI) 天數 (包含特殊 Unicode 如 滅)
python src/cli/commands_a11.py search "滅" [--min-phi-days 7]
```

### 3. `A12` 農檢 MRL 殘留 (`commands_a12.py`)
```bash
# 檢索農藥殘留並僅顯示超標違規品項 (MRLRatio > 1.0)
python src/cli/commands_a12.py search "甘藍" --over-limit-only
```

### 4. `A13` 有機農場認證 (`commands_a13.py`)
```bash
# 檢索有機農場申報資材與驗證機構
python src/cli/commands_a13.py search "硫酸銨" [--cert-body "采園"]
```

### 5. `A14` 肥料登記證 (`commands_a14.py`)
```bash
# 檢索肥料並僅顯示審定合格之有機資材 (ORGANIC_APPROVED)
python src/cli/commands_a14.py search "寶綠多" --organic-approved-only
```

### 6. `A20` 水產行情 (`commands_a20.py`)
```bash
# 檢索水產品並解析管道符描述以篩選臺灣在地標籤
python src/cli/commands_a20.py search "秋刀魚" --local-taiwan-only
```

### 7. `A21` 水質與寒害監測 (`commands_a21.py`)
```bash
# 查詢沿海水質據點並僅顯示水溫 < 15°C 寒害警報 (FREEZING_ALERT)
python src/cli/commands_a21.py search "七股區" --freezing-alert
```

### 8. `A30` 毛豬批發拍賣 (`commands_a30.py`)
```bash
# 查詢毛豬拍賣行情並支援無槓民國年轉碼 (如 1150819 ➔ 2026-08-19)
python src/cli/commands_a30.py search "花蓮縣" [--roc-date "1150819"]
```

### 9. `A31` 動物用藥殘留 (`commands_a31.py`)
```bash
# 檢索動物用藥殘留並僅顯示 MRL = 0.0ppm 國定禁藥 (PROHIBITED)
python src/cli/commands_a31.py search "氯黴素" --prohibited-only
```

### 10. `A40` 農業氣象觀測 (`commands_a40.py`)
```bash
# 查詢氣象站觀測歷史 (氣溫與水氣壓)
python src/cli/commands_a40.py search "100213" [--obs-date "2015-12-03"]
```

### 11. `A41` 土壤與水質環境 (`commands_a41.py`)
```bash
# 查詢重金屬據點並僅顯示 PollutionRatio >= 1.0 高風險區域
python src/cli/commands_a41.py search "北投區" --high-risk-only
```

### 12. `A50` FAO AGROVOC 國際詞庫 (`commands_a50.py`)
```bash
# 多語檢索 FAO 國際概念並展示 SKOS 上位階層 (Broader URI)
python src/cli/commands_a50.py search "coconuts" [--skos-broader]
```
