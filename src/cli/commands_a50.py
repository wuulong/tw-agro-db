import sys
from pathlib import Path
import typer

repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from modules.a50_fao_agrovoc_db.etl import run_etl
from modules.a50_fao_agrovoc_db.fts import build_fts_index
from modules.a50_fao_agrovoc_db.metadata_gen import update_metadata
from src.a00_core.utils.cli_template import execute_common_build, execute_common_search, execute_common_doctor

app = typer.Typer(help="🌐 A50 fao_agrovoc_db (國際農學多語主題詞庫) CLI 工具鏈")
META_PATH = Path(__file__).parent.parent.parent / "modules" / "a50_fao_agrovoc_db" / "metadata.json"

@app.command("build")
def build(
    json_file: str = typer.Option("agro_poc_samples/A50_fao_agrovoc.json", "--input", "-i", help="A50 AGROVOC JSON 路徑"),
    db_path: str = typer.Option("db/agro.db", "--db", "-d", help="SQLite 資料庫路徑"),
    force: bool = typer.Option(False, "--force", "-f", help="強制重新 ETL 入庫不跳過")
):
    """建置 A50 國際農學主題詞庫與 FTS5 倒排"""
    execute_common_build(
        module_name_display="A50 fao_agrovoc_db",
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
    keyword: str = typer.Argument(..., help="農學主題詞關鍵字 (如 椰子, coconut, 益達胺)"),
    db_path: str = typer.Option("db/agro.db", "--db", "-d", help="SQLite 資料庫路徑")
):
    """查詢 AGROVOC 國際農學標籤 FTS5"""
    sql = """
        SELECT l.concept_uri, l.lang_code, l.label_text, l.label_type
        FROM a50_agrovoc_fts f
        JOIN a50_agrovoc_labels l ON f.concept_uri = l.concept_uri AND f.lang_code = l.lang_code AND f.label_text = l.label_text
        WHERE a50_agrovoc_fts MATCH ?
        LIMIT 10
    """
    execute_common_search(
        module_name_display="A50 AGROVOC 主題詞",
        keyword=keyword,
        db_path=db_path,
        repo_root=repo_root,
        sql_query=sql,
        headers=["Concept URI", "語言", "主題詞標籤", "標籤類型"]
    )

@app.command("doctor")
def doctor(
    db_path: str = typer.Option("db/agro.db", "--db", "-d", help="SQLite 資料庫路徑")
):
    """A50 模組健康度診斷"""
    execute_common_doctor("A50 fao_agrovoc_db", db_path, repo_root, "a50_agrovoc_concepts")

if __name__ == "__main__":
    app()
