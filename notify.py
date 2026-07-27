"""
Send notifications to Discord using the BOT token via the REST API.

Why REST and not a discord.py gateway bot? GitHub Actions runs this script and
then exits, so there's no long-lived process to hold a gateway connection. The
REST endpoint lets us post as our bot from a short-lived job. Messages still
come from your bot account, with real embeds.

If you later move to an always-on host and want slash commands, you'd add a
discord.py client alongside this -- this module keeps working unchanged.
"""

import time
import requests

from config import DISCORD_BOT_TOKEN, DISCORD_CHANNEL_ID
from job import Job

API = "https://discord.com/api/v10"


def _headers() -> dict:
    return {
        "Authorization": f"Bot {DISCORD_BOT_TOKEN}",
        "Content-Type": "application/json",
    }


def _embed(job: Job) -> dict:
    return {
        "title": f"{job.title}",
        "url": job.url or None,
        "color": 0x2ECC71,
        "fields": [
            {"name": "Company", "value": job.company or "—", "inline": True},
            {"name": "Location", "value": job.location or "—", "inline": True},
            {"name": "Source", "value": job.source or "—", "inline": True},
        ],
        "footer": {"text": "Summer 2027 Tech Internship"},
    }


def send_jobs(jobs) -> None:
    """Post one message per job. Handles Discord rate limits politely."""
    if not (DISCORD_BOT_TOKEN and DISCORD_CHANNEL_ID):
        raise RuntimeError(
            "DISCORD_BOT_TOKEN and DISCORD_CHANNEL_ID must be set in the "
            "environment. See README.md."
        )

    url = f"{API}/channels/{DISCORD_CHANNEL_ID}/messages"
    total = len(jobs)
    for i, job in enumerate(jobs, 1):
        payload = {"embeds": [_embed(job)]}
        for attempt in range(6):  # bounded: never loop on 429 forever
            resp = requests.post(url, headers=_headers(), json=payload, timeout=30)
            if resp.status_code == 429:  # rate limited -- back off and retry
                try:
                    retry = float(resp.json().get("retry_after", 1))
                except ValueError:
                    retry = 1.0
                print(f"  rate limited, waiting {retry:.1f}s (attempt {attempt+1})")
                time.sleep(retry + 0.25)
                continue
            if not resp.ok:
                # Surface Discord's own error code/message -- e.g. 50001 Missing
                # Access (bot not in server / can't see channel) vs 50013 Missing
                # Permissions (in channel but can't Send). Far more useful than a
                # bare HTTP status.
                try:
                    body = resp.json()
                    detail = f"code {body.get('code')}: {body.get('message')}"
                except ValueError:
                    detail = resp.text[:300]
                raise RuntimeError(f"Discord {resp.status_code} -> {detail}")
            print(f"  posted {i}/{total}: {job.company} — {job.title[:60]}")
            break
        else:
            # Exhausted retries (persistent 429). Skip rather than hang the run.
            print(f"  gave up on {i}/{total} after repeated rate limits")
        # Gentle spacing so a big first batch doesn't trip global limits.
        time.sleep(0.6)
