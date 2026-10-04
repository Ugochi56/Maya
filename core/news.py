"""
Real-Time Financial & Company News Ingestion Engine for Maya.
Provides live headlines and media scuttlebutt for both:
1. Home (NGX Nigerian equities via Google News Nigeria)
2. Away (Global & US equities via Google News Global / Yahoo)
Automates Fund.md: "Watch what the company actually does" and "Listen to customer reviews".
"""

import urllib.parse
import xml.etree.ElementTree as ET
from typing import List, Dict, Any
import requests

class NewsFetcher:
    @staticmethod
    def fetch_news(symbol: str, company_name: str, is_ngx: bool = False, limit: int = 4) -> List[Dict[str, str]]:
        """
        Fetch real-time news headlines for any Nigerian or Global company.
        """
        clean_symbol = symbol.strip().upper().replace(".LG", "")
        # Build search query
        if is_ngx:
            query = f"{clean_symbol} {company_name} Nigeria stock"
            url = f"https://news.google.com/rss/search?q={urllib.parse.quote(query)}&hl=en-NG&gl=NG&ceid=NG:en"
        else:
            query = f"{clean_symbol} {company_name} stock news"
            url = f"https://news.google.com/rss/search?q={urllib.parse.quote(query)}&hl=en-US&gl=US&ceid=US:en"

        articles = []
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            r = requests.get(url, headers=headers, timeout=5)
            if r.status_code == 200:
                root = ET.fromstring(r.text)
                items = root.findall(".//item")[:limit]
                for item in items:
                    title_elem = item.find("title")
                    date_elem = item.find("pubDate")
                    link_elem = item.find("link")
                    source_elem = item.find("source")

                    title = title_elem.text if title_elem is not None else ""
                    pub_date = date_elem.text[:16] if date_elem is not None and date_elem.text else ""
                    source = source_elem.text if source_elem is not None and source_elem.text else "Market Wire"

                    # If source is part of title (e.g. "Title - Source"), split it
                    if " - " in title and source == "Market Wire":
                        parts = title.rsplit(" - ", 1)
                        title = parts[0]
                        source = parts[1]

                    articles.append({
                        "title": title,
                        "source": source,
                        "date": pub_date,
                        "link": link_elem.text if link_elem is not None else ""
                    })
        except Exception as e:
            # Fallback gracefully without breaking analysis
            pass

        return articles
