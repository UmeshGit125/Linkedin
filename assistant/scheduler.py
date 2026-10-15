"""Background jobs (macOS launchd), both run only while the Mac is awake:

- com.linkedin-assistant.run   every 10 min: publish approved posts that are due
- com.linkedin-assistant.jobs  every 30 min: LinkedIn job search -> Jobs.xlsx
- com.linkedin-assistant.bot   always on: the Telegram bot (approvals, /post, /comment)
"""
import plistlib
from datetime import datetime
import shutil
import subprocess
from pathlib import Path

from . import bot, linkedin, notify, posts
from .config import CFG, LOG_DIR, ROOT, TZ
from .db import get_kv, now, set_kv

AGENTS_DIR = Path.home() / "Library/LaunchAgents"
BOT_LABEL = "com.linkedin-assistant.bot"
BOT_PLIST = AGENTS_DIR / f"{BOT_LABEL}.plist"
POSTS_LABEL = "com.linkedin-assistant.run"
JOBS_LABEL = "com.linkedin-assistant.jobs"
PLIST = AGENTS_DIR / f"{POSTS_LABEL}.plist"
JOBS_PLIST = AGENTS_DIR / f"{JOBS_LABEL}.plist"


def _due_today(conn, key: str, hhmm: str) -> bool:
    """True once per day, after hh:mm local time."""
    t = datetime.now(TZ)
    return get_kv(conn, key) != t.date().isoformat() and t.strftime("%H:%M") >= hhmm


def daily_draft(conn) -> None:
    """One post a day, rotating tofu -> mofu -> authority, sent to Telegram for approval."""
    if not _due_today(conn, "daily_draft_date", CFG["posting"].get("daily_draft_time", "08:00")):
        return
    set_kv(conn, "daily_draft_date", datetime.now(TZ).date().isoformat())  # set first: a failure must not retry every 10 minutes
    slot = posts.SLOTS[datetime.now(TZ).toordinal() % len(posts.SLOTS)]
    try:
        pid = posts.draft(conn, slot, notify_result=False)
        bot.present_post(conn, pid, f"Today's {slot.upper()} draft")
    except Exception as e:
        notify.send("Daily LinkedIn draft failed", str(e))


def daily_digest(conn) -> None:
    if not _due_today(conn, "digest_date", CFG.get("telegram", {}).get("digest_time", "09:30")):
        return
    set_kv(conn, "digest_date", datetime.now(TZ).date().isoformat())
    try:
        bot.digest(conn)
    except Exception as e:
        print(f"[digest] {e}")


def tick(conn) -> None:
    published = posts.publish_due(conn)
    if published:
        print(f"[{now()}] published posts: {published}")
    if CFG["notify"].get("telegram") and notify.env("TELEGRAM_BOT_TOKEN"):
        daily_draft(conn)
        daily_digest(conn)

    # A ready post nobody approved never publishes; remind once per post when its slot passes.
    for r in conn.execute("SELECT id, slot, scheduled_for FROM posts WHERE status = 'ready'").fetchall():
        if r["scheduled_for"] and datetime.fromisoformat(r["scheduled_for"]) <= datetime.now(TZ) \
                and get_kv(conn, f"unapproved_warned_{r['id']}") is None:
            notify.send("LinkedIn post NOT approved", f"Post #{r['id']} ({r['slot'].upper()}) missed its {r['scheduled_for']} slot because it isn't approved.\nApprove: uv run assistant approve {r['id']} --at <time>")
            set_kv(conn, f"unapproved_warned_{r['id']}", now())

    days = linkedin.days_until_expiry()
    if days is not None and days <= 7 and get_kv(conn, "expiry_warned") != days:
        notify.send("LinkedIn sign-in expiring", f"Your LinkedIn connection expires in {days} day(s). Run: uv run assistant auth")
        set_kv(conn, "expiry_warned", days)


def _install_agent(label: str, plist_path: Path, args: list[str], every_minutes: int | None, log_name: str) -> None:
    uv = shutil.which("uv")
    if not uv:
        raise RuntimeError("uv not found on PATH.")
    AGENTS_DIR.mkdir(parents=True, exist_ok=True)
    plist = {
        "Label": label,
        "ProgramArguments": [uv, "run", "--project", str(ROOT), "python", "-m", "assistant", *args],
        "WorkingDirectory": str(ROOT),
        "RunAtLoad": True,
        # launchd agents get a bare PATH; the claude CLI (used for AI calls) lives in ~/.local/bin.
        "EnvironmentVariables": {"PATH": f"{Path.home()}/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"},
        "StandardOutPath": str(LOG_DIR / f"{log_name}.log"),
        "StandardErrorPath": str(LOG_DIR / f"{log_name}.err.log"),
    }
    if every_minutes:
        plist["StartInterval"] = every_minutes * 60
    else:  # a long-running service: launchd restarts it if it ever stops
        plist["KeepAlive"] = True
        plist["ThrottleInterval"] = 15
    with open(plist_path, "wb") as f:
        plistlib.dump(plist, f)
    subprocess.run(["launchctl", "unload", str(plist_path)], capture_output=True)
    subprocess.run(["launchctl", "load", str(plist_path)], check=True)


def install(every_minutes: int = 10) -> list[Path]:
    _install_agent(POSTS_LABEL, PLIST, ["run"], every_minutes, "posts")
    jobs_every = int(CFG["jobs"].get("search_every_minutes", 30))
    _install_agent(JOBS_LABEL, JOBS_PLIST, ["jobs", "search"], jobs_every, "jobs")
    _install_agent(BOT_LABEL, BOT_PLIST, ["bot"], None, "bot")
    return [PLIST, JOBS_PLIST, BOT_PLIST]


def uninstall() -> None:
    for p in (PLIST, JOBS_PLIST, BOT_PLIST):
        if p.exists():
            subprocess.run(["launchctl", "unload", str(p)], capture_output=True)
            p.unlink()
