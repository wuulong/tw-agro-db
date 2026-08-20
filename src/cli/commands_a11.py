import sys
from pathlib import Path
import typer

repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from modules.a11_pesticide_db.etl import run_etl
from modules.a11_pesticide_db.fts import build_fts_index
from modules.a11_pesticide_db.metadata_gen import update_metadata
from src.a00_core.utils.cli_template import execute_common_build, execute_common_search, execute_common_doctor

app = typer.Typer(help="🌾 A11 pesticide_db (登記農藥許可證) CLI 工具鏈")
META_PATH = Path(__file__).parent.parent.parent / "modules" / "a11_pesticide_db" / "metadata.json"

@app.command("build")
def build(
    json_file: str = typer.Option("agro_poc_samples/A11_pesticide_licenses.json", "--input", "-i", help="A11 農藥許可證 JSON 路徑"),
    db_path: str = typer.Option("db/agro.db", "--db", "-d", help="SQLite 資料庫路徑"),
    force: bool = typer.Option(False, "--force", "-f", help="強制重新 ETL 入庫不跳過")
):
    """建置 A11 農藥許可證庫與 FTS5 倒排"""
    execute_common_build(
        module_name_display="A11 pesticide_db",
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
    keyword: str = typer.Argument(..., help="農藥名稱或廠牌 (如 滅, 益達胺)"),
    db_path: str = typer.Option("db/agro.db", "--db", "-d", help="SQLite 資料庫路徑")
):
    """查詢農藥許可證 FTS5"""
    sql = """
        SELECT r.pesticide_lic_id, r.pesticide_name, r.brand_name, r.vendor_name, r.expire_date
        FROM a11_pesticide_fts f
        JOIN a11_pesticide_licenses r ON f.pesticide_lic_id = r.pesticide_lic_id
        WHERE a11_pesticide_fts MATCH ?
        LIMIT 10
    """
    execute_common_search(
        module_name_display="A11 農藥許可證",
        keyword=keyword,
        db_path=db_path,
        repo_root=repo_root,
        sql_query=sql,
        headers=["許可證字號", "農藥名稱", "廠牌名稱", "申請廠商", "有效期限"]
    )

@app.command("doctor")
def doctor(
    db_path: str = typer.Option("db/agro.db", "--db", "-d", help="SQLite 資料庫路徑")
):
    """A11 模組健康度診斷"""
    execute_common_doctor("A11 pesticide_db", db_path, repo_root, "a11_pesticide_licenses")

if __name__ == "__main__":
    app()
