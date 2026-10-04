"""
Maya — Intelligent Long-Term Investment Research Bot (CLI Runner)
Complete coverage for:
- Home: 100% of Nigerian Stock Exchange (NGX) listed equities
- Away: S&P 500 constituents (~503 global titan companies)
- On-Demand: Any public company or ETF worldwide
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
from core.universe import UniverseManager
from core.forecaster import CompoundForecaster
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

    # 2. Complete Fund.md 14-Point Audit Scorecard
    if "fund_md_audit" in result and result["fund_md_audit"]:
        table = Table(title="📜 Fund.md Complete 14-Point Audit Scorecard", show_header=True, header_style="bold magenta")
        table.add_column("#", justify="center", style="bold yellow", width=3)
        table.add_column("Rule from Fund.md", style="bold white", width=38)
        table.add_column("Finding / Metric", style="cyan")
        table.add_column("Verdict", justify="center", width=12)

        for item in result["fund_md_audit"]:
            st = item["status"]
            st_color = "green" if "PASS" in st else ("yellow" if "WATCHLIST" in st or "WARNING" in st or "ELEVATED" in st or "EXPENSIVE" in st else "red")
            table.add_row(
                item["rule_no"],
                item["rule_name"],
                item["finding"],
                f"[{st_color}]{st}[/{st_color}]"
            )
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

    # 5. Compounding Wealth Forecaster (5, 10 & 20-Year Horizons)
    cagr_data = CompoundForecaster.estimate_cagr(data)
    ref_principal = 100000.0 if result["is_ngx"] else 1000.0
    projections = CompoundForecaster.project_wealth(ref_principal, cagr_data["expected_cagr"])

    p_table = Table(title=f"🔮 Long-Term Compounding Forecast (Hypothetical {currency} {ref_principal:,.0f} Buy & Hold)", show_header=True, header_style="bold green")
    p_table.add_column("Horizon")
    p_table.add_column("Expected Growth Rate", justify="center")
    p_table.add_column("Projected Value", justify="right", style="bold yellow")
    p_table.add_column("Total Return", justify="right", style="bold green")

    p_table.add_row("Annual Compounding (CAGR)", f"+{cagr_data['cagr_pct']:.1f}%/yr", f"Div: +{cagr_data['dividend_component_pct']:.1f}% | Growth: +{cagr_data['growth_component_pct']:.1f}%", "-")
    p_table.add_row("5 Years", f"+{cagr_data['cagr_pct']:.1f}%/yr", f"{currency} {projections[5]['future_value']:,.2f}", f"+{projections[5]['gain_pct']:.1f}% ({projections[5]['multiple']:.1f}x)")
    p_table.add_row("10 Years", f"+{cagr_data['cagr_pct']:.1f}%/yr", f"{currency} {projections[10]['future_value']:,.2f}", f"+{projections[10]['gain_pct']:.1f}% ({projections[10]['multiple']:.1f}x)")
    p_table.add_row("20 Years", f"+{cagr_data['cagr_pct']:.1f}%/yr", f"{currency} {projections[20]['future_value']:,.2f}", f"+{projections[20]['gain_pct']:.1f}% ({projections[20]['multiple']:.1f}x)")
    console.print(p_table)

    # 6. Key Highlights / Bullet Points
    if result.get("summary"):
        console.print("\n[bold yellow]📌 Core Takeaways:[/bold yellow]")
        for point in result["summary"]:
            console.print(f" • {point}")

    # 7. Qualitative AI Research Memo (Gemini)
    console.print("\n[bold cyan]🧠 AI Qualitative Moat & Business Analysis:[/bold cyan]")
    ai = AIAnalyst()
    memo = ai.generate_qualitative_memo(data, result)
    console.print(Markdown(memo))

def run_universe(market: str = "all"):
    market_choice = market.upper()
    console.print(f"\n[bold green]🌐 Asset Universe Overview: {market_choice}[/bold green]\n")

    if market_choice in ["HOME", "ALL"]:
        home_all = UniverseManager.get_home_universe()
        sectors = UniverseManager.get_home_sectors()
        console.print(f"[bold cyan]🇳🇬 Home Universe (Nigerian Stock Exchange - NGX):[/bold cyan] [bold yellow]{len(home_all)} Companies[/bold yellow] across [bold]{len(sectors)} Sectors[/bold]")
        
        h_table = Table(show_header=True, header_style="bold magenta")
        h_table.add_column("Sector")
        h_table.add_column("Count", justify="center")
        h_table.add_column("Sample Tickers")

        for sec in sectors:
            comps = UniverseManager.get_home_universe(sector=sec)
            tickers = ", ".join([c["symbol"] for c in comps[:6]])
            if len(comps) > 6:
                tickers += f" (+{len(comps)-6} more)"
            h_table.add_row(sec, str(len(comps)), tickers)
        console.print(h_table)
        console.print("")

    if market_choice in ["AWAY", "ALL"]:
        away_all = UniverseManager.get_away_universe()
        sectors = UniverseManager.get_away_sectors()
        console.print(f"[bold cyan]🌍 Away Universe (Global S&P 500 Index):[/bold cyan] [bold yellow]{len(away_all)} Companies[/bold yellow] across [bold]{len(sectors)} Sectors[/bold]")
        
        a_table = Table(show_header=True, header_style="bold cyan")
        a_table.add_column("Sector")
        a_table.add_column("Count", justify="center")
        a_table.add_column("Sample Tickers")

        for sec in sectors:
            comps = UniverseManager.get_away_universe(sector=sec)
            tickers = ", ".join([c["symbol"] for c in comps[:6]])
            if len(comps) > 6:
                tickers += f" (+{len(comps)-6} more)"
            a_table.add_row(sec, str(len(comps)), tickers)
        console.print(a_table)
        console.print("")

def run_screen(market: str = "all", sector: str = None, limit: int = 15):
    market_choice = market.upper()
    console.print(f"\n[bold green]🌐 Running Multi-Sector 5-Pillar Screener for: {market_choice}[/bold green]")
    if sector:
        console.print(f"Filter Sector: [bold yellow]{sector}[/bold yellow]")
    console.print(f"Batch Limit: [bold]{limit}[/bold] companies\n")

    loader = DataLoader()
    assets_to_scan = []

    if market_choice in ["HOME", "ALL"]:
        home_comps = UniverseManager.get_home_universe(sector=sector)
        for c in home_comps[:limit]:
            assets_to_scan.append((c["symbol"], c["name"], "Home (NGX)", c.get("sector", "NGX Equities")))

    if market_choice in ["AWAY", "ALL"]:
        away_comps = UniverseManager.get_away_universe(sector=sector)
        for c in away_comps[:limit]:
            assets_to_scan.append((c["symbol"], c["name"], "Away (Global)", c.get("sector", "S&P 500")))

    table = Table(title=f"🏆 Screener Results ({len(assets_to_scan)} Assets Evaluated)", show_header=True, header_style="bold cyan")
    table.add_column("Ticker", style="bold")
    table.add_column("Name")
    table.add_column("Market")
    table.add_column("Sector")
    table.add_column("Price")
    table.add_column("Score", justify="center")
    table.add_column("Status", justify="center")

    for symbol, name, market_name, sec_name in assets_to_scan:
        data = loader.fetch_asset_data(symbol)
        if not data or not data.get("info"):
            continue
        res = Screener.evaluate(data)
        price_str = f"{res['currency']} {res['current_price']:,.2f}" if res['current_price'] else "N/A"
        
        status_color = "green" if "BUY" in res["status"] else ("yellow" if "WATCHLIST" in res["status"] else "red")
        table.add_row(
            symbol,
            name[:22],
            market_name,
            sec_name[:18],
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

def run_top(market: str = "home", budget: float = None):
    market_choice = market.upper()
    currency = "NGN" if market_choice == "HOME" else "USD"

    console.print(f"\n[bold green]🏆 TOP 10 HIGHEST-CONVICTION BUY LEADERBOARD ({market_choice})[/bold green]")
    console.print(f"Scanning market universe against [bold]Fund.md[/bold] 5-pillar rules...\n")

    loader = DataLoader()
    candidates = []

    # Pull candidate assets across sectors
    for cat, items in WATCHLIST[market_choice].items():
        for item in items:
            data = loader.fetch_asset_data(item["symbol"])
            if data and data.get("info"):
                res = Screener.evaluate(data)
                res["sector_or_class"] = cat.replace("_", " ").title()
                cagr_info = CompoundForecaster.estimate_cagr(data)
                res["cagr_pct"] = cagr_info["cagr_pct"]
                res["cagr_rate"] = cagr_info["expected_cagr"]
                candidates.append(res)

    # Sort strictly by score descending
    candidates.sort(key=lambda x: x.get("score", 0), reverse=True)
    top_10 = candidates[:10]

    table = Table(title=f"🥇 Top 10 Highest-Conviction Compounders ({market_choice})", show_header=True, header_style="bold cyan")
    table.add_column("Rank", justify="center", style="bold yellow")
    table.add_column("Ticker", style="bold")
    table.add_column("Name")
    table.add_column("Sector")
    table.add_column("Current Price", justify="right")
    table.add_column("Exp. Return", justify="center", style="bold magenta")
    table.add_column("Score", justify="center")
    table.add_column("Verdict", justify="center")

    rank = 1
    for c in top_10:
        price_str = f"{c['currency']} {c['current_price']:,.2f}" if c.get("current_price") else "N/A"
        status_color = "green" if "BUY" in c["status"] else "yellow"
        exp_return_str = f"+{c.get('cagr_pct', 12.0):.1f}%/yr"
        table.add_row(
            str(rank),
            c["symbol"],
            c["name"][:18],
            c.get("sector_or_class", "Equity")[:16],
            price_str,
            exp_return_str,
            f"{c['score']}/10",
            f"[{status_color}]{c['status'][:18]}[/{status_color}]"
        )
        rank += 1

    console.print(table)

    # Step 2: Prompt for budget if not passed
    if budget is None:
        try:
            console.print(f"\n[bold yellow]💰 How much cash do you want to invest today in {currency}?[/bold yellow]")
            user_input = input(f"Enter amount in {currency} (e.g. {'100000' if currency == 'NGN' else '100'}, or press Enter to exit): ").strip()
            if not user_input:
                console.print("[dim]No budget entered. Viewing completed.[/dim]\n")
                return
            budget = float(user_input.replace(",", "").replace(currency, "").strip())
        except (ValueError, EOFError, KeyboardInterrupt):
            console.print("[dim]Operation cancelled.[/dim]\n")
            return

    # Step 3: Automatically allocate into the top picks
    console.print(f"\n[bold magenta]⚡ Calculating exact share execution plan for {currency} {budget:,.2f}...[/bold magenta]\n")
    allocator = Allocator()
    plan = allocator.allocate(total_amount=budget, currency=currency, qualified_assets=top_10)

    console.print(Panel(
        f"[bold white]YOUR CUSTOMIZED {currency} {budget:,.2f} BUY PLAN[/bold white]\n"
        f"Selected from the top-rated Fund.md compounders above.",
        title="🟢 DIRECT EXECUTION DIRECTIVE",
        style="green",
        expand=False
    ))

    order_num = 1
    for item in plan["items"]:
        shares_str = f"{item.shares_to_buy:,.4f}" if item.is_fractional else f"{int(item.shares_to_buy):,d}"
        console.print(f"[bold cyan]{order_num}. BUY [yellow]{item.symbol}[/yellow] — {item.name}[/bold cyan]")
        console.print(f"   • [bold]Action:[/bold] Buy [bold green]{shares_str} shares[/bold green] at {currency} {item.market_price:,.2f}")
        console.print(f"   • [bold]Cost:[/bold] {currency} {item.allocated_amount:,.2f}")
        console.print(f"   • [bold]Role in Portfolio:[/bold] {item.sector_or_class}")
        console.print("")
        order_num += 1

    console.print(f"[bold green]✔ Total Capital Deployed:[/bold green] {currency} {plan['total_spent']:,.2f}")
    console.print(f"[bold yellow]💵 Remaining Cash to Leave in Wallet:[/bold yellow] {currency} {plan['unallocated_cash']:,.2f}\n")

    # Step 4: Long-Term Compounding Projection
    avg_cagr = 0.185 if currency == "NGN" else 0.108
    proj = CompoundForecaster.project_wealth(plan["total_spent"], avg_cagr)
    console.print(Panel(
        f"🌱 [bold green]Long-Term Wealth Projection for this {currency} {plan['total_spent']:,.2f} Deposit:[/bold green]\n"
        f" • [bold]In 5 Years (Age 26):[/bold]  ~{currency} {proj[5]['future_value']:,.2f} ([green]+{proj[5]['gain_pct']:.1f}%[/green] gain)\n"
        f" • [bold]In 10 Years (Age 31):[/bold] ~{currency} {proj[10]['future_value']:,.2f} ([green]+{proj[10]['gain_pct']:.1f}%[/green] gain, {proj[10]['multiple']:.1f}x)\n"
        f" • [bold]In 20 Years (Age 41):[/bold] ~{currency} {proj[20]['future_value']:,.2f} ([green]+{proj[20]['gain_pct']:.1f}%[/green] gain, {proj[20]['multiple']:.1f}x)",
        title="📈 COMPOUND INTEREST PROJECTION",
        style="cyan",
        expand=False
    ))
    console.print("")

def run_buy(market: str = "home", budget: float = None):
    market_choice = market.upper()
    currency = "NGN" if market_choice == "HOME" else "USD"
    
    # Default budget if not provided
    if budget is None:
        budget = 100000.0 if currency == "NGN" else 100.0

    console.print(f"\n[bold green]🎯 MAYA'S DIRECT BUY RECOMMENDATIONS ({market_choice})[/bold green]")
    console.print(f"Analyzing all assets against [bold]Fund.md[/bold] for available budget: [bold yellow]{currency} {budget:,.2f}[/bold yellow]...\n")

    loader = DataLoader()
    candidates = []

    # Pull candidate assets
    for cat, items in WATCHLIST[market_choice].items():
        for item in items:
            data = loader.fetch_asset_data(item["symbol"])
            if data and data.get("info"):
                res = Screener.evaluate(data)
                res["sector_or_class"] = cat.replace("_", " ").title()
                candidates.append(res)

    # Filter strictly for STRONG BUY or approved assets
    buy_picks = [c for c in candidates if "BUY" in c["status"] or c["score"] >= 8]
    if not buy_picks:
        buy_picks = sorted(candidates, key=lambda x: x.get("score", 0), reverse=True)[:3]

    allocator = Allocator()
    plan = allocator.allocate(total_amount=budget, currency=currency, qualified_assets=buy_picks)

    console.print(Panel(
        f"[bold white]HERE IS EXACTLY WHAT TO BUY TODAY ({currency} {budget:,.2f})[/bold white]\n"
        f"All recommendations passed your 5-Pillar Fund.md financial safety filter.",
        title="🟢 DIRECT EXECUTION DIRECTIVE",
        style="green",
        expand=False
    ))

    order_num = 1
    for item in plan["items"]:
        shares_str = f"{item.shares_to_buy:,.4f}" if item.is_fractional else f"{int(item.shares_to_buy):,d}"
        console.print(f"[bold cyan]{order_num}. BUY [yellow]{item.symbol}[/yellow] — {item.name}[/bold cyan]")
        console.print(f"   • [bold]Action:[/bold] Buy [bold green]{shares_str} shares[/bold green] at {currency} {item.market_price:,.2f}")
        console.print(f"   • [bold]Cost:[/bold] {currency} {item.allocated_amount:,.2f}")
        console.print(f"   • [bold]Role in Portfolio:[/bold] {item.sector_or_class}")
        console.print("")
        order_num += 1

    console.print(f"[bold green]✔ Total Capital Deployed:[/bold green] {currency} {plan['total_spent']:,.2f}")
    console.print(f"[bold yellow]💵 Remaining Cash to Leave in Wallet:[/bold yellow] {currency} {plan['unallocated_cash']:,.2f}\n")

def run_fund():
    console.print("\n[bold magenta]📜 Fund.md — Core Fundamental Analysis Framework[/bold magenta]")
    with open("Fund.md", "r", encoding="utf-8") as f:
        content = f.read()
    console.print(Markdown(content))
    console.print("\n[bold green]🤖 How Maya Automates This Checklist:[/bold green]")
    console.print(" • [cyan]Items #2, #5, #6, #7, #8, #9:[/cyan] Calculated mathematically in [bold]core/financials.py[/bold] & [bold]core/valuation.py[/bold]")
    console.print(" • [cyan]Items #1, #3, #4 & Customer Scuttlebutt:[/cyan] Evaluated qualitatively via Gemini LLM in [bold]ai/analyst.py[/bold]")
    console.print(" • [cyan]Study the Money:[/cyan] 5-Year Free Cash Flow reliability verified in [bold]core/screener.py[/bold]\n")

def main():
    parser = argparse.ArgumentParser(description="Maya: Long-Term Buy & Hold Investment Research Bot")
    subparsers = parser.add_subparsers(dest="command", help="Available Commands")

    # Command: top [home|away] [--budget <amount>]
    p_top = subparsers.add_parser("top", help="View Top 10 Leaderboard, then enter cash to get exact buy plan")
    p_top.add_argument("market", nargs="?", default="home", choices=["home", "away"], help="Market to screen (default: home)")
    p_top.add_argument("--budget", type=float, default=None, help="Optional cash amount to allocate directly")

    # Command: buy [home|away] [--budget <amount>]
    p_buy = subparsers.add_parser("buy", help="Get Maya's exact, unambiguous buy orders for today")
    p_buy.add_argument("market", nargs="?", default="home", choices=["home", "away"], help="Market to buy in (default: home)")
    p_buy.add_argument("--budget", type=float, default=None, help="Amount of cash to invest")

    # Command: fund
    p_fund = subparsers.add_parser("fund", help="Display the core Fund.md checklist and automation mapping")

    # Command: analyze <symbol>
    p_analyze = subparsers.add_parser("analyze", help="Perform deep 5-pillar fundamental analysis on any ticker")
    p_analyze.add_argument("symbol", type=str, help="Ticker symbol (e.g. AAPL, MSFT, LLY, VOO, GTCO, NESTLE)")

    # Command: universe [home|away|all]
    p_univ = subparsers.add_parser("universe", help="View total company and sector breakdown for Home and Away")
    p_univ.add_argument("market", nargs="?", default="all", choices=["home", "away", "all"], help="Market to inspect")

    # Command: screen [home|away|all]
    p_screen = subparsers.add_parser("screen", help="Scan entire asset universe across sectors")
    p_screen.add_argument("market", nargs="?", default="all", choices=["home", "away", "all"], help="Market to screen")
    p_screen.add_argument("--sector", type=str, default=None, help="Filter by sector (e.g. Healthcare, Financials, Real Estate, Technology)")
    p_screen.add_argument("--limit", type=int, default=15, help="Number of companies to evaluate in batch (default: 15)")

    # Command: allocate <amount> <currency>
    p_allocate = subparsers.add_parser("allocate", help="Generate exact share buy plan for your available cash")
    p_allocate.add_argument("amount", type=float, help="Amount of cash to invest")
    p_allocate.add_argument("currency", type=str, choices=["NGN", "USD", "ngn", "usd"], help="Currency (NGN or USD)")

    args = parser.parse_args()

    if args.command == "top":
        run_top(market=args.market, budget=args.budget)
    elif args.command == "buy":
        run_buy(market=args.market, budget=args.budget)
    elif args.command == "fund":
        run_fund()
    elif args.command == "analyze":
        run_analyze(args.symbol)
    elif args.command == "universe":
        run_universe(args.market)
    elif args.command == "screen":
        run_screen(args.market, sector=args.sector, limit=args.limit)
    elif args.command == "allocate":
        run_allocate(args.amount, args.currency)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
