"""Drafts the rule documents that are missing from Docs/, from your resume and the documents you already have.

Every file starts with a DRAFT banner so you know to review it. Nothing here invents proof, metrics or
real people: those parts are left as TBD for you to fill in.
"""
from pydantic import BaseModel

from . import knowledge, llm
from .config import CFG, DOCS_DIR

FILES = {
    "operating": "LinkedIn_Operating_System.md",
    "comment_intel": "LinkedIn_Comment_Intelligence_System.md",
    "hashtag": "LinkedIn_Hashtag_Intelligence_System.md",
    "self_learning": "LinkedIn_Self_Learning_System.md",
    "scheduling": "LinkedIn_Scheduling_System.md",
    "learning_memory": "LINKEDIN_LEARNING_MEMORY.md",
    "creator_research": "LinkedIn_Creator_Research.md",
}

BRIEF = {
    "operating": "How the whole LinkedIn system runs day to day: the daily flow (draft -> gate -> Telegram approval -> publish), "
                 "the 3-post series structure, which post types need a visual (Authority/Proof/Breakdown posts get an image; "
                 "an AI-generated illustration with no text or data is allowed for non-proof posts), and a Section 34B on visuals.",
    "comment_intel": "Rules for commenting on other people's posts: relevance to the specific post, 1-3 lines, allowed tones "
                     "(plain, curious, dry humour or light sarcasm aimed at ideas, never at people), banned filler, how to comment on hiring "
                     "posts, how to comment on senior engineers' posts, and that comments are pasted by the author himself.",
    "hashtag": "Hashtag rules: 0-3 per post, topic-first, chosen after the content, no stuffing, a short vocabulary of tags that fit his topics.",
    "self_learning": "How the system learns from results: what to record after a post (impressions, comments, followers), how often to review, "
                     "how findings update the learning memory. No invented numbers.",
    "scheduling": "Posting schedule: one post a day, rotating TOFU/MOFU/Authority, posts publish when the author approves in Telegram, "
                  "preferred windows in Asia/Kolkata, rules against posting twice in one day or two similar posts in a row.",
    "learning_memory": "An empty-but-structured learning memory: sections for active experiments, what worked, what did not, audience notes. "
                       "Leave every data row as TBD. Do not invent results.",
    "creator_research": "Who to read and learn from: categories of creators worth following for applied AI / GenAI (by type and topic), "
                        "how to study a creator without copying, and an empty table for real names to be added by the author. "
                        "Do NOT name real people unless they appear in the existing documents.",
}


class DocText(BaseModel):
    markdown: str


def draft_missing(force: bool = False) -> list[tuple[str, str]]:
    st = knowledge.status()
    context = []
    for key in ("readme", "master", "verification", "first_comment"):
        path = knowledge.find(key)
        if path:
            context.append(f'<document name="{path.name}">\n{path.read_text(errors="ignore")}\n</document>')
    resume = knowledge.resume_text()
    system = (
        "You write one rule document for a personal LinkedIn content system, in the same style, tone and structure as the "
        "existing documents provided. Write only what follows from the existing documents, the resume and the brief. "
        "Where a real fact, number, result or person is needed and not provided, write TBD. "
        f"The owner is {CFG['profile']['name']}.\n\n" + "\n\n".join(context)
        + f"\n\n<resume>\n{resume[:5000]}\n</resume>\n\n{knowledge.NO_FABRICATION}"
    )
    out = []
    for key, name in FILES.items():
        if st.get(key) == "ok" and not force:
            continue
        path = DOCS_DIR / name
        if path.exists() and path.read_text(errors="ignore").strip() and "DRAFT" not in path.read_text(errors="ignore")[:200]:
            out.append((key, "kept (already has your content)"))
            continue
        d = llm.structured(system, f"Write the document `{name}`.\nBrief: {BRIEF[key]}\nMarkdown only, under 1,500 words.", DocText, CFG["llm"]["effort_writing"])
        path.write_text("> **DRAFT written by the assistant — review and edit before relying on it.**\n\n" + d.markdown.strip() + "\n")
        out.append((key, f"drafted -> Docs/{name}"))
    return out
