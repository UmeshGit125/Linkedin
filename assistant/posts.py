"""Post pipeline: draft -> verification gate -> your approval -> scheduled publish.

Nothing reaches LinkedIn unless the gate returned READY *and* you approved it.
"""
import json
import random
from datetime import datetime, timedelta
from typing import Literal

from pydantic import BaseModel

from concurrent.futures import ThreadPoolExecutor

from . import imagegen, knowledge, linkedin, llm, notify
from .config import CFG, DATA_DIR, TZ

OWNER = CFG["profile"]["name"]
from .db import connect, now

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
    image_prompt: str = ""
    image_alt: str = ""


class PostVariants(BaseModel):
    variants: list[PostDraft]


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


def _recent_posts(conn, limit: int = 9, exclude_id: int = 0) -> str:
    rows = conn.execute(
        "SELECT slot, hook, body FROM posts WHERE status IN ('approved','published') AND id != ? ORDER BY id DESC LIMIT ?",
        (exclude_id, limit),
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


def _writer_system() -> str:
    docs, missing = knowledge.bundle("write_post")
    return (
        f"You write LinkedIn posts for {OWNER}, strictly following his content system below. "
        "The documents are the authority on positioning, voice, series, hooks, proof rules, "
        "first comments and hashtags. If MY_POST_EXAMPLES is present, copy his voice from it: sentence length, "
        "vocabulary, openings, how he ends. Facts about projects and learning come only from the master "
        "document and MY_LEARNING_AND_PROJECTS; anything marked '(nothing added yet)' is not available.\n\n"
        f"{knowledge.no_names_rule()} "
        "You may also write accurate, general explanations of techniques beyond what he built (for example other "
        "RAG variants: what they are, how they work, when to use them), following the notes he left in "
        "LinkedIn_Creator_Research. Only state what is well established and say so when unsure; first-person "
        "experience claims still need his notes.\n\n"
        f"{docs}\n\n{knowledge.NO_FABRICATION}{knowledge.unavailable_note(missing)}"
    )


FIELD_RULES = (
    "Rules for the fields:\n"
    "- post: the full post text exactly as it should appear on LinkedIn, no markdown.\n"
    "- hashtags: 0-3, without the # sign, topic-first; empty list is fine.\n"
    "- first_comment: only if it genuinely adds a new layer (per the first-comment rules); "
    "otherwise first_comment_needed=false and first_comment=''.\n"
    "- open_questions_for_author: anything you would need from him to make the post stronger "
    "or to verify a claim (empty list if none).\n"
    "- image_prompt: " + ("a one-paragraph description of a clean editorial illustration or abstract diagram that "
                         "matches the post's idea. No text, logos, faces or invented numbers in the image. "
                         "Required for Authority posts; for other posts only when a visual adds real value, else ''."
                         if imagegen.enabled() else "always '' (image generation is not configured).") + "\n"
    "- image_alt: one-sentence alt text for the image ('' if no image)."
)


def _tag(t: str) -> str:
    return "".join(w[:1].upper() + w[1:] for w in t.lstrip("#").split())


def _insert(conn, d: PostDraft, slot: str, parent_id: int | None = None, scheduled_for: str | None = None) -> int:
    cur = conn.execute(
        """INSERT INTO posts(created_at, slot, post_type, topic, hook, body, hashtags, first_comment, why,
                             source, originality, confidence, status, scheduled_for, image_prompt, alt_text, parent_id, error)
           VALUES(?,?,?,?,?,?,?,?,?,?,?,?, 'draft', ?, ?, ?, ?, ?)""",
        (
            now(), slot, d.post_type, d.topic, d.hook, d.post.strip(), json.dumps([_tag(t) for t in d.hashtags if t.strip()]),
            d.first_comment.strip() if d.first_comment_needed and d.first_comment.strip() else None,
            d.why_this_works, d.source_inspiration, d.originality, d.confidence,
            scheduled_for or next_slot_time(conn, slot).isoformat(timespec="minutes"),
            d.image_prompt.strip() or None, d.image_alt.strip() or None, parent_id,
            ("Questions for you: " + " | ".join(d.open_questions_for_author)) if d.open_questions_for_author else None,
        ),
    )
    conn.commit()
    return cur.lastrowid


def attach_image(conn, post_id: int) -> None:
    """Generates the post's image when an image API is configured. A failure never blocks the post."""
    p = conn.execute("SELECT image_prompt FROM posts WHERE id = ?", (post_id,)).fetchone()
    if not (p and p["image_prompt"] and imagegen.enabled()):
        return
    try:
        path = imagegen.generate(p["image_prompt"], DATA_DIR / "images" / f"post_{post_id}.png")
        conn.execute("UPDATE posts SET image_path = ? WHERE id = ?", (str(path), post_id))
        conn.commit()
    except Exception as e:
        print(f"[image] post #{post_id}: {e}")


def draft(conn, slot: str, topic_hint: str = "", notify_result: bool = True) -> int:
    prompt = (
        f"Write one post for the {slot.upper()} slot.\nSlot definition: {SLOT_LABEL[slot]}\n"
        f"Today: {datetime.now(TZ):%A %d %B %Y}.\n"
        + (f"Topic direction from {OWNER}: {topic_hint}\n" if topic_hint else "Choose the topic yourself from his topics to own.\n")
        + "\nRecent posts — do not repeat their hooks, structures or angles:\n"
        + _recent_posts(conn)
        + "\n\n" + FIELD_RULES
    )
    d = llm.structured(_writer_system(), prompt, PostDraft, CFG["llm"]["effort_writing"])
    post_id = _insert(conn, d, slot)
    attach_image(conn, post_id)
    verify(conn, post_id, notify_result=notify_result)
    return post_id


def variants(conn, topic: str, n: int | None = None) -> list[int]:
    """Several different posts on one topic, each drafted, illustrated and gate-checked."""
    n = n or int(CFG["posting"].get("variants", 3))
    prompt = (
        f"{OWNER} wants a post about this topic: {topic}\n"
        f"Write {n} genuinely different posts on it: different angle, structure and post type each "
        "(for example one story or observation, one speaking to the ICP's problem, one technical "
        "lesson or opinion). Use only real experience from the documents; if the topic needs a fact "
        "you do not have, write around it and list the question.\n"
        f"Today: {datetime.now(TZ):%A %d %B %Y}.\n\nRecent posts — do not repeat their hooks, structures or angles:\n"
        + _recent_posts(conn) + "\n\n" + FIELD_RULES
    )
    result = llm.structured(_writer_system(), prompt, PostVariants, CFG["llm"]["effort_writing"])
    ids = []
    for i, d in enumerate(result.variants[:n]):
        pid = _insert(conn, d, SLOTS[i % len(SLOTS)], scheduled_for=datetime.now(TZ).isoformat(timespec="minutes"))
        ids.append(pid)
    _finish_in_parallel(ids)
    return ids


def _finish_in_parallel(ids: list[int]) -> None:
    """Image + verification gate for each draft, at the same time."""
    def work(pid: int) -> None:
        c = connect()
        try:
            attach_image(c, pid)
            verify(c, pid, notify_result=False)
        except Exception as e:
            print(f"[posts] #{pid} finish failed: {e}")
        finally:
            c.close()

    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(work, ids))


def redraft(conn, post_id: int, feedback: str) -> int:
    """New version of a post that applies the author's (or the gate's) feedback. The old one is rejected."""
    old = conn.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
    if old is None:
        raise ValueError(f"No post #{post_id}.")
    prompt = (
        f"Revise this {old['slot'].upper()} post.\n\nCURRENT VERSION:\n{old['body']}\n\n"
        f"HASHTAGS: {old['hashtags']}\nFIRST COMMENT: {old['first_comment'] or 'none'}\n\n"
        f"WHAT {OWNER.upper()} WANTS CHANGED:\n{feedback}\n\n"
        "Apply exactly those changes and keep everything else that works. Still follow every rule in the documents.\n\n"
        + "Recent posts — do not repeat their hooks, structures or angles:\n" + _recent_posts(conn) + "\n\n" + FIELD_RULES
    )
    d = llm.structured(_writer_system(), prompt, PostDraft, CFG["llm"]["effort_writing"])
    new_id = _insert(conn, d, old["slot"], parent_id=post_id, scheduled_for=old["scheduled_for"])
    conn.execute("UPDATE posts SET status = 'rejected' WHERE id = ? AND status NOT IN ('published','approved')", (post_id,))
    conn.commit()
    attach_image(conn, new_id)
    verify(conn, new_id, notify_result=False)
    return new_id


def discard(conn, post_id: int) -> None:
    conn.execute("UPDATE posts SET status = 'rejected' WHERE id = ? AND status NOT IN ('published','publishing')", (post_id,))
    conn.commit()


def _visual_line(p) -> str:
    if p["image_path"]:
        return f"Visual: an AI-generated illustration is attached (described as: {p['image_prompt']}). It contains no text, data or people."
    return "Visual: none attached (text-only post)"


def verify(conn, post_id: int, notify_result: bool = True) -> GateResult:
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
        """SELECT id, slot, status, scheduled_for FROM posts WHERE id != ? AND status IN ('approved','published')
           AND substr(COALESCE(published_at, scheduled_for),1,10) = ? ORDER BY scheduled_for""",
        (post_id, (p["scheduled_for"] or "")[:10]),
    ).fetchall()
    day_plan = "\n".join(f"  #{r['id']} {r['slot']} at {r['scheduled_for']} ({r['status']})" for r in same_day)
    prompt = (
        f"Slot: {p['slot'].upper()} ({SLOT_LABEL[p['slot']]})\n"
        f"Planned publish time: {p['scheduled_for']} ({TZ.key})"
        + (" — indicative only: the post goes out as soon as the author approves it in Telegram, which is his confirmation of that post and its time. No timezone-target experiment has recorded parameters, so treat none as active.\n" if CFG["posting"].get("publish_on_approve") else "\n")
        +
        "Other posts already approved or published that day (unapproved drafts are alternatives, not commitments; this is the complete list known to the system):\n"
        + (day_plan or "  none")
        + f"\nConfigured base slot times ({TZ.key}): {CFG['posting']['slots']}, ±{CFG['posting'].get('jitter_minutes', 0)} min natural variation\n"
        + _visual_line(p) + "\nLinks/tags intended: none unless present in the text\n\n"
        f"POST TYPE: {p['post_type']}\nTOPIC: {p['topic']}\nHOOK: {p['hook']}\n"
        f"POST:\n{p['body']}\n\n"
        f"HASHTAGS (the publisher adds the # and places them at the end): {', '.join(json.loads(p['hashtags'] or '[]')) or '(none)'}\n"
        f"FIRST COMMENT: {p['first_comment'] or 'N/A — Not needed'}\n\n"
        "Recent posts for the repetition check (this post is not in the list):\n" + _recent_posts(conn, exclude_id=post_id)
    )
    g = llm.structured(system, prompt, GateResult, CFG["llm"]["effort_writing"])

    leaked = knowledge.banned_names(f"{p['body']} {p['first_comment'] or ''} {p['hook'] or ''} {p['topic'] or ''} {p['image_prompt'] or ''} {p['alt_text'] or ''}")
    if leaked:  # enforced in code, whatever the model said
        g.final_status = "BLOCKED"
        g.problems = [*g.problems, f"Names a private project/employer ({', '.join(leaked)}). Say 'one of my projects' instead."]
        g.blocked_reason = "; ".join(g.problems)

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
    if not notify_result:
        return g
    if status == "ready":
        notify.send("LinkedIn post ready for approval", f"Post #{post_id} ({p['slot'].upper()}) passed the gate, planned for {p['scheduled_for']}.\nReview: uv run assistant show {post_id}\nApprove: uv run assistant approve {post_id}")
    else:
        notify.send("LinkedIn post BLOCKED", f"Post #{post_id} ({p['slot'].upper()}) failed the gate:\n{g.blocked_reason or '; '.join(g.problems)}")
    return g


def approve(conn, post_id: int, at: datetime | None = None, quiet: bool = False) -> datetime:
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
    if not quiet:
        notify.send("LinkedIn post scheduled", f"Post #{post_id} ({p['slot'].upper()}) approved; it will publish at {when.isoformat(timespec='minutes')}.")
    return when


def _claim(conn, post_id: int, from_status: str) -> bool:
    """Atomically takes a post for publishing, so the scheduler and a Telegram tap can never both post it."""
    cur = conn.execute("UPDATE posts SET status = 'publishing' WHERE id = ? AND status = ?", (post_id, from_status))
    conn.commit()
    return cur.rowcount == 1


def _publish_claimed(conn, post_id: int) -> str:
    p = conn.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
    try:
        urn = linkedin.publish(p["body"], json.loads(p["hashtags"] or "[]"), p["image_path"], p["alt_text"] or "")
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


def publish(conn, post_id: int) -> str:
    """Publishes an approved post (used by the scheduler and `assistant publish`)."""
    if not _claim(conn, post_id, "approved"):
        p = conn.execute("SELECT status FROM posts WHERE id = ?", (post_id,)).fetchone()
        raise ValueError(f"Post #{post_id} is '{p['status'] if p else 'missing'}', not approved.")
    return _publish_claimed(conn, post_id)


def approve_and_publish(conn, post_id: int) -> str:
    """Telegram 'Approve': the gate must have passed (ready); posts to LinkedIn right away."""
    if not _claim(conn, post_id, "ready"):
        p = conn.execute("SELECT status FROM posts WHERE id = ?", (post_id,)).fetchone()
        raise ValueError(f"Post #{post_id} is '{p['status'] if p else 'missing'}'. Only posts that passed the gate (ready) can be approved.")
    return _publish_claimed(conn, post_id)


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
