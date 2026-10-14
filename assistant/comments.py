"""Drafts comments on other people's posts. You post them yourself — your own rules
(and LinkedIn's) rule out automated commenting."""
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
