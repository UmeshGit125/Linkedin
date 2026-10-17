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
    "my_learning": "mylearning",       # Docs/MY_LEARNING_AND_PROJECTS.md, written by Umesh
    "my_posts": "mypostexamples",      # Docs/MY_POST_EXAMPLES.md, written by Umesh
}

# Which docs each task needs, following the "Read order by task" section of the README.
TASK_DOCS = {
    "write_post": ["master", "my_learning", "my_posts", "creator_research", "operating", "learning_memory", "first_comment", "hashtag", "scheduling"],
    "verify_post": ["verification", "master", "my_learning", "operating", "first_comment", "hashtag", "scheduling", "learning_memory"],
    "comment": ["comment_intel", "creator_research", "master", "my_learning"],
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


def no_names_rule() -> str:
    names = ", ".join(CFG["posting"].get("never_name", []))
    return (
        "PRIVACY RULE FOR EVERYTHING PUBLIC (posts, first comments, comments): never name his projects, "
        f"products or employer ({names}, or any other project name from the documents) because they belong to his office. "
        "Talk about the experience without the name: say 'one of my projects', 'a project I built', 'a side project', "
        "'a system I worked on'. Technical lessons are fine; internal details, data and client information are not."
    )


def banned_names(text: str) -> list[str]:
    """Names from posting.never_name that appear in the text (case-insensitive)."""
    return [n for n in CFG["posting"].get("never_name", []) if re.search(re.escape(n), text or "", re.I)]


NOTE_SECTIONS = {   # key -> (button label, heading in Docs/MY_LEARNING_AND_PROJECTS.md)
    "learning": ("📚 Learning now", "## What I am learning right now"),
    "lesson": ("🧯 Hard lesson", "## Things I learned the hard way"),
    "project": ("🛠 Project detail", "## Project details beyond the resume"),
    "number": ("🔢 Measured number", "## Real numbers I can state"),
    "opinion": ("💡 Opinion", "## Opinions I actually hold"),
    "avoid": ("🚫 Don't post about", "## Topics I do NOT want to post about"),
}


def add_note(section: str, text: str) -> Path:
    """Append one bullet to a section of Docs/MY_LEARNING_AND_PROJECTS.md (created if missing)."""
    path = find("my_learning") or (DOCS_DIR / "MY_LEARNING_AND_PROJECTS.md")
    lines = path.read_text(errors="ignore").splitlines() if path.exists() else []
    heading = NOTE_SECTIONS[section][1]
    bullet = "- " + " ".join(text.split())
    for i, line in enumerate(lines):
        if line.startswith(heading):
            end = next((k for k in range(i + 1, len(lines)) if lines[k].startswith("## ")), len(lines))
            lines = lines[:i + 1] + [l for l in lines[i + 1:end] if "(nothing added yet)" not in l] + lines[end:]
            end = next((k for k in range(i + 1, len(lines)) if lines[k].startswith("## ")), len(lines))
            while end > i + 1 and not lines[end - 1].strip():
                end -= 1
            lines.insert(end, bullet)
            break
    else:
        lines += ["", heading, bullet]
    path.write_text("\n".join(lines) + "\n")
    return path


def independent_rule() -> str:
    if not CFG["posting"].get("independent_posts", True):
        return ""
    return (
        "INDEPENDENT POSTS (default): write each post as a standalone piece about the topic itself: how it works, "
        "why it fails, a common mistake, a comparison, a mental model, a clear opinion with reasons, a worked example "
        "with made-up-but-labelled data. Do NOT tell stories about his own projects, work, team, employer or builds, "
        "not even unnamed ('one of my projects', 'while building', 'I built', 'at work', 'we split it'). "
        "Do not invent anecdotes. Use first person only for an opinion or a learning that is written in "
        "MY_LEARNING_AND_PROJECTS (for example something he is currently learning). "
        "Teach something specific and correct; if unsure a technical claim is accurate, leave it out."
    )


def project_mentions(text: str) -> list[str]:
    """Phrases in the text that point at his own projects/work (posting.project_phrases)."""
    pat = CFG["posting"].get("project_phrases", "")
    if not pat or not CFG["posting"].get("independent_posts", True):
        return []
    return sorted({m.group(0).lower() for m in re.finditer(pat, text or "", re.I)})
