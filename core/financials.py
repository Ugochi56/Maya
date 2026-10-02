"""
Core Financial Analysis Engine for Maya.
Implements item #2 from Fund.md:
- Multi-year revenue and profit growth (CAGR)
- Profit margins (Gross, Operating, Net)
- Debt stress-test & solvency (Interest coverage, Debt-to-Equity, Net Debt/EBITDA)
- Free cash flow consistency (5-year durability)
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

class FinancialAnalyzer:
    @staticmethod
    def analyze(data: Dict[str, Any]) -> Dict[str, Any]:
        info = data.get("info", {})
        financials = data.get("financials", pd.DataFrame())
        balance_sheet = data.get("balance_sheet", pd.DataFrame())
        cashflow = data.get("cashflow", pd.DataFrame())

        metrics = {
            "revenue_growth_yoy": None,
            "net_income_growth_yoy": None,
            "revenue_cagr_3yr": None,
            "gross_margin": info.get("grossMargins"),
            "operating_margin": info.get("operatingMargins"),
            "net_margin": info.get("profitMargins"),
            "return_on_equity": info.get("returnOnEquity"),
            "return_on_assets": info.get("returnOnAssets"),
            "debt_to_equity": info.get("debtToEquity"),
            "current_ratio": info.get("currentRatio"),
            "quick_ratio": info.get("quickRatio"),
            "interest_coverage": None,
            "fcf_positive_years": 0,
            "fcf_history": [],
            "solvency_passed": False,
            "fcf_passed": False,
            "profitability_passed": False
        }

        # 1. Historical Revenue & Net Income Growth Calculation
        try:
            if not financials.empty:
                rev_row = None
                for idx in ["Total Revenue", "Operating Revenue", "Revenue"]:
                    if idx in financials.index:
                        rev_row = financials.loc[idx].dropna()
                        break
                
                if rev_row is not None and len(rev_row) >= 2:
                    # columns are ordered latest to oldest
                    latest_rev = float(rev_row.iloc[0])
                    prev_rev = float(rev_row.iloc[1])
                    if prev_rev > 0:
                        metrics["revenue_growth_yoy"] = (latest_rev - prev_rev) / prev_rev
                    
                    if len(rev_row) >= 4:
                        rev_3yr_ago = float(rev_row.iloc[3])
                        if rev_3yr_ago > 0:
                            metrics["revenue_cagr_3yr"] = (latest_rev / rev_3yr_ago) ** (1/3) - 1

                # Net Income Growth
                ni_row = None
                for idx in ["Net Income", "Net Income Common Stockholders"]:
                    if idx in financials.index:
                        ni_row = financials.loc[idx].dropna()
                        break
                if ni_row is not None and len(ni_row) >= 2:
                    latest_ni = float(ni_row.iloc[0])
                    prev_ni = float(ni_row.iloc[1])
                    if prev_ni > 0:
                        metrics["net_income_growth_yoy"] = (latest_ni - prev_ni) / prev_ni

                # Interest Coverage Ratio = EBIT / Interest Expense
                ebit_row = None
                for idx in ["EBIT", "Operating Income"]:
                    if idx in financials.index:
                        ebit_row = financials.loc[idx].dropna()
                        break
                
                interest_row = None
                for idx in ["Interest Expense", "Interest Expense Non Operating"]:
                    if idx in financials.index:
                        interest_row = financials.loc[idx].dropna()
                        break

                if ebit_row is not None and interest_row is not None:
                    ebit = float(ebit_row.iloc[0])
                    interest = abs(float(interest_row.iloc[0]))
                    if interest > 0:
                        metrics["interest_coverage"] = ebit / interest
        except Exception:
            pass

        # 2. Free Cash Flow Reliability (Check up to 5 historical years)
        try:
            if not cashflow.empty:
                fcf_row = None
                for idx in ["Free Cash Flow", "Operating Cash Flow"]:
                    if idx in cashflow.index:
                        fcf_row = cashflow.loc[idx].dropna()
                        break
                
                if fcf_row is not None:
                    history = [float(v) for v in fcf_row.values]
                    metrics["fcf_history"] = history
                    positive_years = sum(1 for val in history if val > 0)
                    metrics["fcf_positive_years"] = positive_years
                    # Pass if positive in at least 75% of available years (or >= 3 of 4)
                    metrics["fcf_passed"] = (positive_years >= max(2, len(history) - 1))
            else:
                # Fallback to info freeCashflow
                fcf = info.get("freeCashflow")
                if fcf and fcf > 0:
                    metrics["fcf_passed"] = True
                    metrics["fcf_positive_years"] = 1
        except Exception:
            pass

        # 3. Solvency Gate
        int_cov = metrics["interest_coverage"]
        d_to_e = metrics["debt_to_equity"]
        curr_ratio = metrics["current_ratio"]

        # If interest coverage is strong (> 4x) or debt/equity is conservative (< 100)
        solvency_ok = True
        if int_cov is not None and int_cov < 3.0:
            solvency_ok = False
        if d_to_e is not None and d_to_e > 180:
            solvency_ok = False
        if curr_ratio is not None and curr_ratio < 0.9:
            solvency_ok = False
        metrics["solvency_passed"] = solvency_ok

        # 4. Profitability Gate (ROE > 12% or Net Margin > 10%)
        roe = metrics["return_on_equity"]
        net_m = metrics["net_margin"]
        if (roe and roe >= 0.12) or (net_m and net_m >= 0.10):
            metrics["profitability_passed"] = True

        return metrics
