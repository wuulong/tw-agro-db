-- 🌾 a10_tw_crop_db Schema Definition

-- 農作物字典主表
CREATE TABLE IF NOT EXISTS a10_crop_dictionary (
    crop_id TEXT PRIMARY KEY,
    crop_name TEXT NOT NULL,
    category_code TEXT NOT NULL,
    category_name TEXT NOT NULL,
    aliases_json TEXT DEFAULT '[]',
    attributes_json TEXT NOT NULL DEFAULT '{"_v":"1.0.0"}'
);

CREATE INDEX IF NOT EXISTS idx_a10_crop_name ON a10_crop_dictionary(crop_name);
CREATE INDEX IF NOT EXISTS idx_a10_crop_cat ON a10_crop_dictionary(category_code);

-- 每日批發市場交易行情表
CREATE TABLE IF NOT EXISTS a10_crop_trans_daily (
    trans_date TEXT NOT NULL,         -- YYYY-MM-DD
    crop_id TEXT NOT NULL,            -- 作物代號
    market_id TEXT NOT NULL,          -- 市場代號
    market_name TEXT NOT NULL,        -- 市場中文名稱
    price_high REAL NOT NULL,         -- 上價
    price_mid REAL NOT NULL,          -- 中價
    price_low REAL NOT NULL,          -- 下價
    price_avg REAL NOT NULL,          -- 平均價
    volume_kg REAL NOT NULL,          -- 交易量 (kg)
    is_rest INTEGER DEFAULT 0,        -- 0: 正常交易, 1: 休市
    attributes_json TEXT NOT NULL DEFAULT '{"_v":"1.0.0"}',
    PRIMARY KEY (trans_date, crop_id, market_id)
);

CREATE INDEX IF NOT EXISTS idx_a10_trans_date_crop ON a10_crop_trans_daily(trans_date, crop_id);
CREATE INDEX IF NOT EXISTS idx_a10_trans_market ON a10_crop_trans_daily(market_id);

-- FTS5 全文倒排索引表
CREATE VIRTUAL TABLE IF NOT EXISTS a10_crop_fts USING fts5(
    crop_id UNINDEXED,
    crop_name,
    market_name,
    category_name,
    tokenize='unicode61'
);

-- E2 解耦母大腦視圖
CREATE VIEW IF NOT EXISTS v_a10_crop_market_summary AS
SELECT 
    t.trans_date,
    t.crop_id,
    d.crop_name,
    d.category_code,
    d.category_name,
    t.market_id,
    t.market_name,
    t.price_high,
    t.price_mid,
    t.price_low,
    t.price_avg,
    t.volume_kg,
    t.is_rest,
    CASE WHEN t.price_low > 0 THEN ROUND((t.price_high - t.price_low) / t.price_low * 100.0, 2) ELSE 0.0 END AS spread_pct
FROM a10_crop_trans_daily t
LEFT JOIN a10_crop_dictionary d ON t.crop_id = d.crop_id;
