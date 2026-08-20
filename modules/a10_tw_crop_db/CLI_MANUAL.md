# 📖 a10_tw_crop_db CLI 操作說明書 (CLI_MANUAL.md)

本模組 CLI 指令已註冊至 `tw-agro-db` 主入口 `src/cli/main.py`，支援以下操作命令：

```bash
# 1. 執行 ETL 建立/更新實體 DB
python src/cli/main.py a10 build --input agro_poc_samples/A10_crop_farm_trans.json --db db/agro.db

# 2. 檢索農作物與行情
python src/cli/main.py a10 search "椰子" --db db/agro.db

# 3. 診斷模組健康度
python src/cli/main.py a10 doctor --db db/agro.db
```
