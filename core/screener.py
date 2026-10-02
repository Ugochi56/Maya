"""
Screener and 5-Pillar Qualification Engine for Maya.
Evaluates whether an asset qualifies as a 'Sound Long-Term Buy & Hold' candidate.
"""

from typing import Dict, Any
from core.classifier import classify_asset, AssetType
from core.financials import FinancialAnalyzer
from core.valuation import ValuationAnalyzer
from core.etf_analyzer import ETFAnalyzer
from core.reit_analyzer import REITAnalyzer

class Screener:
    @staticmethod
    def evaluate(asset_data: Dict[str, Any]) -> Dict[str, Any]:
        symbol = asset_data["symbol"]
        info = asset_data.get("info", {})
        asset_type = classify_asset(symbol, info)

        result = {
            "symbol": symbol,
            "name": info.get("longName") or info.get("shortName") or symbol,
            "currency": info.get("currency", "USD" if not asset_data.get("is_ngx") else "NGN"),
            "asset_type": asset_type,
            "is_ngx": asset_data.get("is_ngx", False),
            "current_price": info.get("currentPrice") or info.get("regularMarketPrice") or info.get("previousClose"),
            "pillar_checks": {},
            "status": "ANALYZED",
            "score": 0,
            "summary": []
        }

        # Handle ETFs separately
        if asset_type == AssetType.ETF:
            etf_res = ETFAnalyzer.analyze(asset_data)
            result["etf_analysis"] = etf_res
            result["score"] = etf_res["etf_score"]
            result["status"] = "CORE BUY & HOLD" if etf_res["etf_score"] >= 2 else "WATCHLIST"
            result["summary"] = etf_res["insights"]
            return result

        # Handle REITs separately
        if asset_type == AssetType.REIT:
            reit_res = REITAnalyzer.analyze(asset_data)
            result["reit_analysis"] = reit_res
            result["score"] = reit_res["reit_score"]
            result["status"] = "CORE BUY & HOLD" if reit_res["reit_score"] >= 3 else "QUALIFIED INCOME"
            result["summary"] = reit_res["insights"]
            return result

        # For General Equities, Pharma, and Banks: Run Financials & Valuation
        fin_res = FinancialAnalyzer.analyze(asset_data)
        val_res = ValuationAnalyzer.analyze(asset_data)
        result["financials"] = fin_res
        result["valuation"] = val_res

        # Evaluate the 5 Pillars of Sound Investing:
        # Pillar 1: Cash Flow Reliability
        p1_pass = fin_res["fcf_passed"]
        # Pillar 2: Capital Efficiency (ROE/ROIC)
        p2_pass = fin_res["profitability_passed"]
        # Pillar 3: Solvency Stress-Test
        p3_pass = fin_res["solvency_passed"]
        # Pillar 4: Valuation Margin of Safety
        p4_pass = (val_res["valuation_score"] >= 2)

        pillars = {
            "Pillar 1: Free Cash Flow Reliability": p1_pass,
            "Pillar 2: Compounding Engine (ROE/Margins)": p2_pass,
            "Pillar 3: Solvency & Debt Stress-Test": p3_pass,
            "Pillar 4: Margin of Safety Valuation": p4_pass
        }
        result["pillar_checks"] = pillars

        # Calculate Total Score out of 10
        total_score = sum(2 for passed in pillars.values() if passed)
        if val_res["valuation_score"] >= 4:
            total_score += 2

        result["score"] = min(total_score, 10)

        # Classify final recommendation
        if p1_pass and p2_pass and p3_pass:
            if p4_pass:
                result["status"] = "STRONG BUY & HOLD (High Conviction)"
            else:
                result["status"] = "WATCHLIST (Great Business, Wait for Cheaper Price)"
        elif p2_pass and p3_pass:
            result["status"] = "QUALIFIED (Monitor FCF / Growth)"
        else:
            result["status"] = "DO NOT BUY (Fails Soundness Filter)"

        # Collect bullet points
        summary = []
        if p1_pass:
            summary.append("Reliable positive free cash generation")
        else:
            summary.append("Inconsistent cash flows or cash burn")

        if p2_pass:
            roe_val = fin_res['return_on_equity']
            roe_str = f"{roe_val*100:.1f}%" if roe_val else "N/A"
            summary.append(f"High capital efficiency (ROE: {roe_str})")

        if p3_pass:
            summary.append("Clean balance sheet & safe interest coverage")
        else:
            summary.append("Elevated debt or tight liquidity")

        summary.extend(val_res["insights"])
        result["summary"] = summary

        return result
