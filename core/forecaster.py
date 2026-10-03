"""
Long-Term Compounding & Wealth Forecaster for Maya.
Uses John Bogle / Warren Buffett's fundamental total return formula:
Expected Return = Dividend Yield + Earnings/FCF Growth +/- Valuation Multiple Expansion
"""

from typing import Dict, Any, List

class CompoundForecaster:
    @staticmethod
    def estimate_cagr(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Estimate conservative long-term annual return (CAGR).
        """
        info = data.get("info", {})
        is_ngx = data.get("is_ngx", False)
        
        # 1. Dividend Yield component
        div_yield = float(info.get("dividendYield") or 0.0)
        if div_yield > 1.0: # If given as percentage e.g. 8.5
            div_yield = div_yield / 100.0

        # 2. Earnings / FCF Growth component
        earnings_growth = float(info.get("earningsGrowth") or info.get("revenueGrowth") or 0.0)
        
        # Guardrails: clamp growth rates to realistic 10-20 year sustainable levels
        if is_ngx:
            # Nigerian nominal growth reflects local inflation + volume expansion
            base_growth = max(0.08, min(earnings_growth, 0.22)) if earnings_growth > 0 else 0.12
            # Blue-chip Nigerian dividends
            div_component = max(0.05, min(div_yield, 0.15)) if div_yield > 0 else 0.07
            cagr = div_component + base_growth
            # Clamp Nigerian nominal return between 14% and 26%
            cagr = max(0.14, min(cagr, 0.25))
        else:
            # Global / US market expectations
            quote_type = info.get("quoteType", "").upper()
            if quote_type == "ETF":
                # Broad index (e.g. VOO / S&P 500) historical average is ~10% in USD
                cagr = 0.102
                div_component = div_yield if div_yield > 0 else 0.015
                base_growth = 0.087
            else:
                base_growth = max(0.05, min(earnings_growth, 0.16)) if earnings_growth > 0 else 0.09
                div_component = min(div_yield, 0.07)
                cagr = div_component + base_growth
                # Clamp US equity return between 8% and 18%
                cagr = max(0.085, min(cagr, 0.17))

        return {
            "expected_cagr": cagr,
            "cagr_pct": cagr * 100.0,
            "dividend_component_pct": div_component * 100.0,
            "growth_component_pct": (cagr - div_component) * 100.0
        }

    @staticmethod
    def project_wealth(principal: float, annual_rate: float, years: List[int] = [5, 10, 20]) -> Dict[int, Dict[str, float]]:
        """
        Calculate future values for principal over 5, 10, and 20-year horizons.
        """
        projections = {}
        for y in years:
            future_val = principal * ((1.0 + annual_rate) ** y)
            gain_pct = ((future_val - principal) / principal) * 100.0
            projections[y] = {
                "future_value": future_val,
                "gain_pct": gain_pct,
                "multiple": future_val / principal
            }
        return projections
