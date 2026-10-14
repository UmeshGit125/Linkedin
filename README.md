# LinkedIn Assistant

Personal assistant that runs on this Mac:

- **Posts**: drafts posts with your content system in `Docs/` and runs every draft through `LinkedIn_Verification_Gate.md`. A post goes out through LinkedIn's official API only if it is 🟢 READY **and** you approved it. After it publishes, you get a notification with the link and the first comment for you to post yourself.
- **Jobs and internships**: every 30 minutes it searches LinkedIn's official public job-search URLs with a time filter (only jobs posted in the last 60 minutes, newest first) for each role and location in `config.yaml`. **Every job it finds is added to `Jobs.xlsx`**, along with role, company, location, work mode, employment type, seniority, experience required, tech stack, salary, applicant count, industry, AI fit score and notes, and a clickable **Apply** link. Your own `My status` and `My notes` columns are never overwritten. Jobs scoring at or above `min_score` also send you a notification. You apply yourself. It can draft a cover letter for any job.
- **Comments**: drafts a comment on someone else's post (or tells you to skip it). You post it yourself.

Nothing logs into LinkedIn as you in a browser, and nothing comments or applies automatically, so your account isn't at risk.

## One-time setup

1. **AI access**: `cp .env.example .env`, then put your AgentRouter key in `AGENTROUTER_API_KEY`. All AI calls go through the `claude` CLI (Claude Code), with AgentRouter applied only to those calls. Leave the key empty to use Claude Code's own login. Set the model in `config.yaml` → `llm.agentrouter_model`.
2. **Resume**: save it as `resume.pdf` in this folder.
3. **LinkedIn app** (needed to publish):
   1. Go to https://www.linkedin.com/developers/apps → *Create app*. It asks for a Company Page; any page you admin works, including a small personal one you create for this.
   2. On the **Products** tab, add **Share on LinkedIn** and **Sign In with LinkedIn using OpenID Connect**.
   3. On the **Auth** tab, add the redirect URL `http://localhost:8765/callback`, then copy the Client ID and Secret into `.env`.
   4. Run `uv run assistant auth`. The token lasts 60 days, and you're warned 7 days before it expires.
4. **Telegram** (recommended for phone alerts): message @BotFather → `/newbot` → put the token in `.env` as `TELEGRAM_BOT_TOKEN`. Send your bot "hi", run `uv run assistant notify --telegram-setup`, and put the chat id it prints in `.env`.
5. **Preferences**: edit `config.yaml` to set job roles, locations, keywords, the minimum match score and posting times.
6. **Background scheduler**: `uv run assistant schedule install`. It installs two background jobs that run while the Mac is awake: one publishes approved posts when they're due (checks every 10 min), the other searches for jobs every 30 min and fills `Jobs.xlsx`. Logs are in `logs/`. If `Jobs.xlsx` is open in Excel, the update waits for the next run so your edits are never overwritten, so close the file when you're done with it.

Check everything with `uv run assistant status`.

## Daily use

```bash
uv run assistant draft all                 # draft TOFU + MOFU + Authority for the next free slots
uv run assistant draft mofu --topic "why our OCR pipeline routes low-confidence pages to a human"
uv run assistant show 3                    # full post + POST VERIFICATION block
uv run assistant edit 3                    # change text in your editor -> automatically re-verified
uv run assistant approve 3                 # schedule it (only READY posts can be approved)
uv run assistant approve 3 --at "2026-10-05 09:40"
uv run assistant publish 3                 # publish right now instead
uv run assistant metrics 3 impressions=180 comments=4 followers=2

uv run assistant jobs search               # run a search now
uv run assistant jobs sheet                # open Jobs.xlsx (recreated from history if you deleted it)
uv run assistant jobs list
uv run assistant jobs letter 12            # cover letter -> data/letters/job_12.md
uv run assistant jobs mark 12 applied      # interested | applied | interview | rejected | ignored

uv run assistant comment --text "...their post..." --author "Name" --url "https://..."
uv run assistant comment --done 4          # after you posted it
```

## Docs this uses

The tool finds each document in `Docs/` by a keyword in its file name, so the exact filename doesn't matter. Run `uv run assistant status` to see which docs are loaded. Drafts and the verification gate are told which docs are missing, and they are instructed to block a post rather than guess when a missing doc matters. For example, with no Proof Inventory, any post that claims numbers or client results is blocked.
