"""
Source: Jobright (jobright.ai).  READ THIS.

Honest status: Jobright is an AI job-*matching* platform. Its listings are
personalized to your profile and served behind a login (web app + iOS/Android),
with **no public/developer API**. There is no ToS-friendly way for a headless
GitHub Actions job to pull it, and its underlying feed is itself aggregated from
LinkedIn and other boards you already cover.

Realistic options:
  1. Skip it (recommended) -- it's a personalized front-end over sources you
     already have, not a data provider.
  2. Keep using the Jobright app directly for its matching/UX; use THIS bot for
     the raw firehose of new postings. They complement rather than overlap.

No-op by default. Would be raw postings -> trust_year=False.
"""

ENABLED = False


def _fetch_authenticated():
    raise NotImplementedError(
        "Jobright has no public API and is login/ToS-gated. Not implemented."
    )


def fetch():
    """Return (jobs, trust_year=False)."""
    if not ENABLED:
        return [], False
    return _fetch_authenticated(), False
