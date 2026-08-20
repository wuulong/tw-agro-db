import json
import sqlite3
from pathlib import Path
from typing import Union, Dict, Any

from src.a00_core.utils.metadata_manager import write_dual_metadata

def update_metadata(db_path: Union[str, Path]) -> Dict[str, Any]:
    db_p = Path(db_path)
    meta_p = Path(__file__).parent / "metadata.json"
    sample_p = Path(__file__).parent.parent.parent / "agro_poc_samples" / "A31_vet_drug_food_residue.json"
    
    return write_dual_metadata(
        db_path=db_p,
        module_id="A12",
        module_name="a12_pest_mrl_alert_db",
        table_name="a12_mrl_inspection_records",
        agency_name="衛福部食藥署 (TFDA)",
        dataset_name="市售農產品殘留農藥監測 (PestMRL)",
        source_url="https://data.gov.tw/dataset/140061",
        local_sample_path=str(sample_p),
        tables=["a12_mrl_inspection_records", "a12_mrl_fts"],
        views=["v_a12_pest_mrl"],
        json_output_path=meta_p
    )
