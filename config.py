"""
Central configuration for the internship notifier.

Everything here is plain data so you can tweak behavior without touching logic.
Secrets (bot token, channel id) come from environment variables, NOT this file,
so you never commit them. See README.md.
"""

import os

# ---------------------------------------------------------------------------
# Discord (read from environment / GitHub Actions secrets)
# ---------------------------------------------------------------------------
# .strip() guards against a stray newline/space pasted into the secret, which
# would otherwise corrupt the Authorization header ("Bot <token>\n").
DISCORD_BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN", "").strip()
DISCORD_CHANNEL_ID = os.environ.get("DISCORD_CHANNEL_ID", "").strip()

# ---------------------------------------------------------------------------
# What counts as a match
# ---------------------------------------------------------------------------
# A posting must look like a technical / software-adjacent role. Keywords are
# matched as whole words (see filters.py), so short acronyms like "ai"/"ml" are
# safe -- they won't match inside "available" or "html". Add/remove freely.
ROLE_KEYWORDS = [
    # --- Core software engineering ---
    "software", "swe", "sde", "developer", "development", "engineer",
    "engineering", "programmer", "programming", "full stack", "full-stack",
    "backend", "back end", "frontend", "front end", "web", "mobile", "ios",
    "android", "embedded", "firmware", "devops", "sre", "site reliability",
    "distributed systems", "platform", "infrastructure", "compiler",
    # --- AI / ML ---
    "machine learning", "ml", "deep learning", "artificial intelligence", "ai",
    "nlp", "natural language", "computer vision", "llm", "genai",
    "generative ai", "reinforcement learning", "mlops",
    # --- Data ---
    "data science", "data scientist", "data engineer", "data engineering",
    "data analyst", "data analytics", "analytics", "data platform",
    "data infrastructure",
    # --- Robotics / autonomy / perception ---
    "robotics", "robot", "autonomy", "autonomous", "self-driving",
    "perception", "slam", "motion planning", "sensor fusion", "controls", "VLA"
    # --- Adjacent technical research / engineering ---
    "research engineer", "research scientist", "applied scientist",
    "quantitative", "security engineer", "cybersecurity", "cryptography",
    "graphics", "simulation", "hardware", "fpga", "asic",
]

# ...AND look like an internship. Variants are explicit because matching is
# whole-word (a plain "intern" no longer implies "internship").
INTERN_KEYWORDS = [
    "intern",
    "internship",
    "co-op",
    "coop",
]

# ...AND target the right season/year. We accept a title/desc that mentions
# 2027, OR a listing whose season metadata says Summer 2027. Titles are often
# vague ("Software Engineer Intern"), so YEAR_KEYWORDS is applied loosely:
# see filters.py for exactly how these combine.
YEAR_KEYWORDS = [
    "2027",
    "summer 2027",
]

# Titles we almost never want, even if they match above.
NEGATIVE_KEYWORDS = [
    "phd",
    "ph.d",
    "senior",
    "staff",
    "principal",
    "manager",
    "director",
]

# ---------------------------------------------------------------------------
# GitHub aggregated lists
# ---------------------------------------------------------------------------
# Each entry points at a raw listings.json maintained by the community.
# The Summer2027 repos may not exist yet at your run date; missing repos are
# skipped gracefully. Add/remove freely.
GITHUB_LISTING_URLS = [
    "https://raw.githubusercontent.com/SimplifyJobs/Summer2027-Internships/dev/.github/scripts/listings.json",
    "https://raw.githubusercontent.com/vanshb03/Summer2027-Internships/dev/.github/scripts/listings.json",
    "https://raw.githubusercontent.com/cvrve/Summer2027-Internships/dev/.github/scripts/listings.json",
    # 2026 repos as a fallback so you see the pipeline working today:
    "https://raw.githubusercontent.com/SimplifyJobs/Summer2026-Internships/dev/.github/scripts/listings.json",
]

# ---------------------------------------------------------------------------
# ATS boards to poll directly (fastest signal for non-FAANG companies).
# Slug = the company identifier in that platform's URL. Seed these from the
# GitHub lists / company career pages. See companies.py.
# ---------------------------------------------------------------------------
# Imported here to keep one import site for main.py.
from companies import (  # noqa: E402
    GREENHOUSE_SLUGS,
    LEVER_SLUGS,
    ASHBY_SLUGS,
    SMARTRECRUITERS_SLUGS,
    WORKDAY_COMPANIES,
)

# Workday search text sent to each tenant to keep the response small; "intern"
# is broad enough to catch SWE intern titles without pulling the whole board.
WORKDAY_SEARCH_TEXT = "intern"

# ---------------------------------------------------------------------------
# Indeed
# ---------------------------------------------------------------------------
# Free-text query used if you wire up an Indeed source. See sources/indeed.py
# for the important caveat about Indeed access.
INDEED_QUERY = "software engineer intern 2027"
INDEED_LOCATION = "United States"

# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------
SEEN_STORE_PATH = "seen.json"

# Cap how many postings we notify in a single run. If more than this are new,
# we send the first N, mark only those as seen, and the rest roll over to the
# next run -- this paces big catch-up batches so Discord doesn't rate-limit us
# into a multi-minute crawl. Set to 0 for no cap.
MAX_NOTIFY_PER_RUN = 40

# On the very first run there is no history, so EVERY current posting would be
# "new" and spam your channel. When True, the first run records everything as
# seen WITHOUT notifying, and you get alerts only for postings that appear
# afterwards. Set to False if you actually want the initial dump.
SUPPRESS_FIRST_RUN = True
