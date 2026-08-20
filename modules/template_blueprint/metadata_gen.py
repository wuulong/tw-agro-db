import json
import sqlite3
from pathlib import Path
from typing import Union, Dict, Any

from src.a00_core.utils.metadata_manager import write_dual_metadata

def update_metadata(db_path: Union[str, Path]) -> Dict[str, Any]:
    """藍圖範本: 呼叫核心雙軌 Metadata 寫入器，自動產生 sha256_hash"""
    db_p = Path(db_path)
    meta_p = Path(__file__).parent / "metadata.json"
    sample_p = Path(__file__).parent.parent.parent / "agro_poc_samples" / "sample.json"
    
    return write_dual_metadata(
        db_path=db_p,
        module_id="AXX",
        module_name="axx_template_db",
        table_name="axx_template_table",
        agency_name="農業部 (MOA)",
        dataset_name="範本數據集 (TemplateDataset)",
        source_url="https://data.moa.gov.tw/...",
        local_sample_path=str(sample_p),
        tables=["axx_template_table", "axx_template_fts"],
        views=["v_axx_template"],
        json_output_path=meta_p
    )
