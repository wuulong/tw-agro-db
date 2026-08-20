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
        module_id="A31",
        module_name="a31_vet_drug_food_residue_db",
        table_name="a31_vet_drug_residue",
        agency_name="衛生福利部食品藥物管理署 (TFDA)",
        dataset_name="全台畜產品動物用藥殘留容許量標準資料庫",
        source_url="https://data.gov.tw/dataset/A31_VET_DRUG",
        local_sample_path=str(sample_p),
        tables=["a31_vet_drug_residue", "a31_vet_drug_fts"],
        views=["v_a31_vet_drug"],
        json_output_path=meta_p
    )
