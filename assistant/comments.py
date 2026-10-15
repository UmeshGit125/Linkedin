"""Drafts comments on other people's posts. You post them yourself — your own rules
(and LinkedIn's) rule out automated commenting."""
import json

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel

from . import knowledge, llm
from .config import CFG
from .db import now


class CommentDraft(BaseModel):
    worth_commenting: bool
    reasoning: str
    comment: str


def draft(conn, text: str, author: str = "", url: str = "") -> int:
    docs, missing = knowledge.bundle("comment")
    system = (
        f"You decide whether {CFG['profile']['name']} should comment on someone else's LinkedIn post and, if "
        "so, write the comment in his voice following his comment rules. A comment must add a "
        "real layer — experience-based detail, a nuance, a respectful counterpoint or a genuine "
        "question — never praise filler ('Great post!'), never self-promotion, never a summary "
        "of the post. If there is nothing valuable to add, set worth_commenting=false.\n\n"
        f"{docs}\n\n{knowledge.NO_FABRICATION}{knowledge.unavailable_note(missing)}"
    )
    prompt = f"Author: {author or 'unknown'}\nURL: {url or 'n/a'}\n\nPost:\n{text}"
    c = llm.structured(system, prompt, CommentDraft, CFG["llm"]["effort_writing"])
    cur = conn.execute(
        """INSERT INTO comment_drafts(created_at, target_url, target_author, target_text,
                                      worth_commenting, comment, reasoning, status)
           VALUES(?,?,?,?,?,?,?, ?)""",
        (now(), url, author, text, int(c.worth_commenting), c.comment, c.reasoning,
         "drafted" if c.worth_commenting else "skipped"),
    )
    conn.commit()
    return cur.lastrowid


class CommentOption(BaseModel):
    style: str   # one-liner | short | witty
    angle: str   # one plain sentence: what this comment says / when to pick it
    text: str


class CommentOptions(BaseModel):
    worth_commenting: bool
    post_summary: str   # 1-2 plain sentences: what the post says and who wrote it
    reasoning: str      # only when worth_commenting is false: one short sentence why
    options: list[CommentOption]


def options(conn, text: str, author: str = "", url: str = "", avoid: list[str] | None = None) -> int:
    """Three ready-to-paste comment options for one specific post. You post the one you like."""
    docs, missing = knowledge.bundle("comment")
    system = (
        f"You write LinkedIn comments for {CFG['profile']['name']} on other people's posts. Every comment must be "
        "clearly about THIS specific post: react to something concrete in it. Give three options: "
        "'one-liner' (one sharp line), 'short' (two or three lines that add a real layer: an experience-based detail, "
        "a nuance, a respectful counterpoint or a genuine question) and 'witty' (a light joke or dry, playful "
        "sarcasm aimed at the situation or idea, never at the author or anyone's identity). "
        "No filler like 'Great post!', no self-promotion, no summary of the post, no hashtags, no emojis unless the "
        "post's tone calls for one. Plain human voice, never corporate. "
        "Only claim experience that appears in the documents or resume; never invent numbers or projects. "
        "If the post is a job or hiring post, a good comment shows genuine interest in the role or asks one smart question. "
        "Write in simple, everyday English, short words, the way a smart student would talk. No fancy or abstract phrases. "
        "Also fill: post_summary = what the post says in 1-2 very plain sentences (max 40 words); "
        "angle for each option = one plain sentence (max 20 words) saying what that comment says and when to pick it. "
        "If there is truly nothing worth adding, set worth_commenting=false and give one short sentence in reasoning.\n\n"
        f"{docs}\n\n<resume>\n{knowledge.resume_text()[:4000]}\n</resume>\n\n"
        f"{knowledge.NO_FABRICATION}{knowledge.unavailable_note(missing)}"
    )
    prompt = f"Author: {author or 'unknown'}\nURL: {url or 'n/a'}\n\nPost:\n{text}"
    if avoid:
        prompt += "\n\nAlready offered, give clearly different ones:\n- " + "\n- ".join(avoid)
    c = llm.structured(system, prompt, CommentOptions, CFG["llm"]["effort_writing"])
    first = c.options[0].text if c.options else ""
    cur = conn.execute(
        """INSERT INTO comment_drafts(created_at, target_url, target_author, target_text,
                                      worth_commenting, comment, reasoning, status, options)
           VALUES(?,?,?,?,?,?,?,?,?)""",
        (now(), url, author, text, int(c.worth_commenting and bool(c.options)), first,
         c.post_summary if c.worth_commenting else c.reasoning,
         "drafted" if c.worth_commenting and c.options else "skipped",
         json.dumps([o.model_dump() for o in c.options])),
    )
    conn.commit()
    return cur.lastrowid


def fetch_post_text(url: str) -> str:
    """Best effort: the public preview text of a LinkedIn post URL (no login). Empty when LinkedIn hides it."""
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 Chrome/130.0", "Accept-Language": "en-US,en;q=0.9"}, timeout=20)
    except requests.RequestException:
        return ""
    if r.status_code != 200:
        return ""
    s = BeautifulSoup(r.text, "html.parser")
    for sel in ('meta[property="og:description"]', 'meta[name="description"]', 'meta[property="og:title"]'):
        node = s.select_one(sel)
        if node and len(node.get("content", "")) > 60:
            return node["content"].strip()
    return ""
