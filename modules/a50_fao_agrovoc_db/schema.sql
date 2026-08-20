-- 🌐 A50 fao_agrovoc_db Schema Definition

-- 1. 核心概念表 (Concept URI)
CREATE TABLE IF NOT EXISTS a50_agrovoc_concepts (
    concept_uri TEXT PRIMARY KEY,    -- 國際標準 URI (如 http://aims.fao.org/aos/agrovoc/c_1784)
    concept_id TEXT NOT NULL,        -- 概念 ID (如 c_1784)
    attributes_json TEXT NOT NULL DEFAULT '{"_v":"1.0.0"}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 多語言詞彙標籤表 (Multilingual Labels)
CREATE TABLE IF NOT EXISTS a50_agrovoc_labels (
    label_id INTEGER PRIMARY KEY AUTOINCREMENT,
    concept_uri TEXT NOT NULL,
    lang_code TEXT NOT NULL,         -- 'en', 'zh-TW', 'zh-CN' (預留其他語系擴充)
    label_text TEXT NOT NULL,        -- 詞條 (如 "椰子", "Coconut")
    label_type TEXT DEFAULT 'prefLabel', -- 'prefLabel' (首選) 或 'altLabel' (同義詞)
    FOREIGN KEY(concept_uri) REFERENCES a50_agrovoc_concepts(concept_uri)
);

-- 3. 本體圖譜階層關係表 (SKOS Hierarchy)
CREATE TABLE IF NOT EXISTS a50_agrovoc_hierarchy (
    subject_uri TEXT NOT NULL,
    predicate TEXT NOT NULL,         -- 'broader' 或 'narrower'
    object_uri TEXT NOT NULL,
    PRIMARY KEY (subject_uri, predicate, object_uri)
);

-- 4. 全文檢索倒排表
CREATE VIRTUAL TABLE IF NOT EXISTS a50_agrovoc_fts USING fts5(
    concept_uri,
    lang_code,
    label_text,
    tokenize='unicode61'
);

-- 5. 母大腦語意連網視圖
CREATE VIEW IF NOT EXISTS v_a50_agrovoc_semantic AS
SELECT 
    'A50' AS domain_code,
    c.concept_uri,
    c.concept_id,
    l.lang_code,
    l.label_text,
    l.label_type
FROM a50_agrovoc_concepts c
JOIN a50_agrovoc_labels l ON c.concept_uri = l.concept_uri;
