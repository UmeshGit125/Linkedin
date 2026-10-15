# Architecture

Python 3.12 CLI + background agents. Run with `uv run assistant <command>` or `.venv/bin/python -m assistant <command>`.

## Layout
```
Linkedin/
  assistant/          the whole backend (one package)
    cli.py            entry point: argparse commands -> cmd_* functions
    scheduler.py      launchd agents + tick(): due posts, daily draft, daily digest
    bot.py            Telegram bot: long-poll, buttons, /post /comment /jobs /watch
    posts.py          post drafting, 3-variant mode, quality gate (verify), approve/publish
    comments.py       3 comment options for someone else's post (user pastes them manually)
    jobs.py           job search (LinkedIn guest + Y Combinator), scoring, pay filter
    sheet.py          Jobs.xlsx export
    linkedin.py       official LinkedIn API: OAuth, text/image publish
    imagegen.py       OpenAI-compatible image API (off until IMAGE_API_KEY is set)
    llm.py            one function `structured()`: calls the model, returns a validated pydantic object
    knowledge.py      loads the rule documents from Docs/ and the resume into prompts
    notify.py         Telegram/desktop/email senders, button helpers, job card
    docsgen.py        drafts missing Docs/ files for review
    db.py, config.py  SQLite connection + migrations; config.yaml + .env loading
  Docs/               the rule documents that steer the writing (voice, gate, scheduling...)
  config.yaml         all tunable settings (times, filters, model names)
  data/  logs/  .env  private runtime state, gitignored
  .ai/                this folder: AI working rules (committed)
  knowledge/          private notes for Umesh: decisions, flow, quiz (gitignored)
```

## Layering rules
- `cli.py` and `bot.py` and `scheduler.py` are entry points. They call into `posts`, `comments`, `jobs`, `linkedin`.
- `posts`, `comments`, `jobs` hold the logic and may call `llm`, `knowledge`, `notify`, `db`.
- `llm`, `linkedin`, `imagegen`, `notify`, `db`, `config` are leaf modules: they must not import entry points or business modules.
- Every model call returns a pydantic schema via `llm.structured`. Do not parse free text.
- All settings live in `config.yaml`; all secrets live in `.env`. No hard-coded keys, times or model names in code.
- Post state machine: `drafted -> ready | blocked -> scheduled -> publishing -> published` (`rejected` and `discarded` are dead ends).
