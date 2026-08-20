import json
import sqlite3
from pathlib import Path
from typing import Union, Dict, Any

from src.a00_core.utils.metadata_manager import write_dual_metadata

def update_metadata(db_path: Union[str, Path]) -> Dict[str, Any]:
    db_p = Path(db_path)
    meta_p = Path(__file__).parent / "metadata.json"
    sample_p = Path(__file__).parent.parent.parent / "agro_poc_samples" / "A41_soil_water_pollution.json"
    
    return write_dual_metadata(
        db_path=db_p,
        module_id="A41",
        module_name="a41_soil_water_pollution_db",
        table_name="a41_soil_water_monitoring",
        agency_name="環境保護署 / 農業部農糧署",
        dataset_name="全台農地土壤與水質監測資料庫",
        source_url="https://data.gov.tw/dataset/A41_SOIL_WATER",
        local_sample_path=str(sample_p),
        tables=["a41_soil_water_monitoring", "a41_soil_water_fts"],
        views=["v_a41_soil_water"],
        json_output_path=meta_p
    )
