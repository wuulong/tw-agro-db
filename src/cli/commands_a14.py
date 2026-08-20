import sys
from pathlib import Path
import typer

repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from modules.a14_organic_fertilizer_db.etl import run_etl
from modules.a14_organic_fertilizer_db.fts import build_fts_index
from modules.a14_organic_fertilizer_db.metadata_gen import update_metadata
from src.a00_core.utils.cli_template import execute_common_build, execute_common_search, execute_common_doctor

app = typer.Typer(help="🌿 A14 organic_fertilizer_db (農糧資材與肥料登記證) CLI 工具鏈")
META_PATH = Path(__file__).parent.parent.parent / "modules" / "a14_organic_fertilizer_db" / "metadata.json"

@app.command("build")
def build(
    json_file: str = typer.Option("agro_poc_samples/A14_organic_fertilizer.json", "--input", "-i", help="A14 JSON 路徑"),
    db_path: str = typer.Option("db/agro.db", "--db", "-d", help="SQLite 資料庫路徑"),
    force: bool = typer.Option(False, "--force", "-f", help="強制重新 ETL 入庫不跳過")
):
    """建置 A14 肥料登記證與有機資材庫與 FTS5 倒排"""
    execute_common_build(
        module_name_display="A14 organic_fertilizer_db",
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
    keyword: str = typer.Argument(..., help="搜尋關鍵字 (如 有機肥, 台肥, 泥炭)"),
    db_path: str = typer.Option("db/agro.db", "--db", "-d", help="SQLite 資料庫路徑")
):
    """查詢 A14 肥料登記證與資材 FTS5"""
    sql = """
        SELECT m.fertilizer_lic_id, m.brand_name, m.manufacturer_name, m.fertilizer_type, m.nitrogen_pct, m.phosphorus_pct, m.potassium_pct, m.is_organic_cert
        FROM a14_fertilizer_fts f
        JOIN a14_fertilizer_licenses m ON f.fertilizer_lic_id = m.fertilizer_lic_id
        WHERE a14_fertilizer_fts MATCH ?
        LIMIT 10
    """
    execute_common_search(
        module_name_display="A14 肥料資材",
        keyword=keyword,
        db_path=db_path,
        repo_root=repo_root,
        sql_query=sql,
        headers=["登記證字號", "廠牌名稱", "製造業者", "肥料品目", "N(%)", "P(%)", "K(%)", "有機審定"]
    )

@app.command("doctor")
def doctor(
    db_path: str = typer.Option("db/agro.db", "--db", "-d", help="SQLite 資料庫路徑")
):
    """A14 模組健康度診斷"""
    execute_common_doctor("A14 organic_fertilizer_db", db_path, repo_root, "a14_fertilizer_licenses")

if __name__ == "__main__":
    app()
