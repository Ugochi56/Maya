"""
Watchlist and asset universe definition for Maya.
Categorized into Home (NGX - Nigeria) and Away (Global / US),
covering multiple sectors, REITs, and ETFs.
"""

WATCHLIST = {
    "HOME": {
        "REAL_ESTATE_REITS": [
            {"symbol": "SFSREIT", "name": "SFS Real Estate Investment Trust", "type": "REIT", "notes": "Commercial real estate yield"},
            {"symbol": "UPDCREIT", "name": "UPDC Real Estate Investment Trust", "type": "REIT", "notes": "Residential & commercial property"},
            {"symbol": "NREIT", "name": "Nigeria REIT", "type": "REIT", "notes": "NGX listed property trust"}
        ],
        "PHARMA_HEALTHCARE": [
            {"symbol": "FIDSON", "name": "Fidson Healthcare Plc", "type": "Pharma", "notes": "Leading local pharmaceutical manufacturing"},
            {"symbol": "MAYBAKER", "name": "May & Baker Nigeria Plc", "type": "Pharma", "notes": "Pharmaceuticals and vaccines"},
            {"symbol": "NEIMETH", "name": "Neimeth International Pharmaceuticals", "type": "Pharma", "notes": "Therapeutics and generics"}
        ],
        "FINANCIALS_BANKING": [
            {"symbol": "GTCO", "name": "Guaranty Trust Holding Company", "type": "Bank", "notes": "Tier-1 retail and digital banking cash cow"},
            {"symbol": "ZENITHBANK", "name": "Zenith Bank Plc", "type": "Bank", "notes": "Tier-1 dividend powerhouse"},
            {"symbol": "ACCESSCORP", "name": "Access Holdings Plc", "type": "Bank", "notes": "Pan-African expansion and banking"},
            {"symbol": "UBA", "name": "United Bank for Africa", "type": "Bank", "notes": "Global footprint and FX cash generation"}
        ],
        "TELECOM_AND_INDUSTRIAL": [
            {"symbol": "MTNN", "name": "MTN Nigeria Communications", "type": "Telecom", "notes": "Data, fintech, and telecom monopoly moat"},
            {"symbol": "DANGCEM", "name": "Dangote Cement Plc", "type": "Industrial", "notes": "Dominant regional cement producer"},
            {"symbol": "PRESCO", "name": "Presco Plc", "type": "Agriculture", "notes": "Oil palm plantation and export cash flows"}
        ],
        "ENERGY": [
            {"symbol": "SEPLAT", "name": "Seplat Energy Plc", "type": "Energy", "notes": "Indigenous upstream oil & gas with USD dividends"}
        ]
    },
    "AWAY": {
        "CORE_ETFS": [
            {"symbol": "VOO", "name": "Vanguard S&P 500 ETF", "type": "ETF", "notes": "Top 500 US companies (Core Pillar)"},
            {"symbol": "VT", "name": "Vanguard Total World Stock ETF", "type": "ETF", "notes": "Global diversification across 9,000+ companies"},
            {"symbol": "QQQ", "name": "Invesco QQQ Trust (Nasdaq 100)", "type": "ETF", "notes": "Innovation and secular tech growth"},
            {"symbol": "SCHD", "name": "Schwab U.S. Dividend Equity ETF", "type": "ETF", "notes": "High quality dividend compounders"}
        ],
        "PHARMA_HEALTHCARE": [
            {"symbol": "XLV", "name": "Health Care Select Sector SPDR ETF", "type": "ETF", "notes": "Diversified healthcare & biotech basket"},
            {"symbol": "LLY", "name": "Eli Lilly and Company", "type": "Pharma", "notes": "GLP-1 metabolic/diabetes monopoly moat"},
            {"symbol": "NVO", "name": "Novo Nordisk A/S", "type": "Pharma", "notes": "Insulin and obesity therapeutics leader"},
            {"symbol": "JNJ", "name": "Johnson & Johnson", "type": "Pharma", "notes": "MedTech and innovative medicine titan"}
        ],
        "REAL_ESTATE": [
            {"symbol": "VNQ", "name": "Vanguard Real Estate ETF", "type": "ETF", "notes": "US real estate investment trust basket"},
            {"symbol": "O", "name": "Realty Income Corporation", "type": "REIT", "notes": "The Monthly Dividend Company (triple-net retail leases)"}
        ],
        "TECH_AND_COMPOUNDERS": [
            {"symbol": "MSFT", "name": "Microsoft Corporation", "type": "Tech", "notes": "Enterprise cloud, OS, and productivity moat"},
            {"symbol": "GOOGL", "name": "Alphabet Inc.", "type": "Tech", "notes": "Search, YouTube, and AI computing platform"}
        ]
    }
}
