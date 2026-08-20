import json
import sqlite3
from pathlib import Path
from typing import Union, Dict, Any

from src.a00_core.utils.metadata_manager import write_dual_metadata

def update_metadata(db_path: Union[str, Path]) -> Dict[str, Any]:
    db_p = Path(db_path)
    meta_p = Path(__file__).parent / "metadata.json"
    sample_p = Path(__file__).parent.parent.parent / "agro_poc_samples" / "A11_pesticide_licenses.json"
    
    return write_dual_metadata(
        db_path=db_p,
        module_id="A11",
        module_name="a11_pesticide_db",
        table_name="a11_pesticide_licenses",
        agency_name="農業部防檢署 (BAPHIQ)",
        dataset_name="農藥許可證資料庫 (PesticideLic)",
        source_url="https://data.moa.gov.tw/Service/OpenData/FromM/PesticideLic.aspx",
        local_sample_path=str(sample_p),
        tables=["a11_pesticide_licenses", "a11_prohibited_pesticides", "a11_pesticide_fts"],
        views=["v_a11_pesticide_safety"],
        json_output_path=meta_p
    )
