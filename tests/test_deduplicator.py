"""Tests for deduplication across runs."""

import json
import tempfile
from pathlib import Path
import pytest
from src.deduplicator import Deduplicator


def make_jobs(urls):
    return [{"url": u, "title": f"Job at {u}", "score": 50} for u in urls]


@pytest.fixture
def tmp_state(tmp_path):
    """Temporary state file path."""
    return tmp_path / "seen_urls.json"


def test_first_run_all_new(tmp_state):
    d = Deduplicator(state_file=tmp_state)
    jobs = make_jobs(["https://a.com/1", "https://a.com/2", "https://a.com/3"])
    new = d.filter_new(jobs)
    assert len(new) == 3


def test_second_run_deduped(tmp_state):
    d = Deduplicator(state_file=tmp_state)
    jobs = make_jobs(["https://a.com/1", "https://a.com/2"])
    d.filter_new(jobs)  # first run

    d2 = Deduplicator(state_file=tmp_state)
    jobs2 = make_jobs(["https://a.com/1", "https://a.com/3"])  # 1 repeat, 1 new
    new = d2.filter_new(jobs2)

    assert len(new) == 1
    assert new[0]["url"] == "https://a.com/3"


def test_intra_batch_dedup(tmp_state):
    d = Deduplicator(state_file=tmp_state)
    jobs = make_jobs(["https://a.com/1", "https://a.com/1"])  # duplicate in same batch
    new = d.filter_new(jobs)
    assert len(new) == 1


def test_state_persisted(tmp_state):
    d = Deduplicator(state_file=tmp_state)
    d.filter_new(make_jobs(["https://x.com/job"]))

    assert tmp_state.exists()
    saved = json.loads(tmp_state.read_text())
    assert "https://x.com/job" in saved


def test_empty_input(tmp_state):
    d = Deduplicator(state_file=tmp_state)
    assert d.filter_new([]) == []
