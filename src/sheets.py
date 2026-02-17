"""Google Sheets writer — pushes job results via gog CLI."""

import json
import logging
import subprocess
from typing import List, Dict

from .config import GOG_ACCOUNT, SHEET_OWNER_EMAIL

logger = logging.getLogger(__name__)

# Column order in the sheet
COLUMNS = ["date_found", "score", "title", "company", "location", "salary",
           "source", "status", "url", "description"]

SHEET_HEADER = ["Date Found", "Score", "Title", "Company", "Location", "Salary",
                "Source", "Status", "URL", "Description"]


class SheetsWriter:
    """Writes job results to Google Sheets via the gog CLI."""

    def __init__(self, sheet_id: str = ""):
        self.sheet_id = sheet_id

    def ensure_sheet(self, name: str = "Job Search Tracker") -> str:
        """
        Create sheet if it doesn't exist, return sheet ID.

        If self.sheet_id is already set, returns it unchanged.
        """
        if self.sheet_id:
            return self.sheet_id

        logger.info(f"Creating new spreadsheet: {name}")
        result = self._run_gog([
            "spreadsheet", "create",
            f"--account={GOG_ACCOUNT}",
            f"--title={name}",
        ])
        # gog prints the sheet ID on stdout
        sheet_id = result.strip().split()[-1]
        self.sheet_id = sheet_id
        logger.info(f"Created sheet: {sheet_id}")

        # Share with Jurek
        self._run_gog([
            "spreadsheet", "share",
            f"--account={GOG_ACCOUNT}",
            f"--spreadsheet-id={sheet_id}",
            f"--email={SHEET_OWNER_EMAIL}",
            "--role=writer",
        ])
        logger.info(f"Shared sheet with {SHEET_OWNER_EMAIL}")

        # Write header row
        self._write_header(sheet_id)
        return sheet_id

    def append_jobs(self, jobs: List[Dict], sheet_tab: str = "Jobs") -> int:
        """
        Append new jobs to the sheet.

        Returns number of rows written.
        """
        if not jobs:
            logger.info("No new jobs to append")
            return 0

        if not self.sheet_id:
            raise ValueError("sheet_id not set — call ensure_sheet() first")

        rows = []
        for job in jobs:
            row = [str(job.get(col, "")) for col in COLUMNS]
            rows.append(row)

        # Build TSV payload for gog
        tsv_rows = "\n".join("\t".join(r) for r in rows)

        # Write via gog update (append mode by appending to next empty row)
        # First find current last row, then write from there
        result = self._run_gog([
            "spreadsheet", "append",
            f"--account={GOG_ACCOUNT}",
            f"--spreadsheet-id={self.sheet_id}",
            f"--range={sheet_tab}!A:J",
            "--value-input-option=USER_ENTERED",
            "--data", json.dumps({"values": rows}),
        ])

        logger.info(f"Appended {len(rows)} rows to sheet")
        return len(rows)

    def _write_header(self, sheet_id: str):
        """Write header row to sheet."""
        self._run_gog([
            "spreadsheet", "update",
            f"--account={GOG_ACCOUNT}",
            f"--spreadsheet-id={sheet_id}",
            "--range=Sheet1!A1:J1",
            "--value-input-option=USER_ENTERED",
            "--data", json.dumps({"values": [SHEET_HEADER]}),
        ])

    def _run_gog(self, args: List[str]) -> str:
        """Run gog CLI command and return stdout."""
        cmd = ["gog"] + args
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode != 0:
                logger.error(f"gog error: {result.stderr}")
            return result.stdout
        except subprocess.TimeoutExpired:
            logger.error(f"gog command timed out: {' '.join(cmd)}")
            return ""
        except FileNotFoundError:
            logger.error("gog CLI not found. Install it or set up Google Sheets manually.")
            return ""
