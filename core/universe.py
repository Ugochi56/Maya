"""
Asset Universe Management for Maya.
Provides complete access to:
1. Home Universe: Full Nigerian Stock Exchange (NGX) equities across all 11 official sectors.
2. Away Universe: Full S&P 500 index constituents (~503 top global US companies).
"""

import os
import json
from typing import List, Dict, Any, Optional

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
NGX_FILE = os.path.join(DATA_DIR, "universe_ngx.json")
SP500_FILE = os.path.join(DATA_DIR, "universe_sp500.json")

class UniverseManager:
    @staticmethod
    def get_home_universe(sector: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all listed Nigerian Stock Exchange (NGX) companies.
        Optional sector filter (e.g. 'Financials', 'Healthcare', 'Industrials', 'Consumer Goods', 'Real Estate').
        """
        if not os.path.exists(NGX_FILE):
            return []
        with open(NGX_FILE, "r", encoding="utf-8") as f:
            companies = json.load(f)

        if sector:
            sec_lower = sector.lower()
            return [c for c in companies if sec_lower in c.get("sector", "").lower() or sec_lower in c.get("industry", "").lower()]
        return companies

    @staticmethod
    def get_away_universe(sector: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all official S&P 500 constituents (~503 companies).
        Optional sector filter (e.g. 'Health Care', 'Information Technology', 'Real Estate', 'Financials').
        """
        if not os.path.exists(SP500_FILE):
            return []
        with open(SP500_FILE, "r", encoding="utf-8") as f:
            companies = json.load(f)

        if sector:
            sec_lower = sector.lower()
            return [c for c in companies if sec_lower in c.get("sector", "").lower() or sec_lower in c.get("sub_industry", "").lower()]
        return companies

    @staticmethod
    def get_home_sectors() -> List[str]:
        companies = UniverseManager.get_home_universe()
        return sorted(list(set(c.get("sector") for c in companies if c.get("sector"))))

    @staticmethod
    def get_away_sectors() -> List[str]:
        companies = UniverseManager.get_away_universe()
        return sorted(list(set(c.get("sector") for c in companies if c.get("sector"))))
