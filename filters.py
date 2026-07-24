"""
Decide whether a normalized Job is a Summer-2027 technical internship we care
about (software, ML/AI, data, robotics, and adjacent engineering roles).

The rule (all must hold):
  1. Looks like a technical role         (ROLE_KEYWORDS)
  2. Looks like an internship             (INTERN_KEYWORDS)
  3. Is not obviously excluded            (NEGATIVE_KEYWORDS)
  4. Targets 2027                          (YEAR_KEYWORDS) -- see note below

Matching is WHOLE-WORD, not substring. Each keyword is compiled into
`\b(?:...)s?\b` (case-insensitive), so:
  * short acronyms are safe -- "ai" matches "AI" / "AI/ML" but NOT "available",
    "ml" matches "ML" but NOT "html", "swe" matches "SWE" but NOT "answer".
  * a trailing plural "s" is tolerated -- "engineer" also matches "engineers".
Because whole-word matching means "intern" no longer covers "internship",
INTERN_KEYWORDS lists the needed variants explicitly.

Note on the year check: many titles omit the year ("Software Engineer Intern").
GitHub-list sources carry season metadata, so for those we trust the source to
already be a 2027 list and RELAX rule 4. For ATS/Workday/Indeed sources (raw
postings), we ENFORCE rule 4 so we don't grab a 2026 posting. Sources signal
this via the `trust_year` argument.
"""

import re

from config import (
    ROLE_KEYWORDS,
    INTERN_KEYWORDS,
    YEAR_KEYWORDS,
    NEGATIVE_KEYWORDS,
)
from job import Job


def _compile(keywords):
    """One case-insensitive whole-word alternation regex for a keyword list."""
    alts = "|".join(re.escape(k) for k in keywords)
    # \b ... s?\b -> whole word, optional trailing plural. See module docstring.
    return re.compile(r"\b(?:" + alts + r")s?\b", re.IGNORECASE)


_ROLE_RE = _compile(ROLE_KEYWORDS)
_INTERN_RE = _compile(INTERN_KEYWORDS)
_YEAR_RE = _compile(YEAR_KEYWORDS)
_NEG_RE = _compile(NEGATIVE_KEYWORDS)


def is_relevant(job: Job, trust_year: bool = False) -> bool:
    hay = job.haystack()

    if not _ROLE_RE.search(hay):
        return False
    if not _INTERN_RE.search(hay):
        return False
    if _NEG_RE.search(hay):
        return False
    if not trust_year and not _YEAR_RE.search(hay):
        return False

    return True
