"""
ETF Analysis Engine for Maya.
Evaluates exchange-traded funds (both Home & Away) on:
- Expense ratio (lower is better, ideally < 0.20%)
- Fund size / AUM (liquidity safety)
- Dividend yield
- Asset class & focus
"""

from typing import Dict, Any

class ETFAnalyzer:
    @staticmethod
    def analyze(data: Dict[str, Any]) -> Dict[str, Any]:
        info = data.get("info", {})
        is_ngx = data.get("is_ngx", False)

        name = info.get("longName") or info.get("shortName") or data.get("symbol")
        expense_ratio = info.get("netExpenseRatio") or info.get("expenseRatio") or info.get("annualReportExpenseRatio")
        total_assets = info.get("totalAssets") or info.get("marketCap")
        div_yield = info.get("yield") or info.get("dividendYield")
        category = info.get("category") or info.get("fundFamily") or "Broad Market"
        nav_price = info.get("navPrice") or info.get("previousClose")

        etf_score = 0
        reasons = []

        # 1. Expense Ratio Check
        if expense_ratio is not None:
            exp_pct = expense_ratio * 100 if expense_ratio < 1 else expense_ratio
            if exp_pct <= 0.15:
                etf_score += 2
                reasons.append(f"Ultra-low expense ratio ({exp_pct:.2f}%/yr)")
            elif exp_pct <= 0.50:
                etf_score += 1
                reasons.append(f"Acceptable expense ratio ({exp_pct:.2f}%/yr)")
            else:
                reasons.append(f"High expense drag ({exp_pct:.2f}%/yr)")
        else:
            # Some international/NGX ETFs don't report netExpenseRatio through Yahoo
            reasons.append("Expense ratio not published via API (check fund factsheet)")

        # 2. Fund Size / Liquidity
        if total_assets:
            if total_assets > 1_000_000_000:
                etf_score += 2
                reasons.append("Deep liquidity (> $1B AUM)")
            elif total_assets > 50_000_000:
                etf_score += 1
                reasons.append("Sufficient fund size")

        # 3. Dividend Yield
        div_pct = (div_yield * 100) if div_yield else 0.0
        if div_pct > 0:
            reasons.append(f"Distribution yield: {div_pct:.2f}%")

        verdict = "APPROVED CORE ASSET" if etf_score >= 2 or is_ngx else "SUITABLE ETF"

        return {
            "name": name,
            "category": category,
            "expense_ratio": expense_ratio,
            "total_assets": total_assets,
            "dividend_yield_pct": div_pct,
            "nav_price": nav_price,
            "etf_score": etf_score,
            "verdict": verdict,
            "insights": reasons
        }
