-- 🌾 A12 pest_mrl_alert_db Schema Definition

-- 農藥殘留與用藥抽驗主表
CREATE TABLE IF NOT EXISTS a12_mrl_inspection_records (
    record_id INTEGER PRIMARY KEY AUTOINCREMENT,
    period_year_month TEXT NOT NULL,  -- 年度月份 (如 110年1-12月)
    inspection_agency TEXT NOT NULL,  -- 抽樣衛生局 (如 基隆市)
    sample_name TEXT NOT NULL,        -- 檢體名稱 (如 好呷雞, 椰子)
    vendor_name TEXT,                 -- 抽樣廠商名稱 (如 全聯福利中心義二店)
    vendor_address TEXT,              -- 抽樣廠商地址
    test_result TEXT NOT NULL,        -- 檢出項目及殘留容許量 (如 合格, 超標)
    is_compliant INTEGER DEFAULT 1,   -- 是否合格 (1: 合格, 0: 違規)
    attributes_json TEXT NOT NULL DEFAULT '{"_v":"1.0.0"}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 農藥 MRL 容許量標準表
CREATE TABLE IF NOT EXISTS a12_pesticide_mrl_limits (
    crop_name TEXT NOT NULL,          -- 作物名稱
    pesticide_name TEXT NOT NULL,     -- 農藥化學成分
    mrl_ppm REAL NOT NULL,            -- 最大殘留容許量 (ppm)
    attributes_json TEXT NOT NULL DEFAULT '{"_v":"1.0.0"}',
    PRIMARY KEY (crop_name, pesticide_name)
);

-- 農檢全文檢索倒排表
CREATE VIRTUAL TABLE IF NOT EXISTS a12_mrl_fts USING fts5(
    record_id UNINDEXED,
    sample_name,
    vendor_name,
    inspection_agency,
    test_result,
    tokenize='unicode61'
);

-- 母大腦連網視圖
CREATE VIEW IF NOT EXISTS v_a12_pest_mrl AS
SELECT 
    'A12' AS domain_code,
    record_id,
    period_year_month,
    inspection_agency,
    sample_name,
    vendor_name,
    test_result,
    is_compliant
FROM a12_mrl_inspection_records;
