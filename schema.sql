-- ==============================================================================
-- tw-agro-db (台灣農業開放大數據引擎) 大一統全庫 Schema 與 DDL 定義檔 (自動生成)
-- 生成腳本: scripts/generate_schema_sql.py
-- 備註來源: src/config/schema_comments.json
-- ==============================================================================

CREATE INDEX idx_a00_cross_date_crop ON a00_master_cross_market_index(trans_date, crop_id);

CREATE INDEX idx_a10_crop_cat ON a10_crop_dictionary(category_code);

CREATE INDEX idx_a10_crop_name ON a10_crop_dictionary(crop_name);

CREATE INDEX idx_a10_trans_date_crop ON a10_crop_trans_daily(trans_date, crop_id);

CREATE INDEX idx_a10_trans_market ON a10_crop_trans_daily(market_id);

CREATE TABLE a00_agrovoc_cross_domain_mesh (
    concept_uri TEXT NOT NULL,         -- FAO AGROVOC URI (如 http://aims.fao.org/aos/agrovoc/c_1784)
    concept_id TEXT NOT NULL,          -- 概念 ID (如 c_1784)
    domain_code TEXT NOT NULL,         -- A10, A11, A20, A30, A40
    local_entity_id TEXT NOT NULL,      -- 本地主鍵
    local_entity_name TEXT NOT NULL,    -- 本地名稱 (如 '椰子', '益達胺', '毛豬')
    semantic_match_score REAL DEFAULT 1.0, -- 1.0 = EXACT_PREF_LABEL, 0.8 = ALT_LABEL
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (concept_uri, domain_code, local_entity_id)
);

CREATE TABLE a00_crop_pesticide_safety_mesh (
            crop_id TEXT NOT NULL,            -- 作物主碼 (A10)
            crop_name TEXT NOT NULL,          -- 作物名稱
            pesticide_lic_id TEXT NOT NULL,   -- 農藥許可證號 (A11)
            pesticide_name TEXT NOT NULL,     -- 農藥名稱
            dilution_ratio TEXT,              -- 推薦稀釋倍數
            safety_period_days INTEGER,       -- 安全採收停藥期 (天數)
            mrl_ppm REAL,                     -- MRL 容許量 (ppm, A12)
            risk_level TEXT DEFAULT 'SAFE',   -- SAFE, CAUTION, HIGH_RISK
            attributes_json TEXT NOT NULL DEFAULT '{"_v":"1.0.0"}',
            PRIMARY KEY (crop_id, pesticide_lic_id)
        );

-- ------------------------------------------------------------------------------
-- a00_graph_triples (A00 GraphRAG 實體圖譜三元組主表)
-- ------------------------------------------------------------------------------
CREATE TABLE a00_graph_triples (
    triple_id INTEGER PRIMARY KEY AUTOINCREMENT  -- 三元組主鍵 (自增),
    subject_uri TEXT NOT NULL  -- 主體 URI/名稱,
    predicate TEXT NOT NULL,           -- 'is_a', 'broader', 'has_pesticide', 'has_mrl', 'has_climate_obs'  -- 關係 Predicate
    object_uri TEXT NOT NULL  -- 物體 URI/名稱,
    domain_code TEXT NOT NULL,         -- A10, A11, A12, A20, A30, A40, A50
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- 紀錄建立時間戳記
);

CREATE TABLE a00_master_cross_market_index (
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

CREATE TABLE a00_regional_environmental_safety_mesh (
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

CREATE TABLE a10_crop_dictionary (
    crop_id TEXT PRIMARY KEY,
    crop_name TEXT NOT NULL,
    category_code TEXT NOT NULL,
    category_name TEXT NOT NULL,
    aliases_json TEXT DEFAULT '[]',
    attributes_json TEXT NOT NULL DEFAULT '{"_v":"1.0.0"}'
);

CREATE VIRTUAL TABLE a10_crop_fts USING fts5(
    crop_id UNINDEXED,
    crop_name,
    market_name,
    category_name,
    tokenize='unicode61'
);

CREATE TABLE 'a10_crop_fts_config'(k PRIMARY KEY, v) WITHOUT ROWID;

CREATE TABLE 'a10_crop_fts_content'(id INTEGER PRIMARY KEY, c0, c1, c2, c3);

CREATE TABLE 'a10_crop_fts_data'(id INTEGER PRIMARY KEY, block BLOB);

CREATE TABLE 'a10_crop_fts_docsize'(id INTEGER PRIMARY KEY, sz BLOB);

CREATE TABLE 'a10_crop_fts_idx'(segid, term, pgno, PRIMARY KEY(segid, term)) WITHOUT ROWID;

CREATE TABLE a10_crop_trans_daily (
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

CREATE VIRTUAL TABLE a11_pesticide_fts USING fts5(
    pesticide_lic_id UNINDEXED,
    pesticide_name,
    pesticide_en_name,
    brand_name,
    vendor_name,
    tokenize='unicode61'
);

CREATE TABLE 'a11_pesticide_fts_config'(k PRIMARY KEY, v) WITHOUT ROWID;

CREATE TABLE 'a11_pesticide_fts_content'(id INTEGER PRIMARY KEY, c0, c1, c2, c3, c4);

CREATE TABLE 'a11_pesticide_fts_data'(id INTEGER PRIMARY KEY, block BLOB);

CREATE TABLE 'a11_pesticide_fts_docsize'(id INTEGER PRIMARY KEY, sz BLOB);

CREATE TABLE 'a11_pesticide_fts_idx'(segid, term, pgno, PRIMARY KEY(segid, term)) WITHOUT ROWID;

-- ------------------------------------------------------------------------------
-- a11_pesticide_licenses (A11 農藥許可證與安全採收期主表)
-- ------------------------------------------------------------------------------
CREATE TABLE a11_pesticide_licenses (
    pesticide_lic_id TEXT PRIMARY KEY, -- 許可證字號 (如 農藥進00001)  -- 許可證字號 (主鍵, 如 農藥製字第00123號)
    lic_type TEXT NOT NULL,           -- 許可證字 (農藥進 / 農藥製)
    lic_no TEXT NOT NULL,             -- 許可證號
    pesticide_name TEXT,              -- 中文名稱  -- 農藥中文名稱 (含 Unicode 特殊字元如 滅)
    pesticide_en_name TEXT,           -- 英文名稱  -- 農藥英文名稱
    brand_name TEXT,                  -- 廠牌名稱 (如 滅)  -- 廠牌商品名稱
    pesticide_code TEXT,              -- 農藥代號
    formulation TEXT,                 -- 劑型 (如 EC, WP)
    active_ingredient_pct TEXT,       -- 含量
    manufacturer TEXT,                -- 國內/外原製造廠商
    vendor_name TEXT,                 -- 申請廠商名稱  -- 廠商/代理商名稱
    expire_date TEXT,                 -- 有效期限 (ISO 8601 YYYY-MM-DD)
    revoke_type TEXT,                 -- 撤銷/廢止類別 (如 逾期廢止)
    revoke_date TEXT,                 -- 撤銷日期
    detail_url TEXT,                  -- 農藥使用範圍連結
    attributes_json TEXT NOT NULL DEFAULT '{"_v":"1.0.0"}'  -- JSON 擴充欄位 (含 PHI 採收等待期天數),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- 紀錄建立時間戳記
);

CREATE TABLE a11_prohibited_pesticides (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pesticide_name TEXT NOT NULL,     -- 農藥名稱 (如 安特靈)
    pesticide_en_name TEXT,           -- 英文名稱
    prohibited_mfg_import_date TEXT,  -- 禁止製造/輸入日期 (ISO 8601)
    prohibited_sale_use_date TEXT,    -- 禁止銷售/使用日期 (ISO 8601)
    attributes_json TEXT NOT NULL DEFAULT '{"_v":"1.0.0"}'
);

CREATE VIRTUAL TABLE a12_mrl_fts USING fts5(
    record_id UNINDEXED,
    sample_name,
    vendor_name,
    inspection_agency,
    test_result,
    tokenize='unicode61'
);

CREATE TABLE 'a12_mrl_fts_config'(k PRIMARY KEY, v) WITHOUT ROWID;

CREATE TABLE 'a12_mrl_fts_content'(id INTEGER PRIMARY KEY, c0, c1, c2, c3, c4);

CREATE TABLE 'a12_mrl_fts_data'(id INTEGER PRIMARY KEY, block BLOB);

CREATE TABLE 'a12_mrl_fts_docsize'(id INTEGER PRIMARY KEY, sz BLOB);

CREATE TABLE 'a12_mrl_fts_idx'(segid, term, pgno, PRIMARY KEY(segid, term)) WITHOUT ROWID;

CREATE TABLE a12_mrl_inspection_records (
    record_id INTEGER PRIMARY KEY AUTOINCREMENT,
    period_year_month TEXT NOT NULL,  -- 年度月份 (如 110年1-12月)
    inspection_agency TEXT NOT NULL,  -- 抽樣衛生局 (如 基隆市)
    sample_name TEXT NOT NULL,        -- 檢體名稱 (如 好呷雞, 椰子)
    vendor_name TEXT,                 -- 抽樣廠商名稱 (如 全聯福利中心義二店)
    vendor_address TEXT,              -- 抽樣廠商地址
    test_result TEXT NOT NULL,        -- 檢出項目及殘留容許量 (如 合格, 超標)
    is_compliant INTEGER DEFAULT 1,   -- 是否合格 (1: 合格, 0: 違規)
    attributes_json TEXT NOT NULL DEFAULT '{"_v":"1.0.0"}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE a12_pesticide_mrl_limits (
    crop_name TEXT NOT NULL,          -- 作物名稱
    pesticide_name TEXT NOT NULL,     -- 農藥化學成分
    mrl_ppm REAL NOT NULL,            -- 最大殘留容許量 (ppm)
    attributes_json TEXT NOT NULL DEFAULT '{"_v":"1.0.0"}',
    PRIMARY KEY (crop_name, pesticide_name)
);

CREATE VIRTUAL TABLE a13_organic_fts USING fts5(
    registry_id UNINDEXED,
    material_name,
    category_type,
    period_year,
    tokenize='unicode61'
);

CREATE TABLE 'a13_organic_fts_config'(k PRIMARY KEY, v) WITHOUT ROWID;

CREATE TABLE 'a13_organic_fts_content'(id INTEGER PRIMARY KEY, c0, c1, c2, c3);

CREATE TABLE 'a13_organic_fts_data'(id INTEGER PRIMARY KEY, block BLOB);

CREATE TABLE 'a13_organic_fts_docsize'(id INTEGER PRIMARY KEY, sz BLOB);

CREATE TABLE 'a13_organic_fts_idx'(segid, term, pgno, PRIMARY KEY(segid, term)) WITHOUT ROWID;

CREATE TABLE a13_organic_materials_registry (
    registry_id INTEGER PRIMARY KEY AUTOINCREMENT,
    period_year TEXT NOT NULL,         -- 年度 (如 2025)
    material_name TEXT NOT NULL,       -- 肥料別 / 資材名稱 (如 硫酸銨, 尿素)
    category_type TEXT NOT NULL,       -- 產銷類別 (如 進口, 國產)
    quantity_tons REAL DEFAULT 0.0,    -- 數量 (公噸)
    value_thousand_ntd REAL DEFAULT 0, -- 價值 (千元)
    attributes_json TEXT NOT NULL DEFAULT '{"_v":"1.0.0"}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE VIRTUAL TABLE a14_fertilizer_fts USING fts5(
    fertilizer_lic_id,
    brand_name,
    manufacturer_name,
    fertilizer_type,
    tokenize='unicode61'
);

CREATE TABLE 'a14_fertilizer_fts_config'(k PRIMARY KEY, v) WITHOUT ROWID;

CREATE TABLE 'a14_fertilizer_fts_content'(id INTEGER PRIMARY KEY, c0, c1, c2, c3);

CREATE TABLE 'a14_fertilizer_fts_data'(id INTEGER PRIMARY KEY, block BLOB);

CREATE TABLE 'a14_fertilizer_fts_docsize'(id INTEGER PRIMARY KEY, sz BLOB);

CREATE TABLE 'a14_fertilizer_fts_idx'(segid, term, pgno, PRIMARY KEY(segid, term)) WITHOUT ROWID;

-- ------------------------------------------------------------------------------
-- a14_fertilizer_licenses (A14 農糧資材與肥料登記證主表)
-- ------------------------------------------------------------------------------
CREATE TABLE a14_fertilizer_licenses (
    fertilizer_lic_id TEXT PRIMARY KEY,  -- 肥料登記證字號 (如 肥製(質)字第0001234號)  -- 肥料登記證字號 (主鍵, 如 肥製(質)字第0001001號)
    brand_name TEXT NOT NULL,           -- 廠牌商品名稱 (如 金綠滿有機肥)  -- 廠牌商品名稱
    manufacturer_name TEXT NOT NULL,    -- 業者/製造廠名稱 (如 豐綠生物科技)  -- 製造廠/業者名稱
    fertilizer_type TEXT NOT NULL,      -- 肥料品目類別 (如 5-01 有機質肥料)  -- 肥料品目類別
    nitrogen_pct REAL DEFAULT 0.0,      -- 全氮含量 (%)  -- 全氮含量 (%)
    phosphorus_pct REAL DEFAULT 0.0,    -- 全磷酸含量 (%)  -- 全磷酸含量 (%)
    potassium_pct REAL DEFAULT 0.0,     -- 全氧化鉀含量 (%)  -- 全氧化鉀含量 (%)
    is_organic_cert INTEGER DEFAULT 0,  -- 有機資材審定旗標 (1=審定合格, 0=一般)  -- 有機審定旗標 (1=審定合格/ORGANIC_APPROVED, 0=一般)
    expire_date TEXT,                   -- 有效期限 (如 2028-12-31)  -- 有效期限
    attributes_json TEXT NOT NULL DEFAULT '{"_v":"1.0.0"}'  -- JSON 擴充欄位 (含 NPK_Total 總和),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- 紀錄建立時間戳記
);

CREATE VIRTUAL TABLE a20_fishery_fts USING fts5(
    product_id UNINDEXED,
    product_name,
    origin_location,
    tokenize='unicode61'
);

CREATE TABLE 'a20_fishery_fts_config'(k PRIMARY KEY, v) WITHOUT ROWID;

CREATE TABLE 'a20_fishery_fts_content'(id INTEGER PRIMARY KEY, c0, c1, c2);

CREATE TABLE 'a20_fishery_fts_data'(id INTEGER PRIMARY KEY, block BLOB);

CREATE TABLE 'a20_fishery_fts_docsize'(id INTEGER PRIMARY KEY, sz BLOB);

CREATE TABLE 'a20_fishery_fts_idx'(segid, term, pgno, PRIMARY KEY(segid, term)) WITHOUT ROWID;

-- ------------------------------------------------------------------------------
-- a20_fishery_products (A20 水產產品名冊與行情主表)
-- ------------------------------------------------------------------------------
CREATE TABLE a20_fishery_products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT  -- 水產品紀錄主鍵 (自增),
    product_name TEXT NOT NULL,       -- 水產品名稱 (如 秋刀魚, 透抽(大))  -- 水產品名稱
    origin_location TEXT,             -- 來源產地 (如 北太平洋海域, 臺灣, 宜蘭)  -- 來源產地
    weight_spec TEXT,                 -- 產品重量規格 (如 500g, 300g/包)  -- 重量規格
    storage_method TEXT,              -- 保存方式 (如 零下-18℃以下保存)  -- 保存方式
    attributes_json TEXT NOT NULL DEFAULT '{"_v":"1.0.0"}'  -- JSON 擴充欄位 (含 80% 臺灣在地標籤),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- 紀錄建立時間戳記
);

CREATE VIRTUAL TABLE a21_aquaculture_fts USING fts5(
    farm_id,
    county_name,
    town_name,
    aquaculture_species,
    tokenize='unicode61'
);

CREATE TABLE 'a21_aquaculture_fts_config'(k PRIMARY KEY, v) WITHOUT ROWID;

CREATE TABLE 'a21_aquaculture_fts_content'(id INTEGER PRIMARY KEY, c0, c1, c2, c3);

CREATE TABLE 'a21_aquaculture_fts_data'(id INTEGER PRIMARY KEY, block BLOB);

CREATE TABLE 'a21_aquaculture_fts_docsize'(id INTEGER PRIMARY KEY, sz BLOB);

CREATE TABLE 'a21_aquaculture_fts_idx'(segid, term, pgno, PRIMARY KEY(segid, term)) WITHOUT ROWID;

-- ------------------------------------------------------------------------------
-- a21_aquaculture_monitoring (A21 水產養殖水質與寒害監測主表)
-- ------------------------------------------------------------------------------
CREATE TABLE a21_aquaculture_monitoring (
    farm_id TEXT PRIMARY KEY,           -- 養殖場/魚塭代號 (如 TW_AQUA_201)
    county_name TEXT NOT NULL,          -- 縣市 (如 屏東縣)  -- 縣市名稱
    town_name TEXT NOT NULL,            -- 鄉鎮市區 (如 佳冬鄉)  -- 鄉鎮名稱
    aquaculture_species TEXT NOT NULL,  -- 養殖物種 (如 石斑魚, 虱目魚, 泰國蝦)
    obs_time TEXT NOT NULL,             -- 觀測時間 (如 2025-01-15 06:00:00)
    water_temp_c REAL NOT NULL,         -- 水溫 (°C)  -- 水溫 (°C)
    dissolved_oxygen_mg_l REAL NOT NULL,-- 溶氧量 (mg/L)  -- 溶氧量 (mg/L)
    salinity_ppt REAL DEFAULT 30.0,     -- 鹽度 (ppt)
    ph_value REAL DEFAULT 7.8,          -- pH 值  -- pH 值
    risk_level TEXT NOT NULL,           -- 'SAFE', 'WARNING', 'HIGH_RISK'
    attributes_json TEXT NOT NULL DEFAULT '{"_v":"1.0.0"}'  -- JSON 擴充欄位,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- 紀錄建立時間戳記
);

CREATE VIRTUAL TABLE a30_pork_fts USING fts5(
    trans_date UNINDEXED,
    market_name,
    tokenize='unicode61'
);

CREATE TABLE 'a30_pork_fts_config'(k PRIMARY KEY, v) WITHOUT ROWID;

CREATE TABLE 'a30_pork_fts_content'(id INTEGER PRIMARY KEY, c0, c1);

CREATE TABLE 'a30_pork_fts_data'(id INTEGER PRIMARY KEY, block BLOB);

CREATE TABLE 'a30_pork_fts_docsize'(id INTEGER PRIMARY KEY, sz BLOB);

CREATE TABLE 'a30_pork_fts_idx'(segid, term, pgno, PRIMARY KEY(segid, term)) WITHOUT ROWID;

-- ------------------------------------------------------------------------------
-- a30_pork_trans_daily (A30 毛豬批發拍賣每日行情主表)
-- ------------------------------------------------------------------------------
CREATE TABLE a30_pork_trans_daily (
    trans_date TEXT NOT NULL,         -- 交易日期 ISO 8601 (YYYY-MM-DD)  -- 交易日期 (ISO 8601: YYYY-MM-DD)
    market_name TEXT NOT NULL,        -- 肉品市場名稱 (如 花蓮縣, 彰化縣)  -- 市場名稱 (如 花蓮縣)
    total_heads INTEGER DEFAULT 0,    -- 成交頭數-總數  -- 總拍賣頭數 (頭)
    avg_weight_kg REAL DEFAULT 0.0,   -- 成交頭數-平均重量 (kg)  -- 平均成交重量 (公斤)
    avg_price_ntd REAL DEFAULT 0.0,   -- 成交頭數-平均價格 (元/kg)  -- 平均成交價格 (新台幣元/公斤)
    spec_heads INTEGER DEFAULT 0,     -- 規格豬-頭數
    spec_weight_kg REAL DEFAULT 0.0,  -- 規格豬-平均重量
    spec_price_ntd REAL DEFAULT 0.0,  -- 規格豬-平均價格
    attributes_json TEXT NOT NULL DEFAULT '{"_v":"1.0.0"}'  -- JSON 擴充欄位 (含無槓民國年原始日期),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- 紀錄建立時間戳記,
    PRIMARY KEY (trans_date, market_name)
);

CREATE VIRTUAL TABLE a31_vet_drug_fts USING fts5(
    drug_name,
    target_livestock,
    tokenize='unicode61'
);

CREATE TABLE 'a31_vet_drug_fts_config'(k PRIMARY KEY, v) WITHOUT ROWID;

CREATE TABLE 'a31_vet_drug_fts_content'(id INTEGER PRIMARY KEY, c0, c1);

CREATE TABLE 'a31_vet_drug_fts_data'(id INTEGER PRIMARY KEY, block BLOB);

CREATE TABLE 'a31_vet_drug_fts_docsize'(id INTEGER PRIMARY KEY, sz BLOB);

CREATE TABLE 'a31_vet_drug_fts_idx'(segid, term, pgno, PRIMARY KEY(segid, term)) WITHOUT ROWID;

-- ------------------------------------------------------------------------------
-- a31_vet_drug_residue (A31 動物用藥殘留管制主表)
-- ------------------------------------------------------------------------------
CREATE TABLE a31_vet_drug_residue (
    residue_id INTEGER PRIMARY KEY AUTOINCREMENT  -- 殘留標準主鍵 (自增),
    drug_name TEXT NOT NULL,           -- 用藥名稱 (如 氯黴素, 萊克多巴胺, 恩氟沙星)  -- 動物用藥名稱 (如 氯黴素)
    target_livestock TEXT NOT NULL,    -- 適用畜產品/部位 (如 豬肉, 豬肝, 家禽肉)  -- 適用畜產品/部位
    mrl_ppm REAL NOT NULL,              -- 殘留容許標準 (ppm) (0.0 表示不得檢出)  -- 殘留容許量上限 (0.0 表示國定禁藥)
    withdrawal_period_days INTEGER DEFAULT 7, -- 停藥期 (天)  -- 停藥期 (天)
    is_prohibited INTEGER DEFAULT 0,    -- 禁用用藥旗標 (1=禁用, 0=核准)  -- 禁藥旗標 (1=PROHIBITED, 0=一般)
    attributes_json TEXT NOT NULL DEFAULT '{"_v":"1.0.0"}'  -- JSON 擴充欄位,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- 紀錄建立時間戳記,
    UNIQUE(drug_name, target_livestock)
);

CREATE TABLE a40_climate_daily_obs (
    station_sn TEXT NOT NULL,         -- 測站流水號 (如 100213)
    obs_date TEXT NOT NULL,           -- 觀測日期 (ISO 8601 YYYY-MM-DD)
    obs_count INTEGER DEFAULT 0,      -- 觀測筆數 (如 96 筆)
    download_url TEXT,                -- CSV 資料下載連結
    attributes_json TEXT NOT NULL DEFAULT '{"_v":"1.0.0"}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (station_sn, obs_date)
);

CREATE VIRTUAL TABLE a40_climate_fts USING fts5(
    station_sn,
    obs_date,
    tokenize='unicode61'
);

CREATE TABLE 'a40_climate_fts_config'(k PRIMARY KEY, v) WITHOUT ROWID;

CREATE TABLE 'a40_climate_fts_content'(id INTEGER PRIMARY KEY, c0, c1);

CREATE TABLE 'a40_climate_fts_data'(id INTEGER PRIMARY KEY, block BLOB);

CREATE TABLE 'a40_climate_fts_docsize'(id INTEGER PRIMARY KEY, sz BLOB);

CREATE TABLE 'a40_climate_fts_idx'(segid, term, pgno, PRIMARY KEY(segid, term)) WITHOUT ROWID;

CREATE VIRTUAL TABLE a41_soil_water_fts USING fts5(
    site_id,
    county_name,
    town_name,
    pollutant_type,
    tokenize='unicode61'
);

CREATE TABLE 'a41_soil_water_fts_config'(k PRIMARY KEY, v) WITHOUT ROWID;

CREATE TABLE 'a41_soil_water_fts_content'(id INTEGER PRIMARY KEY, c0, c1, c2, c3);

CREATE TABLE 'a41_soil_water_fts_data'(id INTEGER PRIMARY KEY, block BLOB);

CREATE TABLE 'a41_soil_water_fts_docsize'(id INTEGER PRIMARY KEY, sz BLOB);

CREATE TABLE 'a41_soil_water_fts_idx'(segid, term, pgno, PRIMARY KEY(segid, term)) WITHOUT ROWID;

CREATE TABLE a41_soil_water_monitoring (
    site_id TEXT PRIMARY KEY,          -- 監測點代號 (如 TW_SOIL_101)
    county_name TEXT NOT NULL,         -- 縣市 (如 彰化縣)
    town_name TEXT NOT NULL,           -- 鄉鎮市區 (如 和美鎮)
    sample_date TEXT NOT NULL,         -- 採樣日期 (如 2025-05-10)
    pollutant_type TEXT NOT NULL,      -- 檢驗項目 (如 鎘 Cd, 砷 As, 鉛 Pb)
    concentration_ppm REAL NOT NULL,   -- 實測濃度 (ppm)
    regulatory_limit_ppm REAL NOT NULL,-- 管制標準值 (ppm)
    is_polluted INTEGER DEFAULT 0,     -- 超標旗標 (1=超標/管制, 0=正常)
    attributes_json TEXT NOT NULL DEFAULT '{"_v":"1.0.0"}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------------------------
-- a50_agrovoc_concepts (A50 FAO AGROVOC 國際農學詞庫概念主表)
-- ------------------------------------------------------------------------------
CREATE TABLE a50_agrovoc_concepts (
    concept_uri TEXT PRIMARY KEY,    -- 國際標準 URI (如 http://aims.fao.org/aos/agrovoc/c_1784)  -- 國際概念 URI (主鍵)
    concept_id TEXT NOT NULL,        -- 概念 ID (如 c_1784)
    attributes_json TEXT NOT NULL DEFAULT '{"_v":"1.0.0"}'  -- JSON 擴充欄位,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- 紀錄建立時間戳記
);

CREATE VIRTUAL TABLE a50_agrovoc_fts USING fts5(
    concept_uri,
    lang_code,
    label_text,
    tokenize='unicode61'
);

CREATE TABLE 'a50_agrovoc_fts_config'(k PRIMARY KEY, v) WITHOUT ROWID;

CREATE TABLE 'a50_agrovoc_fts_content'(id INTEGER PRIMARY KEY, c0, c1, c2);

CREATE TABLE 'a50_agrovoc_fts_data'(id INTEGER PRIMARY KEY, block BLOB);

CREATE TABLE 'a50_agrovoc_fts_docsize'(id INTEGER PRIMARY KEY, sz BLOB);

CREATE TABLE 'a50_agrovoc_fts_idx'(segid, term, pgno, PRIMARY KEY(segid, term)) WITHOUT ROWID;

CREATE TABLE a50_agrovoc_hierarchy (
    subject_uri TEXT NOT NULL,
    predicate TEXT NOT NULL,         -- 'broader' 或 'narrower'
    object_uri TEXT NOT NULL,
    PRIMARY KEY (subject_uri, predicate, object_uri)
);

CREATE TABLE a50_agrovoc_labels (
    label_id INTEGER PRIMARY KEY AUTOINCREMENT,
    concept_uri TEXT NOT NULL,
    lang_code TEXT NOT NULL,         -- 'en', 'zh-TW', 'zh-CN' (預留其他語系擴充)
    label_text TEXT NOT NULL,        -- 詞條 (如 "椰子", "Coconut")
    label_type TEXT DEFAULT 'prefLabel', -- 'prefLabel' (首選) 或 'altLabel' (同義詞)
    FOREIGN KEY(concept_uri) REFERENCES a50_agrovoc_concepts(concept_uri)
);

CREATE VIRTUAL TABLE fts_agro_global USING fts5(
            domain_code UNINDEXED,
            entity_id UNINDEXED,
            primary_name,
            secondary_name,
            detail_payload UNINDEXED,
            tokenize='unicode61'
        );

CREATE TABLE 'fts_agro_global_config'(k PRIMARY KEY, v) WITHOUT ROWID;

CREATE TABLE 'fts_agro_global_content'(id INTEGER PRIMARY KEY, c0, c1, c2, c3, c4);

CREATE TABLE 'fts_agro_global_data'(id INTEGER PRIMARY KEY, block BLOB);

CREATE TABLE 'fts_agro_global_docsize'(id INTEGER PRIMARY KEY, sz BLOB);

CREATE TABLE 'fts_agro_global_idx'(segid, term, pgno, PRIMARY KEY(segid, term)) WITHOUT ROWID;

CREATE TABLE sys_module_metadata (
            module_id TEXT PRIMARY KEY,
            module_name TEXT NOT NULL,
            table_name TEXT NOT NULL,
            record_count INTEGER DEFAULT 0,
            schema_version TEXT DEFAULT '1.0.0',
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

CREATE VIEW v_a10_crop_market_summary AS
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

CREATE VIEW v_a11_pesticide_safety AS
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

CREATE VIEW v_a12_pest_mrl AS
SELECT 
    'A12' AS domain_code,
    record_id,
    period_year_month,
    inspection_agency,
    sample_name,
    vendor_name,
    test_result,
    is_compliant
FROM a12_mrl_inspection_records;

CREATE VIEW v_a13_organic_cert AS
SELECT 
    'A13' AS domain_code,
    registry_id,
    period_year,
    material_name,
    category_type,
    quantity_tons,
    value_thousand_ntd
FROM a13_organic_materials_registry;

CREATE VIEW v_a14_fertilizer AS
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

CREATE VIEW v_a20_fishery_product AS
SELECT 
    'A20' AS domain_code,
    product_id,
    product_name,
    origin_location,
    weight_spec,
    storage_method
FROM a20_fishery_products;

CREATE VIEW v_a21_aquaculture AS
SELECT 
    'A21' AS domain_code,
    farm_id,
    county_name,
    town_name,
    aquaculture_species,
    obs_time,
    water_temp_c,
    dissolved_oxygen_mg_l,
    salinity_ppt,
    risk_level
FROM a21_aquaculture_monitoring;

CREATE VIEW v_a30_livestock_pork AS
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

CREATE VIEW v_a31_vet_drug AS
SELECT 
    'A31' AS domain_code,
    residue_id,
    drug_name,
    target_livestock,
    mrl_ppm,
    withdrawal_period_days,
    is_prohibited
FROM a31_vet_drug_residue;

CREATE VIEW v_a40_agro_climate AS
SELECT 
    'A40' AS domain_code,
    station_sn,
    obs_date,
    obs_count,
    download_url
FROM a40_climate_daily_obs;

CREATE VIEW v_a41_soil_water AS
SELECT 
    'A41' AS domain_code,
    site_id,
    county_name,
    town_name,
    sample_date,
    pollutant_type,
    concentration_ppm,
    regulatory_limit_ppm,
    is_polluted
FROM a41_soil_water_monitoring;

CREATE VIEW v_a50_agrovoc_semantic AS
SELECT 
    'A50' AS domain_code,
    c.concept_uri,
    c.concept_id,
    l.lang_code,
    l.label_text,
    l.label_type
FROM a50_agrovoc_concepts c
JOIN a50_agrovoc_labels l ON c.concept_uri = l.concept_uri;

CREATE VIEW v_master_agro_climate AS
        SELECT 
            'A40' AS domain_code,
            station_sn,
            obs_date,
            obs_count,
            download_url
        FROM a40_climate_daily_obs;

CREATE VIEW v_master_agrovoc_semantic AS
        SELECT 
            'A50' AS domain_code,
            c.concept_uri,
            c.concept_id,
            l.lang_code,
            l.label_text,
            l.label_type
        FROM a50_agrovoc_concepts c
        JOIN a50_agrovoc_labels l ON c.concept_uri = l.concept_uri;

CREATE VIEW v_master_crop_market AS
        SELECT 
            'A10' AS domain_code,
            trans_date,
            crop_id,
            crop_name,
            category_code,
            category_name,
            market_id,
            market_name,
            price_high,
            price_mid,
            price_low,
            price_avg,
            volume_kg,
            spread_pct,
            is_rest
        FROM v_a10_crop_market_summary;

CREATE VIEW v_master_fishery_product AS
        SELECT 
            'A20' AS domain_code,
            product_id,
            product_name,
            origin_location,
            weight_spec,
            storage_method
        FROM a20_fishery_products;

CREATE VIEW v_master_livestock_pork AS
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

CREATE VIEW v_master_organic_cert AS
        SELECT 
            'A13' AS domain_code,
            registry_id,
            period_year,
            material_name,
            category_type,
            quantity_tons,
            value_thousand_ntd
        FROM a13_organic_materials_registry;

CREATE VIEW v_master_pest_mrl AS
        SELECT 
            'A12' AS domain_code,
            record_id,
            period_year_month,
            inspection_agency,
            sample_name,
            vendor_name,
            test_result,
            is_compliant
        FROM a12_mrl_inspection_records;

CREATE VIEW v_master_pesticide_safety AS
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

CREATE VIEW v_master_soil_water AS
        SELECT 
            'A41' AS domain_code,
            site_id,
            county_name,
            town_name,
            sample_date,
            pollutant_type,
            concentration_ppm,
            regulatory_limit_ppm,
            is_polluted
        FROM a41_soil_water_monitoring;
