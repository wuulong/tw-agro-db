import sys
from pathlib import Path
import typer

repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from modules.a31_vet_drug_food_residue_db.etl import run_etl
from modules.a31_vet_drug_food_residue_db.fts import build_fts_index
from modules.a31_vet_drug_food_residue_db.metadata_gen import update_metadata
from src.a00_core.utils.cli_template import execute_common_build, execute_common_search, execute_common_doctor

app = typer.Typer(help="🐖 A31 vet_drug_food_residue_db (動物用藥與畜產品殘留管制) CLI 工具鏈")
META_PATH = Path(__file__).parent.parent.parent / "modules" / "a31_vet_drug_food_residue_db" / "metadata.json"

@app.command("build")
def build(
    json_file: str = typer.Option("agro_poc_samples/A31_vet_drug_food_residue.json", "--input", "-i", help="A31 JSON 路徑"),
    db_path: str = typer.Option("db/agro.db", "--db", "-d", help="SQLite 資料庫路徑"),
    force: bool = typer.Option(False, "--force", "-f", help="強制重新 ETL 入庫不跳過")
):
    """建置 A31 動物用藥殘留庫與 FTS5 倒排"""
    execute_common_build(
        module_name_display="A31 vet_drug_food_residue_db",
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
    keyword: str = typer.Argument(..., help="搜尋關鍵字 (如 氯黴素, 雞肉, 羊肉)"),
    db_path: str = typer.Option("db/agro.db", "--db", "-d", help="SQLite 資料庫路徑")
):
    """查詢 A31 動物用藥殘留 FTS5"""
    sql = """
        SELECT m.residue_id, m.drug_name, m.target_livestock, m.mrl_ppm, m.withdrawal_period_days, m.is_prohibited
        FROM a31_vet_drug_fts f
        JOIN a31_vet_drug_residue m ON f.rowid = m.residue_id
        WHERE a31_vet_drug_fts MATCH ?
        LIMIT 10
    """
    execute_common_search(
        module_name_display="A31 動物用藥殘留",
        keyword=keyword,
        db_path=db_path,
        repo_root=repo_root,
        sql_query=sql,
        headers=["ID", "用藥名稱", "畜產品部位", "MRL(ppm)", "停藥期(天)", "禁用旗標"]
    )

@app.command("doctor")
def doctor(
    db_path: str = typer.Option("db/agro.db", "--db", "-d", help="SQLite 資料庫路徑")
):
    """A31 模組健康度診斷"""
    execute_common_doctor("A31 vet_drug_food_residue_db", db_path, repo_root, "a31_vet_drug_residue")

if __name__ == "__main__":
    app()
