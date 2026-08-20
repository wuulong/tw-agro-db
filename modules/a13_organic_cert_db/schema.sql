-- 🌾 A13 organic_cert_db Schema Definition

-- 有機資材與產銷名冊表
CREATE TABLE IF NOT EXISTS a13_organic_materials_registry (
    registry_id INTEGER PRIMARY KEY AUTOINCREMENT,
    period_year TEXT NOT NULL,         -- 年度 (如 2025)
    material_name TEXT NOT NULL,       -- 肥料別 / 資材名稱 (如 硫酸銨, 尿素)
    category_type TEXT NOT NULL,       -- 產銷類別 (如 進口, 國產)
    quantity_tons REAL DEFAULT 0.0,    -- 數量 (公噸)
    value_thousand_ntd REAL DEFAULT 0, -- 價值 (千元)
    attributes_json TEXT NOT NULL DEFAULT '{"_v":"1.0.0"}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 資材全文檢索倒排表
CREATE VIRTUAL TABLE IF NOT EXISTS a13_organic_fts USING fts5(
    registry_id UNINDEXED,
    material_name,
    category_type,
    period_year,
    tokenize='unicode61'
);

-- 母大腦連網視圖
CREATE VIEW IF NOT EXISTS v_a13_organic_cert AS
SELECT 
    'A13' AS domain_code,
    registry_id,
    period_year,
    material_name,
    category_type,
    quantity_tons,
    value_thousand_ntd
FROM a13_organic_materials_registry;
