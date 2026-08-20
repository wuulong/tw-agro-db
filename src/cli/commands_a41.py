import sys
from pathlib import Path
import typer

repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from modules.a41_soil_water_pollution_db.etl import run_etl
from modules.a41_soil_water_pollution_db.fts import build_fts_index
from modules.a41_soil_water_pollution_db.metadata_gen import update_metadata
from src.a00_core.utils.cli_template import execute_common_build, execute_common_search, execute_common_doctor

app = typer.Typer(help="🌿 A41 soil_water_pollution_db (土壤與水質環境安全) CLI 工具鏈")
META_PATH = Path(__file__).parent.parent.parent / "modules" / "a41_soil_water_pollution_db" / "metadata.json"

@app.command("build")
def build(
    json_file: str = typer.Option("agro_poc_samples/A41_soil_water_pollution.json", "--input", "-i", help="A41 JSON 路徑"),
    db_path: str = typer.Option("db/agro.db", "--db", "-d", help="SQLite 資料庫路徑"),
    force: bool = typer.Option(False, "--force", "-f", help="強制重新 ETL 入庫不跳過")
):
    """建置 A41 土壤與水質環境監測庫與 FTS5 倒排"""
    execute_common_build(
        module_name_display="A41 soil_water_pollution_db",
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
    keyword: str = typer.Argument(..., help="搜尋關鍵字 (如 彰化縣, 和美鎮, 鎘)"),
    db_path: str = typer.Option("db/agro.db", "--db", "-d", help="SQLite 資料庫路徑")
):
    """查詢 A41 土壤與水質監測 FTS5"""
    sql = """
        SELECT m.site_id, m.county_name, m.town_name, m.pollutant_type, m.concentration_ppm, m.regulatory_limit_ppm, m.is_polluted
        FROM a41_soil_water_fts f
        JOIN a41_soil_water_monitoring m ON f.site_id = m.site_id
        WHERE a41_soil_water_fts MATCH ?
        LIMIT 10
    """
    execute_common_search(
        module_name_display="A41 土壤與水質監測",
        keyword=keyword,
        db_path=db_path,
        repo_root=repo_root,
        sql_query=sql,
        headers=["監測點", "縣市", "鄉鎮", "檢測項目", "實測濃度(ppm)", "管制標準(ppm)", "超標旗標"]
    )

@app.command("doctor")
def doctor(
    db_path: str = typer.Option("db/agro.db", "--db", "-d", help="SQLite 資料庫路徑")
):
    """A41 模組健康度診斷"""
    execute_common_doctor("A41 soil_water_pollution_db", db_path, repo_root, "a41_soil_water_monitoring")

if __name__ == "__main__":
    app()
