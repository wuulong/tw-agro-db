import sys
from pathlib import Path
import typer

repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from modules.a40_agro_climate_db.etl import run_etl
from modules.a40_agro_climate_db.fts import build_fts_index
from modules.a40_agro_climate_db.metadata_gen import update_metadata
from src.a00_core.utils.cli_template import execute_common_build, execute_common_search, execute_common_doctor

app = typer.Typer(help="🌧️ A40 agro_climate_db (農業氣象觀測與災防) CLI 工具鏈")
META_PATH = Path(__file__).parent.parent.parent / "modules" / "a40_agro_climate_db" / "metadata.json"

@app.command("build")
def build(
    json_file: str = typer.Option("agro_poc_samples/A40_agro_climate_stations.json", "--input", "-i", help="A40 氣象站 JSON 路徑"),
    db_path: str = typer.Option("db/agro.db", "--db", "-d", help="SQLite 資料庫路徑"),
    force: bool = typer.Option(False, "--force", "-f", help="強制重新 ETL 入庫不跳過")
):
    """建置 A40 農業氣象觀測庫與 FTS5 倒排"""
    execute_common_build(
        module_name_display="A40 agro_climate_db",
        json_file=json_file,
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
    keyword: str = typer.Argument(..., help="測站編號或日期 (如 100213, 2015-12-03)"),
    db_path: str = typer.Option("db/agro.db", "--db", "-d", help="SQLite 資料庫路徑")
):
    """查詢農業氣象觀測紀錄 FTS5"""
    sql = """
        SELECT r.station_sn, r.obs_date, r.obs_count, r.download_url
        FROM a40_climate_fts f
        JOIN a40_climate_daily_obs r ON f.station_sn = r.station_sn AND f.obs_date = r.obs_date
        WHERE a40_climate_fts MATCH ?
        LIMIT 10
    """
    execute_common_search(
        module_name_display="A40 農業氣象觀測",
        keyword=keyword,
        db_path=db_path,
        repo_root=repo_root,
        sql_query=sql,
        headers=["測站流水號", "觀測日期", "觀測筆數", "下載連結"]
    )

@app.command("doctor")
def doctor(
    db_path: str = typer.Option("db/agro.db", "--db", "-d", help="SQLite 資料庫路徑")
):
    """A40 模組健康度診斷"""
    execute_common_doctor("A40 agro_climate_db", db_path, repo_root, "a40_climate_daily_obs")

if __name__ == "__main__":
    app()
