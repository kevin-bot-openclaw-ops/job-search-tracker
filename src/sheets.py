"""Google Sheets writer — pushes job results via gog CLI."""

import json
import logging
import subprocess
from typing import List, Dict

from .config import GOG_ACCOUNT, SHEET_OWNER_EMAIL

logger = logging.getLogger(__name__)

COLUMNS = ["date_found", "score", "title", "company", "location",
           "salary", "source", "status", "url", "description"]

HEADER = ["Date Found", "Score", "Title", "Company", "Location",
          "Salary", "Source", "Status", "URL", "Description"]


class SheetsWriter:
    """Writes job results to Google Sheets via the gog CLI."""

    def __init__(self, sheet_id: str = ""):
        self.sheet_id = sheet_id

    # ── Public API ────────────────────────────────────────────────────────────

    def create_and_share(self, title: str = "Job Search Tracker — OpenClaw") -> str:
        """
        Create a new spreadsheet, share with Jurek, write header.

        Returns the new sheet ID.
        """
        out = self._gog(["sheets", "create", title, f"--account={GOG_ACCOUNT}", "--json"])
        try:
            data = json.loads(out)
            sheet_id = data["spreadsheetId"]
        except (json.JSONDecodeError, KeyError) as e:
            raise RuntimeError(f"Failed to parse sheet create response: {out}") from e

        logger.info(f"Created sheet {sheet_id}: {data.get('spreadsheetUrl')}")

        # Share with Jurek
        self._gog([
            "drive", "share", sheet_id,
            f"--email={SHEET_OWNER_EMAIL}",
            "--role=writer",
            f"--account={GOG_ACCOUNT}",
        ])
        logger.info(f"Shared with {SHEET_OWNER_EMAIL}")

        # Write header row
        self._write_row(sheet_id, "Sheet1!A1:J1", [HEADER])
        self.sheet_id = sheet_id
        return sheet_id

    def append_jobs(self, jobs: List[Dict]) -> int:
        """
        Append new job rows to the sheet.

        Returns number of rows written.
        """
        if not jobs:
            return 0
        if not self.sheet_id:
            raise ValueError("sheet_id not set — call create_and_share() first")

        written = 0
        for job in jobs:
            row_values = "|".join(str(job.get(col, "")).replace("|", " ") for col in COLUMNS)
            self._gog([
                "sheets", "append", self.sheet_id, "Sheet1!A:J",
                row_values,
                f"--account={GOG_ACCOUNT}",
                "--input=USER_ENTERED",
                "--insert=INSERT_ROWS",
            ])
            written += 1

        logger.info(f"Appended {written} rows to sheet {self.sheet_id}")
        return written

    def sheet_url(self) -> str:
        return f"https://docs.google.com/spreadsheets/d/{self.sheet_id}/edit"

    # ── Internals ────────────────────────────────────────────────────────────

    def _write_row(self, sheet_id: str, range_: str, values: List[List[str]]):
        """Write a single row via gog sheets update."""
        row_str = "|".join(str(v) for v in values[0])
        self._gog([
            "sheets", "update", sheet_id, range_,
            row_str,
            f"--account={GOG_ACCOUNT}",
            "--input=USER_ENTERED",
        ])

    def _gog(self, args: List[str]) -> str:
        """Run gog CLI and return stdout. Logs errors."""
        cmd = ["gog"] + args
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                logger.warning(f"gog stderr: {result.stderr.strip()}")
            return result.stdout.strip()
        except subprocess.TimeoutExpired:
            logger.error(f"gog timed out: {' '.join(cmd[:4])}")
            return ""
        except FileNotFoundError:
            logger.error("gog not found — install it to enable Sheets output")
            return ""
