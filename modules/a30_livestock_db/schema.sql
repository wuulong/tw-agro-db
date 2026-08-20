-- 🐖 A30 livestock_db Schema Definition

-- 毛豬每日交易行情表
CREATE TABLE IF NOT EXISTS a30_pork_trans_daily (
    trans_date TEXT NOT NULL,         -- 交易日期 ISO 8601 (YYYY-MM-DD)
    market_name TEXT NOT NULL,        -- 肉品市場名稱 (如 花蓮縣, 彰化縣)
    total_heads INTEGER DEFAULT 0,    -- 成交頭數-總數
    avg_weight_kg REAL DEFAULT 0.0,   -- 成交頭數-平均重量 (kg)
    avg_price_ntd REAL DEFAULT 0.0,   -- 成交頭數-平均價格 (元/kg)
    spec_heads INTEGER DEFAULT 0,     -- 規格豬-頭數
    spec_weight_kg REAL DEFAULT 0.0,  -- 規格豬-平均重量
    spec_price_ntd REAL DEFAULT 0.0,  -- 規格豬-平均價格
    attributes_json TEXT NOT NULL DEFAULT '{"_v":"1.0.0"}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (trans_date, market_name)
);

-- 全文檢索倒排表
CREATE VIRTUAL TABLE IF NOT EXISTS a30_pork_fts USING fts5(
    trans_date UNINDEXED,
    market_name,
    tokenize='unicode61'
);

-- 母大腦連網視圖
CREATE VIEW IF NOT EXISTS v_a30_livestock_pork AS
SELECT 
    'A30' AS domain_code,
    trans_date,
    market_name,
    total_heads,
    avg_weight_kg,
    avg_price_ntd,
    spec_heads,
    spec_price_ntd
FROM a30_pork_trans_daily;
