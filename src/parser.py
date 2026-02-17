"""Result parser — extracts structured job info and scores relevance."""

import re
import logging
from typing import List, Dict
from datetime import datetime, timezone

from .config import SCORE_WEIGHTS, REMOTE_REJECT_PHRASES

logger = logging.getLogger(__name__)


def score_result(result: Dict) -> int:
    """
    Score a result by relevance to Jurek's target criteria.

    HARD FILTER: Returns 0 immediately if any remote-reject phrase is found
    (on-site, hybrid, country-specific location requirements).
    Jurek is based in Canary Islands, Spain — fully remote only.
    """
    text = f"{result.get('title', '')} {result.get('description', '')}".lower()

    # Hard filter: reject non-remote roles immediately
    for phrase in REMOTE_REJECT_PHRASES:
        if phrase in text:
            return 0

    score = 0
    for keyword, weight in SCORE_WEIGHTS.items():
        if keyword.lower() in text:
            score += weight
    return score


def extract_salary(text: str) -> str:
    """Extract salary range from text if present."""
    patterns = [
        r"€\s*\d+[k,]?\s*[-–]\s*€?\s*\d+[k]?",  # €100k - €150k
        r"\$\s*\d+[k,]?\s*[-–]\s*\$?\s*\d+[k]?",  # $100k - $150k
        r"\d+[,.]?\d*\s*[-–]\s*\d+[,.]?\d*\s*(?:EUR|USD|GBP|PLN)",  # 100,000 - 150,000 EUR
        r"up to\s*[€$]\d+k?",                        # up to €150k
        r"[€$]\d+k?\+",                              # €100k+
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0).strip()
    return ""


def extract_location(text: str) -> str:
    """Infer location/remote status from text."""
    text_lower = text.lower()
    signals = []
    if "fully remote" in text_lower or "100% remote" in text_lower:
        signals.append("Remote")
    elif "remote" in text_lower:
        signals.append("Remote")
    for region in ["eu", "europe", "uk", "germany", "netherlands", "poland",
                   "portugal", "spain", "france", "amsterdam", "berlin",
                   "warsaw", "london", "lisbon", "madrid"]:
        if region in text_lower:
            signals.append(region.title())
            break
    return ", ".join(signals) if signals else "Unknown"


def parse_results(raw_results: List[Dict]) -> List[Dict]:
    """
    Parse and enrich raw Brave Search results.

    Returns list of structured job dicts.
    """
    jobs = []
    for raw in raw_results:
        title = raw.get("title", "").strip()
        url = raw.get("url", "").strip()
        description = raw.get("description", "").strip()

        if not url or not title:
            continue

        full_text = f"{title} {description}"
        score = score_result(raw)

        # Skip very low scores — clearly not relevant
        if score < 5:
            logger.debug(f"Skipping low-score result (score={score}): {title[:50]}")
            continue

        # Skip salary guides / articles masquerading as jobs
        if _is_non_job(url, title):
            logger.debug(f"Skipping non-job page: {title[:50]}")
            continue

        jobs.append({
            "title": title,
            "url": url,
            "description": description[:300],  # truncate for sheet
            "salary": extract_salary(full_text),
            "location": extract_location(full_text),
            "score": score,
            "date_found": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "source": _extract_source(url),
            "status": "new",
        })

    logger.info(f"Parsed {len(jobs)} relevant jobs from {len(raw_results)} raw results")
    return jobs


NON_JOB_URL_PATTERNS = [
    "salary", "calculator", "guide", "article", "blog", "news",
    "reddit.com", "quora.com", "medium.com", "levels.fyi",
    "glassdoor.com/salary", "indeed.com/career", "builtin.com/salary",
    "ziprecruiter.com/salary", "payscale.com", "compensation",
    "wikipedia.org",
    "udemy.com", "coursera.org", "edx.org",  # courses, not jobs
]
NON_JOB_TITLE_PATTERNS = [
    "salary guide", "salary calculator", "complete guide", "how to",
    "what is", "breakdown by", "average salary", "salaries in",
    "salary in 20", "salary for", "a guide to",
    " - wikipedia",  # wiki articles
    "job description",  # "Job Description [Updated...]" style articles
    "hire ", "vetted talent", "talent marketplace",  # staffing marketplaces
    "vs ", " vs.",  # comparison articles
    "key differences",
]


def _is_non_job(url: str, title: str) -> bool:
    """Return True if the result looks like a non-job page."""
    url_lower = url.lower()
    title_lower = title.lower()

    # remoteok.com category listing pages (not individual job postings)
    if "remoteok.com" in url_lower and "/remote-jobs/" not in url_lower:
        return True

    for pattern in NON_JOB_URL_PATTERNS:
        if pattern in url_lower:
            return True
    for pattern in NON_JOB_TITLE_PATTERNS:
        if pattern in title_lower:
            return True
    return False


def _extract_source(url: str) -> str:
    """Identify job board from URL."""
    url_lower = url.lower()
    if "linkedin.com" in url_lower:
        return "LinkedIn"
    if "remoteok" in url_lower:
        return "RemoteOK"
    if "weworkremotely" in url_lower:
        return "WeWorkRemotely"
    if "indeed.com" in url_lower:
        return "Indeed"
    if "glassdoor" in url_lower:
        return "Glassdoor"
    if "ycombinator" in url_lower or "workatastartup" in url_lower:
        return "YC Jobs"
    return "Web"
