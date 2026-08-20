# 📖 aXX_module_name CLI 操作說明書 (CLI_MANUAL.md)

子模組 CLI 命令整合於 `tw-agro-db` 主入口 `src/cli/main.py`：

```bash
# 1. 執行子模組建置
python src/cli/main.py aXX build --input agro_poc_samples/AXX_sample.json --db db/agro.db

# 2. 發動增量同步 (Sync)
python src/cli/main.py aXX sync --db db/agro.db

# 3. 發動專屬 FTS5 倒排檢索
python src/cli/main.py aXX search "<關鍵字>" --db db/agro.db

# 4. 子模組健康度 Doctor Check
python src/cli/main.py aXX doctor --db db/agro.db
```
