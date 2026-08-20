import sqlite3
from pathlib import Path
from typing import Union, Dict, Any

from src.a00_core.master_builder.views_domestic import inject_master_views
from src.a00_core.master_builder.builder_analytics import build_analytics

def run_etl(json_path: Union[str, Path], db_path: Union[str, Path]) -> Dict[str, Any]:
    # 母大腦 ETL 為建立全庫視圖與延伸分析指標
    res_v = inject_master_views(db_path)
    res_a = build_analytics(db_path)
    return {"views": res_v, "analytics": res_a}

if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 3:
        res = run_etl(sys.argv[1], sys.argv[2])
        print(f"A00 ETL 執行完成: {res}")
