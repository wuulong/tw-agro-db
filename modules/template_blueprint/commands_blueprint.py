import sys
from pathlib import Path
import typer

repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from modules.template_blueprint.etl import run_etl
from modules.template_blueprint.fts import build_fts_index
from modules.template_blueprint.metadata_gen import update_metadata
from src.a00_core.utils.cli_template import execute_common_build, execute_common_search, execute_common_doctor

app = typer.Typer(help="🧱 AXX template_blueprint (子模組藍圖範本) CLI 工具鏈")
META_PATH = Path(__file__).parent.parent.parent / "modules" / "template_blueprint" / "metadata.json"

@app.command("build")
def build(
    json_file: str = typer.Option("agro_poc_samples/sample.json", "--input", "-i", help="範本 JSON 路徑"),
    db_path: str = typer.Option("db/agro.db", "--db", "-d", help="SQLite 資料庫路徑"),
    force: bool = typer.Option(False, "--force", "-f", help="強制重新 ETL 入庫不跳過")
):
    """建置 AXX 藍圖庫與 FTS5 倒排"""
    execute_common_build(
        module_name_display="AXX template_blueprint",
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
    keyword: str = typer.Argument(..., help="搜尋關鍵字"),
    db_path: str = typer.Option("db/agro.db", "--db", "-d", help="SQLite 資料庫路徑")
):
    """查詢範本 FTS5"""
    sql = """
        SELECT rowid, * FROM axx_template_fts
        WHERE axx_template_fts MATCH ?
        LIMIT 10
    """
    execute_common_search(
        module_name_display="AXX 藍圖範本",
        keyword=keyword,
        db_path=db_path,
        repo_root=repo_root,
        sql_query=sql,
        headers=["ROWID", "內容樣例"]
    )

@app.command("doctor")
def doctor(
    db_path: str = typer.Option("db/agro.db", "--db", "-d", help="SQLite 資料庫路徑")
):
    """AXX 模組健康度診斷"""
    execute_common_doctor("AXX template_blueprint", db_path, repo_root, "axx_template_table")

if __name__ == "__main__":
    app()
