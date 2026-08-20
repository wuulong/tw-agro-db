import sqlite3
from pathlib import Path
from typing import Union, Dict, Any

def inject_master_views(db_path: Union[str, Path]) -> Dict[str, Any]:
    db_p = Path(db_path)
    if not db_p.exists():
        raise FileNotFoundError(f"DB 檔案不存在: {db_p}")
        
    conn = sqlite3.connect(str(db_p))
    cursor = conn.cursor()
    
    # 建立 v_master_crop_market (連網 A10)
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS v_master_crop_market AS
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
    """)
    
    # 建立 v_master_pesticide_safety (連網 A11)
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS v_master_pesticide_safety AS
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
    """)
    
    # 建立 v_master_pest_mrl (連網 A12)
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS v_master_pest_mrl AS
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
    """)
    
    # 建立 v_master_organic_cert (連網 A13)
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS v_master_organic_cert AS
        SELECT 
            'A13' AS domain_code,
            registry_id,
            period_year,
            material_name,
            category_type,
            quantity_tons,
            value_thousand_ntd
        FROM a13_organic_materials_registry;
    """)
    
    # 建立 v_master_fishery_product (連網 A20)
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS v_master_fishery_product AS
        SELECT 
            'A20' AS domain_code,
            product_id,
            product_name,
            origin_location,
            weight_spec,
            storage_method
        FROM a20_fishery_products;
    """)
    
    # 建立 v_master_livestock_pork (連網 A30)
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS v_master_livestock_pork AS
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
    """)
    
    # 建立 v_master_agro_climate (連網 A40)
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS v_master_agro_climate AS
        SELECT 
            'A40' AS domain_code,
            station_sn,
            obs_date,
            obs_count,
            download_url
        FROM a40_climate_daily_obs;
    """)
    
    # 建立 v_master_agrovoc_semantic (連網 A50)
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS v_master_agrovoc_semantic AS
        SELECT 
            'A50' AS domain_code,
            c.concept_uri,
            c.concept_id,
            l.lang_code,
            l.label_text,
            l.label_type
        FROM a50_agrovoc_concepts c
        JOIN a50_agrovoc_labels l ON c.concept_uri = l.concept_uri;
    """)
    
    # 建立 v_master_soil_water (連網 A41)
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS v_master_soil_water AS
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
    """)
    
    # 建立 v_master_aquaculture (連網 A21)
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS v_master_aquaculture AS
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
    """)
    
    # 建立 v_master_vet_drug (連網 A31)
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS v_master_vet_drug AS
        SELECT 
            'A31' AS domain_code,
            residue_id,
            drug_name,
            target_livestock,
            mrl_ppm,
            withdrawal_period_days,
            is_prohibited
        FROM a31_vet_drug_residue;
    """)
    
    # 建立 v_master_fertilizer (連網 A14)
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS v_master_fertilizer AS
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
    """)
    
    conn.commit()
    conn.close()
    return {"injected_views": ["v_master_crop_market", "v_master_pesticide_safety", "v_master_pest_mrl", "v_master_organic_cert", "v_master_fishery_product", "v_master_livestock_pork", "v_master_agro_climate", "v_master_agrovoc_semantic", "v_master_soil_water", "v_master_aquaculture", "v_master_vet_drug", "v_master_fertilizer"]}
