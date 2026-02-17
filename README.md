# Job Search Tracker

> Automated AI/ML senior job search — Brave Search API → relevance scoring → Google Sheets

Runs 8 targeted search queries, scores results by relevance, deduplicates across runs, and pushes ranked results to a shared Google Sheet updated daily.

**Target roles:** Senior/Principal/Staff ML Engineer, AI Engineer, ML Platform Engineer  
**Target market:** Remote-friendly, EU-based, €100k+ salary floor

---

## 🏗️ Architecture

```
Brave Search API
    ↓  8 queries (senior ML/AI, EU/remote, salary signals)
Raw results (80-160 results)
    ↓  parse_results(): extract salary, location, score each
Scored jobs (filtered: score ≥ 5)
    ↓  Deduplicator: filter already-seen URLs (JSON state file)
New jobs only
    ↓  Sort by score desc, take top 50
    ↓  SheetsWriter: append to Google Sheet via gog CLI
```

---

## 🚀 Setup

### 1. Install

```bash
git clone https://github.com/your-username/job-search-tracker.git
cd job-search-tracker
pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
# Set:
#   BRAVE_API_KEY=your-key-here   (https://api.search.brave.com/)
#   GOG_ACCOUNT=your-google-account  (optional — defaults to kevin.forge@plocha.eu)
```

### 3. Run

```bash
# Dry run — print results, skip sheet write
python3 -m src.main --dry-run

# Full run — create/update Google Sheet
python3 -m src.main

# Append to existing sheet
python3 -m src.main --sheet-id=1ABC...XYZ
```

---

## 📊 Example Output

```
================================================================================
RANK  SCORE  SOURCE        SALARY           TITLE
================================================================================
   1     82  LinkedIn      €120k - €150k    Senior ML Platform Engineer — Remote EU
   2     77  RemoteOK      $150k+           Principal Machine Learning Engineer
   3     72  LinkedIn      —                Senior AI Engineer (LLM, RAG, AWS)
   4     68  LinkedIn      €100k - €130k    Staff Backend Engineer — ML Infrastructure
   5     65  WeWorkRemot   —                Senior ML Engineer, Financial Services
   ...
================================================================================
Total new jobs: 23
```

### Google Sheet columns

| Column | Description |
|--------|-------------|
| Date Found | ISO date of discovery |
| Score | Relevance score (higher = better fit) |
| Title | Job title |
| Company | Company name (if extractable) |
| Location | Remote / EU / city |
| Salary | Extracted salary range (if present) |
| Source | LinkedIn, RemoteOK, etc. |
| Status | new / applied / rejected / offer |
| URL | Direct job link |
| Description | First 300 chars of snippet |

---

## ⚙️ Customisation

### Adjust search queries — `src/config.py`

```python
SEARCH_QUERIES = [
    'site:linkedin.com/jobs "senior ML engineer" remote OR EU "150k"',
    # Add your own...
]
```

### Tune scoring — `src/config.py`

```python
SCORE_WEIGHTS = {
    "ml platform": 15,   # increase weight for platform roles
    "java": 8,           # your Java background as edge
    "intern": -30,       # strong negative signal
    # ...
}
```

### Change freshness — `.env`

```env
FRESHNESS=pw    # pd=past day, pw=past week, pm=past month
```

---

## 🧪 Tests

```bash
pytest tests/ -v

# tests/test_parser.py       — scoring, salary/location extraction, filtering
# tests/test_deduplicator.py — cross-run deduplication and state persistence
```

---

## 📁 Structure

```
job-search-tracker/
├── src/
│   ├── config.py          # Queries, scoring weights, API config
│   ├── searcher.py        # Brave Search API client
│   ├── parser.py          # Result scoring, salary/location extraction
│   ├── deduplicator.py    # Cross-run URL deduplication (JSON state)
│   ├── sheets.py          # Google Sheets writer via gog CLI
│   └── main.py            # Pipeline orchestrator + CLI
├── tests/
│   ├── test_parser.py
│   └── test_deduplicator.py
├── data/
│   ├── seen_urls.json     # State file (gitignored)
│   └── sheet_id.txt       # Persisted Sheet ID (gitignored)
├── .env.example
├── requirements.txt
└── README.md
```

---

## 🔄 Running Daily (cron)

```bash
# Add to crontab: every morning at 8am
0 8 * * * cd /path/to/job-search-tracker && python3 -m src.main >> logs/daily.log 2>&1
```

Or set up an OpenClaw cron job for autonomous daily execution.

---

## 📝 License

MIT
