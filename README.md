# Summer 2027 SWE Internship Notifier

A Discord bot that checks for new Summer 2027 software-engineering internship
postings every ~15 minutes and posts new ones to a channel.

## How it actually finds jobs

It does **not** try to scrape every company website (impossible + fragile).
Instead it pulls from stable, structured sources:

| Source | What it covers | Speed |
|---|---|---|
| **GitHub community lists** (`listings.json`) | Broadest coverage, **including FAANG** | Minutes–hours after a posting goes live |
| **ATS boards** (Greenhouse / Lever / Ashby / **SmartRecruiters** JSON APIs) | Startups + many known tech cos (Stripe, Databricks, Visa, …). **Not** FAANG. | Fastest — you poll the origin |
| **Workday** (per-tenant CxS JSON) | Big enterprises on Workday (NVIDIA, Salesforce, …) | Fast — you poll the origin |
| **Indeed / Intern-List / Jobright** | *Disabled stubs* — none expose a ToS-friendly public API; they re-aggregate sources already covered above. See `sources/indeed.py`, `internlist.py`, `jobright.py`. | — |

New postings are de-duplicated against `seen.json` so you're alerted **once** per
role, never re-spammed.

## Architecture

```
main.py
  ├─ sources/github_lists.py   fetch listings.json (trust_year=True)
  ├─ sources/ats.py            Greenhouse/Lever/Ashby JSON (trust_year=False)
  ├─ sources/indeed.py         no-op stub (see caveat)
  ├─ filters.py                SWE + intern + (2027) - excludes
  ├─ store.py                  seen.json de-dup (committed back by CI)
  └─ notify.py                 posts embeds via Discord REST using your bot token
```

## Setup

### 1. Discord
1. In the [Developer Portal](https://discord.com/developers/applications) open your
   app → **Bot** → copy the **token**.
2. Invite the bot to your server (OAuth2 URL with the `bot` scope) and make sure
   it can **View Channel** + **Send Messages** in your target channel.
3. Turn on Developer Mode in Discord → right-click the channel → **Copy Channel ID**.

### 2. Run locally (test)
```powershell
pip install -r requirements.txt
$env:DISCORD_BOT_TOKEN = "your-token"
$env:DISCORD_CHANNEL_ID = "your-channel-id"
python main.py
```
The **first run** records a baseline and sends nothing (so you don't get 500
alerts at once). Every run after that posts only newly-appeared roles.

**Confirm Discord works first** — send a single sample embed without touching the
real pipeline or `seen.json`:
```powershell
$env:DISCORD_BOT_TOKEN  = "your-token"
$env:DISCORD_CHANNEL_ID = "1530081281126436946"
python main.py --test
```
You should see one "Software Engineer Intern (Summer 2027) — TEST" card appear in
your channel. If it errors, it'll tell you what's missing (token, or the bot
isn't in the server / lacks Send Messages). Once that works, run `python main.py`
for the real thing.

### 3. Deploy on GitHub Actions (runs when your PC is off)
1. Push this folder to a GitHub repo.
2. Repo → **Settings → Secrets and variables → Actions** → add
   `DISCORD_BOT_TOKEN` and `DISCORD_CHANNEL_ID`.
3. The workflow in `.github/workflows/check.yml` runs every ~15 min and commits
   `seen.json` back so state survives between runs. Trigger a first run manually
   from the **Actions** tab (`workflow_dispatch`).

> GitHub's scheduled runners are best-effort and can lag under load, and cron is
> UTC. If you need hard 15-min precision or slash commands, host it always-on
> (Railway/Fly/VPS) instead and add a discord.py client next to `notify.py`.

## Tuning

- **More companies / faster signal:** add slugs to `companies.py`. When a listing
  arrives whose apply URL is `boards.greenhouse.io/foo`, add `"foo"` to
  `GREENHOUSE_SLUGS` (same idea for Lever/Ashby/SmartRecruiters).
- **Workday companies** need three parts, not one slug — `host`, `tenant`, `site`
  — read straight off the careers-page URL. See the commented example in
  `companies.py`. The bundled entries are illustrative; replace with tenants you
  want. A wrong entry simply 404s and is skipped.
- **The bundled slugs are examples.** `Square`/`Bosch`/etc. are placeholders to
  show the shape and may return 0 — swap in the real companies you care about.
- **Different year/role/filters:** edit the keyword lists in `config.py`.
- **New 2027 repos:** update `GITHUB_LISTING_URLS` in `config.py` as the
  `Summer2027-Internships` repos appear.

## Files
- `config.py` — all tunables + secrets from env
- `companies.py` — ATS slugs to poll
- `job.py` — the normalized posting shape + de-dup id
- `filters.py`, `store.py`, `notify.py`, `main.py`, `sources/`
