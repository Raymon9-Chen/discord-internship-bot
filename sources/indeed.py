"""
Source: Indeed.  READ THIS before relying on it.

Honest caveat: Indeed does not offer an open public jobs API anymore. Its old
Publisher API is deprecated/closed, and scraping indeed.com HTML violates their
Terms of Service and is actively blocked (CAPTCHAs, IP bans). So there is no
clean, ToS-friendly way for a self-hosted GitHub Actions bot to pull Indeed the
way it can pull Greenhouse/Lever/Ashby or the GitHub lists.

Your realistic options:
  1. Skip Indeed. The GitHub lists already ingest many Indeed-origin postings,
     so coverage loss is smaller than it looks. (Recommended.)
  2. Use a paid, ToS-compliant jobs API that includes Indeed data (e.g. a
     licensed aggregator). Plug your provider's client in below.
  3. Official Indeed partner/ATS access if you qualify.

This module is a safe no-op by default so the rest of the pipeline runs. Flip
ENABLED to True and implement _fetch_from_provider() once you have a compliant
data source.
"""

ENABLED = False


def _fetch_from_provider(query, location):
    # Implement against your licensed provider. Must return a list[Job] with
    # trust_year handled by the caller (we return trust_year=False below since
    # these would be raw postings).
    raise NotImplementedError(
        "Wire up a ToS-compliant jobs API here. See module docstring."
    )


def fetch(query, location):
    """Return (jobs, trust_year=False)."""
    if not ENABLED:
        return [], False
    return _fetch_from_provider(query, location), False
