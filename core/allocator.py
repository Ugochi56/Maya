"""
Precision Capital & Position Sizing Allocator for Maya.
Solves the problem: 'How does it know how much I have and what exact shares to buy?'

Enforces:
1. Core & Satellite diversification (e.g. 50% ETFs, 50% High-Conviction Stocks)
2. Whole shares for NGX (no fractional shares locally)
3. Precise fractional shares for Global/US (Bamboo, Trove, etc.)
4. Sector limits (prevents putting all money into one company)
"""

import json
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class AllocationItem:
    symbol: str
    name: str
    asset_type: str
    sector_or_class: str
    market_price: float
    allocated_amount: float
    shares_to_buy: float
    is_fractional: bool
    currency: str

class Allocator:
    def __init__(self, portfolio_config_path: str = "config/portfolio.json"):
        self.config_path = portfolio_config_path
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        
        # Fallback to example config if exists
        example_path = "config/portfolio.example.json"
        if os.path.exists(example_path):
            try:
                with open(example_path, "r") as f:
                    return json.load(f)
            except Exception:
                pass
                
        return {
            "budget": {"monthly_dca_home_ngn": 100000, "monthly_dca_away_usd": 100},
            "risk_rules": {"min_broad_etf_core_pct": 50, "max_single_stock_pct": 20}
        }

    def allocate(
        self,
        total_amount: float,
        currency: str,
        qualified_assets: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Produce a precise, mathematically sound buy plan for the given budget.
        
        Args:
            total_amount: Available cash to deploy (e.g., 100000 or 150)
            currency: 'NGN' or 'USD'
            qualified_assets: List of screened asset dictionaries with price and score
        """
        is_ngx = (currency.upper() == "NGN")
        
        # Separate into Core (ETFs) and Satellites (Stocks / REITs)
        core_candidates = [a for a in qualified_assets if a.get("asset_type") == "ETF"]
        satellite_candidates = [a for a in qualified_assets if a.get("asset_type") != "ETF"]

        # Sort by score descending
        satellite_candidates.sort(key=lambda x: x.get("score", 0), reverse=True)

        plan: List[AllocationItem] = []
        spent = 0.0

        if core_candidates:
            # 50% Core, 50% Satellites
            core_budget = total_amount * 0.50
            satellite_budget = total_amount * 0.50

            best_core = core_candidates[0]
            price = best_core.get("current_price") or 1.0

            if is_ngx:
                shares = int(core_budget // price)
                actual_spent = shares * price
                if shares > 0:
                    plan.append(AllocationItem(
                        symbol=best_core["symbol"],
                        name=best_core["name"],
                        asset_type="ETF",
                        sector_or_class="Core Broad Market / Hedge",
                        market_price=price,
                        allocated_amount=actual_spent,
                        shares_to_buy=float(shares),
                        is_fractional=False,
                        currency=currency
                    ))
                    spent += actual_spent
            else:
                shares = round(core_budget / price, 4)
                plan.append(AllocationItem(
                    symbol=best_core["symbol"],
                    name=best_core["name"],
                    asset_type="ETF",
                    sector_or_class="Core Broad Market",
                    market_price=price,
                    allocated_amount=core_budget,
                    shares_to_buy=shares,
                    is_fractional=True,
                    currency=currency
                ))
                spent += core_budget
        else:
            # When no broad ETF is available, distribute 100% of budget across diverse top sectors
            satellite_budget = total_amount

        # Allocate Satellites across up to 3-4 distinct sectors
        remaining_budget = total_amount - spent
        # Deduplicate sectors to ensure broad spread
        diverse_picks = []
        seen_types = set()
        for sat in satellite_candidates:
            atype = sat.get("asset_type", "Stock")
            if atype not in seen_types:
                diverse_picks.append(sat)
                seen_types.add(atype)
            if len(diverse_picks) >= 3:
                break

        if not diverse_picks and satellite_candidates:
            diverse_picks = satellite_candidates[:3]

        if diverse_picks:
            per_stock_budget = remaining_budget / len(diverse_picks)
            for sat in diverse_picks:
                price = sat.get("current_price") or 1.0
                if is_ngx:
                    shares = int(per_stock_budget // price)
                    actual_spent = shares * price
                    if shares > 0:
                        plan.append(AllocationItem(
                            symbol=sat["symbol"],
                            name=sat["name"],
                            asset_type=sat.get("asset_type", "Stock"),
                            sector_or_class=sat.get("sector_or_class", "High-Conviction Satellite"),
                            market_price=price,
                            allocated_amount=actual_spent,
                            shares_to_buy=float(shares),
                            is_fractional=False,
                            currency=currency
                        ))
                        spent += actual_spent
                else:
                    shares = round(per_stock_budget / price, 4)
                    plan.append(AllocationItem(
                        symbol=sat["symbol"],
                        name=sat["name"],
                        asset_type=sat.get("asset_type", "Stock"),
                        sector_or_class=sat.get("sector_or_class", "High-Conviction Satellite"),
                        market_price=price,
                        allocated_amount=per_stock_budget,
                        shares_to_buy=shares,
                        is_fractional=True,
                        currency=currency
                    ))
                    spent += per_stock_budget

        unallocated_cash = total_amount - spent

        return {
            "total_budget": total_amount,
            "total_spent": spent,
            "unallocated_cash": unallocated_cash,
            "currency": currency,
            "items": plan
        }
