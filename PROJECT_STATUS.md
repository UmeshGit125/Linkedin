# LinkedIn Assistant — Implementation Status

_A snapshot of what this project is, what is already built and running, what is not,
its tech stack, and what still needs doing._

Last reviewed: 2026-10-06

---

## 1. What the project is

A personal **LinkedIn assistant** that runs on this Mac. It has three jobs:

1. **Posts** — drafts LinkedIn posts (TOFU / MOFU / Authority) from the content system
   in `Docs/`, runs every draft through a verification gate, and publishes only when the
   gate says `READY` **and** you approved it. First comments are posted by you, manually.
2. **Jobs & internships** — every 30 minutes it searches LinkedIn's official public
   job-search URLs for recent postings, fetches details, extracts the tech stack /
   experience / work mode, AI-scores each job, appends it to `Jobs.xlsx`, and notifies
   you about strong matches.
3. **Comments** — reads someone else's post and either drafts a comment in your voice
   (for you to post manually) or tells you to skip it.

Design principle: **nothing logs in as you in a browser, and nothing comments/applies
automatically.** Publishing uses LinkedIn's official API only; job search uses public
guest endpoints without logging in.

---

## 2. Tech stack

| Layer | What is used |
|---|---|
| Language | **Python ≥ 3.12** (the virtualenv here is Python 3.14) |
| Packaging / runner | **uv** (`uv run assistant …`), Hatchling build backend |
| CLI | Python **argparse** (single entry point: `assistant.cli:main`) |
| AI backend | **Claude Code CLI** (`claude -p`) by default, run headless with a JSON schema for structured output. Optional **Anthropic API** (`anthropic` SDK). Optional **AgentRouter** gateway (`ANTHROPIC_BASE_URL` override for the child process only) |
| Data validation | **pydantic v2** (all AI outputs are validated model objects) |
| Local database | **SQLite** (stdlib `sqlite3`), file `data/assistant.db` |
| Web / parsing | **requests** + **BeautifulSoup4** (LinkedIn public job pages) |
| Spreadsheet | **openpyxl** → `Jobs.xlsx` |
| Resume parsing | **pypdf** |
| Config | **PyYAML** (`config.yaml`) + **python-dotenv** (`.env`) |
| Scheduling (macOS) | **launchd** launch agents (`~/Library/LaunchAgents/com.linkedin-assistant.*.plist`) |
| Notifications | macOS **osascript** desktop notifications, **Telegram Bot API**, **SMTP** email |
| Publishing | LinkedIn **REST API** (`/rest/posts`, versioned) via **OAuth 2.0 + OpenID Connect** |

---

## 3. Code map

All source lives in `assistant/` (~1,800 lines total):

| File | Responsibility |
|---|---|
| `cli.py` | Argparse commands and output; the single entry point |
| `config.py` | Loads `config.yaml`, `.env`; resolves paths, timezone, docs dir |
| `db.py` | SQLite schema + connection + auto column migration + key/value store |
| `knowledge.py` | Finds and loads the rule docs in `Docs/` by keyword; loads resume; builds the candidate profile |
| `llm.py` | All AI calls. Claude Code CLI backend (default) or Anthropic API. Structures outputs against a pydantic schema |
| `posts.py` | Post pipeline: draft → verify → approve → publish; same-day scheduling with jitter; verification gate |
| `linkedin.py` | OAuth sign-in, token storage/expiry, "little text" commentary escaping, publishing |
| `jobs.py` | LinkedIn public job search, detail fetch, tech-stack/experience/work-mode extraction, AI scoring, notifications, cover letters |
| `sheet.py` | Builds/updates `Jobs.xlsx` from the DB, never overwriting your own columns; atomic save |
| `comments.py` | Comment decision + draft |
| `notify.py` | Desktop / Telegram / email notification fan-out |
| `scheduler.py` | Installs/removes the two launchd agents; one "tick" publishes due posts and warns on token expiry |
| `__main__.py` | `python -m assistant` entry point |

---

## 4. What is implemented and working

### ✅ Post pipeline (code complete)
- Three slots with configurable base times (`09:00 / 13:00 / 18:00`) plus ±`jitter_minutes`
  natural variation; `next_slot_time()` avoids collisions and past times.
- `draft` asks the model for a structured `PostDraft` (hook, body, hashtags, optional
  first comment, why-it-works, originality, confidence, open questions), stores it, then
  auto-runs verification. Recent posts are fed in to avoid repetition.
- `verify` runs an independent `GateResult` check against `LinkedIn_Verification_Gate.md`.
  **The gate's hard rule is also enforced in code**: any applicable `fail` forces
  `BLOCKED` regardless of what the model says.
- `approve` requires status `ready`; `publish` requires `approved`. Publishing failures
  are recorded and notified. `edit` re-runs the gate after you edit.
- Same-day plan and scheduling rules are passed to the gate.

### ✅ Job & internship search (working end-to-end)
- Official public guest search URLs with a `f_TPR` time filter, sortBy newest,
  experience-type and job-type filters, optional remote-only ("Worldwide").
- Detail fetch per job: description, seniority, employment type, industries, function,
  applicants, salary, company URL, external apply URL.
- Heuristic extraction of **tech stack** (large regex table), **experience required**,
  and **work mode** (remote / hybrid / on-site).
- Keyword include/exclude filtering → `new` vs `filtered`.
- AI fit scoring (0–100 + verdict + reasons + red flags) in parallel batches through
  pydantic; results are written back and status becomes `scored`.
- Notification for matches at/above `min_score`; below-threshold jobs go to `low-fit`.
- Cover letter generation → `data/letters/job_<id>.md`.
- **Proof it runs:** log shows repeated successful runs today (`new` up to 80 per run,
  `scored`, `added_to_sheet`, `notified`). DB currently holds **43 `notified`,
  146 `filtered`, 1,865 `low-fit`** jobs, and `Jobs.xlsx` exists (~533 KB).

### ✅ Jobs spreadsheet (`Jobs.xlsx`)
- 23 columns incl. role, company, location, work mode, type, seniority, experience,
  tech stack, salary, applicants, industry, fit score, fit notes, apply links, source.
- `My status` / `My notes` columns are preserved (existing rows are never rewritten).
- Scores fill in later for rows added before scoring finished; score cells are
  colour-coded; links are clickable; atomic save; skips safely if the file is open.

### ✅ LinkedIn publishing integration (code complete)
- OAuth 2.0 + OpenID Connect sign-in via a localhost callback server; token cached to
  `data/linkedin_token.json` (60-day life) with 7-day expiry warnings.
- Correct "little text" commentary escaping (reserved characters, hashtag entities) so
  posts don't get truncated, using the versioned REST API.

### ✅ Comments, notifications, scheduler, config
- Comment drafting with a "worth commenting / skip" decision.
- Notification fan-out (desktop always; Telegram + email when configured), each channel
  isolated so a failure doesn't block the others; Telegram message chunking.
- Two launchd agents installed (`run` every 10 min, `jobs` every 30 min), logs in `logs/`.
- SQLite schema for `posts`, `jobs`, `comment_drafts`, `kv`, with automatic column
  migration for existing databases.

---

## 5. What is NOT done yet / gaps

### 🔴 Blocking real use
| # | Gap | Effect |
|---|---|---|
| 1 | **LinkedIn account not connected** — no `assistant auth` run yet; `.env` LinkedIn client id/secret are empty | Cannot publish anything |
| 2 | **`resume.pdf` missing** from the project folder | Job scoring and cover letters run without your resume |
| 3 | **`.env` almost empty** — only `SMTP_HOST/PORT` set. `AGENTROUTER_API_KEY`, `ANTHROPIC_API_KEY`, `LINKEDIN_*`, `TELEGRAM_*`, `SMTP_USER/PASSWORD`, `NOTIFY_EMAIL_TO` all empty | AI currently runs on this Mac's Claude Code login; no AgentRouter; no Telegram/email alerts |

### 🟠 Content-system docs missing (degrade quality; some posts get blocked)
The code looks up 11 logical docs; only 5 exist and one is empty:

| Logical doc | File expected | State |
|---|---|---|
| readme | `Linkedin_System_readme.md` | ✅ ok |
| master | `Linked_Master_system.md` | ✅ ok |
| verification | `LinkedIn_Verification_Gate.md` | ✅ ok |
| first_comment | `LinkedIn_Author_First_Comment_System.md` | ✅ ok |
| **comment_intel** | `LinkedIn_Comment_Intelligence_System.md` | ⚠️ **present but empty (0 bytes)** |
| operating | `LinkedIn_Operating_System.md` | ❌ missing |
| hashtag | `LinkedIn_Hashtag_Intelligence_System.md` | ❌ missing |
| self_learning | `LinkedIn_Self_Learning_System.md` | ❌ missing |
| scheduling | `LinkedIn_Scheduling_System.md` | ❌ missing |
| learning_memory | `LINKEDIN_LEARNING_MEMORY.md` | ❌ missing |
| creator_research | `LinkedIn_Creator_Research.md` | ❌ missing |

Consequences: `draft`/`verify` are told these docs are unavailable and must not guess —
so any claim needing a Proof Inventory gets **blocked** (indeed the only post currently
in the DB is a **blocked** TOFU draft). Comment drafting has no rules doc to follow.
The `Docs/Linkedin_System_readme.md` also references `linkedin_content_system.xlsx`,
`linkedin_outreach_tracker.xlsx` and `reviewable_automation_diagram.png` — **none of
these files are present**, and the code does not read them.

### 🟡 Behaviour is currently unproven
- **No post has ever been published** — posts table has only 1 row (blocked). The
  publish path is written but untested end-to-end against the real API.
- **No metrics loop yet in practice** — `metrics` is manual entry; nothing feeds results
  back into a learning memory automatically.

### 🟡 Robustness / engineering gaps
- **Network errors crash the job run:** a `requests.ConnectionError` (DNS failure) is in
  `logs/jobs.err.log` from `_linkedin_details`. `RateLimited` is caught, but general
  connection errors during search/detail are **not**, so one outage can abort a run.
- **Aggressive rate-limiting:** LinkedIn returns 429 frequently; runs sometimes stop
  early ("rate-limited; saving what we have"). Common enough to consider backoff/jitter
  and caching of already-fetched detail pages.
- **No tests, no CI, not a git repo** (only a `.gitignore` exists) — no safety net for
  changes and no version history.
- **Visuals unsupported:** text-only posts; the gate is told "Visual: none attached".
- **Remotive source** is implemented but disabled (`config.yaml → sources.remotive: false`).
- **Comment posting** is manual by design; there is no "done" workflow beyond marking a
  draft posted.
- `anthropic` API backend path exists but is unexercised; there is no automatic fallback
  between backends if the Claude Code login fails.

---

## 6. Current live state (as of this review)

```
Docs:        readme ✅  master ✅  verification ✅  first_comment ✅
             comment_intel ⚠️ empty   operating/hashtag/self_learning/
             scheduling/learning_memory/creator_research ❌ missing
Resume:      missing
AI:          Claude Code CLI using this Mac's login (AgentRouter key not set)
LinkedIn:    not connected
Telegram:    not set
Scheduler:   installed (run + jobs launch agents present)
Jobs sheet:  Jobs.xlsx  (~533 KB)
Posts:       1 blocked, 0 published
Jobs:        43 notified · 146 filtered · 1,865 low-fit
```

---

## 7. Suggested next steps (priority order)

1. **Fill `.env`** — add AgentRouter (or Anthropic) key, LinkedIn client id/secret,
   Telegram token/chat id; then run `uv run assistant auth` to connect LinkedIn.
2. **Add `resume.pdf`** to the project folder.
3. **Restore the missing content docs** (`Operating_System`, `Hashtag_Intelligence`,
   `Self_Learning`, `Scheduling`, `Learning_Memory`, `Creator_Research`) and paste the
   real Comment Intelligence content into its (currently empty) file. These directly
   unblock the post pipeline and improve job scoring.
4. **Harden the job fetcher** — wrap network calls so a DNS/connection error retries or
   skips one job instead of aborting, and add backoff for 429s.
5. **Publish one test post** end-to-end to validate the LinkedIn path.
6. **Initialise git** and add a minimal test suite around `jobs.py`, `sheet.py`,
   `posts.py` (pure functions are easy to test).

---

## 8. How to run

```bash
uv run assistant status          # setup + data overview
uv run assistant auth            # connect LinkedIn (official API)

uv run assistant draft all       # draft + verify posts
uv run assistant show 3          # full post + verification block
uv run assistant approve 3       # schedule a READY post
uv run assistant publish 3       # publish now

uv run assistant jobs search     # run a job search now
uv run assistant jobs sheet      # open Jobs.xlsx
uv run assistant jobs letter 12  # cover letter
uv run assistant jobs mark 12 applied

uv run assistant comment --text "..." --author "Name" --url "https://..."

uv run assistant schedule install   # background: posts every 10 min, jobs every 30 min
```
