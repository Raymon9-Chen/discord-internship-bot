"""
Source: Applicant Tracking System public JSON boards.

Instead of scraping N company career pages, we hit the handful of platforms
those pages are built on. Each returns clean JSON. These are your FASTEST signal
for non-FAANG companies -- you're polling the origin, often ahead of the lists.

Covered here: Greenhouse, Lever, Ashby. Adding Workday/SmartRecruiters later is
the same pattern (fetch -> map to Job).

Raw postings rarely put "2027" in the title, but we MUST NOT relax the year
check here or we'd grab 2026 roles -- so these return trust_year=False, and we
enrich each Job's extra_text with any description so the year filter has a
chance to match.
"""

import requests

from job import Job

TIMEOUT = 30


def _get_json(url):
    try:
        resp = requests.get(url, timeout=TIMEOUT)
        if resp.status_code == 404:
            return None  # unknown/relocated slug -- skip
        resp.raise_for_status()
        return resp.json()
    except (requests.RequestException, ValueError) as e:
        print(f"[ats] {url} failed: {e}")
        return None


def _greenhouse(slug):
    # content=true includes the job description text (helps the year filter).
    data = _get_json(
        f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true"
    )
    if not data:
        return []
    out = []
    for j in data.get("jobs", []):
        loc = (j.get("location") or {}).get("name", "")
        out.append(
            Job(
                company=slug,
                title=j.get("title", "").strip(),
                url=j.get("absolute_url", ""),
                location=loc,
                source="greenhouse",
                date_posted=j.get("updated_at", ""),
                extra_text=j.get("content", "") or "",
            )
        )
    return out


def _lever(slug):
    data = _get_json(f"https://api.lever.co/v0/postings/{slug}?mode=json")
    if not data:
        return []
    out = []
    for j in data:
        cats = j.get("categories") or {}
        out.append(
            Job(
                company=slug,
                title=j.get("text", "").strip(),
                url=j.get("hostedUrl", ""),
                location=cats.get("location", ""),
                source="lever",
                date_posted=str(j.get("createdAt", "")),
                extra_text=(j.get("descriptionPlain", "") or ""),
            )
        )
    return out


def _ashby(slug):
    data = _get_json(
        f"https://api.ashbyhq.com/posting-api/job-board/{slug}?includeCompensation=false"
    )
    if not data:
        return []
    out = []
    for j in data.get("jobs", []):
        out.append(
            Job(
                company=slug,
                title=j.get("title", "").strip(),
                url=j.get("jobUrl", ""),
                location=j.get("location", ""),
                source="ashby",
                date_posted=j.get("publishedAt", ""),
                extra_text=j.get("descriptionPlain", "") or "",
            )
        )
    return out


def _smartrecruiters(slug):
    # Public postings API; paginated 100 at a time.
    out = []
    offset = 0
    for _ in range(5):  # cap at 500 postings/company -- plenty
        data = _get_json(
            f"https://api.smartrecruiters.com/v1/companies/{slug}/postings"
            f"?limit=100&offset={offset}"
        )
        if not data:
            break
        content = data.get("content", [])
        for j in content:
            loc = j.get("location", {}) or {}
            loc_str = ", ".join(
                p for p in [loc.get("city"), loc.get("region"), loc.get("country")] if p
            )
            if loc.get("remote"):
                loc_str = (loc_str + ", Remote").lstrip(", ")
            jid = j.get("id", "")
            out.append(
                Job(
                    company=j.get("company", {}).get("name", slug) or slug,
                    title=j.get("name", "").strip(),
                    url=f"https://jobs.smartrecruiters.com/{slug}/{jid}",
                    location=loc_str,
                    source="smartrecruiters",
                    date_posted=j.get("releasedDate", ""),
                )
            )
        # Stop when we've read the last page.
        if offset + len(content) >= data.get("totalFound", 0) or not content:
            break
        offset += 100
    return out


def fetch(greenhouse_slugs, lever_slugs, ashby_slugs, smartrecruiters_slugs=()):
    """Return (jobs, trust_year=False). See module docstring."""
    jobs = []
    for s in greenhouse_slugs:
        jobs.extend(_greenhouse(s))
    for s in lever_slugs:
        jobs.extend(_lever(s))
    for s in ashby_slugs:
        jobs.extend(_ashby(s))
    for s in smartrecruiters_slugs:
        jobs.extend(_smartrecruiters(s))
    return jobs, False
