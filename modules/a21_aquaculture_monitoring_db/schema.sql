-- 🐟 A21 aquaculture_monitoring_db Schema Definition

-- 1. 水產養殖環境與水質監測實體表
CREATE TABLE IF NOT EXISTS a21_aquaculture_monitoring (
    farm_id TEXT PRIMARY KEY,           -- 養殖場/魚塭代號 (如 TW_AQUA_201)
    county_name TEXT NOT NULL,          -- 縣市 (如 屏東縣)
    town_name TEXT NOT NULL,            -- 鄉鎮市區 (如 佳冬鄉)
    aquaculture_species TEXT NOT NULL,  -- 養殖物種 (如 石斑魚, 虱目魚, 泰國蝦)
    obs_time TEXT NOT NULL,             -- 觀測時間 (如 2025-01-15 06:00:00)
    water_temp_c REAL NOT NULL,         -- 水溫 (°C)
    dissolved_oxygen_mg_l REAL NOT NULL,-- 溶氧量 (mg/L)
    salinity_ppt REAL DEFAULT 30.0,     -- 鹽度 (ppt)
    ph_value REAL DEFAULT 7.8,          -- pH 值
    risk_level TEXT NOT NULL,           -- 'SAFE', 'WARNING', 'HIGH_RISK'
    attributes_json TEXT NOT NULL DEFAULT '{"_v":"1.0.0"}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 全文檢索倒排表
CREATE VIRTUAL TABLE IF NOT EXISTS a21_aquaculture_fts USING fts5(
    farm_id,
    county_name,
    town_name,
    aquaculture_species,
    tokenize='unicode61'
);

-- 3. 母大腦水產連網視圖
CREATE VIEW IF NOT EXISTS v_a21_aquaculture AS
SELECT 
    'A21' AS domain_code,
    farm_id,
    county_name,
    town_name,
    aquaculture_species,
    obs_time,
    water_temp_c,
    dissolved_oxygen_mg_l,
    salinity_ppt,
    risk_level
FROM a21_aquaculture_monitoring;
