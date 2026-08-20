-- 🌾 aXX_module_template Schema Definition (aXX 黃金開箱範本)

-- 子模組實體主表
CREATE TABLE IF NOT EXISTS aXX_entity_table (
    entity_id TEXT PRIMARY KEY,       -- 主鍵
    entity_name TEXT NOT NULL,        -- 中文名稱
    category_name TEXT,              -- 分類 / 類別
    attributes_json TEXT NOT NULL DEFAULT '{"_v":"1.0.0"}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 全文檢索 FTS5 虛擬表
CREATE VIRTUAL TABLE IF NOT EXISTS aXX_entity_fts USING fts5(
    entity_id UNINDEXED,
    entity_name,
    category_name,
    tokenize='unicode61'
);

-- 母大腦織連視圖 (v_master_aXX_name)
CREATE VIEW IF NOT EXISTS v_master_aXX_name AS
SELECT 
    'AXX' AS domain_code,
    entity_id,
    entity_name,
    category_name
FROM aXX_entity_table;
