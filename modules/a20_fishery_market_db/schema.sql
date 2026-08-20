-- 🐟 A20 fishery_market_db Schema Definition

-- 水產品資產名冊表
CREATE TABLE IF NOT EXISTS a20_fishery_products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT NOT NULL,       -- 水產品名稱 (如 秋刀魚, 透抽(大))
    origin_location TEXT,             -- 來源產地 (如 北太平洋海域, 臺灣, 宜蘭)
    weight_spec TEXT,                 -- 產品重量規格 (如 500g, 300g/包)
    storage_method TEXT,              -- 保存方式 (如 零下-18℃以下保存)
    attributes_json TEXT NOT NULL DEFAULT '{"_v":"1.0.0"}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 全文檢索倒排表
CREATE VIRTUAL TABLE IF NOT EXISTS a20_fishery_fts USING fts5(
    product_id UNINDEXED,
    product_name,
    origin_location,
    tokenize='unicode61'
);

-- 母大腦連網視圖
CREATE VIEW IF NOT EXISTS v_a20_fishery_product AS
SELECT 
    'A20' AS domain_code,
    product_id,
    product_name,
    origin_location,
    weight_spec,
    storage_method
FROM a20_fishery_products;
