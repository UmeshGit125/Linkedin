# Keeping `knowledge/` up to date (after every code change and every pull)

`knowledge/` is gitignored and private. After each change, before saying "done", update:

| File | What goes in | When |
|---|---|---|
| `decisions.md` | Each meaningful decision: what, why this over the alternatives, library choices, trade-offs | every change with a choice in it |
| `flow.md` | Entry points, which function calls which and why, how data moves between files | every time the call flow changes |
| `mental-model.md` | Quiz for the change, Umesh's answers, score, running score table | after every change; quiz is run in chat |
| `next-to-learn.md` | Topics Umesh scored low on, with what to study and why it matters | after each quiz |

Rules:
- Write in simple English. Short sentences. Explain jargon the first time.
- Newest entries on top, each with a date.
- Never record secrets. Never invent history; if unsure why something was done, say "reason unknown".
- After a `git pull`, re-read the changed files and fix any entry that is now wrong.
- Quiz and scoring rules are written at the top of `mental-model.md`.
