-- 🌧️ A40 agro_climate_db Schema Definition

-- 農業氣象每日觀測表
CREATE TABLE IF NOT EXISTS a40_climate_daily_obs (
    station_sn TEXT NOT NULL,         -- 測站流水號 (如 100213)
    obs_date TEXT NOT NULL,           -- 觀測日期 (ISO 8601 YYYY-MM-DD)
    obs_count INTEGER DEFAULT 0,      -- 觀測筆數 (如 96 筆)
    download_url TEXT,                -- CSV 資料下載連結
    attributes_json TEXT NOT NULL DEFAULT '{"_v":"1.0.0"}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (station_sn, obs_date)
);

-- 全文檢索倒排表
CREATE VIRTUAL TABLE IF NOT EXISTS a40_climate_fts USING fts5(
    station_sn,
    obs_date,
    tokenize='unicode61'
);

-- 母大腦連網視圖
CREATE VIEW IF NOT EXISTS v_a40_agro_climate AS
SELECT 
    'A40' AS domain_code,
    station_sn,
    obs_date,
    obs_count,
    download_url
FROM a40_climate_daily_obs;
