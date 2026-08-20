-- 🌾 A11 pesticide_db Schema Definition

-- 農藥許可證主表
CREATE TABLE IF NOT EXISTS a11_pesticide_licenses (
    pesticide_lic_id TEXT PRIMARY KEY, -- 許可證字號 (如 農藥進00001)
    lic_type TEXT NOT NULL,           -- 許可證字 (農藥進 / 農藥製)
    lic_no TEXT NOT NULL,             -- 許可證號
    pesticide_name TEXT,              -- 中文名稱
    pesticide_en_name TEXT,           -- 英文名稱
    brand_name TEXT,                  -- 廠牌名稱 (如 滅)
    pesticide_code TEXT,              -- 農藥代號
    formulation TEXT,                 -- 劑型 (如 EC, WP)
    active_ingredient_pct TEXT,       -- 含量
    manufacturer TEXT,                -- 國內/外原製造廠商
    vendor_name TEXT,                 -- 申請廠商名稱
    expire_date TEXT,                 -- 有效期限 (ISO 8601 YYYY-MM-DD)
    revoke_type TEXT,                 -- 撤銷/廢止類別 (如 逾期廢止)
    revoke_date TEXT,                 -- 撤銷日期
    detail_url TEXT,                  -- 農藥使用範圍連結
    attributes_json TEXT NOT NULL DEFAULT '{"_v":"1.0.0"}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 禁用/管制農藥表
CREATE TABLE IF NOT EXISTS a11_prohibited_pesticides (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pesticide_name TEXT NOT NULL,     -- 農藥名稱 (如 安特靈)
    pesticide_en_name TEXT,           -- 英文名稱
    prohibited_mfg_import_date TEXT,  -- 禁止製造/輸入日期 (ISO 8601)
    prohibited_sale_use_date TEXT,    -- 禁止銷售/使用日期 (ISO 8601)
    attributes_json TEXT NOT NULL DEFAULT '{"_v":"1.0.0"}'
);

-- 農藥全文檢索倒排表
CREATE VIRTUAL TABLE IF NOT EXISTS a11_pesticide_fts USING fts5(
    pesticide_lic_id UNINDEXED,
    pesticide_name,
    pesticide_en_name,
    brand_name,
    vendor_name,
    tokenize='unicode61'
);

-- 母大腦連網視圖
CREATE VIEW IF NOT EXISTS v_a11_pesticide_safety AS
SELECT 
    'A11' AS domain_code,
    pesticide_lic_id,
    pesticide_name,
    brand_name,
    formulation,
    active_ingredient_pct,
    vendor_name,
    expire_date,
    revoke_type,
    detail_url
FROM a11_pesticide_licenses;
