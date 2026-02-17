"""Brave Search API client — fetches job postings."""

import logging
import time
from typing import List, Dict

import requests

from .config import BRAVE_API_KEY, BRAVE_ENDPOINT, MAX_RESULTS_PER_QUERY, FRESHNESS

logger = logging.getLogger(__name__)


class BraveSearcher:
    """Fetches search results from Brave Search API."""

    def __init__(self):
        if not BRAVE_API_KEY:
            raise ValueError("BRAVE_API_KEY not set. Add it to .env or environment.")
        self.headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": BRAVE_API_KEY,
        }

    def search(self, query: str, count: int = None, freshness: str = None) -> List[Dict]:
        """
        Execute a single search query.

        Returns list of raw result dicts with keys:
            title, url, description
        """
        params = {
            "q": query,
            "count": count or MAX_RESULTS_PER_QUERY,
            "search_lang": "en",
            "country": "ALL",
        }
        if freshness:
            params["freshness"] = freshness
        elif FRESHNESS:
            params["freshness"] = FRESHNESS

        try:
            resp = requests.get(
                BRAVE_ENDPOINT,
                headers=self.headers,
                params=params,
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()

            results = []
            for item in data.get("web", {}).get("results", []):
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "description": item.get("description", ""),
                })
            logger.info(f"Query returned {len(results)} results: {query[:60]}...")
            return results

        except requests.HTTPError as e:
            logger.error(f"HTTP error for query '{query[:40]}': {e}")
            return []
        except Exception as e:
            logger.error(f"Search failed for query '{query[:40]}': {e}")
            return []

    def search_all(self, queries: List[str], delay: float = 1.1) -> List[Dict]:
        """
        Run all queries with a polite delay between requests.

        Rate limit: Brave free tier = 1 req/sec.
        """
        all_results = []
        for i, query in enumerate(queries, 1):
            logger.info(f"Running query {i}/{len(queries)}")
            results = self.search(query)
            all_results.extend(results)
            if i < len(queries):
                time.sleep(delay)  # respect 1 req/sec rate limit

        logger.info(f"Total raw results: {len(all_results)}")
        return all_results
