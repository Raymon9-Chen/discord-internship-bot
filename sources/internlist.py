"""
Source: Intern-List (intern-list.com).  READ THIS.

Honest status: Intern-List is a subscription product with **no public API or
JSON feed**. It advertises that it aggregates from "LinkedIn, Indeed, Handshake,
and 200K+ career sites" -- i.e. it re-aggregates the same origins your GitHub
lists already ingest, so enabling it would add little unique coverage. Scraping
its paid/gated pages would violate its ToS.

Realistic options if you still want it:
  1. Skip it (recommended) -- coverage overlaps your existing sources.
  2. If you pay for it and it offers an authenticated export/feed, implement
     _fetch_authenticated() below using YOUR account credentials, and store
     them as environment secrets (never in code).

No-op by default so the pipeline runs. These would be raw postings, hence
trust_year=False.
"""

ENABLED = False


def _fetch_authenticated(query):
    raise NotImplementedError(
        "Intern-List has no public API. Implement only against an authenticated "
        "export you're entitled to. See module docstring."
    )


def fetch(query):
    """Return (jobs, trust_year=False)."""
    if not ENABLED:
        return [], False
    return _fetch_authenticated(query), False
