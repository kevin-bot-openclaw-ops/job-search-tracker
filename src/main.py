"""Job Search Tracker — main runner.

Usage:
    python -m src.main                    # run all queries, push to sheet
    python -m src.main --dry-run          # print results, skip sheet write
    python -m src.main --sheet-id=<id>   # use existing sheet
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path

from .config import SEARCH_QUERIES, SHEET_ID, DATA_DIR
from .searcher import BraveSearcher
from .parser import parse_results
from .deduplicator import Deduplicator
from .sheets import SheetsWriter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

SHEET_ID_FILE = DATA_DIR / "sheet_id.txt"


def load_or_create_sheet_id(writer: SheetsWriter) -> str:
    """Load persisted sheet ID or create a new sheet."""
    # Priority: CLI arg > env var > saved file > create new
    if writer.sheet_id:
        return writer.sheet_id

    if SHEET_ID:
        writer.sheet_id = SHEET_ID
        return SHEET_ID

    if SHEET_ID_FILE.exists():
        saved = SHEET_ID_FILE.read_text().strip()
        if saved:
            writer.sheet_id = saved
            logger.info(f"Using saved sheet ID: {saved}")
            return saved

    # Create new sheet
    sheet_id = writer.create_and_share()
    DATA_DIR.mkdir(exist_ok=True)
    SHEET_ID_FILE.write_text(sheet_id)
    logger.info(f"New sheet created and saved: {sheet_id}")
    return sheet_id


def run(dry_run: bool = False, sheet_id: str = "", top_n: int = 50):
    """Execute the full job search pipeline."""

    logger.info("=== Job Search Tracker ===")

    # 1. Search
    logger.info(f"Running {len(SEARCH_QUERIES)} search queries via Brave API...")
    searcher = BraveSearcher()
    raw = searcher.search_all(SEARCH_QUERIES)
    logger.info(f"Raw results: {len(raw)}")

    # 2. Parse + score
    jobs = parse_results(raw)

    # 3. Deduplicate across runs
    dedup = Deduplicator()
    new_jobs = dedup.filter_new(jobs)

    # 4. Sort by relevance score, take top N
    new_jobs.sort(key=lambda j: j["score"], reverse=True)
    new_jobs = new_jobs[:top_n]

    logger.info(f"New jobs after deduplication: {len(new_jobs)}")

    # 5. Print summary
    _print_summary(new_jobs)

    if dry_run:
        logger.info("DRY RUN — skipping Google Sheets write")
        return new_jobs

    # 6. Push to Google Sheets
    writer = SheetsWriter(sheet_id=sheet_id)
    sid = load_or_create_sheet_id(writer)
    written = writer.append_jobs(new_jobs)

    logger.info(f"Written {written} rows to sheet: {writer.sheet_url()}")
    print(f"\n✅ Done. Sheet URL: {writer.sheet_url()}")
    return new_jobs


def _print_summary(jobs):
    """Print ranked job list to stdout."""
    if not jobs:
        print("\nNo new jobs found this run.")
        return

    print(f"\n{'='*80}")
    print(f"{'RANK':>4}  {'SCORE':>5}  {'SOURCE':<12}  {'SALARY':<15}  TITLE")
    print(f"{'='*80}")

    for i, job in enumerate(jobs, 1):
        salary = job.get("salary", "")[:15] or "—"
        source = job.get("source", "")[:12]
        title = job.get("title", "")[:55]
        score = job.get("score", 0)
        print(f"{i:>4}  {score:>5}  {source:<12}  {salary:<15}  {title}")

    print(f"{'='*80}")
    print(f"Total new jobs: {len(jobs)}\n")


def main():
    parser = argparse.ArgumentParser(description="Job Search Tracker")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print results without writing to Google Sheets")
    parser.add_argument("--sheet-id", default="",
                        help="Existing Google Sheet ID to append to")
    parser.add_argument("--top", type=int, default=50,
                        help="Maximum jobs to write per run (default: 50)")
    args = parser.parse_args()

    jobs = run(
        dry_run=args.dry_run,
        sheet_id=args.sheet_id,
        top_n=args.top,
    )

    return 0 if jobs is not None else 1


if __name__ == "__main__":
    sys.exit(main())
