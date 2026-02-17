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
    # RemoteOK — open, well-indexed, good remote tech jobs
    'site:remoteok.com "machine learning" OR "ML engineer" OR "AI engineer" senior',
    'site:remoteok.com "backend" "AI" OR "LLM" OR "RAG" senior engineer',
    # workatastartup.com (YC companies)
    'site:workatastartup.com "machine learning" OR "AI" senior engineer remote',
    # Broad web — job postings that escape paywalls
    '"senior machine learning engineer" OR "senior ML engineer" remote EU hiring 2025 OR 2026',
    '"senior AI engineer" "LLM" OR "RAG" OR "GenAI" remote Europe "apply" OR "job" OR "position"',
    # ML Platform / MLOps niche (Jurek's infrastructure angle)
    '"ML platform engineer" OR "MLOps engineer" senior remote Europe hiring',
    # Backend + AI hybrid (Jurek's strongest niche)
    '"backend engineer" "machine learning" OR "LLM" OR "RAG" senior remote Europe contract',
    # EU-specific job boards
    'site:euremotejobs.com OR site:remote.io "machine learning" OR "AI engineer" senior',
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
