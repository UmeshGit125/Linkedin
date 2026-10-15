"""Telegram control room. Everything that needs your decision arrives here and waits for your tap.

- Posts: drafted -> gate-checked -> sent with the image -> [Approve] publishes, [Reject] asks what to change
- /post <topic>: three options to choose from
- /comment or any forwarded post: ready-to-paste comment options (you paste them on LinkedIn yourself)
- Jobs: cards with Apply link, Cover letter, Applied, Skip
Only the chat in TELEGRAM_CHAT_ID is answered.
"""
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

import requests

from . import comments, jobs, notify, posts
from .config import CFG, TZ, env
from .db import connect, get_kv, now, set_kv
from .notify import btn, link, tg_send

HELP = """LinkedIn assistant

/post <topic>  3 post options on a topic you choose
/comment  then send (or forward) a post: get comment options
Any forwarded post or pasted post text also gets comment options.
/jobs  latest job matches
/hiring  LinkedIn searches for hiring posts (last 24h)
/watch add Name | profile-url   /watch list   /watch remove <id>
/status  what is waiting
/cancel  drop whatever I was asking you for

A daily post draft arrives each morning. Nothing goes to LinkedIn until you tap Approve."""

URL = re.compile(r"https?://\S+")


# ---- presenting things ------------------------------------------------------------------------

def present_post(conn, post_id: int, header: str = "") -> None:
    p = conn.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
    if p["image_path"] and Path(p["image_path"]).exists():
        try:
            notify.tg_photo(p["image_path"], f"Image for post #{post_id}")
        except Exception as e:
            print(f"[bot] photo failed: {e}")
    v = json.loads(p["verification"] or "{}")
    ready = p["status"] == "ready"
    tags = " ".join("#" + t.lstrip("#") for t in json.loads(p["hashtags"] or "[]"))
    parts = [
        (header + "\n\n" if header else "") + f"POST #{post_id} · {p['slot'].upper()} · {p['post_type'] or ''}",
        p["body"] + (f"\n\n{tags}" if tags else ""),
    ]
    if p["first_comment"]:
        parts.append(f"FIRST COMMENT (you post it yourself after publishing):\n{p['first_comment']}")
    if ready:
        parts.append("Gate: READY ✅")
    else:
        why = v.get("blocked_reason") or "; ".join(v.get("problems", [])) or "not checked"
        parts.append(f"Gate: BLOCKED ❌\n{why[:900]}")
    if p["error"] and "Questions for you" in p["error"]:
        parts.append(p["error"][:700])
    buttons = (
        [[btn("✅ Approve & post", f"ap:{post_id}"), btn("❌ Reject", f"rj:{post_id}")]]
        if ready
        else [[btn("🔧 Fix it", f"fx:{post_id}"), btn("❌ Reject", f"rj:{post_id}")]]
    )
    tg_send("\n\n".join(parts), buttons)


def present_comment(conn, cid: int) -> None:
    c = conn.execute("SELECT * FROM comment_drafts WHERE id = ?", (cid,)).fetchone()
    opts = json.loads(c["options"] or "[]")
    if not c["worth_commenting"] or not opts:
        tg_send(f"Skip this one.\n{c['reasoning']}", [[btn("⏭ OK", f"cs:{cid}")]])
        return
    tg_send(f"📌 What the post says:\n{c['reasoning']}\n\nPick a comment below, copy it, post it on LinkedIn.")
    icon = {"one-liner": "⚡", "short": "💬", "witty": "😏"}
    for o in opts:
        angle = f"\n({o['angle']})" if o.get("angle") else ""
        tg_send(f"{icon.get(o['style'], '•')} {o['style'].upper()}{angle}\n\n{o['text']}")
    row = [btn("🔄 More options", f"cr:{cid}"), btn("✅ Posted", f"cd:{cid}"), btn("⏭ Skip", f"cs:{cid}")]
    buttons = [[link("Open the post ↗", c["target_url"])]] if c["target_url"] else []
    tg_send("Done with this one?", buttons + [row])


def digest(conn) -> None:
    """Daily morning message: where to look for hiring posts and whose posts to read."""
    roles = CFG["jobs"]["roles"][:4]
    rows = [
        [link(f"Hiring: {r}", "https://www.linkedin.com/search/results/content/?keywords="
              + quote(f"hiring {r}") + "&datePosted=%22past-24h%22&sortBy=%22date_posted%22")]
        for r in roles
    ]
    watch = conn.execute("SELECT * FROM watchlist ORDER BY id").fetchall()
    text = ["Good morning. Today's reading list:", "", "1. Hiring posts from the last 24 hours (tap a search below)."]
    if watch:
        text.append("2. People you follow. Open their latest posts and forward the good ones here:")
        rows += [[link(w["name"], w["url"])] for w in watch[:12] if w["url"]]
        text += [f"   · {w['name']}" for w in watch if not w["url"]]
    else:
        text.append("2. Your watchlist is empty. Add people worth reading: /watch add Name | profile-url")
    text.append("\nForward any post here and I'll write you comment options for it.")
    tg_send("\n".join(text), rows)


# ---- actions ----------------------------------------------------------------------------------

def _clear_pending(conn) -> None:
    set_kv(conn, "pending", None)


def start_variants(conn, topic: str) -> None:
    tg_send(f"Writing {CFG['posting'].get('variants', 3)} options on “{topic}”. This takes a few minutes.")
    ids = posts.variants(conn, topic)
    for pid in ids:
        present_post(conn, pid, "Option")


def do_comment(conn, text: str, author: str = "") -> None:
    url = (URL.search(text) or [""])[0] if URL.search(text) else ""
    body = URL.sub("", text).strip()
    if url and len(body) < 60:
        tg_send("Reading that post…")
        body = comments.fetch_post_text(url)
        if not body:
            tg_send("LinkedIn won't show me that post without a login. Paste the post's text here (or forward it) and I'll write the comment.")
            set_kv(conn, "pending", {"type": "comment", "url": url})
            return
    if len(body) < 25:
        tg_send("Send me the post text (or forward the post) and I'll write comment options.")
        set_kv(conn, "pending", {"type": "comment", "url": url})
        return
    tg_send("Writing comment options…")
    cid = comments.options(conn, body, author, url)
    present_comment(conn, cid)


def _author(msg: dict) -> str:
    o = msg.get("forward_origin") or {}
    u = o.get("sender_user") or {}
    return o.get("sender_user_name") or " ".join(filter(None, [u.get("first_name"), u.get("last_name")])) or (o.get("chat") or {}).get("title", "")


def cmd_status(conn) -> None:
    c = lambda q: conn.execute(q).fetchone()[0]
    tg_send(
        f"Posts ready for you: {c('SELECT COUNT(*) FROM posts WHERE status=\"ready\"')}\n"
        f"Posts published: {c('SELECT COUNT(*) FROM posts WHERE status=\"published\"')}\n"
        f"Job matches (notified): {c('SELECT COUNT(*) FROM jobs WHERE status=\"notified\"')}\n"
        f"Watchlist: {c('SELECT COUNT(*) FROM watchlist')} people\n"
        f"Images: {'on' if env('IMAGE_API_KEY') else 'off (no IMAGE_API_KEY)'}"
    )


def cmd_watch(conn, arg: str) -> None:
    verb, _, rest = arg.partition(" ")
    if verb == "add" and rest:
        name, _, url = rest.partition("|")
        conn.execute("INSERT INTO watchlist(name, url, added_at) VALUES(?,?,?)", (name.strip(), url.strip(), now()))
        conn.commit()
        tg_send(f"Added {name.strip()}.")
    elif verb == "remove" and rest.strip().isdigit():
        conn.execute("DELETE FROM watchlist WHERE id = ?", (int(rest),))
        conn.commit()
        tg_send("Removed.")
    else:
        rows = conn.execute("SELECT * FROM watchlist ORDER BY id").fetchall()
        tg_send("\n".join(f"{w['id']}. {w['name']} {w['url'] or ''}" for w in rows) or "Watchlist is empty. Add: /watch add Name | profile-url")


def cmd_jobs(conn) -> None:
    rows = conn.execute("SELECT * FROM jobs WHERE status = 'notified' ORDER BY id DESC LIMIT 5").fetchall()
    if not rows:
        tg_send("No job matches waiting.")
    for j in rows:
        notify.send_job_card(j)


# ---- updates ----------------------------------------------------------------------------------

def on_message(conn, msg: dict) -> None:
    text = (msg.get("text") or msg.get("caption") or "").strip()
    if not text:
        return
    cmd, _, arg = text.partition(" ")
    cmd = cmd.split("@")[0].lower()
    arg = arg.strip()
    pending = get_kv(conn, "pending")

    if cmd in ("/start", "/help"):
        tg_send(HELP)
    elif cmd == "/cancel":
        _clear_pending(conn)
        tg_send("Okay, dropped.")
    elif cmd == "/post":
        if arg:
            _clear_pending(conn)
            start_variants(conn, arg)
        else:
            set_kv(conn, "pending", {"type": "post_topic"})
            tg_send("What topic should the post be about?")
    elif cmd == "/comment":
        if arg:
            do_comment(conn, arg, _author(msg))
        else:
            set_kv(conn, "pending", {"type": "comment"})
            tg_send("Send me the post (paste the text, forward it, or send the link).")
    elif cmd == "/jobs":
        cmd_jobs(conn)
    elif cmd == "/hiring":
        digest(conn)
    elif cmd == "/watch":
        cmd_watch(conn, arg)
    elif cmd == "/status":
        cmd_status(conn)
    elif text.startswith("/"):
        tg_send("I don't know that command.\n\n" + HELP)
    elif pending and pending.get("type") == "edit":
        _clear_pending(conn)
        tg_send("Rewriting with your changes… a minute or two.")
        present_post(conn, posts.redraft(conn, pending["post_id"], text), "Revised")
    elif pending and pending.get("type") == "post_topic":
        _clear_pending(conn)
        start_variants(conn, text)
    else:
        _clear_pending(conn)
        if pending and pending.get("type") == "comment" and pending.get("url"):
            text = pending["url"] + " " + text
        do_comment(conn, text, _author(msg))


def on_callback(conn, cq: dict) -> None:
    msg = cq["message"]
    chat_id, mid = msg["chat"]["id"], msg["message_id"]
    notify.tg_answer(cq["id"])
    action, _, arg = cq["data"].partition(":")
    n = int(arg) if arg.isdigit() else 0

    if action == "ap":
        notify.tg_clear_buttons(chat_id, mid)
        if not CFG["posting"].get("publish_on_approve", True):
            when = posts.approve(conn, n)
            tg_send(f"Approved. Post #{n} will publish at {when:%a %d %b %H:%M}.")
            return
        tg_send(f"Publishing post #{n} to LinkedIn…")
        try:
            posts.approve_and_publish(conn, n)  # the "published" message with the link is sent by posts.publish
        except Exception as e:
            tg_send(f"❌ Could not publish #{n}: {e}")
    elif action == "rj":
        notify.tg_clear_buttons(chat_id, mid)
        set_kv(conn, "pending", {"type": "edit", "post_id": n})
        tg_send("What should I change? Reply with your changes and I'll redraft it, or discard it.", [[btn("🗑 Discard", f"dc:{n}")]])
    elif action == "dc":
        notify.tg_clear_buttons(chat_id, mid)
        posts.discard(conn, n)
        _clear_pending(conn)
        tg_send(f"Post #{n} discarded.")
    elif action == "fx":
        notify.tg_clear_buttons(chat_id, mid)
        p = conn.execute("SELECT verification FROM posts WHERE id = ?", (n,)).fetchone()
        v = json.loads(p["verification"] or "{}")
        tg_send("Fixing what the gate flagged…")
        present_post(conn, posts.redraft(conn, n, "Fix these gate problems: " + (v.get("blocked_reason") or "; ".join(v.get("problems", [])))), "Revised")
    elif action == "cr":
        c = conn.execute("SELECT * FROM comment_drafts WHERE id = ?", (n,)).fetchone()
        notify.tg_clear_buttons(chat_id, mid)
        tg_send("Another round…")
        old = [o["text"] for o in json.loads(c["options"] or "[]")]
        present_comment(conn, comments.options(conn, c["target_text"], c["target_author"] or "", c["target_url"] or "", avoid=old))
    elif action in ("cd", "cs"):
        conn.execute("UPDATE comment_drafts SET status = ? WHERE id = ?", ("posted" if action == "cd" else "skipped", n))
        conn.commit()
        notify.tg_clear_buttons(chat_id, mid)
        tg_send("Marked as posted." if action == "cd" else "Skipped.")
    elif action == "jc":
        tg_send("Writing the cover letter…")
        tg_send(jobs.cover_letter(conn, n))
    elif action in ("ja", "jx", "ju"):
        status = {"ja": "applied", "jx": "ignored", "ju": "notified"}[action]
        conn.execute("UPDATE jobs SET status = ? WHERE id = ?", (status, n))
        conn.commit()
        j = conn.execute("SELECT * FROM jobs WHERE id = ?", (n,)).fetchone()
        buttons = notify.job_buttons(j) if action == "ju" else notify.job_marked_buttons(j)
        try:  # change this card's buttons in place: the link stays, Undo appears
            notify.tg_api("editMessageReplyMarkup", chat_id=chat_id, message_id=mid, reply_markup={"inline_keyboard": buttons})
        except RuntimeError:
            pass
        tg_send({"ja": "Marked as applied. Tap Undo on the card if that was a mistake.",
                 "jx": "Skipped. Tap Undo on the card to bring it back.",
                 "ju": "Back to waiting, no status set."}[action])


def handle(update: dict) -> None:
    conn = connect()
    try:
        cq, msg = update.get("callback_query"), update.get("message")
        chat = ((cq or {}).get("message") or msg or {}).get("chat", {}).get("id")
        if str(chat) != env("TELEGRAM_CHAT_ID"):
            return  # only you
        if cq:
            on_callback(conn, cq)
        elif msg:
            on_message(conn, msg)
    except Exception as e:
        print(f"[bot] {type(e).__name__}: {e}", flush=True)
        try:
            tg_send(f"⚠️ That failed: {e}")
        except Exception:
            pass
    finally:
        conn.close()


def run() -> None:
    if not (env("TELEGRAM_BOT_TOKEN") and env("TELEGRAM_CHAT_ID")):
        raise RuntimeError("Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env first.")
    conn = connect()
    offset = get_kv(conn, "tg_offset", 0)
    try:
        notify.tg_api("deleteWebhook")
        notify.tg_api("setMyCommands", commands=[
            {"command": "post", "description": "Write post options on a topic"},
            {"command": "comment", "description": "Comment options for a post"},
            {"command": "jobs", "description": "Latest job matches"},
            {"command": "hiring", "description": "Hiring-post searches"},
            {"command": "watch", "description": "People to follow"},
            {"command": "status", "description": "What is waiting"},
            {"command": "cancel", "description": "Drop the current question"},
        ])
    except RuntimeError as e:
        print(f"[bot] setup: {e}", flush=True)
    print(f"[{now()}] Telegram bot running.", flush=True)
    pool = ThreadPoolExecutor(max_workers=4)
    token = env("TELEGRAM_BOT_TOKEN")
    while True:
        try:
            r = requests.get(
                f"https://api.telegram.org/bot{token}/getUpdates",
                params={"timeout": 50, "offset": offset, "allowed_updates": json.dumps(["message", "callback_query"])},
                timeout=65,
            )
            updates = r.json().get("result", [])
        except (requests.RequestException, ValueError):
            time.sleep(5)
            continue
        for u in updates:
            offset = u["update_id"] + 1
            set_kv(conn, "tg_offset", offset)
            pool.submit(handle, u)
