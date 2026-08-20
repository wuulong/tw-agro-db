import sys
from pathlib import Path
import typer

repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from modules.a21_aquaculture_monitoring_db.etl import run_etl
from modules.a21_aquaculture_monitoring_db.fts import build_fts_index
from modules.a21_aquaculture_monitoring_db.metadata_gen import update_metadata
from src.a00_core.utils.cli_template import execute_common_build, execute_common_search, execute_common_doctor

app = typer.Typer(help="🐟 A21 aquaculture_monitoring_db (水產養殖水質與寒害監測) CLI 工具鏈")
META_PATH = Path(__file__).parent.parent.parent / "modules" / "a21_aquaculture_monitoring_db" / "metadata.json"

@app.command("build")
def build(
    json_file: str = typer.Option("agro_poc_samples/A21_aquaculture_monitoring.json", "--input", "-i", help="A21 JSON 路徑"),
    db_path: str = typer.Option("db/agro.db", "--db", "-d", help="SQLite 資料庫路徑"),
    force: bool = typer.Option(False, "--force", "-f", help="強制重新 ETL 入庫不跳過")
):
    """建置 A21 水產養殖水質監測庫與 FTS5 倒排"""
    execute_common_build(
        module_name_display="A21 aquaculture_monitoring_db",
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
    keyword: str = typer.Argument(..., help="搜尋關鍵字 (如 台南市, 石斑魚, 虱目魚)"),
    db_path: str = typer.Option("db/agro.db", "--db", "-d", help="SQLite 資料庫路徑")
):
    """查詢 A21 水產養殖水質監測 FTS5"""
    sql = """
        SELECT m.farm_id, m.county_name, m.town_name, m.aquaculture_species, m.water_temp_c, m.dissolved_oxygen_mg_l, m.risk_level
        FROM a21_aquaculture_fts f
        JOIN a21_aquaculture_monitoring m ON f.farm_id = m.farm_id
        WHERE a21_aquaculture_fts MATCH ?
        LIMIT 10
    """
    execute_common_search(
        module_name_display="A21 水產養殖監測",
        keyword=keyword,
        db_path=db_path,
        repo_root=repo_root,
        sql_query=sql,
        headers=["魚塭代號", "縣市", "鄉鎮", "養殖物種", "水溫(°C)", "溶氧量(mg/L)", "風險等級"]
    )

@app.command("doctor")
def doctor(
    db_path: str = typer.Option("db/agro.db", "--db", "-d", help="SQLite 資料庫路徑")
):
    """A21 模組健康度診斷"""
    execute_common_doctor("A21 aquaculture_monitoring_db", db_path, repo_root, "a21_aquaculture_monitoring")

if __name__ == "__main__":
    app()
