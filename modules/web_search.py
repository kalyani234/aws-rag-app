# modules/web_search.py
"""
Handles live AWS Docs retrieval using SerpAPI and optional Groq summarization.
Falls back to https://docs.aws.amazon.com/ if PGVector has no relevant info.
"""

import os
import requests
from bs4 import BeautifulSoup

SERP_API_KEY = os.getenv("SERPAPI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# -----------------------------------------------
# 🔍 Search AWS Docs via SerpAPI (Google Engine)
# -----------------------------------------------
def search_aws_docs(query, site="https://docs.aws.amazon.com/"):
    """Search AWS Docs pages for a given query using SerpAPI"""
    if not SERP_API_KEY:
        print("⚠️ SERPAPI_API_KEY missing, skipping live search.")
        return []

    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google",
        "q": f"site:{site} {query}",
        "api_key": SERP_API_KEY,
    }

    try:
        res = requests.get(url, params=params, timeout=15)
        res.raise_for_status()
        data = res.json()
        links = [r["link"] for r in data.get("organic_results", []) if "link" in r]
        print(f"🔗 Found {len(links)} AWS Docs links via SerpAPI.")
        return links[:3]
    except Exception as e:
        print(f"❌ SerpAPI search failed: {e}")
        return []


# -----------------------------------------------
# 📄 Scrape AWS Docs page content
# -----------------------------------------------
def fetch_page_content(url):
    """Fetch and clean paragraphs from an AWS Docs page"""
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
        content = " ".join(paragraphs)
        return content[:6000]  # limit to avoid token overflow
    except Exception as e:
        print(f"⚠️ Error fetching {url}: {e}")
        return ""


# -----------------------------------------------
# ⚡ Optional: Summarize scraped text via Groq
# -----------------------------------------------
def summarize_with_groq(text):
    """Use Groq API to summarize scraped AWS Docs text"""
    if not GROQ_API_KEY:
        return text[:6000]

    try:
        url = "https://api.groq.com/openai/v1"
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
        payload = {
            "model": "qwen/qwen3-32b",
            "messages": [
                {"role": "system", "content": "Summarize AWS documentation clearly and concisely."},
                {"role": "user", "content": text[:10000]},
            ],
            "temperature": 0.3,
        }
        res = requests.post(url, headers=headers, json=payload, timeout=30)
        res.raise_for_status()
        summary = res.json()["choices"][0]["message"]["content"]
        print("🧩 Groq summary complete.")
        return summary
    except Exception as e:
        print(f"⚠️ Groq summarization failed: {e}")
        return text[:6000]