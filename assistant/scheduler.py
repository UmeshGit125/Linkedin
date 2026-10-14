"""Background jobs (macOS launchd), both run only while the Mac is awake:

- com.linkedin-assistant.run   every 10 min: publish approved posts that are due
- com.linkedin-assistant.jobs  every 30 min: LinkedIn job search -> Jobs.xlsx
"""
import plistlib
from datetime import datetime
import shutil
import subprocess
from pathlib import Path

from . import linkedin, notify, posts
from .config import CFG, LOG_DIR, ROOT, TZ
from .db import get_kv, now, set_kv

AGENTS_DIR = Path.home() / "Library/LaunchAgents"
POSTS_LABEL = "com.linkedin-assistant.run"
JOBS_LABEL = "com.linkedin-assistant.jobs"
PLIST = AGENTS_DIR / f"{POSTS_LABEL}.plist"
JOBS_PLIST = AGENTS_DIR / f"{JOBS_LABEL}.plist"


def tick(conn) -> None:
    published = posts.publish_due(conn)
    if published:
        print(f"[{now()}] published posts: {published}")

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


def _install_agent(label: str, plist_path: Path, args: list[str], every_minutes: int, log_name: str) -> None:
    uv = shutil.which("uv")
    if not uv:
        raise RuntimeError("uv not found on PATH.")
    AGENTS_DIR.mkdir(parents=True, exist_ok=True)
    plist = {
        "Label": label,
        "ProgramArguments": [uv, "run", "--project", str(ROOT), "python", "-m", "assistant", *args],
        "WorkingDirectory": str(ROOT),
        "StartInterval": every_minutes * 60,
        "RunAtLoad": True,
        # launchd agents get a bare PATH; the claude CLI (used for AI calls) lives in ~/.local/bin.
        "EnvironmentVariables": {"PATH": f"{Path.home()}/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"},
        "StandardOutPath": str(LOG_DIR / f"{log_name}.log"),
        "StandardErrorPath": str(LOG_DIR / f"{log_name}.err.log"),
    }
    with open(plist_path, "wb") as f:
        plistlib.dump(plist, f)
    subprocess.run(["launchctl", "unload", str(plist_path)], capture_output=True)
    subprocess.run(["launchctl", "load", str(plist_path)], check=True)


def install(every_minutes: int = 10) -> list[Path]:
    _install_agent(POSTS_LABEL, PLIST, ["run"], every_minutes, "posts")
    jobs_every = int(CFG["jobs"].get("search_every_minutes", 30))
    _install_agent(JOBS_LABEL, JOBS_PLIST, ["jobs", "search"], jobs_every, "jobs")
    return [PLIST, JOBS_PLIST]


def uninstall() -> None:
    for p in (PLIST, JOBS_PLIST):
        if p.exists():
            subprocess.run(["launchctl", "unload", str(p)], capture_output=True)
            p.unlink()
