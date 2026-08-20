import json
import sqlite3
from pathlib import Path
from typing import Union, Dict, Any

from src.a00_core.utils.metadata_manager import write_dual_metadata

def update_metadata(db_path: Union[str, Path]) -> Dict[str, Any]:
    db_p = Path(db_path)
    meta_p = Path(__file__).parent / "metadata.json"
    sample_p = Path(__file__).parent.parent.parent / "agro_poc_samples" / "A13_organic_farm_list.json"
    
    return write_dual_metadata(
        db_path=db_p,
        module_id="A13",
        module_name="a13_organic_cert_db",
        table_name="a13_organic_materials_registry",
        agency_name="農業部 (MOA)",
        dataset_name="有機農場與品牌審查資材 (OrganicFarmList)",
        source_url="https://data.moa.gov.tw/Service/OpenData/FromM/OrganicFarmList.aspx",
        local_sample_path=str(sample_p),
        tables=["a13_organic_materials_registry", "a13_organic_fts"],
        views=["v_a13_organic_cert"],
        json_output_path=meta_p
    )
