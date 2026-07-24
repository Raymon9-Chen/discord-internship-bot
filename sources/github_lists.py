"""
Source: community-maintained aggregated listings (listings.json).

These repos already normalize thousands of postings across companies -- including
FAANG, which the ATS sources can't reach. This is your highest-coverage source.

Because the repo is season-scoped (a "Summer 2027" repo only holds 2027 roles),
we mark these jobs trust_year=True so filters.py won't reject titles that omit
the year. We still apply the SWE + internship keyword checks.

The Simplify-style schema (fields we rely on; extras ignored):
  {
    "company_name": "...",
    "title": "...",
    "url": "...",
    "locations": ["..."],
    "date_posted": 1700000000,        # unix seconds (optional)
    "active": true,
    "is_visible": true
  }
"""

import requests

from job import Job

TIMEOUT = 30


def _one_repo(url: str):
    try:
        resp = requests.get(url, timeout=TIMEOUT)
        if resp.status_code == 404:
            return []  # repo/season doesn't exist yet -- fine, skip quietly
        resp.raise_for_status()
        rows = resp.json()
    except (requests.RequestException, ValueError) as e:
        print(f"[github] {url} failed: {e}")
        return []

    # Label the source with the repo owner for readable Discord embeds.
    try:
        owner = url.split("githubusercontent.com/")[1].split("/")[0]
    except IndexError:
        owner = "github"

    jobs = []
    for row in rows:
        # Respect the list's own visibility/active flags when present.
        if row.get("active") is False or row.get("is_visible") is False:
            continue
        locations = row.get("locations") or []
        jobs.append(
            Job(
                company=row.get("company_name", "").strip(),
                title=row.get("title", "").strip(),
                url=(row.get("url") or "").strip(),
                location=", ".join(locations) if isinstance(locations, list) else str(locations),
                source=f"github:{owner}",
                date_posted=str(row.get("date_posted", "")),
            )
        )
    return jobs


def fetch(urls):
    """Return (jobs, trust_year). trust_year=True -- see module docstring."""
    all_jobs = []
    for url in urls:
        all_jobs.extend(_one_repo(url))
    return all_jobs, True
