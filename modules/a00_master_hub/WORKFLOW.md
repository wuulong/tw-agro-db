# 🤖 a00_master_hub AI Agent 呼叫手冊 (WORKFLOW.md)

當 LLM 農務 Agent 處理複雜農業諮詢時，請依據以下順序發動：

1. **第一步 (全域檢索)**: 呼叫 `python main.py search "<關鍵字>"` 從 `fts_agro_global` 快速定位領域 (A10/A11)。
2. **第二步 (延伸分析)**: 呼叫 `python main.py analytics --crop-id <ID>` 檢查全台均價與離散係數 $CV$。
3. **第三步 (診斷)**: 發動 `python main.py doctor` 驗證全庫健康狀態。
