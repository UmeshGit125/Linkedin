# Working rules

## 1. Say what you are doing in plain words, before doing it
Umesh wants to read what is happening, not decode commands. Before every action that needs approval
(shell command, file edit, folder access, network call), write one plain sentence first:
- Instead of `cd assistant && ls`: "Give me access to the `assistant` folder so I can list its files."
- Instead of `sed -i ... posts.py`: "Edit `assistant/posts.py` to change how hashtags are cleaned, because they were publishing with spaces."
Format: **what** (plain words) + **where** (folder/file) + **why** (one short reason).
After the change, say what actually changed and anything that went differently than planned.
You cannot change the permission pop-up text itself, so this sentence in chat is the readable version.

## 2. Frontend lock
This project is a Python backend (`assistant/`) plus a Telegram bot. It has no web frontend today.
Do not create or edit any UI/web/HTML/JS/CSS or published-page files without asking first and getting a clear yes.
Telegram message layout (inside `bot.py` / `notify.py`) counts as backend, but say so when changing what the user sees.

## 3. Things that always need a fresh yes
- Anything that posts, comments, sends or applies on Umesh's behalf (LinkedIn, Telegram to others, email).
- `git commit`, `git push`, changing remotes, force anything. See `github-push.md`.
- Deleting or overwriting files, DB rows, or launchd agents. Look at the target first.
- Installing/removing packages, changing `pyproject.toml`.
- Calling a paid or external API that has not been used in this project before.

## 4. Hard boundaries (from Umesh's own rules)
- Nothing reaches LinkedIn without Umesh's approval.
- No auto-commenting, no auto job-apply, no browser-login bots, no spoofed headers or bypassing a firewall.
- Never invent metrics, claims, companies or experience. Never reuse another person's details.
- Never print, log, commit or paste secrets: `.env`, `data/` (tokens, DB), `logs/`, `*.pdf`.

## 5. Working style
- Prefer the smallest change that solves the problem. Match the style of the file you are editing.
- Test what you can; say clearly what you could not test (for example the real LinkedIn publish path).
- Report failures with the real output. Do not say "done" for something unverified.
- Explain trade-offs in simple English. Umesh is a student learning from the code, so teach as you go.
