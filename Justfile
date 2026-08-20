# Justfile for tw-agro-db (台灣農業開放大數據引擎)

PYTHON := "/Users/wuulong/opt/anaconda3/envs/m2504/bin/python"

# 1. 執行 12 大垂直 DB 與 A00 母大腦全量建置
agro-build-all:
	@echo "🚀 開始執行 12 大垂直 DB 與 A00 全量建置..."
	PYTHONPATH=. {{PYTHON}} src/a00_core/master_builder/builder_main.py

# 2. 發動 63/63 全網單元測試與 Quiet Log 歸檔
agro-test-all:
	@echo "🧪 開始發動 63/63 全網單元測試..."
	PYTHONPATH=. {{PYTHON}} -m pytest tests/

# 3. 執行系統工程 100% 對合度與 Buildlogs 審計
agro-audit-syseng:
	@echo "📋 執行系統工程 100% 對合度審計..."
	@cat ../sys_eng/05_verification_testing/SYSTEM_ENGINEERING_ALIGNMENT_AUDIT.md

# 4. 讀取實體 DB 原生 .schema 與 JSON 備註，一鍵自動編譯產出 schema.sql
agro-schema-gen:
	@echo "🔄 自動編譯產出最新帶備註之 schema.sql..."
	PYTHONPATH=. {{PYTHON}} scripts/generate_schema_sql.py --db db/agro.db --config src/config/schema_comments.json --out schema.sql

# 5. 一鍵將全書獨立章節打包為 FULL_BOOK_TAIWAN_AGRO_DB.md 全本手冊
agro-book-combine:
	@echo "📚 一鍵打包全書獨立章節至 FULL_BOOK_TAIWAN_AGRO_DB.md..."
	PYTHONPATH=. {{PYTHON}} ../../../scripts/blog/combine_tw_agro_db_book.py


