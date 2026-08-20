import sys
from pathlib import Path
import typer

repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from modules.a12_pest_mrl_alert_db.etl import run_etl
from modules.a12_pest_mrl_alert_db.fts import build_fts_index
from modules.a12_pest_mrl_alert_db.metadata_gen import update_metadata
from src.a00_core.utils.cli_template import execute_common_build, execute_common_search, execute_common_doctor

app = typer.Typer(help="🧪 A12 pest_mrl_alert_db (農藥殘留容許量 MRL 監測) CLI 工具鏈")
META_PATH = Path(__file__).parent.parent.parent / "modules" / "a12_pest_mrl_alert_db" / "metadata.json"

@app.command("build")
def build(
    json_file: str = typer.Option("agro_poc_samples/A31_vet_drug_food_residue.json", "--input", "-i", help="A12 殘留監測 JSON 路徑"),
    db_path: str = typer.Option("db/agro.db", "--db", "-d", help="SQLite 資料庫路徑"),
    force: bool = typer.Option(False, "--force", "-f", help="強制重新 ETL 入庫不跳過")
):
    """建置 A12 殘留監測庫與 FTS5 倒排"""
    execute_common_build(
        module_name_display="A12 pest_mrl_alert_db",
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
    keyword: str = typer.Argument(..., help="抽驗樣品名稱或業者 (如 高麗菜, 全聯)"),
    db_path: str = typer.Option("db/agro.db", "--db", "-d", help="SQLite 資料庫路徑")
):
    """查詢殘留監測紀錄 FTS5"""
    sql = """
        SELECT r.record_id, r.sample_name, r.inspection_agency, r.vendor_name, r.test_result, r.is_compliant
        FROM a12_mrl_fts f
        JOIN a12_mrl_inspection_records r ON f.record_id = r.record_id
        WHERE a12_mrl_fts MATCH ?
        LIMIT 10
    """
    execute_common_search(
        module_name_display="A12 農檢殘留監測",
        keyword=keyword,
        db_path=db_path,
        repo_root=repo_root,
        sql_query=sql,
        headers=["紀錄號", "樣品名稱", "檢驗單位", "抽驗業者", "檢驗結果", "是否合格(1=是)"]
    )

@app.command("doctor")
def doctor(
    db_path: str = typer.Option("db/agro.db", "--db", "-d", help="SQLite 資料庫路徑")
):
    """A12 模組健康度診斷"""
    execute_common_doctor("A12 pest_mrl_alert_db", db_path, repo_root, "a12_mrl_inspection_records")

if __name__ == "__main__":
    app()
