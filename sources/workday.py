"""
Source: Workday career sites (CxS JSON endpoint).

Workday is per-company ("tenant"), so unlike Greenhouse/Lever there's no single
host -- each company entry supplies host/tenant/site (see companies.py). The
career-site JSON API lives at:

    POST https://{host}/wday/cxs/{tenant}/{site}/jobs
    body: {"appliedFacets":{}, "limit":20, "offset":0, "searchText":"intern"}

Response shape we use:
    {
      "total": 137,
      "jobPostings": [
        {"title": "...", "externalPath": "/job/Loc/Title_R-123",
         "locationsText": "...", "postedOn": "Posted 3 Days Ago"}
      ]
    }

Workday caps `limit` at 20, so we page with `offset` until we've read `total`
(bounded so a huge board can't hang the run). These are raw postings, so we
return trust_year=False and enforce the 2027 filter upstream.
"""

import requests

from job import Job

TIMEOUT = 15       # Workday can stall from datacenter IPs -- fail fast
PAGE = 20          # Workday's hard max per request
MAX_PAGES = 4      # safety bound: up to 80 matches per tenant per run


def _one_company(entry, search_text):
    host = entry.get("host", "")
    tenant = entry.get("tenant", "")
    site = entry.get("site", "")
    if not (host and tenant and site):
        return []

    api = f"https://{host}/wday/cxs/{tenant}/{site}/jobs"
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    out = []
    offset = 0

    for _ in range(MAX_PAGES):
        body = {
            "appliedFacets": {},
            "limit": PAGE,
            "offset": offset,
            "searchText": search_text,
        }
        try:
            resp = requests.post(api, json=body, headers=headers, timeout=TIMEOUT)
            if resp.status_code == 404:
                return []  # bad tenant/site -- skip quietly
            resp.raise_for_status()
            data = resp.json()
        except (requests.RequestException, ValueError) as e:
            print(f"[workday] {tenant} failed: {e}")
            break

        postings = data.get("jobPostings", []) or []
        for j in postings:
            ext = j.get("externalPath", "") or ""
            # Canonical external URL. If a tenant 404s on this shape, drop the
            # "/en-US" segment for that company -- some sites omit the locale.
            url = f"https://{host}/en-US/{site}{ext}" if ext else ""
            out.append(
                Job(
                    company=tenant,
                    title=j.get("title", "").strip(),
                    url=url,
                    location=j.get("locationsText", "") or "",
                    source="workday",
                    date_posted=j.get("postedOn", "") or "",
                )
            )

        total = data.get("total", 0)
        offset += PAGE
        if offset >= total or not postings:
            break

    return out


def fetch(companies, search_text="intern"):
    """Return (jobs, trust_year=False). See module docstring."""
    jobs = []
    for entry in companies:
        jobs.extend(_one_company(entry, search_text))
    return jobs, False
