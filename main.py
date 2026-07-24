"""
Orchestrator: gather -> filter -> de-dup -> notify -> persist.

Run once per invocation. GitHub Actions calls this every 15 minutes; on your
machine you can also just `python main.py`.
"""

import sys

import config
from filters import is_relevant
from store import load_seen, save_seen, is_first_run
from notify import send_jobs
from job import Job
from sources import github_lists, ats, workday, indeed, internlist, jobright


def gather():
    """
    Pull from every source. Each returns (jobs, trust_year).

    We keep trust_year attached per-source because GitHub lists are already
    season-scoped (relax the year filter) while raw ATS/Indeed postings are not
    (enforce it). See filters.py.
    """
    batches = []
    batches.append(github_lists.fetch(config.GITHUB_LISTING_URLS))
    batches.append(
        ats.fetch(
            config.GREENHOUSE_SLUGS,
            config.LEVER_SLUGS,
            config.ASHBY_SLUGS,
            config.SMARTRECRUITERS_SLUGS,
        )
    )
    batches.append(
        workday.fetch(config.WORKDAY_COMPANIES, config.WORKDAY_SEARCH_TEXT)
    )
    # Disabled stubs (no public API) -- return empty, kept for easy enabling.
    batches.append(indeed.fetch(config.INDEED_QUERY, config.INDEED_LOCATION))
    batches.append(internlist.fetch(config.INDEED_QUERY))
    batches.append(jobright.fetch())
    return batches


def run_test():
    """
    Send ONE sample embed to the channel to verify token / permissions / channel
    id -- without touching the real pipeline or seen.json. Invoked via
    `python main.py --test`.
    """
    sample = Job(
        company="Example Corp",
        title="Software Engineer Intern (Summer 2027) — TEST",
        url="https://example.com/careers/swe-intern-2027",
        location="Remote / New York, NY",
        source="self-test",
    )
    print("sending one test embed to Discord...")
    send_jobs([sample])
    print("test embed sent -- check your channel.")


def main():
    first_run = is_first_run(config.SEEN_STORE_PATH)
    seen = load_seen(config.SEEN_STORE_PATH)

    # Collect relevant jobs, de-duping within this run and against history.
    relevant = {}  # uid -> Job
    total_scanned = 0
    for jobs, trust_year in gather():
        for job in jobs:
            total_scanned += 1
            if not job.title or not job.company:
                continue
            if not is_relevant(job, trust_year=trust_year):
                continue
            relevant[job.uid()] = job

    new_uids = [uid for uid in relevant if uid not in seen]
    new_jobs = [relevant[uid] for uid in new_uids]

    print(
        f"scanned={total_scanned} relevant={len(relevant)} "
        f"new={len(new_jobs)} known={len(seen)} first_run={first_run}"
    )

    # First-run guard: record everything as seen but DON'T blast the channel.
    if first_run and config.SUPPRESS_FIRST_RUN:
        seen.update(relevant.keys())
        save_seen(config.SEEN_STORE_PATH, seen)
        print("first run: recorded baseline, suppressed notifications")
        return

    if new_jobs:
        # Oldest-ish first is nicer to read; sources give rough order already.
        send_jobs(new_jobs)
        print(f"notified {len(new_jobs)} new posting(s)")
    else:
        print("no new postings")

    seen.update(new_uids)
    save_seen(config.SEEN_STORE_PATH, seen)


if __name__ == "__main__":
    try:
        if "--test" in sys.argv[1:]:
            run_test()
        else:
            main()
    except Exception as e:  # noqa: BLE001 -- surface any failure to Actions logs
        print(f"FATAL: {e}", file=sys.stderr)
        sys.exit(1)
