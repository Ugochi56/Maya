"""
Real Estate & REIT Analysis Engine for Maya.
Specialized for evaluating income-producing real estate trusts (Home & Away).
"""

from typing import Dict, Any

class REITAnalyzer:
    @staticmethod
    def analyze(data: Dict[str, Any]) -> Dict[str, Any]:
        info = data.get("info", {})
        is_ngx = data.get("is_ngx", False)

        name = info.get("longName") or data.get("symbol")
        div_yield = info.get("dividendYield")
        payout_ratio = info.get("payoutRatio")
        debt_to_equity = info.get("debtToEquity")
        price_to_book = info.get("priceToBook")
        current_price = info.get("currentPrice") or info.get("regularMarketPrice") or info.get("previousClose")

        reit_score = 0
        reasons = []

        div_pct = (div_yield * 100) if div_yield else 0.0
        # 1. Dividend Yield Check (REITs are primarily income generators)
        if div_pct >= (9.0 if is_ngx else 4.5):
            reit_score += 2
            reasons.append(f"Strong real estate yield ({div_pct:.2f}%)")
        elif div_pct >= 3.0:
            reit_score += 1
            reasons.append(f"Moderate real estate yield ({div_pct:.2f}%)")
        else:
            reasons.append(f"Low distribution yield for a REIT ({div_pct:.2f}%)")

        # 2. Leverage and Solvency
        if debt_to_equity is not None:
            if debt_to_equity < 120:
                reit_score += 2
                reasons.append(f"Conservative debt profile for real estate (D/E: {debt_to_equity})")
            elif debt_to_equity < 200:
                reit_score += 1
                reasons.append("Manageable leverage")
            else:
                reasons.append(f"High real estate leverage (D/E: {debt_to_equity})")

        # 3. Valuation via Price-to-Book (P/B)
        if price_to_book:
            if price_to_book < 1.0:
                reit_score += 1
                reasons.append(f"Trading below Net Asset Value (P/B: {price_to_book:.2f}x)")
            elif price_to_book <= 1.6:
                reit_score += 1
                reasons.append(f"Reasonable book multiple (P/B: {price_to_book:.2f}x)")

        verdict = "ATTRACTIVE REAL ESTATE COMPOUNDER" if reit_score >= 3 else "QUALIFIED INCOME ASSET"

        return {
            "name": name,
            "current_price": current_price,
            "dividend_yield_pct": div_pct,
            "payout_ratio": payout_ratio,
            "debt_to_equity": debt_to_equity,
            "price_to_book": price_to_book,
            "reit_score": reit_score,
            "verdict": verdict,
            "insights": reasons
        }
