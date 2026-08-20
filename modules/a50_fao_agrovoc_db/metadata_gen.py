import json
import sqlite3
from pathlib import Path
from typing import Union, Dict, Any

from src.a00_core.utils.metadata_manager import write_dual_metadata

def update_metadata(db_path: Union[str, Path]) -> Dict[str, Any]:
    db_p = Path(db_path)
    meta_p = Path(__file__).parent / "metadata.json"
    sample_p = Path(__file__).parent.parent.parent / "agro_poc_samples" / "A50_fao_agrovoc.json"
    
    return write_dual_metadata(
        db_path=db_p,
        module_id="A50",
        module_name="a50_fao_agrovoc_db",
        table_name="a50_agrovoc_concepts",
        agency_name="聯合國糧農組織 (FAO)",
        dataset_name="國際農學多語主題詞庫 (AGROVOC LOD)",
        source_url="https://agrovoc.fao.org/sparql",
        local_sample_path=str(sample_p),
        tables=["a50_agrovoc_concepts", "a50_agrovoc_labels", "a50_agrovoc_hierarchy", "a50_agrovoc_fts"],
        views=["v_a50_agrovoc_semantic"],
        json_output_path=meta_p
    )
