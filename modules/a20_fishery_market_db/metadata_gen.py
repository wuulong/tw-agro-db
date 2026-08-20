import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Union, Dict, Any

from src.a00_core.utils.metadata_manager import write_dual_metadata

def update_metadata(db_path: Union[str, Path]) -> Dict[str, Any]:
    db_p = Path(db_path)
    meta_p = Path(__file__).parent / "metadata.json"
    sample_p = Path(__file__).parent.parent.parent / "agro_poc_samples" / "A20_fishery_product_info.json"
    
    return write_dual_metadata(
        db_path=db_p,
        module_id="A20",
        module_name="a20_fishery_market_db",
        table_name="a20_fishery_products",
        agency_name="農業部漁業署 (Fisheries Agency)",
        dataset_name="水產品資訊與漁獲名冊 (FisheryProductInfo)",
        source_url="https://data.gov.tw/dataset/138541",
        local_sample_path=str(sample_p),
        tables=["a20_fishery_products", "a20_fishery_fts"],
        views=["v_a20_fishery_product"],
        json_output_path=meta_p
    )
