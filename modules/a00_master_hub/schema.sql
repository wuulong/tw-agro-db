-- 全域 SQL 系統元數據表 (sys_module_metadata)
CREATE TABLE IF NOT EXISTS sys_module_metadata (
    module_id TEXT PRIMARY KEY,
    module_name TEXT NOT NULL,
    table_name TEXT NOT NULL,
    record_count INTEGER DEFAULT 0,
    schema_version TEXT DEFAULT '1.0.0',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. 母大腦 A50 跨領域國際 AGROVOC 本體語意網
CREATE TABLE IF NOT EXISTS a00_agrovoc_cross_domain_mesh (
    concept_uri TEXT NOT NULL,         -- FAO AGROVOC URI (如 http://aims.fao.org/aos/agrovoc/c_1784)
    concept_id TEXT NOT NULL,          -- 概念 ID (如 c_1784)
    domain_code TEXT NOT NULL,         -- A10, A11, A20, A30, A40
    local_entity_id TEXT NOT NULL,      -- 本地主鍵
    local_entity_name TEXT NOT NULL,    -- 本地名稱 (如 '椰子', '益達胺', '毛豬')
    semantic_match_score REAL DEFAULT 1.0, -- 1.0 = EXACT_PREF_LABEL, 0.8 = ALT_LABEL
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (concept_uri, domain_code, local_entity_id)
);

-- 7. 母大腦 A41 區域農地環境安全網實體表 (a00_regional_environmental_safety_mesh)
CREATE TABLE IF NOT EXISTS a00_regional_environmental_safety_mesh (
    mesh_id INTEGER PRIMARY KEY AUTOINCREMENT,
    county_name TEXT NOT NULL,
    town_name TEXT NOT NULL,
    total_sites_count INTEGER DEFAULT 0,
    polluted_sites_count INTEGER DEFAULT 0,
    max_pollution_ratio REAL DEFAULT 0.0,
    primary_pollutant TEXT NOT NULL,
    environmental_risk_level TEXT NOT NULL, -- 'SAFE', 'WARNING', 'HIGH_RISK'
    attributes_json TEXT NOT NULL DEFAULT '{"_v":"1.0.0"}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(county_name, town_name)
);
-- 8. 母大腦 A30 ↔ A31 毛豬與畜產品動物用藥安全網實體表 (a00_livestock_pork_safety_mesh)
CREATE TABLE IF NOT EXISTS a00_livestock_pork_safety_mesh (
    mesh_id INTEGER PRIMARY KEY AUTOINCREMENT,
    livestock_market_name TEXT NOT NULL,  -- 批發市場 (如 彰化縣, 雲林縣)
    target_livestock TEXT NOT NULL,       -- 畜產品/部位 (如 毛豬, 豬肉, 豬肝)
    drug_name TEXT NOT NULL,              -- 動物用藥名稱 (如 氯黴素, 萊克多巴胺)
    mrl_ppm REAL NOT NULL,                 -- MRL 殘留容許標準 (ppm)
    is_prohibited INTEGER DEFAULT 0,       -- 是否禁用 (1=禁用, 0=核准)
    food_safety_risk_level TEXT NOT NULL,  -- 'SAFE', 'HIGH_RISK', 'PROHIBITED'
    attributes_json TEXT NOT NULL DEFAULT '{"_v":"1.0.0"}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(livestock_market_name, drug_name)
);

-- 9. 母大腦 A10 ↔ A13 ↔ A14 農糧資材雙輪食安網實體表 (a00_crop_fertilizer_safety_mesh)
CREATE TABLE IF NOT EXISTS a00_crop_fertilizer_safety_mesh (
    mesh_id INTEGER PRIMARY KEY AUTOINCREMENT,
    crop_id TEXT NOT NULL,                -- 作物代號 (A10)
    crop_name TEXT NOT NULL,              -- 作物名稱
    fertilizer_lic_id TEXT NOT NULL,      -- 肥料登記證字號 (A14)
    brand_name TEXT NOT NULL,             -- 廠牌資材名稱
    manufacturer_name TEXT NOT NULL,      -- 製造業者
    is_organic_certified INTEGER DEFAULT 0, -- 是否合規有機資材 (1=有機合格, 0=一般)
    compliance_status TEXT NOT NULL,      -- 'ORGANIC_COMPLIANT', 'CONVENTIONAL_ONLY'
    attributes_json TEXT NOT NULL DEFAULT '{"_v":"1.0.0"}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(crop_id, fertilizer_lic_id)
);
-- 10. 母大腦 1-Hop GraphRAG 實體圖譜表
CREATE TABLE IF NOT EXISTS a00_graph_triples (
    triple_id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_uri TEXT NOT NULL,
    predicate TEXT NOT NULL,           -- 'is_a', 'broader', 'has_pesticide', 'has_mrl', 'has_climate_obs'
    object_uri TEXT NOT NULL,
    domain_code TEXT NOT NULL,         -- A10, A11, A12, A20, A30, A40, A50
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE VIRTUAL TABLE IF NOT EXISTS fts_agro_global USING fts5(
    domain_code UNINDEXED,   -- 'A10', 'A11', 'A20', 'A30'
    entity_id UNINDEXED,     -- crop_id / pesticide_lic_id
    primary_name,            -- crop_name (如 '椰子')
    secondary_name,          -- market_name / category_name
    detail_payload UNINDEXED, -- JSON 格式快照
    tokenize='unicode61'
);

-- 母大腦延伸分析實體表: 全台農產跨市場價格離散指數
CREATE TABLE IF NOT EXISTS a00_master_cross_market_index (
    trans_date TEXT NOT NULL,         -- YYYY-MM-DD
    crop_id TEXT NOT NULL,            -- 作物主碼 (外鍵連至 A10)
    crop_name TEXT NOT NULL,          -- 作物中文名稱
    market_count INTEGER NOT NULL,    -- 參與交易之批發市場總數
    national_avg_price REAL NOT NULL, -- 全台加權平均價 (元/kg)
    national_total_volume REAL NOT NULL, -- 全台總交易量 (kg)
    min_price_market TEXT NOT NULL,   -- 全台最低價市場
    max_price_market TEXT NOT NULL,   -- 全台最高價市場
    price_cv REAL NOT NULL,           -- 價格離散係數 (CV = std_dev / mean)
    attributes_json TEXT NOT NULL DEFAULT '{"_v":"1.0.0"}',
    PRIMARY KEY (trans_date, crop_id)
);

CREATE INDEX IF NOT EXISTS idx_a00_cross_date_crop ON a00_master_cross_market_index(trans_date, crop_id);
