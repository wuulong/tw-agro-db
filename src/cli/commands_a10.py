import sys
from pathlib import Path
from typing import Optional
import typer

repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from modules.a10_tw_crop_db.etl import run_etl
from modules.a10_tw_crop_db.fts import build_fts_index
from modules.a10_tw_crop_db.metadata_gen import update_metadata
from src.a00_core.utils.cli_template import execute_common_build, execute_common_search, execute_common_doctor

app = typer.Typer(help="🌾 A10 tw_crop_db (農作物與行情錨點庫) CLI 命令")
META_PATH = Path(__file__).parent.parent.parent / "modules" / "a10_tw_crop_db" / "metadata.json"

@app.command("build")
def build(
    input_file: str = typer.Option("agro_poc_samples/A10_crop_farm_trans.json", "--input", "-i", help="Raw JSON 檔案路徑"),
    db_path: str = typer.Option("db/agro.db", "--db", "-d", help="SQLite 資料庫路徑"),
    force: bool = typer.Option(False, "--force", "-f", help="強制重新 ETL 入庫不跳過")
):
    """執行 A10 ETL、FTS 索引建立與 Metadata 更新"""
    execute_common_build(
        module_name_display="A10 tw_crop_db",
        json_file=input_file,
        db_path=db_path,
        meta_json_path=META_PATH,
        repo_root=repo_root,
        etl_func=run_etl,
        fts_func=build_fts_index,
        meta_func=update_metadata,
        force=force
    )

@app.command("search")
def search(
    keyword: str = typer.Argument(..., help="農作物名稱或關鍵字 (如 椰子, 高麗菜)"),
    db_path: str = typer.Option("db/agro.db", "--db", "-d", help="SQLite 資料庫路徑")
):
    """查詢農作物字典與 FTS5 行情"""
    sql = """
        SELECT d.crop_id, d.crop_name, d.category_name, t.trans_date, t.price_avg, t.volume_kg
        FROM a10_crop_fts f
        JOIN a10_crop_dictionary d ON f.crop_id = d.crop_id
        LEFT JOIN a10_crop_trans_daily t ON d.crop_id = t.crop_id
        WHERE a10_crop_fts MATCH ?
        LIMIT 10
    """
    execute_common_search(
        module_name_display="A10 農作物行情",
        keyword=keyword,
        db_path=db_path,
        repo_root=repo_root,
        sql_query=sql,
        headers=["作物代號", "作物名稱", "分類", "最新交易日", "均價(元/kg)", "交易量(kg)"]
    )

@app.command("doctor")
def doctor(
    db_path: str = typer.Option("db/agro.db", "--db", "-d", help="SQLite 資料庫路徑")
):
    """A10 模組健康度診斷"""
    execute_common_doctor("A10 tw_crop_db", db_path, repo_root, "a10_crop_trans_daily")

if __name__ == "__main__":
    app()
