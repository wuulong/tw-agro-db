import json
import sqlite3
from pathlib import Path
from typing import Union, Dict, Any

from src.a00_core.utils.metadata_manager import write_dual_metadata

def update_metadata(db_path: Union[str, Path]) -> Dict[str, Any]:
    db_p = Path(db_path)
    meta_p = Path(__file__).parent / "metadata.json"
    sample_p = Path(__file__).parent.parent.parent / "agro_poc_samples" / "A30_livestock_pork_trans.json"
    
    return write_dual_metadata(
        db_path=db_p,
        module_id="A30",
        module_name="a30_livestock_db",
        table_name="a30_pork_trans_daily",
        agency_name="中央畜產會 (NAIF) / 農業部",
        dataset_name="毛豬批發市場交易行情 (LivestockPorkTrans)",
        source_url="https://data.gov.tw/dataset/6057",
        local_sample_path=str(sample_p),
        tables=["a30_pork_trans_daily", "a30_pork_fts"],
        views=["v_a30_livestock_pork"],
        json_output_path=meta_p
    )
