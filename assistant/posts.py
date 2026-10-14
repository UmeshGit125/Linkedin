"""Post pipeline: draft -> verification gate -> your approval -> scheduled publish.

Nothing reaches LinkedIn unless the gate returned READY *and* you approved it.
"""
import json
import random
from datetime import datetime, timedelta
from typing import Literal

from pydantic import BaseModel

from . import knowledge, linkedin, llm, notify
from .config import CFG, TZ

OWNER = CFG["profile"]["name"]
from .db import now

SLOTS = ("tofu", "mofu", "authority")
SLOT_LABEL = {
    "tofu": "TOFU — reach/discovery: story, broad insight, observation, contrarian idea. No proof requirement.",
    "mofu": "MOFU — speaks to the ICP's problems, frustrations, goals and language directly. No proof requirement.",
    "authority": (
        "Authority / Creator Breakdown / BOFU / Experiment — real proof only when it exists in the "
        "documents; otherwise a legitimate non-proof type (opinion, pattern analysis, technical lesson, "
        "proposed experiment, industry insight)."
    ),
}


class PostDraft(BaseModel):
    post_type: str
    topic: str
    hook: str
    post: str
    hashtags: list[str]
    first_comment_needed: bool
    first_comment: str
    why_this_works: str
    source_inspiration: str
    originality: str
    confidence: Literal["HIGH", "MEDIUM", "LOW"]
    open_questions_for_author: list[str]


Check = Literal["pass", "na", "fail"]


class GateResult(BaseModel):
    required_and_verified: list[str]
    not_applicable: list[str]
    content: Literal["pass", "fail"]
    proof: Check
    visual: Check
    hashtags: Check
    cta: Check
    links: Check
    tags: Check
    first_comment: Check
    format: Literal["pass", "fail"]
    schedule: Literal["pass", "fail"]
    strategy: Literal["pass", "fail"]
    problems: list[str]
    final_status: Literal["READY", "BLOCKED"]
    blocked_reason: str
    fixable_now: bool


GATE_FIELDS = ["content", "proof", "visual", "hashtags", "cta", "links", "tags", "first_comment", "format", "schedule", "strategy"]


def _recent_posts(conn, limit: int = 9) -> str:
    rows = conn.execute(
        "SELECT slot, hook, body FROM posts WHERE status IN ('ready','approved','published') ORDER BY id DESC LIMIT ?",
        (limit,),
    ).fetchall()
    if not rows:
        return "(no previous posts recorded in this tool yet)"
    return "\n\n---\n\n".join(f"[{r['slot']}] {r['body']}" for r in rows)


def next_slot_time(conn, slot: str, day: datetime | None = None) -> datetime:
    """Next free occurrence of the slot, with natural variation around the base time."""
    hh, mm = map(int, CFG["posting"]["slots"][slot].split(":"))
    jitter = int(CFG["posting"].get("jitter_minutes", 0))
    cursor = (day or datetime.now(TZ)).replace(hour=hh, minute=mm, second=0, microsecond=0)
    while True:
        taken = conn.execute(
            "SELECT 1 FROM posts WHERE slot = ? AND status IN ('approved','published') AND substr(scheduled_for,1,10) = ?",
            (slot, cursor.date().isoformat()),
        ).fetchone()
        candidate = cursor + timedelta(minutes=random.randint(-jitter, jitter))
        if not taken and candidate > datetime.now(TZ) + timedelta(minutes=10):
            return candidate
        cursor += timedelta(days=1)


def draft(conn, slot: str, topic_hint: str = "") -> int:
    docs, missing = knowledge.bundle("write_post")
    system = (
        f"You write LinkedIn posts for {OWNER}, strictly following his content system below. "
        "The documents are the authority on positioning, voice, series, hooks, proof rules, "
        "first comments and hashtags.\n\n"
        f"{docs}\n\n{knowledge.NO_FABRICATION}{knowledge.unavailable_note(missing)}"
    )
    prompt = (
        f"Write one post for the {slot.upper()} slot.\nSlot definition: {SLOT_LABEL[slot]}\n"
        f"Today: {datetime.now(TZ):%A %d %B %Y}.\n"
        + (f"Topic direction from {OWNER}: {topic_hint}\n" if topic_hint else "Choose the topic yourself from his topics to own.\n")
        + "\nRecent posts — do not repeat their hooks, structures or angles:\n"
        + _recent_posts(conn)
        + "\n\nRules for the fields:\n"
        "- post: the full post text exactly as it should appear on LinkedIn, no markdown.\n"
        "- hashtags: 0-3, without the # sign, topic-first; empty list is fine.\n"
        "- first_comment: only if it genuinely adds a new layer (per the first-comment rules); "
        "otherwise first_comment_needed=false and first_comment=''.\n"
        "- open_questions_for_author: anything you would need from him to make the post stronger "
        "or to verify a claim (empty list if none)."
    )
    d = llm.structured(system, prompt, PostDraft, CFG["llm"]["effort_writing"])
    cur = conn.execute(
        """INSERT INTO posts(created_at, slot, post_type, topic, hook, body, hashtags, first_comment, why,
                             source, originality, confidence, status, scheduled_for)
           VALUES(?,?,?,?,?,?,?,?,?,?,?,?, 'draft', ?)""",
        (
            now(), slot, d.post_type, d.topic, d.hook, d.post.strip(), json.dumps(d.hashtags),
            d.first_comment.strip() if d.first_comment_needed and d.first_comment.strip() else None,
            d.why_this_works, d.source_inspiration, d.originality, d.confidence,
            next_slot_time(conn, slot).isoformat(timespec="minutes"),
        ),
    )
    conn.commit()
    post_id = cur.lastrowid
    if d.open_questions_for_author:
        conn.execute(
            "UPDATE posts SET error = ? WHERE id = ?",
            ("Questions for you: " + " | ".join(d.open_questions_for_author), post_id),
        )
        conn.commit()
    verify(conn, post_id)
    return post_id


def verify(conn, post_id: int) -> GateResult:
    p = conn.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
    docs, missing = knowledge.bundle("verify_post")
    system = (
        f"You are the independent pre-publish verification gate for {OWNER}'s LinkedIn posts. "
        "Apply LinkedIn_Verification_Gate.md exactly: decide what applies to THIS post, mark the "
        "rest N/A, and block on any applicable requirement that is unmet. Be strict about "
        "fabrication and unsupported claims; do not invent requirements that don't apply.\n\n"
        f"{docs}\n\n{knowledge.NO_FABRICATION}{knowledge.unavailable_note(missing)}"
    )
    same_day = conn.execute(
        """SELECT id, slot, status, scheduled_for FROM posts WHERE id != ? AND status IN ('ready','approved','published')
           AND substr(scheduled_for,1,10) = ? ORDER BY scheduled_for""",
        (post_id, (p["scheduled_for"] or "")[:10]),
    ).fetchall()
    day_plan = "\n".join(f"  #{r['id']} {r['slot']} at {r['scheduled_for']} ({r['status']})" for r in same_day)
    prompt = (
        f"Slot: {p['slot'].upper()} ({SLOT_LABEL[p['slot']]})\n"
        f"Planned publish time: {p['scheduled_for']} ({TZ.key})\n"
        "Other posts planned that day (this is the complete list known to the system):\n"
        + (day_plan or "  none")
        + f"\nConfigured base slot times ({TZ.key}): {CFG['posting']['slots']}, ±{CFG['posting'].get('jitter_minutes', 0)} min natural variation\n"
        "Visual: none attached (text-only post)\nLinks/tags intended: none unless present in the text\n\n"
        f"POST TYPE: {p['post_type']}\nTOPIC: {p['topic']}\nHOOK: {p['hook']}\n"
        f"POST:\n{p['body']}\n\n"
        f"HASHTAGS (the publisher adds the # and places them at the end): {', '.join(json.loads(p['hashtags'] or '[]')) or '(none)'}\n"
        f"FIRST COMMENT: {p['first_comment'] or 'N/A — Not needed'}\n\n"
        "Recent posts for the repetition check:\n" + _recent_posts(conn)
    )
    g = llm.structured(system, prompt, GateResult, CFG["llm"]["effort_writing"])

    # The gate's hard rule, enforced in code too: any applicable failure means BLOCKED.
    if any(getattr(g, f) == "fail" for f in GATE_FIELDS):
        g.final_status = "BLOCKED"
        if not g.blocked_reason:
            g.blocked_reason = "; ".join(g.problems) or "an applicable check failed"

    status = "ready" if g.final_status == "READY" else "blocked"
    conn.execute(
        "UPDATE posts SET status = ?, verification = ? WHERE id = ?",
        (status, g.model_dump_json(), post_id),
    )
    conn.commit()
    if status == "ready":
        notify.send("LinkedIn post ready for approval", f"Post #{post_id} ({p['slot'].upper()}) passed the gate, planned for {p['scheduled_for']}.\nReview: uv run assistant show {post_id}\nApprove: uv run assistant approve {post_id}")
    else:
        notify.send("LinkedIn post BLOCKED", f"Post #{post_id} ({p['slot'].upper()}) failed the gate:\n{g.blocked_reason or '; '.join(g.problems)}")
    return g


def approve(conn, post_id: int, at: datetime | None = None) -> datetime:
    p = conn.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
    if p is None:
        raise ValueError(f"No post #{post_id}.")
    if p["status"] != "ready":
        raise ValueError(f"Post #{post_id} is '{p['status']}'. Only posts that passed the verification gate (ready) can be approved.")
    when = at or datetime.fromisoformat(p["scheduled_for"])
    if when.tzinfo is None:
        when = when.replace(tzinfo=TZ)
    conn.execute(
        "UPDATE posts SET status = 'approved', scheduled_for = ? WHERE id = ?",
        (when.isoformat(timespec="minutes"), post_id),
    )
    conn.commit()
    notify.send("LinkedIn post scheduled", f"Post #{post_id} ({p['slot'].upper()}) approved; it will publish at {when.isoformat(timespec='minutes')}.")
    return when


def publish(conn, post_id: int) -> str:
    p = conn.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
    if p["status"] != "approved":
        raise ValueError(f"Post #{post_id} is '{p['status']}', not approved.")
    try:
        urn = linkedin.publish(p["body"], json.loads(p["hashtags"] or "[]"))
    except Exception as e:
        conn.execute("UPDATE posts SET status = 'failed', error = ? WHERE id = ?", (str(e), post_id))
        conn.commit()
        notify.send("LinkedIn post FAILED", f"Post #{post_id} ({p['slot']}) did not publish:\n{e}")
        raise
    conn.execute(
        "UPDATE posts SET status = 'published', published_at = ?, linkedin_urn = ?, error = NULL WHERE id = ?",
        (now(), urn, post_id),
    )
    conn.commit()
    msg = f"Post #{post_id} ({p['slot'].upper()}) is live:\n{linkedin.post_url(urn)}\n\nOpen it and check the text looks right."
    if p["first_comment"]:
        msg += f"\n\nPost this first comment yourself (manual, per your rules):\n\n{p['first_comment']}"
    notify.send("LinkedIn post published ✅", msg)
    return urn


def publish_due(conn) -> list[int]:
    due = conn.execute(
        "SELECT id, scheduled_for FROM posts WHERE status = 'approved' ORDER BY scheduled_for"
    ).fetchall()
    done = []
    for row in due:
        if datetime.fromisoformat(row["scheduled_for"]) <= datetime.now(TZ):
            try:
                publish(conn, row["id"])
                done.append(row["id"])
            except Exception as e:
                print(f"[publish] #{row['id']} failed: {e}")
    return done


def format_post(p) -> str:
    hashtags = ", ".join(json.loads(p["hashtags"] or "[]")) or "(none)"
    out = [
        f"#{p['id']}  [{p['status'].upper()}]  slot={p['slot']}  scheduled={p['scheduled_for'] or '-'}",
        f"POST TYPE: {p['post_type']}",
        f"TOPIC: {p['topic']}",
        f"HOOK: {p['hook']}",
        f"POST:\n{p['body']}",
        f"HASHTAGS: {hashtags}",
        f"FIRST COMMENT: {p['first_comment'] or 'N/A — Not needed'}",
        f"WHY THIS WORKS: {p['why']}",
        f"SOURCE/INSPIRATION: {p['source']}",
        f"ORIGINALITY: {p['originality']}",
        f"CONFIDENCE: {p['confidence']}",
    ]
    if p["verification"]:
        g = GateResult.model_validate_json(p["verification"])
        mark = {"pass": "✅", "na": "N/A", "fail": "❌"}
        out.append("\nPOST VERIFICATION")
        out += [f"  {f.replace('_', ' ').capitalize()}: {mark[getattr(g, f)]}" for f in GATE_FIELDS]
        if g.final_status == "READY":
            out.append("FINAL STATUS: 🟢 READY TO SCHEDULE/PUBLISH")
        else:
            fix = "fixable now" if g.fixable_now else "needs input from you"
            out.append(f"FINAL STATUS: 🔴 BLOCKED — {g.blocked_reason} ({fix})")
        if g.problems:
            out.append("Problems: " + "; ".join(g.problems))
    if p["error"]:
        out.append(f"NOTE: {p['error']}")
    if p["linkedin_urn"]:
        out.append(f"LIVE: {linkedin.post_url(p['linkedin_urn'])}")
    return "\n".join(out)
