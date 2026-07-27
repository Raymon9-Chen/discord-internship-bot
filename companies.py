"""
Company slugs to poll on each ATS platform.

A "slug" is the company identifier inside the board URL, e.g.:
  Greenhouse -> https://boards.greenhouse.io/stripe          -> "stripe"
  Lever      -> https://jobs.lever.co/plaid                  -> "plaid"
  Ashby      -> https://jobs.ashbyhq.com/ramp                -> "ramp"

How to grow this list:
  1. When a listing arrives from the GitHub source, note the company + which
     platform its apply URL points to, and add the slug here.
  2. Or eyeball a company's careers page; the URL tells you platform + slug.

The examples below are illustrative and may drift over time (companies switch
platforms). Wrong slugs just 404 and are skipped, so a stale entry is harmless.
"""

# All slugs below were verified live against each platform's API (they return
# active postings). Add more the same way -- a wrong slug just 404s and is
# skipped, so bad entries are harmless.
GREENHOUSE_SLUGS = [
    "databricks", "stripe", "datadog", "mongodb", "samsara", "brex",
    "verkada", "roblox", "scaleai", "pinterest", "airbnb", "reddit",
    "gitlab", "figma", "affirm", "lyft", "coinbase", "asana", "instacart",
    "robinhood", "gusto", "chime", "faire", "twitch", "sofi", "discord",
    "airtable", "dropbox",
]

LEVER_SLUGS = [
    "palantir",
]

ASHBY_SLUGS = [
    "openai", "cohere", "notion", "ramp", "vanta", "replit", "clickup",
    "watershed", "linear", "posthog", "runway",
]

# SmartRecruiters: slug is the company id in jobs.smartrecruiters.com/{slug}.
SMARTRECRUITERS_SLUGS = [
    "Visa",
]

# Workday is per-tenant, so each company needs THREE parts, not one slug:
#   host   -> the careers hostname, e.g. "nvidia.wd5.myworkdayjobs.com"
#   tenant -> the tenant id in that host, usually the subdomain, e.g. "nvidia"
#   site   -> the career-site id, e.g. "NVIDIAExternalCareerSite"
# How to find them: open a company's Workday careers page and look at the URL:
#   https://{host}/en-US/{site}/...   and the API lives at
#   https://{host}/wday/cxs/{tenant}/{site}/jobs
# The two below are verified working. Tenants DO drift over time; a wrong entry
# just fails and is skipped. Add more the same way.
WORKDAY_COMPANIES = [
    {
        "host": "nvidia.wd5.myworkdayjobs.com",
        "tenant": "nvidia",
        "site": "NVIDIAExternalCareerSite",
    },
    {
        "host": "salesforce.wd12.myworkdayjobs.com",
        "tenant": "salesforce",
        "site": "External_Career_Site",
    },
]
