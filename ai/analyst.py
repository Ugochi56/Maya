"""
Qualitative AI Research Analyst for Maya.
Implements items #1, #3, and #4 from Fund.md:
1. Understand what I am buying (business model & customer monetization)
3. The Moat (network effects, switching costs, barriers to entry)
4. Management scrutiny (incentives, capital allocation, integrity)
* Customer reviews & Competitive landscape
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class AIAnalyst:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.client = None
        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"Warning: Could not initialize Google GenAI client: {e}")

    def generate_qualitative_memo(self, asset_data: Dict[str, Any], screen_results: Dict[str, Any]) -> str:
        symbol = asset_data["symbol"]
        info = asset_data.get("info", {})
        name = info.get("longName", symbol)
        summary = info.get("longBusinessSummary", "No company summary available.")
        sector = info.get("sector", "N/A")
        industry = info.get("industry", "N/A")

        if not self.client:
            return (
                f"### Qualitative Checklist (Fund.md) for {name} ({symbol})\n"
                f"- **Sector / Industry:** {sector} / {industry}\n"
                f"- **Business Summary:** {summary[:350]}...\n\n"
                f"> [!TIP]\n"
                f"> To enable automated AI moat analysis, generate a free API key at **https://aistudio.google.com** "
                f"and add `GEMINI_API_KEY=your_key` to your `.env` file."
            )

        prompt = f"""
You are an expert, disciplined value investor following the exact philosophies of Warren Buffett, Charlie Munger, and Peter Lynch.
Analyze this company strictly according to the user's checklist:

Company: {name} ({symbol})
Sector: {sector} | Industry: {industry}
Business Overview: {summary}

Quantitative Screening Context:
- Screener Status: {screen_results.get('status')}
- Score: {screen_results.get('score')}/10
- Key Financial Highlights: {', '.join(screen_results.get('summary', []))}

Provide a concise, razor-sharp memo addressing these exact points:
1. **Understand What I Am Buying:** How does this business actually make cash? Who is the paying customer?
2. **The Moat (Durability):** What stops a competitor with $10 billion from wiping them out in 5-10 years? (Switching costs, network effects, scale, patents).
3. **Management & Capital Allocation:** Do they behave like owner-operators or empire builders?
4. **Key Risks & Obsolescence:** What could break this business over the next decade?
5. **Customer & Competition Scuttlebutt:** Are customers locked in or looking for alternatives?

Keep your response factual, rigorous, and free of hype.
"""
        models_to_try = ['gemini-flash-latest', 'gemini-3.5-flash', 'gemini-3.8-flash']
        last_error = None
        for model_name in models_to_try:
            try:
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                if response and response.text:
                    return response.text
            except Exception as e:
                last_error = e
                continue

        return f"Error querying Gemini API: {last_error}"
