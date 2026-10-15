# Before making any decision or change

Go through this list. If an answer is "don't know", find out first or ask.

1. **Goal:** what exactly did Umesh ask for? Restate it in one sentence.
2. **Existing code:** does something already do this? Read the file and its callers before adding code (`grep` first).
3. **Boundaries:** does it touch posting, commenting, applying, secrets, or the frontend? If yes, see `rules.md` section 3.
4. **Blast radius:** which files, DB tables, config keys and background agents are affected? `launchd` agents (`bot`, `jobs`, `run`) need a restart to load new code.
5. **Data safety:** does it change the SQLite schema? Add a migration in `db.py`; never drop or rewrite existing rows without asking.
6. **Cost and limits:** LLM calls go through AgentRouter (`deepseek-v4-flash` only). LinkedIn guest job search is rate-limited. Avoid loops that multiply calls.
7. **Failure mode:** what happens if the API is down, returns nothing, or the Mac is asleep? Fail loudly to Telegram or logs, never silently.
8. **Double-action risk:** can this publish or notify twice? Publishing uses an atomic claim in `posts.py`; keep it.
9. **Alternatives:** name at least one other option and why you did not pick it. This goes into `knowledge/decisions.md`.
10. **How to verify:** decide the test before the change (a command to run, a synthetic Telegram update, a DB query).
