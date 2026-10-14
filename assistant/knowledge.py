"""Loads the rule documents in Docs/ so every Claude call follows the system you built.

File names in Docs/ don't have to match exactly — each logical doc is found by a
keyword in its normalized file name (e.g. "Linked_Master_system.md" -> master).
"""
import re
from pathlib import Path

from .config import CFG, DOCS_DIR, ROOT

DOC_KEYS = {
    "readme": "readme",
    "master": "master",
    "operating": "operatingsystem",
    "comment_intel": "commentintelligence",
    "hashtag": "hashtag",
    "self_learning": "selflearning",
    "scheduling": "scheduling",
    "verification": "verificationgate",
    "first_comment": "firstcomment",
    "learning_memory": "learningmemory",
    "creator_research": "creatorresearch",
}

# Which docs each task needs, following the "Read order by task" section of the README.
TASK_DOCS = {
    "write_post": ["master", "operating", "learning_memory", "first_comment", "hashtag", "scheduling"],
    "verify_post": ["verification", "master", "operating", "first_comment", "hashtag", "scheduling", "learning_memory"],
    "comment": ["comment_intel", "creator_research", "master"],
}

NO_FABRICATION = (
    "STANDING RULE THAT OVERRIDES EVERYTHING: never invent a metric, quote, creator, client "
    "result, follower count, or personal experience. If a real number or fact is not present "
    "in the documents or input you were given, write TBD / 'could not verify', or leave the "
    "claim out. A missing fact is a reason to block or skip, never to guess."
)


def _norm(name: str) -> str:
    return re.sub(r"[^a-z]", "", name.lower())


def find(key: str) -> Path | None:
    needle = DOC_KEYS[key]
    if not DOCS_DIR.exists():
        return None
    for path in sorted(DOCS_DIR.iterdir()):
        if path.suffix.lower() in (".md", ".txt") and needle in _norm(path.stem):
            return path
    return None


def status() -> dict[str, str]:
    """key -> 'ok' | 'empty' | 'missing'."""
    out = {}
    for key in DOC_KEYS:
        path = find(key)
        if path is None:
            out[key] = "missing"
        elif not path.read_text(errors="ignore").strip():
            out[key] = "empty"
        else:
            out[key] = "ok"
    return out


def bundle(task: str) -> tuple[str, list[str]]:
    """Returns (documents wrapped in tags, list of unavailable doc keys)."""
    parts, unavailable = [], []
    for key in TASK_DOCS[task]:
        path = find(key)
        text = path.read_text(errors="ignore").strip() if path else ""
        if not text:
            unavailable.append(key)
            continue
        parts.append(f'<document name="{path.name}">\n{text}\n</document>')
    return "\n\n".join(parts), unavailable


def unavailable_note(unavailable: list[str]) -> str:
    if not unavailable:
        return ""
    names = ", ".join(unavailable)
    return (
        f"\nThese system documents are NOT available yet: {names}. Do not assume what they "
        "say. Where a decision depends on one of them, apply the conservative choice and "
        "state the gap explicitly. In particular: with no Proof Inventory available, any "
        "claim about results, clients, metrics, costs or before/after numbers is unverifiable."
    )


def resume_text() -> str:
    path = ROOT / CFG["profile"].get("resume_path", "resume.pdf")
    if not path.exists():
        return ""
    if path.suffix.lower() == ".pdf":
        from pypdf import PdfReader

        return "\n".join(page.extract_text() or "" for page in PdfReader(path).pages).strip()
    return path.read_text(errors="ignore").strip()


def candidate_profile() -> str:
    resume = resume_text()
    master = find("master")
    positioning = ""
    if master:
        text = master.read_text(errors="ignore")
        m = re.search(r"## 1\..*?(?=\n## )", text, re.S)
        positioning = m.group(0) if m else ""
    parts = [f"Summary: {CFG['profile']['summary']}"]
    if positioning:
        parts.append(positioning)
    parts.append(f"<resume>\n{resume}\n</resume>" if resume else "(No resume provided yet.)")
    return "\n\n".join(parts)
