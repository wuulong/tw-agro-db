import sqlite3
import json
from pathlib import Path
from typing import Union, Dict, Any

def build_global_fts(db_path: Union[str, Path]) -> Dict[str, Any]:
    db_p = Path(db_path)
    if not db_p.exists():
        raise FileNotFoundError(f"DB 檔案不存在: {db_p}")
        
    conn = sqlite3.connect(str(db_p))
    cursor = conn.cursor()
    
    # 確保虛擬表存在
    cursor.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS fts_agro_global USING fts5(
            domain_code UNINDEXED,
            entity_id UNINDEXED,
            primary_name,
            secondary_name,
            detail_payload UNINDEXED,
            tokenize='unicode61'
        );
    """)
    
    cursor.execute("DELETE FROM fts_agro_global")
    
    # 輔助函式: 檢查 SQL 表或視圖是否存在
    def has_table(name: str) -> bool:
        cursor.execute("SELECT 1 FROM sqlite_master WHERE name = ?", (name,))
        return cursor.fetchone() is not None

    cnt_a10 = cnt_a11 = cnt_a12 = cnt_a13 = 0

    # 1. 寫入 A10 行情數據至全域倒排
    if has_table("v_master_crop_market") and has_table("a10_crop_dictionary"):
        cursor.execute("""
            INSERT INTO fts_agro_global (domain_code, entity_id, primary_name, secondary_name, detail_payload)
            SELECT 
                'A10',
                crop_id,
                crop_name,
                market_name || ' (' || category_name || ')',
                json_object('price_avg', price_avg, 'volume_kg', volume_kg, 'trans_date', trans_date)
            FROM v_master_crop_market
            WHERE is_rest = 0;
        """)
        cnt_a10 = cursor.rowcount
    
    # 2. 寫入 A11 農藥許可證至全域倒排
    if has_table("v_master_pesticide_safety") and has_table("a11_pesticide_licenses"):
        cursor.execute("""
            INSERT INTO fts_agro_global (domain_code, entity_id, primary_name, secondary_name, detail_payload)
            SELECT 
                'A11',
                pesticide_lic_id,
                pesticide_name,
                brand_name || ' (' || vendor_name || ')',
                json_object('formulation', formulation, 'expire_date', expire_date, 'revoke_type', revoke_type)
            FROM v_master_pesticide_safety;
        """)
        cnt_a11 = cursor.rowcount
    
    # 3. 寫入 A12 農藥殘留抽驗至全域倒排
    if has_table("v_master_pest_mrl") and has_table("a12_mrl_inspection_records"):
        cursor.execute("""
            INSERT INTO fts_agro_global (domain_code, entity_id, primary_name, secondary_name, detail_payload)
            SELECT 
                'A12',
                CAST(record_id AS TEXT),
                sample_name,
                vendor_name || ' (' || inspection_agency || ')',
                json_object('test_result', test_result, 'is_compliant', is_compliant, 'period', period_year_month)
            FROM v_master_pest_mrl;
        """)
        cnt_a12 = cursor.rowcount
    
    # 4. 寫入 A13 有機友善資材至全域倒排
    if has_table("v_master_organic_cert") and has_table("a13_organic_materials_registry"):
        cursor.execute("""
            INSERT INTO fts_agro_global (domain_code, entity_id, primary_name, secondary_name, detail_payload)
            SELECT 
                'A13',
                CAST(registry_id AS TEXT),
                material_name,
                category_type || ' (' || period_year || '年)',
                json_object('quantity_tons', quantity_tons, 'value_thousand_ntd', value_thousand_ntd)
            FROM v_master_organic_cert;
        """)
        cnt_a13 = cursor.rowcount
        
    # 5. 寫入 A20 水產品名冊至全域倒排
    cnt_a20 = 0
    if has_table("v_master_fishery_product") and has_table("a20_fishery_products"):
        cursor.execute("""
            INSERT INTO fts_agro_global (domain_code, entity_id, primary_name, secondary_name, detail_payload)
            SELECT 
                'A20',
                CAST(product_id AS TEXT),
                product_name,
                origin_location || ' (' || weight_spec || ')',
                json_object('storage_method', storage_method)
            FROM v_master_fishery_product;
        """)
        cnt_a20 = cursor.rowcount

    # 6. 寫入 A30 毛豬交易行情至全域倒排
    cnt_a30 = 0
    if has_table("v_master_livestock_pork") and has_table("a30_pork_trans_daily"):
        cursor.execute("""
            INSERT INTO fts_agro_global (domain_code, entity_id, primary_name, secondary_name, detail_payload)
            SELECT 
                'A30',
                trans_date || '_' || market_name,
                market_name,
                trans_date || ' (毛豬批發)',
                json_object('total_heads', total_heads, 'avg_price_ntd', avg_price_ntd, 'avg_weight_kg', avg_weight_kg)
            FROM v_master_livestock_pork;
        """)
        cnt_a30 = cursor.rowcount

    # 7. 寫入 A40 農業氣象觀測至全域倒排
    cnt_a40 = 0
    if has_table("v_master_agro_climate") and has_table("a40_climate_daily_obs"):
        cursor.execute("""
            INSERT INTO fts_agro_global (domain_code, entity_id, primary_name, secondary_name, detail_payload)
            SELECT 
                'A40',
                station_sn || '_' || obs_date,
                station_sn,
                obs_date || ' (農業氣象站)',
                json_object('obs_count', obs_count, 'download_url', download_url)
            FROM v_master_agro_climate;
        """)
        cnt_a40 = cursor.rowcount

    # 8. 寫入 A50 國際 AGROVOC 多語主題詞至全域倒排
    cnt_a50 = 0
    if has_table("v_master_agrovoc_semantic") and has_table("a50_agrovoc_labels"):
        cursor.execute("""
            INSERT INTO fts_agro_global (domain_code, entity_id, primary_name, secondary_name, detail_payload)
            SELECT 
                'A50',
                concept_id,
                label_text,
                lang_code || ' (' || label_type || ')',
                json_object('concept_uri', concept_uri)
            FROM v_master_agrovoc_semantic;
        """)
        cnt_a50 = cursor.rowcount
    
    # 9. 寫入 A41 農地土壤與水質監測至全域倒排
    cnt_a41 = 0
    if has_table("v_master_soil_water") and has_table("a41_soil_water_monitoring"):
        cursor.execute("""
            INSERT INTO fts_agro_global (domain_code, entity_id, primary_name, secondary_name, detail_payload)
            SELECT 
                'A41',
                site_id,
                county_name || town_name || ' (' || pollutant_type || ')',
                sample_date,
                json_object('concentration_ppm', concentration_ppm, 'regulatory_limit_ppm', regulatory_limit_ppm, 'is_polluted', is_polluted)
            FROM v_master_soil_water;
        """)
        cnt_a41 = cursor.rowcount
    
    # 10. 寫入 A21 水產養殖水質監測至全域倒排
    cnt_a21 = 0
    if has_table("v_master_aquaculture") and has_table("a21_aquaculture_monitoring"):
        cursor.execute("""
            INSERT INTO fts_agro_global (domain_code, entity_id, primary_name, secondary_name, detail_payload)
            SELECT 
                'A21',
                farm_id,
                county_name || town_name || ' (' || aquaculture_species || ')',
                obs_time,
                json_object('water_temp_c', water_temp_c, 'dissolved_oxygen_mg_l', dissolved_oxygen_mg_l, 'risk_level', risk_level)
            FROM v_master_aquaculture;
        """)
        cnt_a21 = cursor.rowcount
    
    # 11. 寫入 A31 動物用藥與畜產品殘留至全域倒排
    cnt_a31 = 0
    if has_table("v_master_vet_drug") and has_table("a31_vet_drug_residue"):
        cursor.execute("""
            INSERT INTO fts_agro_global (domain_code, entity_id, primary_name, secondary_name, detail_payload)
            SELECT 
                'A31',
                CAST(residue_id AS TEXT),
                drug_name || ' (' || target_livestock || ')',
                'MRL: ' || mrl_ppm || ' ppm',
                json_object('withdrawal_period_days', withdrawal_period_days, 'is_prohibited', is_prohibited)
            FROM v_master_vet_drug;
        """)
        cnt_a31 = cursor.rowcount
    
    # 12. 寫入 A14 農糧資材與肥料登記證至全域倒排
    cnt_a14 = 0
    if has_table("v_master_fertilizer") and has_table("a14_fertilizer_licenses"):
        cursor.execute("""
            INSERT INTO fts_agro_global (domain_code, entity_id, primary_name, secondary_name, detail_payload)
            SELECT 
                'A14',
                fertilizer_lic_id,
                brand_name || ' (' || manufacturer_name || ')',
                fertilizer_type,
                json_object('nitrogen_pct', nitrogen_pct, 'phosphorus_pct', phosphorus_pct, 'potassium_pct', potassium_pct, 'is_organic_cert', is_organic_cert)
            FROM v_master_fertilizer;
        """)
        cnt_a14 = cursor.rowcount
    
    cnt_total = cnt_a10 + cnt_a11 + cnt_a12 + cnt_a13 + cnt_a14 + cnt_a20 + cnt_a21 + cnt_a30 + cnt_a31 + cnt_a40 + cnt_a41 + cnt_a50
    conn.commit()
    conn.close()
    return {"indexed_records": cnt_total, "a10_cnt": cnt_a10, "a11_cnt": cnt_a11, "a12_cnt": cnt_a12, "a13_cnt": cnt_a13, "a14_cnt": cnt_a14, "a20_cnt": cnt_a20, "a21_cnt": cnt_a21, "a30_cnt": cnt_a30, "a31_cnt": cnt_a31, "a40_cnt": cnt_a40, "a41_cnt": cnt_a41, "a50_cnt": cnt_a50}
