-- 🐖 A31 vet_drug_food_residue_db Schema Definition

-- 1. 動物用藥殘留容許標準實體表
CREATE TABLE IF NOT EXISTS a31_vet_drug_residue (
    residue_id INTEGER PRIMARY KEY AUTOINCREMENT,
    drug_name TEXT NOT NULL,           -- 用藥名稱 (如 氯黴素, 萊克多巴胺, 恩氟沙星)
    target_livestock TEXT NOT NULL,    -- 適用畜產品/部位 (如 豬肉, 豬肝, 家禽肉)
    mrl_ppm REAL NOT NULL,              -- 殘留容許標準 (ppm) (0.0 表示不得檢出)
    withdrawal_period_days INTEGER DEFAULT 7, -- 停藥期 (天)
    is_prohibited INTEGER DEFAULT 0,    -- 禁用用藥旗標 (1=禁用, 0=核准)
    attributes_json TEXT NOT NULL DEFAULT '{"_v":"1.0.0"}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(drug_name, target_livestock)
);

-- 2. 全文檢索倒排表
CREATE VIRTUAL TABLE IF NOT EXISTS a31_vet_drug_fts USING fts5(
    drug_name,
    target_livestock,
    tokenize='unicode61'
);

-- 3. 母大腦動物用藥連網視圖
CREATE VIEW IF NOT EXISTS v_a31_vet_drug AS
SELECT 
    'A31' AS domain_code,
    residue_id,
    drug_name,
    target_livestock,
    mrl_ppm,
    withdrawal_period_days,
    is_prohibited
FROM a31_vet_drug_residue;
