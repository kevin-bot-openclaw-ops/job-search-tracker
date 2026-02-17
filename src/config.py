"""Configuration — search criteria and target filters."""

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ── API ──────────────────────────────────────────────────────────────────────
BRAVE_API_KEY: str = os.getenv("BRAVE_API_KEY", "")
BRAVE_ENDPOINT = "https://api.search.brave.com/res/v1/web/search"

# ── Google Sheets ─────────────────────────────────────────────────────────────
SHEET_ID: str = os.getenv("SHEET_ID", "")
GOG_ACCOUNT: str = os.getenv("GOG_ACCOUNT", "kevin.forge@plocha.eu")
SHEET_OWNER_EMAIL: str = "jerzy.plocha@gmail.com"

# ── Search settings ───────────────────────────────────────────────────────────
MAX_RESULTS_PER_QUERY: int = int(os.getenv("MAX_RESULTS_PER_QUERY", "10"))
FRESHNESS: str = os.getenv("FRESHNESS", "pm")  # pm = past month

# ── Search queries ────────────────────────────────────────────────────────────
# Designed to surface senior AI/ML roles with real budget, EU/remote friendly
SEARCH_QUERIES = [
    'site:linkedin.com/jobs "senior ML engineer" remote OR EU "150k" OR "€150" OR "€120"',
    'site:linkedin.com/jobs "ML platform engineer" senior remote OR Europe contract OR permanent',
    'site:linkedin.com/jobs "AI engineer" senior "LLM" OR "RAG" remote Europe',
    'site:remoteok.com "senior" "machine learning" OR "AI engineer" "$" Europe',
    '"senior machine learning engineer" remote EU "€100k" OR "€120k" OR "€150k" -intern -junior',
    '"ML engineer" OR "AI engineer" senior principal staff remote Europe "100,000" OR "120,000" OR "150,000"',
    'site:weworkremotely.com "machine learning" OR "AI" senior engineer',
    '"backend engineer" "ML" OR "LLM" OR "RAG" OR "AI" senior remote EU contract OR permanent',
]

# ── Relevance scoring weights ─────────────────────────────────────────────────
SCORE_WEIGHTS = {
    # Seniority signals (required)
    "senior": 10, "principal": 15, "staff": 12, "lead": 10, "head of": 15,

    # AI/ML role signals
    "machine learning": 15, "ml engineer": 20, "ai engineer": 15,
    "llm": 12, "rag": 12, "generative ai": 12, "nlp": 10,
    "mlops": 12, "ml platform": 15, "model serving": 10,

    # Salary signals
    "150k": 20, "€150": 20, "120k": 15, "€120": 15,
    "100k": 10, "€100": 10, "$150": 20, "$120": 15,

    # Location/type signals
    "remote": 8, "eu": 5, "europe": 5, "contract": 5,

    # Java/backend crossover (Jurek's edge)
    "java": 8, "spring": 5, "aws": 5, "backend": 5, "api": 3,

    # Negative signals
    "intern": -30, "junior": -30, "entry level": -25, "data scientist": -5,
    "research": -5,  # pure research ≠ engineering
}

# ── State ─────────────────────────────────────────────────────────────────────
DATA_DIR = Path("data")
SEEN_URLS_FILE = DATA_DIR / "seen_urls.json"
