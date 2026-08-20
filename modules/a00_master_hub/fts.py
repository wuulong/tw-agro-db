import sqlite3
from pathlib import Path
from typing import Union, Dict, Any

from src.a00_core.master_builder.builder_fts import build_global_fts

def build_fts_index(db_path: Union[str, Path]) -> Dict[str, Any]:
    return build_global_fts(db_path)

if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 2:
        res = build_fts_index(sys.argv[1])
        print(f"A00 全域 FTS 建立完成: {res}")
