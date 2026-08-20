-- 🌿 A41 soil_water_pollution_db Schema Definition

-- 1. 農地土壤與水質監測實體表
CREATE TABLE IF NOT EXISTS a41_soil_water_monitoring (
    site_id TEXT PRIMARY KEY,          -- 監測點代號 (如 TW_SOIL_101)
    county_name TEXT NOT NULL,         -- 縣市 (如 彰化縣)
    town_name TEXT NOT NULL,           -- 鄉鎮市區 (如 和美鎮)
    sample_date TEXT NOT NULL,         -- 採樣日期 (如 2025-05-10)
    pollutant_type TEXT NOT NULL,      -- 檢驗項目 (如 鎘 Cd, 砷 As, 鉛 Pb)
    concentration_ppm REAL NOT NULL,   -- 實測濃度 (ppm)
    regulatory_limit_ppm REAL NOT NULL,-- 管制標準值 (ppm)
    is_polluted INTEGER DEFAULT 0,     -- 超標旗標 (1=超標/管制, 0=正常)
    attributes_json TEXT NOT NULL DEFAULT '{"_v":"1.0.0"}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 全文檢索倒排表
CREATE VIRTUAL TABLE IF NOT EXISTS a41_soil_water_fts USING fts5(
    site_id,
    county_name,
    town_name,
    pollutant_type,
    tokenize='unicode61'
);

-- 3. 母大腦環境連網視圖
CREATE VIEW IF NOT EXISTS v_a41_soil_water AS
SELECT 
    'A41' AS domain_code,
    site_id,
    county_name,
    town_name,
    sample_date,
    pollutant_type,
    concentration_ppm,
    regulatory_limit_ppm,
    is_polluted
FROM a41_soil_water_monitoring;
