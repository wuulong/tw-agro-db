# 📖 a00_master_hub CLI 操作說明書 (CLI_MANUAL.md)

母大腦 CLI 命令整合於 `tw-agro-db` 主入口 `src/cli/main.py`：

```bash
# 1. 執行母大腦全庫建置 (視圖織連, FTS 倒排, 延伸分析計算)
python src/cli/main.py build-all --db db/agro.db

# 2. 發動全域 FTS5 倒排檢索
python src/cli/main.py search "甘藍" --db db/agro.db

# 3. 檢視全台農產跨市場價格離散指標
python src/cli/main.py analytics --crop-id LA --db db/agro.db

# 4. 全庫健康度 Doctor Check
python src/cli/main.py doctor --db db/agro.db
```
