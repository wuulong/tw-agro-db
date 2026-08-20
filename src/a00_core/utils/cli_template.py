"""
src/a00_core/utils/cli_template.py
通用 CLI 抽象框架執行器 (Common CLI Template Executor)
統一封裝全庫子模組 build, search, doctor 標準命令流程與 Rich 終端機繪製
"""
import sqlite3
from pathlib import Path
from typing import Callable, Dict, Any, List, Optional, Union
from rich.console import Console
from rich.table import Table
import typer

from src.a00_core.utils.sync_guard import should_skip_etl_by_hash

console = Console()

def execute_common_build(
    module_name_display: str,
    json_file: str,
    db_path: str,
    meta_json_path: Path,
    repo_root: Path,
    etl_func: Callable[[Path, Path], Dict[str, Any]],
    fts_func: Callable[[Path], Dict[str, Any]],
    meta_func: Callable[[Path], Dict[str, Any]],
    force: bool = False
) -> None:
    """通用 build 指令樣板執行器"""
    console.print(f"[bold yellow]⚙️ 開始建置 {module_name_display}...[/bold yellow]")
    json_p = repo_root / json_file if not Path(json_file).is_absolute() else Path(json_file)
    db_p = repo_root / db_path if not Path(db_path).is_absolute() else Path(db_path)
    
    if not force and meta_json_path.exists():
        skip, f_hash, reason = should_skip_etl_by_hash(json_p, meta_json_path)
        if skip:
            console.print(f"  [cyan]{reason}[/cyan]")
            console.print(f"[bold green]✅ {module_name_display} 數據未修改，智慧跳過完成！[/bold green]")
            return
            
    res_etl = etl_func(json_p, db_p)
    console.print(f"  • ETL 入庫完成: {res_etl}")
    
    res_fts = fts_func(db_p)
    console.print(f"  • FTS5 全文倒排建立完成: {res_fts.get('indexed_records', 0)} 筆")
    
    res_meta = meta_func(db_p)
    console.print(f"  • Metadata 更新成功: {res_meta.get('record_counts')}")
    console.print(f"[bold green]✅ {module_name_display} 建置完成！[/bold green]")

def execute_common_search(
    module_name_display: str,
    keyword: str,
    db_path: str,
    repo_root: Path,
    sql_query: str,
    headers: List[str],
    column_styles: Optional[List[str]] = None
) -> None:
    """通用 search 指令樣板與 Rich Table 渲染執行器"""
    db_p = repo_root / db_path if not Path(db_path).is_absolute() else Path(db_path)
    if not db_p.exists():
        console.print(f"[bold red]❌ DB 檔案不存在: {db_p}[/bold red]")
        raise typer.Exit(1)
        
    conn = sqlite3.connect(str(db_p))
    cursor = conn.cursor()
    cursor.execute(sql_query, (keyword,))
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        console.print(f"🔍 找不到關鍵字 '{keyword}' 的相關紀錄。")
        return
        
    table = Table(title=f"🔍 {module_name_display} 查詢結果: '{keyword}'")
    styles = column_styles or ["green", "cyan", "yellow", "magenta", "blue"]
    for i, h in enumerate(headers):
        table.add_column(h, style=styles[i % len(styles)])
        
    for r in rows:
        table.add_row(*[str(item) for item in r])
        
    console.print(table)

def execute_common_doctor(
    module_name_display: str,
    db_path: str,
    repo_root: Path,
    target_table: str
) -> None:
    """通用 doctor 健康度診斷執行器"""
    db_p = repo_root / db_path if not Path(db_path).is_absolute() else Path(db_path)
    if not db_p.exists():
        console.print(f"[bold red]❌ DB 檔案不存在: {db_p}[/bold red]")
        raise typer.Exit(1)
        
    conn = sqlite3.connect(str(db_p))
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {target_table}")
    rec_cnt = cursor.fetchone()[0]
    conn.close()
    
    console.print(f"🩺 {module_name_display} Doctor Check: 實體表 '{target_table}' 筆數 [green]{rec_cnt}[/green]")
    if rec_cnt > 0:
        console.print(f"[bold green]✅ {module_name_display} STATUS: [PASS][/bold green]")
    else:
        console.print(f"[bold red]❌ {module_name_display} STATUS: [FAIL - 表無資料][/bold red]")
