import sys
from pathlib import Path
import typer

repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from modules.a13_organic_cert_db.etl import run_etl
from modules.a13_organic_cert_db.fts import build_fts_index
from modules.a13_organic_cert_db.metadata_gen import update_metadata
from src.a00_core.utils.cli_template import execute_common_build, execute_common_search, execute_common_doctor

app = typer.Typer(help="🌱 A13 organic_cert_db (產銷履歷 TAP 與有機資材名冊) CLI 工具鏈")
META_PATH = Path(__file__).parent.parent.parent / "modules" / "a13_organic_cert_db" / "metadata.json"

@app.command("build")
def build(
    json_file: str = typer.Option("agro_poc_samples/A13_organic_farm_list.json", "--input", "-i", help="A13 有機資材 JSON 路徑"),
    db_path: str = typer.Option("db/agro.db", "--db", "-d", help="SQLite 資料庫路徑"),
    force: bool = typer.Option(False, "--force", "-f", help="強制重新 ETL 入庫不跳過")
):
    """建置 A13 有機資材名冊庫與 FTS5 倒排"""
    execute_common_build(
        module_name_display="A13 organic_cert_db",
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
    keyword: str = typer.Argument(..., help="資材名稱或品牌 (如 硫酸銨, 尿素)"),
    db_path: str = typer.Option("db/agro.db", "--db", "-d", help="SQLite 資料庫路徑")
):
    """查詢有機資材名冊 FTS5"""
    sql = """
        SELECT r.registry_id, r.period_year, r.material_name, r.category_type, r.quantity_tons, r.value_thousand_ntd
        FROM a13_organic_fts f
        JOIN a13_organic_materials_registry r ON f.registry_id = r.registry_id
        WHERE a13_organic_fts MATCH ?
        LIMIT 10
    """
    execute_common_search(
        module_name_display="A13 有機資材名冊",
        keyword=keyword,
        db_path=db_path,
        repo_root=repo_root,
        sql_query=sql,
        headers=["登記號", "年度", "資材名稱", "類別", "數量(噸)", "價值(千元)"]
    )

@app.command("doctor")
def doctor(
    db_path: str = typer.Option("db/agro.db", "--db", "-d", help="SQLite 資料庫路徑")
):
    """A13 模組健康度診斷"""
    execute_common_doctor("A13 organic_cert_db", db_path, repo_root, "a13_organic_materials_registry")

if __name__ == "__main__":
    app()
