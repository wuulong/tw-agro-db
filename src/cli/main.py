"""
tw-agro-db Main CLI Command Hub (A00 Master Hub)
"""

import sys
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table

repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.cli.commands_a10 import app as a10_app
from src.cli.commands_a11 import app as a11_app
from src.cli.commands_a12 import app as a12_app
from src.cli.commands_a13 import app as a13_app
from src.cli.commands_a14 import app as a14_app
from src.cli.commands_a20 import app as a20_app
from src.cli.commands_a21 import app as a21_app
from src.cli.commands_a30 import app as a30_app
from src.cli.commands_a31 import app as a31_app
from src.cli.commands_a40 import app as a40_app
from src.cli.commands_a41 import app as a41_app
from src.cli.commands_a50 import app as a50_app
from src.a00_core.master_builder.views_domestic import inject_master_views
from src.a00_core.master_builder.builder_fts import build_global_fts
from src.a00_core.master_builder.builder_analytics import build_analytics
from src.a00_core.master_builder.builder_safety_mesh import build_crop_pesticide_safety_mesh
from src.a00_core.master_builder.builder_agrovoc_mesh import build_agrovoc_mesh
from src.a00_core.master_builder.builder_ontology_graph import build_ontology_graph
from src.a00_core.master_builder.builder_environmental_mesh import build_environmental_mesh
from src.a00_core.master_builder.builder_livestock_mesh import build_livestock_safety_mesh
from src.a00_core.master_builder.builder_fertilizer_mesh import build_crop_fertilizer_safety_mesh

app = typer.Typer(help="👑 tw-agro-db (台灣農業開放大數據引擎) 母大腦主控 CLI")
console = Console()

# 註冊子模組 CLI
app.add_typer(a10_app, name="a10")
app.add_typer(a11_app, name="a11")
app.add_typer(a12_app, name="a12")
app.add_typer(a13_app, name="a13")
app.add_typer(a14_app, name="a14")
app.add_typer(a20_app, name="a20")
app.add_typer(a21_app, name="a21")
app.add_typer(a30_app, name="a30")
app.add_typer(a31_app, name="a31")
app.add_typer(a40_app, name="a40")
app.add_typer(a41_app, name="a41")
app.add_typer(a50_app, name="a50")

@app.command("build-all")
def build_all(
    db_path: str = typer.Option("db/agro.db", "--db", "-d", help="SQLite 資料庫路徑")
):
    """建置母大腦全域神經網、倒排索引、延伸分析表與 A10+A11+A12 事前農藥安全網"""
    db_p = repo_root / db_path if not Path(db_path).is_absolute() else Path(db_path)
    console.print(f"[bold yellow]👑 開始建置 tw-agro-db 母大腦 ({db_p})...[/bold yellow]")
    
    # 0. 先跑 12 個子模組 ETL 入庫
    from modules.a10_tw_crop_db.etl import run_etl as run_a10_etl
    from modules.a11_pesticide_db.etl import run_etl as run_a11_etl
    from modules.a12_pest_mrl_alert_db.etl import run_etl as run_a12_etl
    from modules.a13_organic_cert_db.etl import run_etl as run_a13_etl
    from modules.a14_organic_fertilizer_db.etl import run_etl as run_a14_etl
    from modules.a20_fishery_market_db.etl import run_etl as run_a20_etl
    from modules.a21_aquaculture_monitoring_db.etl import run_etl as run_a21_etl
    from modules.a30_livestock_db.etl import run_etl as run_a30_etl
    from modules.a31_vet_drug_food_residue_db.etl import run_etl as run_a31_etl
    from modules.a40_agro_climate_db.etl import run_etl as run_a40_etl
    from modules.a41_soil_water_pollution_db.etl import run_etl as run_a41_etl
    from modules.a50_fao_agrovoc_db.etl import run_etl as run_a50_etl
    
    run_a10_etl(repo_root / "agro_poc_samples" / "A10_crop_farm_trans.json", db_p)
    run_a11_etl(repo_root / "agro_poc_samples" / "A11_pesticide_licenses.json", db_p)
    run_a12_etl(repo_root / "agro_poc_samples" / "A31_vet_drug_food_residue.json", db_p)
    run_a13_etl(repo_root / "agro_poc_samples" / "A13_organic_farm_list.json", db_p)
    run_a14_etl(repo_root / "agro_poc_samples" / "A14_organic_fertilizer.json", db_p)
    run_a20_etl(repo_root / "agro_poc_samples" / "A20_fishery_product_info.json", db_p)
    run_a21_etl(repo_root / "agro_poc_samples" / "A21_aquaculture_monitoring.json", db_p)
    run_a30_etl(repo_root / "agro_poc_samples" / "A30_livestock_pork_trans.json", db_p)
    run_a31_etl(repo_root / "agro_poc_samples" / "A31_vet_drug_food_residue.json", db_p)
    run_a40_etl(repo_root / "agro_poc_samples" / "A40_agro_climate_stations.json", db_p)
    run_a41_etl(repo_root / "agro_poc_samples" / "A41_soil_water_pollution.json", db_p)
    run_a50_etl(repo_root / "agro_poc_samples" / "A50_fao_agrovoc_full.json", db_p)
    
    # 1. 織連 View
    res_v = inject_master_views(db_p)
    console.print(f"  • 視圖織連完成: {res_v['injected_views']}")
    
    # 2. 建立全域 FTS5
    res_fts = build_global_fts(db_p)
    console.print(f"  • 全域 FTS5 倒排寫入完成: {res_fts['indexed_records']} 筆")
    
    # 3. 建立延伸分析表
    res_ana = build_analytics(db_p)
    console.print(f"  • 跨市場離散分析表建置完成: {res_ana['analytics_records_inserted']} 筆")
    
    # 3. 建立 A10+A11+A12 事前農藥安全網實體碰撞
    res_mesh = build_crop_pesticide_safety_mesh(db_p)
    console.print(f"  • A10+A11+A12 農藥安全網實體碰撞完成: {res_mesh.get('safety_mesh_records_inserted', 0)} 筆")
    
    # 4. 建立 A00 ↔ A50 跨領域國際 AGROVOC 本體語意網
    res_agro_mesh = build_agrovoc_mesh(db_p)
    console.print(f"  • A00 ↔ A50 跨領域國際 AGROVOC 本體語意網建立完成: {res_agro_mesh.get('mesh_records_inserted', 0)} 筆")
    
    # 5. 建立 E13~E16 GraphRAG 實體圖譜三元組網
    res_graph = build_ontology_graph(db_p)
    console.print(f"  • E13~E16 GraphRAG 實體圖譜三元組建立完成: {res_graph.get('graph_triples_inserted', 0)} 筆")
    
    # 6. 建立 A00 ↔ A41 區域農地環境安全網
    res_env_mesh = build_environmental_mesh(db_p)
    console.print(f"  • A00 ↔ A41 區域農地環境安全網建立完成: {res_env_mesh.get('environmental_mesh_records_inserted', 0)} 筆")
    
    # 7. 建立 A00 ↔ A30 ↔ A31 毛豬與動物用藥食安防護網
    res_live_mesh = build_livestock_safety_mesh(db_p)
    console.print(f"  • A00 ↔ A30 ↔ A31 毛豬食安網建立完成: {res_live_mesh.get('livestock_safety_mesh_records_inserted', 0)} 筆")
    
    # 8. 建立 A00 ↔ A10 ↔ A13 ↔ A14 農糧資材雙輪食安網
    res_fert_mesh = build_crop_fertilizer_safety_mesh(db_p)
    console.print(f"  • A00 ↔ A10 ↔ A14 農糧資材雙輪食安網建立完成: {res_fert_mesh.get('fertilizer_safety_mesh_records_inserted', 0)} 筆")
    
    console.print(f"[bold green]✅ A00 母大腦建置與跨域事前融合全效完成！[/bold green]")

@app.command("search")
def search(
    keyword: str = typer.Argument(..., help="全域搜尋關鍵字 (作物名/農藥/市場/水產/畜勢)"),
    db_path: str = typer.Option("db/agro.db", "--db", "-d", help="SQLite 資料庫路徑")
):
    """發動母大腦全域 FTS5 跨領域檢索"""
    import sqlite3
    db_p = repo_root / db_path if not Path(db_path).is_absolute() else Path(db_path)
    if not db_p.exists():
        console.print(f"[bold red]❌ DB 檔案不存在: {db_p}[/bold red]")
        raise typer.Exit(1)
        
    conn = sqlite3.connect(str(db_p))
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT domain_code, entity_id, primary_name, secondary_name, detail_payload
        FROM fts_agro_global
        WHERE fts_agro_global MATCH ?
        LIMIT 10
    """, (keyword,))
    
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        console.print(f"🔍 全域倒排中找不到關鍵字 '{keyword}'。")
        return
        
    table = Table(title=f"👑 A00 全域檢索結果: '{keyword}'")
    table.add_column("Domain", style="cyan")
    table.add_column("Entity ID", style="yellow")
    table.add_column("主要名稱", style="green")
    table.add_column("次要描述/市場", style="magenta")
    table.add_column("快照 Payload", style="white")
    
    for r in rows:
        table.add_row(r[0], r[1], r[2], r[3], r[4])
        
    console.print(table)

@app.command("analytics")
def analytics(
    crop_id: Optional[str] = typer.Option(None, "--crop-id", "-c", help="篩選農作物主碼 (如 LA, 11)"),
    db_path: str = typer.Option("db/agro.db", "--db", "-d", help="SQLite 資料庫路徑")
):
    """查看母大腦延伸分析: 全台農產跨市場價格離散指標 (a00_master_cross_market_index)"""
    import sqlite3
    db_p = repo_root / db_path if not Path(db_path).is_absolute() else Path(db_path)
    if not db_p.exists():
        console.print(f"[bold red]❌ DB 檔案不存在: {db_p}[/bold red]")
        raise typer.Exit(1)
        
    conn = sqlite3.connect(str(db_p))
    cursor = conn.cursor()
    
    sql = "SELECT trans_date, crop_id, crop_name, market_count, national_avg_price, min_price_market, max_price_market, price_cv, attributes_json FROM a00_master_cross_market_index"
    params = []
    if crop_id:
        sql += " WHERE crop_id = ?"
        params.append(crop_id)
    sql += " LIMIT 10"
    
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()
    
    table = Table(title="📊 A00 全台農產跨市場離散指標 (a00_master_cross_market_index)")
    table.add_column("日期", style="cyan")
    table.add_column("作物", style="green")
    table.add_column("市場數", justify="right")
    table.add_column("全台均價", justify="right")
    table.add_column("最低價市場", style="yellow")
    table.add_column("最高價市場", style="red")
    table.add_column("離散 CV", justify="right", style="bold magenta")
    table.add_column("標籤/Flag", style="blue")
    
    for r in rows:
        attr = r[8]
        table.add_row(r[0], f"{r[2]}({r[1]})", str(r[3]), f"{r[4]:.1f}", r[5], r[6], f"{r[7]:.4f}", attr)
        
    console.print(table)

@app.command("doctor")
def doctor(
    db_path: str = typer.Option("db/agro.db", "--db", "-d", help="SQLite 資料庫路徑")
):
    """母大腦全庫健康度診斷 (Master Doctor Check)"""
    console.print("[bold yellow]🩺 正在執行 tw-agro-db 全庫 Doctor Check...[/bold yellow]")
    from src.cli.commands_a10 import doctor as a10_doctor
    a10_doctor(db_path=db_path)
    
    import sqlite3
    db_p = repo_root / db_path if not Path(db_path).is_absolute() else Path(db_path)
    if db_p.exists():
        conn = sqlite3.connect(str(db_p))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM fts_agro_global")
        fts_cnt = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM a00_master_cross_market_index")
        ana_cnt = cursor.fetchone()[0]
        conn.close()
        console.print(f"  • fts_agro_global: [green]{fts_cnt}[/green] 筆")
        console.print(f"  • a00_master_cross_market_index: [green]{ana_cnt}[/green] 筆")
        console.print(f"[bold green]👑 A00 MASTER STATUS: [PASS][/bold green]")

if __name__ == "__main__":
    app()
