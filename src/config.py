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
    # ── Tier 1: Verified sources (return real remote jobs) ────────────────────
    # RemoteOK — only individual postings (not category pages)
    'site:remoteok.com/remote-jobs "machine learning" OR "ML engineer" OR "AI engineer" senior',
    'site:remoteok.com/remote-jobs "backend" "AI" OR "LLM" OR "RAG" senior engineer',
    # EU Remote Jobs — EU-timezone remote, well-indexed
    'site:euremotejobs.com "machine learning" OR "AI engineer" OR "ML engineer"',
    'site:euremotejobs.com "MLOps" OR "LLM" OR "RAG" OR "GenAI" engineer',
    # ── Tier 2: Strong remote-first boards ───────────────────────────────────
    # Himalayas — curated remote-first, good EU coverage
    'site:himalayas.app "machine learning" OR "AI engineer" OR "ML engineer" senior',
    # Arc.dev — remote engineers platform
    'site:arc.dev "senior" "machine learning" OR "AI" OR "LLM" engineer',
    # Wellfound (AngelList) — startup senior AI/ML roles
    'site:wellfound.com "senior" "machine learning" OR "AI engineer" remote Europe',
    # ── Tier 3: Broad keyword (broad net, higher noise) ───────────────────────
    # Backend + AI hybrid — Jurek's strongest niche (Java/Spring/AWS + LLM/RAG)
    '"backend engineer" "LLM" OR "RAG" OR "AI" senior remote Europe contract OR permanent',
]

# ── Relevance scoring weights ─────────────────────────────────────────────────
# ── Hard filters (score override → 0) ────────────────────────────────────────
# Any result matching these phrases fails the remote filter regardless of score
REMOTE_REJECT_PHRASES = [
    # Country/city requirements
    "poland-based", "poland based", "must be in poland", "must be based in poland",
    "krakow", "kraków", "warsaw office", "warsaw-based",
    "germany-based", "uk-based", "netherlands-based", "france-based",
    "must be located", "must reside", "must live in",
    "requires relocation",
    # On-site / hybrid signals
    "on-site", "onsite", "on site",
    "hybrid", "in-office", "in office",
    "days in office", "days in-office", "days per week in",
    "occasional travel required", "travel to office",
    # LatAm-focused (not Spain/EU remote)
    "latin america", "latam", "colombia", "costa rica",
    "mexico city", "bogota", "são paulo",
]

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
