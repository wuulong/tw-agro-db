import sys
from pathlib import Path
import typer

repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from modules.a30_livestock_db.etl import run_etl
from modules.a30_livestock_db.fts import build_fts_index
from modules.a30_livestock_db.metadata_gen import update_metadata
from src.a00_core.utils.cli_template import execute_common_build, execute_common_search, execute_common_doctor

app = typer.Typer(help="🐖 A30 livestock_db (毛豬與肉品批發行情) CLI 工具鏈")
META_PATH = Path(__file__).parent.parent.parent / "modules" / "a30_livestock_db" / "metadata.json"

@app.command("build")
def build(
    json_file: str = typer.Option("agro_poc_samples/A30_livestock_pork_trans.json", "--input", "-i", help="A30 毛豬行情 JSON 路徑"),
    db_path: str = typer.Option("db/agro.db", "--db", "-d", help="SQLite 資料庫路徑"),
    force: bool = typer.Option(False, "--force", "-f", help="強制重新 ETL 入庫不跳過")
):
    """建置 A30 毛豬行情庫與 FTS5 倒排"""
    execute_common_build(
        module_name_display="A30 livestock_db",
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
    keyword: str = typer.Argument(..., help="拍賣市場名稱 (如 花蓮縣, 彰化縣)"),
    db_path: str = typer.Option("db/agro.db", "--db", "-d", help="SQLite 資料庫路徑")
):
    """查詢毛豬批發行情 FTS5"""
    sql = """
        SELECT r.trans_date, r.market_name, r.total_heads, r.avg_weight_kg, r.avg_price_ntd, r.spec_heads
        FROM a30_pork_fts f
        JOIN a30_pork_trans_daily r ON f.rowid = r.rowid
        WHERE a30_pork_fts MATCH ?
        LIMIT 10
    """
    execute_common_search(
        module_name_display="A30 毛豬批發行情",
        keyword=keyword,
        db_path=db_path,
        repo_root=repo_root,
        sql_query=sql,
        headers=["交易日期", "市場名稱", "成交總頭數", "平均重量(kg)", "平均價格(元/kg)", "規格豬頭數"]
    )

@app.command("doctor")
def doctor(
    db_path: str = typer.Option("db/agro.db", "--db", "-d", help="SQLite 資料庫路徑")
):
    """A30 模組健康度診斷"""
    execute_common_doctor("A30 livestock_db", db_path, repo_root, "a30_pork_trans_daily")

if __name__ == "__main__":
    app()
