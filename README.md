# Maya — Intelligent Long-Term Investment Research Bot

> **An automated, sound, and disciplined financial research assistant designed for long-term compounding (10+ year horizon), covering equities, real estate (REITs), pharmaceuticals, and ETFs across domestic (Nigeria - NGX) and international (Global/US) markets.**

---

## 🧭 Philosophy & Foundations

Built on the principles of **Warren Buffett**, **Charlie Munger**, and **Peter Lynch**, *Maya* removes emotion and speculative hype from investing by enforcing rigorous fundamental analysis before a single dollar or naira is deployed.

### Core Framework (from `Fund.md`)
1. **Understand what you are buying:** Clear business model and customer monetization analysis.
2. **Dive into the financials:** Multi-year revenue growth, operating profit margins, debt coverage, and free cash flow durability.
3. **Identify the economic moat:** High switching costs, network effects, brand pricing power, or regulatory/patent protection.
4. **Scrutinize management:** Skin in the game (insider ownership), insider transactions, and rational capital allocation.
5. **Check valuation & multiples:** P/E, Price-to-Sales (P/S), Price-to-Free-Cash-Flow (P/FCF), and EV/EBITDA evaluated against historical medians and peer comps.
6. **Customer & Scuttlebutt Verification:** Product quality, customer retention, and operational momentum.

---

## 🌍 The Dual-Market Coverage: Home & Away

| Market | Primary Focus | Key Asset Classes |
| :--- | :--- | :--- |
| **Home (Nigeria - NGX)** | High dividend cash flows & inflation/currency resilience | Blue-chip banks, dividend aristocrats, commodity hedges (`NEWGOLD.LG`), NGX index ETFs (`STANBICETF30.LG`), NGX REITs (`SFSREIT.LG`, `UPDCREIT.LG`), domestic pharma (`FIDSON.LG`). |
| **Away (Global / US)** | Structural growth, compounding moats, USD currency hedge | Broad-market ETFs (`VOO`, `VT`, `QQQ`), global healthcare/pharma (`XLV`, `LLY`, `JNJ`), global real estate (`VNQ`, `O`), resilient tech/consumer compounders. |

---

## 🏛️ The 5 Pillars of Sound Buy-and-Hold Selection

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Free Cash Flow Reliability (Positive FCF 4 of last 5 yrs)│
├─────────────────────────────────────────────────────────────┤
│ 2. Compounding Engine (ROIC > 12-15% sustained over cycle)  │
├─────────────────────────────────────────────────────────────┤
│ 3. Solvency Stress-Test (Interest Coverage > 5x, Net Debt/  │
│    EBITDA < 2.5x)                                           │
├─────────────────────────────────────────────────────────────┤
│ 4. Durability & Moat (Low obsolescence risk, high pricing   │
│    power)                                                   │
├─────────────────────────────────────────────────────────────┤
│ 5. Margin of Safety (Entry price <= historical valuation   │
│    medians)                                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack & Bootstrap Architecture

- **Language:** Python 3.11+
- **Market Data:** `yfinance` (Global + NGX via `.LG` tickers), Financial Modeling Prep, SEC EDGAR
- **Data & Quantitative Analysis:** `pandas`, `numpy`
- **Qualitative Analyst:** Google Gemini API (Free tier via Google AI Studio)
- **Interface:** CLI & Telegram Bot (`python-telegram-bot`)
- **Cost:** \$0 (100% Bootstrapped with free APIs and open-source tools)

---

## 📁 Repository Structure

```text
Maya/
├── Fund.md                  # Core investment checklist & rules
├── README.md                # Project documentation & roadmap
├── .gitignore               # Keeps API keys and personal portfolio private
├── requirements.txt         # Python dependencies
├── config/
│   ├── settings.py          # API keys & global configurations
│   └── portfolio.example.json # Template for tracking personal budget & holdings
├── core/
│   ├── data_loader.py       # Market data ingestion (US & NGX)
│   ├── classifier.py        # Asset classifier (Stock vs ETF vs REIT vs Pharma vs Bank)
│   ├── screener.py          # 5-Pillar fundamental quantitative filter
│   ├── valuation.py         # Multiples & fair value estimation (P/E, P/FCF, EV/EBITDA)
│   └── allocator.py         # Position sizing based on user budget (whole & fractional)
├── ai/
│   └── analyst.py           # Qualitative moat & filing analyzer via LLM
└── app.py                   # Main runner (CLI / Telegram Bot)
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.11 or higher
- Git

### 2. Setup
```bash
# Clone the repository
git clone https://github.com/Ugochi56/maya.git
cd maya

# Create and activate virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## ⚖️ Disclaimer
*This project is for educational and research purposes only. It is not financial or investment advice. Always perform your own due diligence before deploying real capital.*
