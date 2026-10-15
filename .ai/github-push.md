# GitHub rules

Remote: `origin` = https://github.com/UmeshGit125/Linkedin.git, branch `main`.
Never commit or push without Umesh saying so in this conversation. A yes for one push is not a yes for the next.

## Before committing
1. `git status` and `git diff --stat`: read what is going in and tell Umesh in plain words.
2. Confirm none of these are staged: `.env`, `data/`, `logs/`, `*.pdf`, `knowledge/`, tokens, `Jobs.xlsx` (contains personal job data; ask before tracking).
3. Search the diff for secrets: strings like `sk-`, `Bearer`, `token`, `api_key=`, chat ids.
4. Run the code: `.venv/bin/python -m assistant status` must work and `python -c "import assistant.bot, assistant.posts"` must import.
5. Make sure `knowledge/` files were updated for this change (they stay local).

## Commit
- Small, single-purpose commits. Message: short imperative subject, then why in a line or two.
- End every commit message with: `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`
- Never amend or rewrite pushed history. Never `--force`. Never `--no-verify`.

## Push
- Show Umesh the commit list that will go out, then ask.
- Push only to `main` unless told otherwise; use a branch for risky or large changes.
- If push fails with 403: the saved macOS keychain login is a different account. Do not retry in a loop. Tell Umesh; fix is a token for `UmeshGit125` with `repo` scope.
- Never paste a token into chat or into a command line.
