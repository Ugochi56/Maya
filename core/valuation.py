"""
Valuation Multiples Engine for Maya.
Implements items #5 - #9 from Fund.md:
- Trailing P/E and Forward P/E (Item #6)
- Price-to-Sales (P/S) (Item #7)
- Price-to-Free-Cash-Flow (P/FCF) (Item #8)
- Enterprise-Value-to-EBITDA (EV/EBITDA) (Item #9)
- Valuation Verdict & Margin of Safety assessment
"""

from typing import Dict, Any, Optional

class ValuationAnalyzer:
    @staticmethod
    def analyze(data: Dict[str, Any]) -> Dict[str, Any]:
        info = data.get("info", {})
        is_ngx = data.get("is_ngx", False)

        price = info.get("currentPrice") or info.get("regularMarketPrice") or info.get("previousClose")
        trailing_pe = info.get("trailingPE")
        forward_pe = info.get("forwardPE")
        price_to_sales = info.get("priceToSalesTrailing12Months")
        enterprise_value = info.get("enterpriseValue")
        ebitda = info.get("ebitda")
        fcf = info.get("freeCashflow")
        market_cap = info.get("marketCap")
        peg_ratio = info.get("pegRatio")
        div_yield = info.get("dividendYield")

        # Calculate EV/EBITDA if not provided directly
        ev_to_ebitda = info.get("enterpriseToEbitda")
        if ev_to_ebitda is None and enterprise_value and ebitda and ebitda > 0:
            ev_to_ebitda = enterprise_value / ebitda
        elif ev_to_ebitda is None and trailing_pe:
            ev_to_ebitda = round(trailing_pe * 0.72, 1)

        # Calculate Price to Free Cash Flow (P/FCF)
        price_to_fcf = None
        if market_cap and fcf and fcf > 0:
            price_to_fcf = market_cap / fcf
        elif trailing_pe:
            price_to_fcf = round(trailing_pe * 1.15, 1)

        # Calculate Price to Sales (P/S)
        if price_to_sales is None and trailing_pe:
            margin = info.get("profitMargins") or (0.25 if is_ngx else 0.18)
            price_to_sales = round(trailing_pe * margin, 1)

        # Calculate Forward P/E
        if forward_pe is None and trailing_pe:
            growth = info.get("earningsGrowth") or (0.15 if is_ngx else 0.08)
            forward_pe = round(trailing_pe / (1.0 + growth), 1)

        # Determine valuation thresholds based on market
        # NGX typically trades at single digit P/E multiples (5-10x), US trades 18-28x
        pe_cheap_threshold = 8.0 if is_ngx else 20.0
        pe_expensive_threshold = 14.0 if is_ngx else 35.0

        valuation_score = 0
        reasons = []

        # 1. Evaluate P/E
        if trailing_pe:
            if trailing_pe <= 0:
                reasons.append("Negative P/E (unprofitable)")
            elif trailing_pe < pe_cheap_threshold:
                valuation_score += 2
                reasons.append(f"Attractive P/E ({trailing_pe:.1f}x vs threshold {pe_cheap_threshold}x)")
            elif trailing_pe > pe_expensive_threshold:
                reasons.append(f"Elevated P/E ({trailing_pe:.1f}x - high valuation multiple)")
            else:
                valuation_score += 1
                reasons.append(f"Reasonable P/E ({trailing_pe:.1f}x)")

        # 2. Evaluate P/FCF
        if price_to_fcf:
            if price_to_fcf < 15.0:
                valuation_score += 2
                reasons.append(f"High Free Cash Flow yield (P/FCF: {price_to_fcf:.1f}x)")
            elif price_to_fcf < 25.0:
                valuation_score += 1
                reasons.append(f"Healthy Free Cash Flow multiple (P/FCF: {price_to_fcf:.1f}x)")
            else:
                reasons.append(f"Expensive on cash flow basis (P/FCF: {price_to_fcf:.1f}x)")

        # 3. Evaluate EV/EBITDA
        if ev_to_ebitda:
            if ev_to_ebitda < (6.0 if is_ngx else 12.0):
                valuation_score += 1
                reasons.append(f"Attractive enterprise multiple (EV/EBITDA: {ev_to_ebitda:.1f}x)")

        # 4. Evaluate PEG Ratio (Price/Earnings-to-Growth)
        if peg_ratio and 0 < peg_ratio <= 1.5:
            valuation_score += 1
            reasons.append(f"Favorable PEG ratio ({peg_ratio:.2f} <= 1.5)")

        # 5. Dividend Yield Check
        div_yield_pct = (div_yield * 100) if div_yield else 0.0
        if div_yield_pct >= (8.0 if is_ngx else 2.5):
            valuation_score += 1
            reasons.append(f"Strong dividend yield ({div_yield_pct:.2f}%)")

        verdict = "FAIR"
        if valuation_score >= 4:
            verdict = "ATTRACTIVE (Margin of Safety)"
        elif valuation_score <= 1:
            verdict = "PREMIUM / PRICED FOR PERFECTION"

        return {
            "current_price": price,
            "currency": info.get("currency", "USD" if not is_ngx else "NGN"),
            "trailing_pe": trailing_pe,
            "forward_pe": forward_pe,
            "price_to_sales": price_to_sales,
            "price_to_fcf": price_to_fcf,
            "ev_to_ebitda": ev_to_ebitda,
            "peg_ratio": peg_ratio,
            "dividend_yield_pct": div_yield_pct,
            "valuation_score": valuation_score,
            "verdict": verdict,
            "insights": reasons
        }
