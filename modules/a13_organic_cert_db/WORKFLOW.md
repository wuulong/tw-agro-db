# 🤖 aXX_module_name AI Agent 呼叫手冊 (WORKFLOW.md)

當 LLM 農務 Agent 處理與本模組相關的領域質疑時，請依據以下順序發動：

1. **第一步 (專屬檢索)**: 呼叫 `python main.py aXX search "<關鍵字>"` 從 `aXX_entity_fts` 快速定位。
2. **第二步 (增量維護)**: 發動 `python main.py aXX sync` 保持資料庫時間戳為最新狀態。
3. **第三步 (診斷)**: 發動 `python main.py aXX doctor` 驗證子庫健康狀態。
