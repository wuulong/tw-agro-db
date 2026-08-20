# 🤖 a10_tw_crop_db AI Agent 呼叫手冊 (WORKFLOW.md)

當 LLM 農務 Agent 接收到人類詢問農作物交易價格、批發行情或作物主碼時，應以下列順序呼叫：

1. 詢問「椰子當前批發價」: 呼叫 `a10 search "椰子"` 取得最即時之 `price_avg` 及市場行情。
2. 詢問「甘藍休市狀態」: 呼叫 `a10 search "甘藍"` 並檢查回傳欄位之 `is_rest` 是否為 1。
