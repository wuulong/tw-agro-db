import json
import sqlite3
from pathlib import Path
from typing import Union, Dict, Any

from src.a00_core.utils.metadata_manager import write_dual_metadata

def update_metadata(db_path: Union[str, Path]) -> Dict[str, Any]:
    db_p = Path(db_path)
    meta_p = Path(__file__).parent / "metadata.json"
    sample_p = Path(__file__).parent.parent.parent / "agro_poc_samples" / "A10_crop_farm_trans.json"
    
    return write_dual_metadata(
        db_path=db_p,
        module_id="A10",
        module_name="a10_tw_crop_db",
        table_name="a10_crop_trans_daily",
        agency_name="農業部 (MOA)",
        dataset_name="農產品交易行情 (FarmTransData)",
        source_url="https://data.moa.gov.tw/Service/OpenData/FromM/FarmTransData.aspx?IsTransData=1",
        local_sample_path=str(sample_p),
        tables=["a10_crop_dictionary", "a10_crop_trans_daily", "a10_crop_fts"],
        views=["v_a10_crop_market_summary"],
        json_output_path=meta_p
    )
