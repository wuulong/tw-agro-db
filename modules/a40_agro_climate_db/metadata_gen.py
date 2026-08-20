import json
import sqlite3
from pathlib import Path
from typing import Union, Dict, Any

from src.a00_core.utils.metadata_manager import write_dual_metadata

def update_metadata(db_path: Union[str, Path]) -> Dict[str, Any]:
    db_p = Path(db_path)
    meta_p = Path(__file__).parent / "metadata.json"
    sample_p = Path(__file__).parent.parent.parent / "agro_poc_samples" / "A40_agro_climate_stations.json"
    
    return write_dual_metadata(
        db_path=db_p,
        module_id="A40",
        module_name="a40_agro_climate_db",
        table_name="a40_climate_daily_obs",
        agency_name="農業部試驗所 (TFRI) / 氣象署",
        dataset_name="農業氣象站每日觀測數據 (AgroClimateStations)",
        source_url="https://iesn.tfri.gov.tw/opd/api/",
        local_sample_path=str(sample_p),
        tables=["a40_climate_daily_obs", "a40_climate_fts"],
        views=["v_a40_agro_climate"],
        json_output_path=meta_p
    )
