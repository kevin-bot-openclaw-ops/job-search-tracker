"""Deduplication — tracks seen URLs across runs using a JSON state file."""

import json
import logging
from pathlib import Path
from typing import List, Dict

from .config import SEEN_URLS_FILE, DATA_DIR

logger = logging.getLogger(__name__)


class Deduplicator:
    """Tracks seen job URLs so each posting is recorded only once."""

    def __init__(self, state_file: Path = SEEN_URLS_FILE):
        self.state_file = state_file
        DATA_DIR.mkdir(exist_ok=True)
        self._seen: set = self._load()

    def _load(self) -> set:
        if self.state_file.exists():
            try:
                with open(self.state_file) as f:
                    data = json.load(f)
                logger.info(f"Loaded {len(data)} previously seen URLs")
                return set(data)
            except (json.JSONDecodeError, Exception) as e:
                logger.warning(f"Could not load seen URLs: {e}. Starting fresh.")
        return set()

    def _save(self):
        with open(self.state_file, "w") as f:
            json.dump(sorted(self._seen), f, indent=2)

    def filter_new(self, jobs: List[Dict]) -> List[Dict]:
        """
        Return only jobs not previously seen.

        Deduplicates within the current batch AND against prior runs.
        Updates state file after filtering.
        """
        new_jobs = []
        seen_this_run = set()

        for job in jobs:
            url = job.get("url", "")
            if not url:
                continue
            if url in self._seen or url in seen_this_run:
                logger.debug(f"Duplicate: {url[:80]}")
                continue
            new_jobs.append(job)
            seen_this_run.add(url)

        # Persist new URLs
        self._seen.update(seen_this_run)
        self._save()

        logger.info(f"Deduplication: {len(jobs)} total → {len(new_jobs)} new")
        return new_jobs
