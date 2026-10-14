import argparse
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime

from . import comments, jobs, knowledge, linkedin, notify, posts, scheduler, sheet
from .config import CFG, TZ, env
from .db import connect
from .linkedin import LinkedInError
from .llm import LLMError

JOB_STATUSES = ["interested", "applied", "interview", "rejected", "ignored"]


def cmd_status(conn, a):
    print("Docs:")
    for key, st in knowledge.status().items():
        print(f"  {'✅' if st == 'ok' else '⚠️ '} {key:17} {st}")
    print("\nResume:", "loaded" if knowledge.resume_text() else "missing (put resume.pdf in the project folder)")
    backend = CFG["llm"].get("backend", "claude-code")
    if backend == "anthropic-api":
        print("AI: Anthropic API —", "key set" if env("ANTHROPIC_API_KEY") else "ANTHROPIC_API_KEY MISSING")
    elif env("AGENTROUTER_API_KEY"):
        print(f"AI: Claude Code via AgentRouter (model {CFG['llm'].get('agentrouter_model')})")
    else:
        print("AI: Claude Code with this Mac's login (no AGENTROUTER_API_KEY set)")
    days = linkedin.days_until_expiry()
    print("LinkedIn:", "not connected (run: assistant auth)" if days is None else f"connected, expires in {days} days")
    print("Telegram:", "set" if env("TELEGRAM_BOT_TOKEN") and env("TELEGRAM_CHAT_ID") else "not set")
    print("Scheduler:", "installed" if scheduler.PLIST.exists() and scheduler.JOBS_PLIST.exists() else "not installed (run: assistant schedule install)")
    print("Jobs sheet:", sheet.path())
    print("\nPosts:", dict(conn.execute("SELECT status, COUNT(*) FROM posts GROUP BY status").fetchall()))
    print("Jobs: ", dict(conn.execute("SELECT status, COUNT(*) FROM jobs GROUP BY status").fetchall()))


def cmd_auth(conn, a):
    info = linkedin.authorize()
    print(f"Connected as {info['name']} ({info['person_urn']}). Token valid ~60 days.")


def cmd_notify(conn, a):
    if a.telegram_setup:
        chat = notify.telegram_find_chat_id()
        if chat:
            print(f"Your chat id: {chat}\nAdd to .env:  TELEGRAM_CHAT_ID={chat}")
        else:
            print("No messages found. Open your bot in Telegram, send it 'hi', then run this again.")
        return
    print("Sent via:", notify.send("LinkedIn Assistant", "Test notification — it works.") or "nothing enabled")


def cmd_draft(conn, a):
    slots = posts.SLOTS if a.slot == "all" else [a.slot]
    for slot in slots:
        print(f"Drafting {slot}… (writer, then independent verification gate)")
        pid = posts.draft(conn, slot, a.topic or "")
        print(posts.format_post(conn.execute("SELECT * FROM posts WHERE id = ?", (pid,)).fetchone()), "\n")
    print("Approve a READY post with: uv run assistant approve <id>")


def cmd_list(conn, a):
    q = "SELECT * FROM posts" + (" WHERE status = ?" if a.status else "") + " ORDER BY id DESC LIMIT 30"
    for p in conn.execute(q, (a.status,) if a.status else ()).fetchall():
        print(f"#{p['id']:<4} {p['status']:<10} {p['slot']:<9} {p['scheduled_for'] or '':<17} {p['hook'][:70]}")


def _post(conn, pid):
    p = conn.execute("SELECT * FROM posts WHERE id = ?", (pid,)).fetchone()
    if p is None:
        sys.exit(f"No post #{pid}.")
    return p


def cmd_show(conn, a):
    print(posts.format_post(_post(conn, a.id)))


def cmd_edit(conn, a):
    p = _post(conn, a.id)
    if p["status"] in ("published", "approved"):
        sys.exit(f"Post #{a.id} is {p['status']}; reject it first if you want to change it.")
    sep = "\n\n===== FIRST COMMENT (leave empty for none) =====\n"
    with tempfile.NamedTemporaryFile("w+", suffix=".txt", delete=False) as f:
        f.write(p["body"] + sep + (p["first_comment"] or ""))
        path = f.name
    subprocess.run([os.environ.get("EDITOR", "nano"), path])
    text = open(path).read()
    os.unlink(path)
    body, _, comment = text.partition(sep.strip("\n"))
    conn.execute(
        "UPDATE posts SET body = ?, first_comment = ?, status = 'draft', verification = NULL WHERE id = ?",
        (body.strip(), comment.strip() or None, a.id),
    )
    conn.commit()
    print("Saved. Re-running the verification gate…")
    posts.verify(conn, a.id)
    print(posts.format_post(_post(conn, a.id)))


def cmd_verify(conn, a):
    posts.verify(conn, a.id)
    print(posts.format_post(_post(conn, a.id)))


def cmd_approve(conn, a):
    at = datetime.strptime(a.at, "%Y-%m-%d %H:%M").replace(tzinfo=TZ) if a.at else None
    when = posts.approve(conn, a.id, at)
    print(f"Approved. Post #{a.id} will publish at {when:%a %d %b %H:%M} ({TZ.key}) — the scheduler must be running.")


def cmd_reject(conn, a):
    _post(conn, a.id)
    conn.execute("UPDATE posts SET status = 'rejected' WHERE id = ? AND status != 'published'", (a.id,))
    conn.commit()
    print(f"Post #{a.id} rejected.")


def cmd_publish(conn, a):
    p = _post(conn, a.id)
    if p["status"] == "ready":
        posts.approve(conn, a.id, datetime.now(TZ))
    urn = posts.publish(conn, a.id)
    print(f"Published: {linkedin.post_url(urn)}")


def cmd_metrics(conn, a):
    p = _post(conn, a.id)
    m = json.loads(p["metrics"] or "{}")
    for pair in a.values:
        k, _, v = pair.partition("=")
        m[k.strip()] = int(v) if v.strip().isdigit() else v.strip()
    m["recorded_at"] = datetime.now(TZ).isoformat(timespec="minutes")
    conn.execute("UPDATE posts SET metrics = ? WHERE id = ?", (json.dumps(m), a.id))
    conn.commit()
    print(f"Metrics for #{a.id}: {m}")


def cmd_jobs(conn, a):
    if a.action == "search":
        print(f"[{datetime.now(TZ):%Y-%m-%d %H:%M}] Searching LinkedIn… (polite pacing, takes a few minutes)", flush=True)
        print(jobs.search(conn), flush=True)
    elif a.action == "sheet":
        added = sheet.sync(conn)
        print(f"{added} job(s) added. Sheet: {sheet.path()}")
        subprocess.run(["open", str(sheet.path())])
    elif a.action == "list":
        where = "" if a.all else "WHERE status IN ('notified','interested','applied','interview')"
        for j in conn.execute(f"SELECT * FROM jobs {where} ORDER BY score DESC, id DESC LIMIT 40").fetchall():
            print(f"#{j['id']:<5} {j['score'] if j['score'] is not None else '-':>3}  {j['status']:<10} {j['title'][:45]:<45} {j['company'][:25]}")
    elif a.action == "show":
        j = conn.execute("SELECT * FROM jobs WHERE id = ?", (a.id,)).fetchone()
        if j is None:
            sys.exit(f"No job #{a.id}.")
        print(f"{j['title']} — {j['company']} ({j['location']})\n{j['url']}\nScore {j['score']} ({j['verdict']}) · {j['status']}\n\n{j['reasons'] or ''}\n\n{j['description'] or ''}")
    elif a.action == "mark":
        if a.status not in JOB_STATUSES:
            sys.exit(f"Status must be one of: {', '.join(JOB_STATUSES)}")
        conn.execute("UPDATE jobs SET status = ? WHERE id = ?", (a.status, a.id))
        conn.commit()
        print(f"Job #{a.id} → {a.status}")
    elif a.action == "letter":
        print(jobs.cover_letter(conn, a.id))


def cmd_comment(conn, a):
    if a.done:
        conn.execute("UPDATE comment_drafts SET status = 'posted' WHERE id = ?", (a.done,))
        conn.commit()
        print(f"Comment #{a.done} marked as posted.")
        return
    text = open(a.file).read() if a.file else a.text
    if not text:
        sys.exit("Give the post text with --text '...' or --file post.txt")
    cid = comments.draft(conn, text, a.author or "", a.url or "")
    c = conn.execute("SELECT * FROM comment_drafts WHERE id = ?", (cid,)).fetchone()
    if c["worth_commenting"]:
        print(f"Comment #{cid} — post it yourself:\n\n{c['comment']}\n\nWhy: {c['reasoning']}\n\nAfter posting: uv run assistant comment --done {cid}")
    else:
        print(f"Skip this one. {c['reasoning']}")


def cmd_run(conn, a):
    scheduler.tick(conn)


def cmd_schedule(conn, a):
    if a.action == "install":
        scheduler.install(a.every)
        print(f"Installed. Posts check every {a.every} min; job search every "
              f"{CFG['jobs'].get('search_every_minutes', 30)} min (while your Mac is awake).\n"
              f"Sheet: {sheet.path()}\nLogs: logs/posts.log, logs/jobs.log")
    else:
        scheduler.uninstall()
        print("Scheduler removed.")


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="assistant", description="Personal LinkedIn assistant")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status", help="setup + data overview").set_defaults(fn=cmd_status)
    sub.add_parser("auth", help="connect your LinkedIn account (official API)").set_defaults(fn=cmd_auth)
    s = sub.add_parser("notify", help="send a test notification")
    s.add_argument("--telegram-setup", action="store_true", help="find your Telegram chat id")
    s.set_defaults(fn=cmd_notify)

    s = sub.add_parser("draft", help="draft + verify a post")
    s.add_argument("slot", choices=[*posts.SLOTS, "all"])
    s.add_argument("--topic", help="optional direction, e.g. 'why our OCR pipeline abstains'")
    s.set_defaults(fn=cmd_draft)
    s = sub.add_parser("list", help="list posts")
    s.add_argument("--status")
    s.set_defaults(fn=cmd_list)
    for name, fn, help_ in [
        ("show", cmd_show, "show a post with its verification"),
        ("edit", cmd_edit, "edit a post in your editor, then re-verify"),
        ("verify", cmd_verify, "re-run the verification gate"),
        ("reject", cmd_reject, "reject a post"),
        ("publish", cmd_publish, "publish a READY/approved post right now"),
    ]:
        s = sub.add_parser(name, help=help_)
        s.add_argument("id", type=int)
        s.set_defaults(fn=fn)
    s = sub.add_parser("approve", help="approve a READY post for its scheduled slot")
    s.add_argument("id", type=int)
    s.add_argument("--at", help="override time, 'YYYY-MM-DD HH:MM' local")
    s.set_defaults(fn=cmd_approve)
    s = sub.add_parser("metrics", help="record analytics, e.g. impressions=180 comments=4 followers=3")
    s.add_argument("id", type=int)
    s.add_argument("values", nargs="+")
    s.set_defaults(fn=cmd_metrics)

    s = sub.add_parser("jobs", help="job/internship search")
    s.add_argument("action", choices=["search", "sheet", "list", "show", "mark", "letter"])
    s.add_argument("id", type=int, nargs="?")
    s.add_argument("status", nargs="?")
    s.add_argument("--all", action="store_true")
    s.set_defaults(fn=cmd_jobs)

    s = sub.add_parser("comment", help="draft a comment on someone else's post (you post it)")
    s.add_argument("--text")
    s.add_argument("--file")
    s.add_argument("--author")
    s.add_argument("--url")
    s.add_argument("--done", type=int, help="mark comment draft as posted")
    s.set_defaults(fn=cmd_comment)

    sub.add_parser("run", help="one scheduler tick: publish due posts, search jobs").set_defaults(fn=cmd_run)
    s = sub.add_parser("schedule", help="install/remove the background scheduler")
    s.add_argument("action", choices=["install", "uninstall"])
    s.add_argument("--every", type=int, default=10, help="minutes between post-publishing checks")
    s.set_defaults(fn=cmd_schedule)
    return ap


def main(argv=None):
    a = build_parser().parse_args(argv)
    if a.cmd == "jobs" and a.action in ("show", "mark", "letter") and a.id is None:
        sys.exit(f"jobs {a.action} needs a job id.")
    conn = connect()
    try:
        a.fn(conn, a)
    except (LLMError, LinkedInError, ValueError, RuntimeError) as e:
        sys.exit(f"Error: {e}")
    finally:
        conn.close()
