"""
Asset and Sector Classifier for Maya.
Identifies the asset class to ensure the correct financial evaluation lens is applied.
"""

from typing import Dict, Any

class AssetType:
    ETF = "ETF"
    REIT = "REIT"
    BANK = "BANK"
    PHARMA = "PHARMA"
    EQUITY = "EQUITY"

def classify_asset(ticker_symbol: str, info: Dict[str, Any]) -> str:
    """
    Classify an asset into ETF, REIT, BANK, PHARMA, or STANDARD EQUITY.
    
    Args:
        ticker_symbol: The ticker symbol (e.g. 'VOO', 'O', 'GTCO.LG', 'LLY')
        info: Dictionary from yfinance info or metadata
    """
    quote_type = (info.get("quoteType") or "").upper()
    sector = (info.get("sector") or "").upper()
    industry = (info.get("industry") or "").upper()
    long_name = (info.get("longName") or "").upper()
    symbol = ticker_symbol.upper()

    # 1. Check for ETFs & Mutual Funds
    if quote_type in ["ETF", "MUTUALFUND"] or "ETF" in long_name or "TRUST" in long_name and ("INDEX" in long_name or "GOLD" in long_name):
        return AssetType.ETF
    
    # 2. Check for Real Estate Investment Trusts (REITs)
    if "REIT" in industry or "REAL ESTATE" in sector or "REIT" in long_name or "REIT" in symbol:
        return AssetType.REIT
    
    # 3. Check for Banks & Financial Institutions
    if "BANK" in industry or "BANK" in long_name or "HOLDING COMPANY" in industry and "FINANCIAL" in sector:
        return AssetType.BANK

    # 4. Check for Pharmaceuticals & Biotechnology
    if "PHARMA" in industry or "BIOTECH" in industry or "HEALTHCARE" in sector or "DRUG" in industry:
        return AssetType.PHARMA

    # 5. Default to Standard Operating Equity
    return AssetType.EQUITY
