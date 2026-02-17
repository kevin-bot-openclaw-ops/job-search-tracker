"""Tests for result parsing and scoring."""

import pytest
from src.parser import score_result, extract_salary, extract_location, parse_results


def make_result(title="", description="", url="https://example.com/job"):
    return {"title": title, "description": description, "url": url}


# ── Scoring ────────────────────────────────────────────────────────────────────

def test_score_senior_ml_engineer():
    r = make_result("Senior ML Engineer", "Remote, €150k, machine learning platform")
    score = score_result(r)
    assert score >= 40  # senior + ml engineer + remote + 150k + machine learning


def test_score_junior_penalised():
    r = make_result("Junior ML Engineer", "Entry level machine learning position")
    score = score_result(r)
    assert score < 0  # junior + entry level = heavy negative


def test_score_java_backend_ai():
    r = make_result("Senior Backend Engineer", "Java, Spring, AWS, LLM, RAG pipelines")
    score = score_result(r)
    assert score >= 20  # senior + java + aws + llm + rag


def test_score_empty():
    r = make_result()
    assert score_result(r) == 0


# ── Salary extraction ──────────────────────────────────────────────────────────

def test_extract_salary_eur_range():
    assert "€100k" in extract_salary("Salary: €100k - €150k per year")


def test_extract_salary_usd():
    assert "$" in extract_salary("Up to $150k for senior candidates")


def test_extract_salary_missing():
    assert extract_salary("Great opportunity in Berlin") == ""


# ── Location extraction ────────────────────────────────────────────────────────

def test_location_fully_remote():
    loc = extract_location("Fully remote position, EU timezone preferred")
    assert "Remote" in loc


def test_location_europe():
    loc = extract_location("Based in Amsterdam or Berlin, remote-friendly")
    assert "Remote" in loc or "Amsterdam" in loc or "Berlin" in loc


def test_location_unknown():
    loc = extract_location("No location information provided")
    assert loc == "Unknown"


# ── parse_results ──────────────────────────────────────────────────────────────

def test_parse_results_filters_low_score():
    raw = [
        make_result("Senior ML Engineer", "Remote EU €150k machine learning", "https://a.com/1"),
        make_result("PHP Developer", "WordPress plugin development", "https://a.com/2"),
    ]
    jobs = parse_results(raw)
    # Senior ML Engineer should pass; PHP dev should be filtered (score < 5)
    titles = [j["title"] for j in jobs]
    assert "Senior ML Engineer" in titles
    assert "PHP Developer" not in titles


def test_parse_results_structure():
    raw = [make_result("Senior AI Engineer", "Remote, €120k, LLM, RAG", "https://a.com/3")]
    jobs = parse_results(raw)
    assert len(jobs) == 1
    job = jobs[0]
    for field in ["title", "url", "score", "date_found", "source", "status"]:
        assert field in job


def test_parse_results_empty():
    assert parse_results([]) == []
