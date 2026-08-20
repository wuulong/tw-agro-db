import json
import sqlite3
from pathlib import Path
from typing import Union, Dict, Any

from src.a00_core.utils.metadata_manager import write_dual_metadata

def update_metadata(db_path: Union[str, Path]) -> Dict[str, Any]:
    db_p = Path(db_path)
    meta_p = Path(__file__).parent / "metadata.json"
    sample_p = Path(__file__).parent.parent.parent / "agro_poc_samples" / "A14_organic_fertilizer.json"
    
    return write_dual_metadata(
        db_path=db_p,
        module_id="A14",
        module_name="a14_organic_fertilizer_db",
        table_name="a14_fertilizer_licenses",
        agency_name="農業部農糧署",
        dataset_name="全台農糧資材與肥料登記證資料庫",
        source_url="https://data.gov.tw/dataset/A14_FERTILIZER",
        local_sample_path=str(sample_p),
        tables=["a14_fertilizer_licenses", "a14_fertilizer_fts"],
        views=["v_a14_fertilizer"],
        json_output_path=meta_p
    )
