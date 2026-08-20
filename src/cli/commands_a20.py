import sys
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table

repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from modules.a20_fishery_market_db.etl import run_etl
from modules.a20_fishery_market_db.fts import build_fts_index
from modules.a20_fishery_market_db.metadata_gen import update_metadata

app = typer.Typer(help="🐟 A20 fishery_market_db (水產漁獲與名冊) CLI 工具鏈")
console = Console()

from src.a00_core.utils.sync_guard import should_skip_etl_by_hash

@app.command("build")
def build(
    json_file: str = typer.Option("agro_poc_samples/A20_fishery_product_info.json", "--input", "-i", help="A20 水產名冊 JSON 路徑"),
    db_path: str = typer.Option("db/agro.db", "--db", "-d", help="SQLite 資料庫路徑"),
    force: bool = typer.Option(False, "--force", "-f", help="強制重新 ETL 入庫不跳過")
):
    """建置 A20 水產名冊庫與 FTS5 倒排"""
    console.print(f"[bold yellow]🐟 開始建置 A20 fishery_market_db...[/bold yellow]")
    json_p = repo_root / json_file if not Path(json_file).is_absolute() else Path(json_file)
    db_p = repo_root / db_path if not Path(db_path).is_absolute() else Path(db_path)
    meta_p = Path(__file__).parent.parent.parent / "modules" / "a20_fishery_market_db" / "metadata.json"
    
    if not force:
        skip, f_hash, reason = should_skip_etl_by_hash(json_p, meta_p)
        if skip:
            console.print(f"  [cyan]{reason}[/cyan]")
            console.print("[bold green]✅ A20 數據未修改，智慧跳過完成！[/bold green]")
            return
            
    res_etl = run_etl(json_p, db_p)
    console.print(f"  • ETL 入庫完成: 水產品名冊 {res_etl['records_inserted']} 筆")
    
    res_fts = build_fts_index(db_p)
    console.print(f"  • FTS5 全文倒排建立完成: {res_fts['indexed_records']} 筆")
    
    res_meta = update_metadata(db_p)
    console.print(f"  • Metadata 更新成功: {res_meta.get('record_counts')}")
    console.print("[bold green]✅ A20 fishery_market_db 建置完成！[/bold green]")

@app.command("search")
def search(
    keyword: str = typer.Argument(..., help="魚種名稱或產地關鍵字 (如 透抽, 北太平洋)"),
    db_path: str = typer.Option("db/agro.db", "--db", "-d", help="SQLite 資料庫路徑")
):
    """查詢水產品名冊 FTS5"""
    import sqlite3
    db_p = repo_root / db_path if not Path(db_path).is_absolute() else Path(db_path)
    if not db_p.exists():
        console.print(f"[bold red]❌ DB 檔案不存在: {db_p}[/bold red]")
        raise typer.Exit(1)
        
    conn = sqlite3.connect(str(db_p))
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT r.product_name, r.origin_location, r.weight_spec, r.storage_method
        FROM a20_fishery_fts f
        JOIN a20_fishery_products r ON f.product_id = r.product_id
        WHERE a20_fishery_fts MATCH ?
        LIMIT 10
    """, (keyword,))
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        console.print(f"🔍 找不到關鍵字 '{keyword}' 的水產品紀錄。")
        return
        
    table = Table(title=f"🐟 A20 水產品查詢結果: '{keyword}'")
    table.add_column("水產品名稱", style="green")
    table.add_column("來源產地", style="cyan")
    table.add_column("重量規格", style="yellow")
    table.add_column("保存方式", style="magenta")
    
    for r in rows:
        table.add_row(r[0], r[1], r[2], r[3])
        
    console.print(table)

@app.command("doctor")
def doctor(
    db_path: str = typer.Option("db/agro.db", "--db", "-d", help="SQLite 資料庫路徑")
):
    """A20 模組健康度診斷 (Doctor Check)"""
    import sqlite3
    db_p = repo_root / db_path if not Path(db_path).is_absolute() else Path(db_path)
    if not db_p.exists():
        console.print(f"[bold red]❌ DB 檔案不存在: {db_p}[/bold red]")
        raise typer.Exit(1)
        
    conn = sqlite3.connect(str(db_p))
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM a20_fishery_products")
    rec_cnt = cursor.fetchone()[0]
    conn.close()
    
    console.print(f"🩺 A20 Doctor Check: 水產品筆數 [green]{rec_cnt}[/green]")
    if rec_cnt > 0:
        console.print("[bold green]✅ A20 STATUS: [PASS][/bold green]")
    else:
        console.print("[bold red]❌ A20 STATUS: [FAIL - 表無資料][/bold red]")

if __name__ == "__main__":
    app()
