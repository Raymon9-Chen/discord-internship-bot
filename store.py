"""
Persistence of which postings we've already alerted on.

Implemented as a plain JSON file so it diffs cleanly in git — the GitHub Actions
workflow commits it back after each run, giving us durable state between the
otherwise-stateless 15-minute jobs.
"""

import json
import os
from typing import Set


def load_seen(path: str) -> Set[str]:
    if not os.path.exists(path):
        return set()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return set(data.get("seen", []))
    except (json.JSONDecodeError, OSError):
        # Corrupt/empty file: treat as no history rather than crashing the run.
        return set()


def save_seen(path: str, seen: Set[str]) -> None:
    # Sorted for stable, review-friendly git diffs.
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"seen": sorted(seen)}, f, indent=0)


def is_first_run(path: str) -> bool:
    return not os.path.exists(path)
