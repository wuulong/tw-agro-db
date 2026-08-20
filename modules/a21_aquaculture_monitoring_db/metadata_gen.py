import json
import sqlite3
from pathlib import Path
from typing import Union, Dict, Any

from src.a00_core.utils.metadata_manager import write_dual_metadata

def update_metadata(db_path: Union[str, Path]) -> Dict[str, Any]:
    db_p = Path(db_path)
    meta_p = Path(__file__).parent / "metadata.json"
    sample_p = Path(__file__).parent.parent.parent / "agro_poc_samples" / "A21_aquaculture_monitoring.json"
    
    return write_dual_metadata(
        db_path=db_p,
        module_id="A21",
        module_name="a21_aquaculture_monitoring_db",
        table_name="a21_aquaculture_monitoring",
        agency_name="農業部漁業署",
        dataset_name="全台水產養殖場水質與寒害監測資料庫",
        source_url="https://data.gov.tw/dataset/A21_AQUACULTURE",
        local_sample_path=str(sample_p),
        tables=["a21_aquaculture_monitoring", "a21_aquaculture_fts"],
        views=["v_a21_aquaculture"],
        json_output_path=meta_p
    )
