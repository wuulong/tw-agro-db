-- 🌿 A14 organic_fertilizer_db Schema Definition

-- 1. 肥料登記證與資材實體表
CREATE TABLE IF NOT EXISTS a14_fertilizer_licenses (
    fertilizer_lic_id TEXT PRIMARY KEY,  -- 肥料登記證字號 (如 肥製(質)字第0001234號)
    brand_name TEXT NOT NULL,           -- 廠牌商品名稱 (如 金綠滿有機肥)
    manufacturer_name TEXT NOT NULL,    -- 業者/製造廠名稱 (如 豐綠生物科技)
    fertilizer_type TEXT NOT NULL,      -- 肥料品目類別 (如 5-01 有機質肥料)
    nitrogen_pct REAL DEFAULT 0.0,      -- 全氮含量 (%)
    phosphorus_pct REAL DEFAULT 0.0,    -- 全磷酸含量 (%)
    potassium_pct REAL DEFAULT 0.0,     -- 全氧化鉀含量 (%)
    is_organic_cert INTEGER DEFAULT 0,  -- 有機資材審定旗標 (1=審定合格, 0=一般)
    expire_date TEXT,                   -- 有效期限 (如 2028-12-31)
    attributes_json TEXT NOT NULL DEFAULT '{"_v":"1.0.0"}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 全文檢索倒排表
CREATE VIRTUAL TABLE IF NOT EXISTS a14_fertilizer_fts USING fts5(
    fertilizer_lic_id,
    brand_name,
    manufacturer_name,
    fertilizer_type,
    tokenize='unicode61'
);

-- 3. 母大腦肥料連網視圖
CREATE VIEW IF NOT EXISTS v_a14_fertilizer AS
SELECT 
    'A14' AS domain_code,
    fertilizer_lic_id,
    brand_name,
    manufacturer_name,
    fertilizer_type,
    nitrogen_pct,
    phosphorus_pct,
    potassium_pct,
    is_organic_cert,
    expire_date
FROM a14_fertilizer_licenses;
