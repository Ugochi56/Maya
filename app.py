"""
Maya — Intelligent Long-Term Investment Research Bot (CLI Runner)
"""

import sys
import argparse

# Force UTF-8 stream handling on Windows to prevent UnicodeEncodeError with emojis/symbols
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

from core.data_loader import DataLoader
from core.screener import Screener
from core.allocator import Allocator
from ai.analyst import AIAnalyst
from config.watchlist import WATCHLIST

console = Console(legacy_windows=False)

def run_analyze(symbol: str):
    console.print(f"\n[bold cyan]🔍 Fetching & analyzing asset:[/bold cyan] [yellow]{symbol.upper()}[/yellow]...")
    loader = DataLoader()
    data = loader.fetch_asset_data(symbol)
    if not data or not data.get("info"):
        console.print(f"[bold red]❌ Failed to retrieve data for ticker '{symbol}'. Check symbol spelling or network.[/bold red]")
        return

    # Screen & Evaluate
    result = Screener.evaluate(data)

    # 1. Header Overview
    name = result["name"]
    price = result["current_price"]
    currency = result["currency"]
    asset_type = result["asset_type"]
    status = result["status"]
    score = result["score"]

    status_color = "green" if "BUY" in status else ("yellow" if "WATCHLIST" in status else "red")
    
    header_text = (
        f"[bold white]{name}[/bold white] ({symbol.upper()})\n"
        f"Asset Class: [magenta]{asset_type}[/magenta] | Market: [blue]{'Home (NGX)' if result['is_ngx'] else 'Away (Global)'}[/blue]\n"
        f"Current Price: [bold]{currency} {price:,.2f}[/bold] | Score: [bold]{score}/10[/bold]\n"
        f"Verdict: [{status_color}][bold]{status}[/bold][/{status_color}]"
    )
    console.print(Panel(header_text, title="📊 Asset Profile", expand=False))

    # 2. Pillar Check Table (For Equities / Pharma / Banks)
    if "pillar_checks" in result and result["pillar_checks"]:
        table = Table(title="🏛️ 5-Pillar Long-Term Durability Test (Fund.md)", show_header=True, header_style="bold magenta")
        table.add_column("Pillar Requirement", style="dim")
        table.add_column("Status", justify="center")

        for pillar, passed in result["pillar_checks"].items():
            status_symbol = "[bold green]PASS ✓[/bold green]" if passed else "[bold red]FAIL ✗[/bold red]"
            table.add_row(pillar, status_symbol)
        console.print(table)

    # 3. Valuation & Financial Multiples
    if "valuation" in result and result["valuation"]:
        v = result["valuation"]
        f = result.get("financials", {})
        v_table = Table(title="📈 Valuation Multiples & Capital Efficiency", show_header=True, header_style="bold cyan")
        v_table.add_column("Metric")
        v_table.add_column("Value")
        v_table.add_column("Context")

        pe = f"{v['trailing_pe']:.1f}x" if v.get("trailing_pe") else "N/A"
        v_table.add_row("P/E Ratio (Trailing)", pe, "Lower is cheaper relative to net earnings")

        fwd_pe = f"{v['forward_pe']:.1f}x" if v.get("forward_pe") else "N/A"
        v_table.add_row("P/E Ratio (Forward)", fwd_pe, "Next 12-month expected earnings multiple")

        ps = f"{v['price_to_sales']:.1f}x" if v.get("price_to_sales") else "N/A"
        v_table.add_row("Price-to-Sales (P/S)", ps, "Valuation relative to top-line revenue")

        pfcf = f"{v['price_to_fcf']:.1f}x" if v.get("price_to_fcf") else "N/A"
        v_table.add_row("Price-to-Free-Cash-Flow (P/FCF)", pfcf, "Real cash generation vs market price")

        ev_ebitda = f"{v['ev_to_ebitda']:.1f}x" if v.get("ev_to_ebitda") else "N/A"
        v_table.add_row("EV / EBITDA", ev_ebitda, "Enterprise multiple accounting for debt and cash")

        div = f"{v['dividend_yield_pct']:.2f}%" if v.get("dividend_yield_pct") else "0.00%"
        v_table.add_row("Dividend Yield", div, "Annual cash return paid to shareholders")

        roe = f"{f['return_on_equity']*100:.1f}%" if f.get("return_on_equity") else "N/A"
        v_table.add_row("Return on Equity (ROE)", roe, "Capital compounding engine (> 12% is desirable)")

        console.print(v_table)

    # 4. ETF Specific Table
    if "etf_analysis" in result:
        etf = result["etf_analysis"]
        e_table = Table(title="📦 ETF Inspection", show_header=True, header_style="bold green")
        e_table.add_column("Attribute")
        e_table.add_column("Value")
        
        exp = f"{etf['expense_ratio']*100:.2f}%/yr" if etf.get('expense_ratio') else "N/A"
        e_table.add_row("Expense Ratio", exp)
        e_table.add_row("Asset Class Focus", str(etf.get("category")))
        e_table.add_row("Dividend Yield", f"{etf.get('dividend_yield_pct'):.2f}%")
        e_table.add_row("Classification", etf.get("verdict"))
        console.print(e_table)

    # 5. Key Highlights / Bullet Points
    if result.get("summary"):
        console.print("\n[bold yellow]📌 Core Takeaways:[/bold yellow]")
        for point in result["summary"]:
            console.print(f" • {point}")

    # 6. Qualitative AI Research Memo (Gemini)
    console.print("\n[bold cyan]🧠 AI Qualitative Moat & Business Analysis:[/bold cyan]")
    ai = AIAnalyst()
    memo = ai.generate_qualitative_memo(data, result)
    console.print(Markdown(memo))

def run_screen(market: str = "all"):
    market_choice = market.upper()
    console.print(f"\n[bold green]🌐 Running Multi-Sector 5-Pillar Screener for: {market_choice}[/bold green]...")
    loader = DataLoader()

    categories_to_scan = []
    if market_choice in ["HOME", "ALL"]:
        for cat, items in WATCHLIST["HOME"].items():
            for item in items:
                categories_to_scan.append((item["symbol"], "Home (NGX)", cat))
    if market_choice in ["AWAY", "ALL"]:
        for cat, items in WATCHLIST["AWAY"].items():
            for item in items:
                categories_to_scan.append((item["symbol"], "Away (Global)", cat))

    table = Table(title=f"🏆 Screener Results ({len(categories_to_scan)} Assets)", show_header=True, header_style="bold cyan")
    table.add_column("Ticker", style="bold")
    table.add_column("Name")
    table.add_column("Market")
    table.add_column("Sector/Category")
    table.add_column("Price")
    table.add_column("Score", justify="center")
    table.add_column("Status", justify="center")

    for symbol, market_name, category in categories_to_scan:
        data = loader.fetch_asset_data(symbol)
        if not data or not data.get("info"):
            continue
        res = Screener.evaluate(data)
        price_str = f"{res['currency']} {res['current_price']:,.2f}" if res['current_price'] else "N/A"
        
        status_color = "green" if "BUY" in res["status"] else ("yellow" if "WATCHLIST" in res["status"] else "red")
        table.add_row(
            symbol,
            res["name"][:22],
            market_name,
            category.replace("_", " ").title(),
            price_str,
            f"{res['score']}/10",
            f"[{status_color}]{res['status'][:18]}[/{status_color}]"
        )

    console.print(table)

def run_allocate(amount: float, currency: str):
    console.print(f"\n[bold magenta]💰 Precision Portfolio Budget Allocator[/bold magenta]")
    console.print(f"Deploying Budget: [bold yellow]{currency.upper()} {amount:,.2f}[/bold yellow] into Buy & Hold Assets...")

    loader = DataLoader()
    market = "HOME" if currency.upper() == "NGN" else "AWAY"
    
    # Ingest watchlist assets for this currency
    candidates = []
    for cat, items in WATCHLIST[market].items():
        for item in items:
            data = loader.fetch_asset_data(item["symbol"])
            if data and data.get("info"):
                res = Screener.evaluate(data)
                res["sector_or_class"] = cat.replace("_", " ").title()
                candidates.append(res)

    allocator = Allocator()
    plan = allocator.allocate(total_amount=amount, currency=currency.upper(), qualified_assets=candidates)

    table = Table(title=f"📋 Exact Buy Order Plan ({currency.upper()} {amount:,.2f})", show_header=True, header_style="bold green")
    table.add_column("Ticker", style="bold")
    table.add_column("Asset Class")
    table.add_column("Current Price")
    table.add_column("Shares to Buy", justify="right", style="bold yellow")
    table.add_column("Total Allocated", justify="right")

    for item in plan["items"]:
        shares_str = f"{item.shares_to_buy:,.4f}" if item.is_fractional else f"{int(item.shares_to_buy):,d}"
        table.add_row(
            f"{item.symbol} ({item.name[:18]})",
            item.sector_or_class,
            f"{item.currency} {item.market_price:,.2f}",
            shares_str,
            f"{item.currency} {item.allocated_amount:,.2f}"
        )

    console.print(table)
    console.print(f"\n[bold green]Total Deployed:[/bold green] {currency.upper()} {plan['total_spent']:,.2f}")
    console.print(f"[bold yellow]Remaining Cash Balance:[/bold yellow] {currency.upper()} {plan['unallocated_cash']:,.2f}\n")

def main():
    parser = argparse.ArgumentParser(description="Maya: Long-Term Buy & Hold Investment Research Bot")
    subparsers = parser.add_subparsers(dest="command", help="Available Commands")

    # Command: analyze <symbol>
    p_analyze = subparsers.add_parser("analyze", help="Perform deep 5-pillar fundamental analysis on any ticker")
    p_analyze.add_argument("symbol", type=str, help="Ticker symbol (e.g. AAPL, MSFT, LLY, VOO, GTCO.LG, NEWGOLD.LG)")

    # Command: screen [home|away|all]
    p_screen = subparsers.add_parser("screen", help="Scan entire asset universe across sectors")
    p_screen.add_argument("market", nargs="?", default="all", choices=["home", "away", "all"], help="Market to screen")

    # Command: allocate <amount> <currency>
    p_allocate = subparsers.add_parser("allocate", help="Generate exact share buy plan for your available cash")
    p_allocate.add_argument("amount", type=float, help="Amount of cash to invest")
    p_allocate.add_argument("currency", type=str, choices=["NGN", "USD", "ngn", "usd"], help="Currency (NGN or USD)")

    args = parser.parse_args()

    if args.command == "analyze":
        run_analyze(args.symbol)
    elif args.command == "screen":
        run_screen(args.market)
    elif args.command == "allocate":
        run_allocate(args.amount, args.currency)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
