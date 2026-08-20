import sys
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table

repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from modules.aXX_module_name.etl import run_etl
from modules.aXX_module_name.fts import build_fts_index
from modules.aXX_module_name.metadata_gen import update_metadata

app = typer.Typer(help="🌾 aXX_module_name CLI 工具鏈")
console = Console()

@app.command("build")
def build(
    json_file: str = typer.Option("agro_poc_samples/AXX_sample.json", "--input", "-i", help="來源 JSON 檔案路徑"),
    db_path: str = typer.Option("db/agro.db", "--db", "-d", help="SQLite 資料庫路徑")
):
    """建置 aXX 模組資料庫、FTS5 倒排與註冊 Metadata"""
    console.print(f"[bold yellow]🌾 開始建置 aXX_module_name...[/bold yellow]")
    json_p = repo_root / json_file if not Path(json_file).is_absolute() else Path(json_file)
    db_p = repo_root / db_path if not Path(db_path).is_absolute() else Path(db_path)
    
    res_etl = run_etl(json_p, db_p)
    console.print(f"  • ETL 入庫完成: {res_etl['records_inserted']} 筆")
    
    res_fts = build_fts_index(db_p)
    console.print(f"  • FTS5 全文倒排建立完成: {res_fts['indexed_records']} 筆")
    
    res_meta = update_metadata(db_p)
    console.print(f"  • Metadata 更新成功: {res_meta.get('record_counts')}")
    console.print("[bold green]✅ aXX_module_name 建置完成！[/bold green]")

@app.command("sync")
def sync(
    input_file: Optional[str] = typer.Option(None, "--input", "-i", help="最新 JSON 檔案路徑"),
    db_path: str = typer.Option("db/agro.db", "--db", "-d", help="SQLite 資料庫路徑")
):
    """執行 aXX 增量同步 (Incremental Sync) 與時間戳刷新"""
    console.print(f"[bold yellow]🔄 開始執行 aXX 增量同步...[/bold yellow]")
    db_p = repo_root / db_path if not Path(db_path).is_absolute() else Path(db_path)
    in_p = repo_root / (input_file or "agro_poc_samples/AXX_sample.json")
    
    res_etl = run_etl(in_p, db_p)
    res_fts = build_fts_index(db_p)
    res_meta = update_metadata(db_p)
    
    console.print(f"✅ aXX 增量同步完成: 寫入 {res_etl['records_inserted']} 筆，FTS 倒排 {res_fts['indexed_records']} 筆。")
    console.print(f"📅 最新同步時間: {res_meta.get('data_source', {}).get('last_updated')}")

@app.command("search")
def search(
    keyword: str = typer.Argument(..., help="搜尋關鍵字"),
    db_path: str = typer.Option("db/agro.db", "--db", "-d", help="SQLite 資料庫路徑")
):
    """查詢 aXX 模組 FTS5 倒排"""
    import sqlite3
    db_p = repo_root / db_path if not Path(db_path).is_absolute() else Path(db_path)
    if not db_p.exists():
        console.print(f"[bold red]❌ DB 檔案不存在: {db_p}[/bold red]")
        raise typer.Exit(1)
        
    conn = sqlite3.connect(str(db_p))
    cursor = conn.cursor()
    cursor.execute("""
        SELECT entity_id, entity_name, category_name FROM aXX_entity_fts
        WHERE aXX_entity_fts MATCH ? LIMIT 10
    """, (keyword,))
    rows = cursor.fetchall()
    conn.close()
    
    table = Table(title=f"🌾 aXX 查詢結果: '{keyword}'")
    table.add_column("ID", style="cyan")
    table.add_column("名稱", style="green")
    table.add_column("分類", style="yellow")
    for r in rows:
        table.add_row(r[0], r[1], r[2])
    console.print(table)

@app.command("doctor")
def doctor(
    db_path: str = typer.Option("db/agro.db", "--db", "-d", help="SQLite 資料庫路徑")
):
    """aXX 模組健康度診斷 (Doctor Check)"""
    import sqlite3
    db_p = repo_root / db_path if not Path(db_path).is_absolute() else Path(db_path)
    if not db_p.exists():
        console.print(f"[bold red]❌ DB 檔案不存在: {db_p}[/bold red]")
        raise typer.Exit(1)
        
    conn = sqlite3.connect(str(db_p))
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM aXX_entity_table")
    cnt = cursor.fetchone()[0]
    conn.close()
    
    console.print(f"🩺 aXX Doctor Check: 筆數 [green]{cnt}[/green]")
    if cnt > 0:
        console.print("[bold green]✅ aXX STATUS: [PASS][/bold green]")
    else:
        console.print("[bold red]❌ aXX STATUS: [FAIL - 表無資料][/bold red]")

if __name__ == "__main__":
    app()
