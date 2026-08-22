# 🚀 任務指示：GOV-300 (tw-gov-db) ↔ GOV-A19 (tw-agro-db) 跨部會對接母大腦端實作與驗證

你現在是 **`GOV-300` (`tw-gov-db` 全政府母大腦基石庫)** 的 Agentic AI 開發專家。

子專案 **`GOV-A19` (農業部 `tw-agro-db`)** 已經將權威對接規格 (Synergy Spec) 歸位並更新至 `GOV_A19_SYNERGY_SPEC.md`。請依據契約規範，完成母大腦端的 4 大對接能力實作與測試！

---

## 📍 權威對接規格參照 (Synergy Spec Reference)
請使用 `view_file` 讀取母專案軟連結對接合約：
📄 [book/04_synergy_contracts/4.A19_spec_gov_a19_synergy.md](book/04_synergy_contracts/4.A19_spec_gov_a19_synergy.md)
重點查看 **第 2.2 節 (G300 必須實作之基石服務與介面規格)**。

---

## 🎯 你的 3 大執行任務：

### 1. 驗證與確保母大腦 4 大基石介面 (G300 Implementation Verification)
請確認 `GOV-300` 的 `src/core/` 已具備並暴露以下對接能力：
- **`G300-REQ-001` (OID 歸併)**：`BaseDomainAdapter.align_publisher_oid()` 支援帶入「農糧署中區分署」或「農業部」，回傳對應 OID `2.16.886.101...`。
- **`G300-REQ-002` (門牌反查)**：`universal_keys.sqlite` 暴露 `admin_codes` 表，帶入 "臺北市中正區" 回傳 6 碼門牌區號 `630001`。
- **`G300-REQ-003` (氣象測站對接)**：`station_registry` 暴露 450 個測站座標，供 A19 發動寒害周邊 20km 農場掃描。
- **`G300-REQ-004` (跨部會調度)**：`DomainRegistryResolver` 支援 `get_domain_core_db_connection("GOV-A19", "agro.db")` 直連。

### 2. 執行母大腦端 4 階對接整合測試套件
請切換至 `tw-gov-db` 目錄，執行母大腦端對接測試：
`python3 tests/test_gov_agro_integration.py`
確保 4 階測試 (三層連線 ➜ OID 歸併 ➜ 門牌/氣象碰撞 ➜ P99 < 10ms) 100% 綠燈通過！

### 3. 歸檔 Buildlogs (IMP / WT 雙檔配對)
依據 SE 規範，於 `sys_eng/00_buildlogs/` 歸檔以下雙檔：
- `IMP_GOV_300_A19_INTEGRATION_PLAN.md`
- `WT_GOV_300_A19_INTEGRATION.md`
並於 `sys_eng/05_verification_testing/TR_GOV_300_MASTER_VERIFICATION.md` 增量紀錄測試結果！

---

請先產出 Implementation Plan 並執行測試，回報 100% PASS 結果！
