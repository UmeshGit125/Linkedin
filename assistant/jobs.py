"""Job & internship finder.

Every run (every 30 min by default): search LinkedIn's official public job-search URLs with a
time filter (recent postings only) -> fetch each new job's details -> extract tech stack /
experience / work mode -> AI fit-score -> append to the Jobs sheet -> notify on strong matches.

Nothing logs in as you, so your LinkedIn account is not involved. You apply yourself.
"""
import random
import re
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from typing import Literal

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel

from . import knowledge, llm, notify, sheet
from .config import CFG, DATA_DIR, TZ
from .db import now, set_kv

UA = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}
LI_SEARCH = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
LI_DETAIL = "https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{id}"
EXPERIENCE = {"internship": "1", "entry": "2", "associate": "3", "mid-senior": "4"}
JOB_TYPE = {"full-time": "F", "part-time": "P", "contract": "C", "internship": "I"}
PAGE_SIZE = 10  # LinkedIn's guest search returns 10 cards per page

# Detected in descriptions for the "Tech stack" column. Display name -> regex.
TECH = {
    "Python": r"python", "Java": r"java(?!script)", "JavaScript": r"javascript", "TypeScript": r"typescript",
    "Go": r"golang|\bgo\b(?= developer| programming| language)", "C++": r"c\+\+", "Rust": r"\brust\b", "SQL": r"\bsql\b",
    "PyTorch": r"pytorch", "TensorFlow": r"tensorflow", "Keras": r"keras", "scikit-learn": r"scikit|sklearn",
    "Hugging Face": r"hugging ?face|transformers library", "LangChain": r"langchain", "LlamaIndex": r"llama ?index",
    "LangGraph": r"langgraph", "OpenAI API": r"openai", "Claude/Anthropic": r"anthropic|\bclaude\b",
    "LLMs": r"\bllms?\b|large language model", "RAG": r"\brag\b|retrieval[- ]augmented", "NLP": r"\bnlp\b|natural language",
    "Computer Vision": r"computer vision|\bopencv\b", "Vector DBs": r"pinecone|weaviate|qdrant|milvus|chroma|faiss|pgvector|vector (?:db|database)",
    "MLOps": r"mlops|mlflow|kubeflow|sagemaker|vertex ai", "FastAPI": r"fastapi", "Django": r"django", "Flask": r"flask",
    "Node.js": r"node\.?js", "React": r"\breact\b", "Next.js": r"next\.?js", "AWS": r"\baws\b|amazon web services",
    "GCP": r"\bgcp\b|google cloud", "Azure": r"azure", "Docker": r"docker", "Kubernetes": r"kubernetes|\bk8s\b",
    "Spark": r"\bspark\b|pyspark", "Airflow": r"airflow", "Kafka": r"kafka", "PostgreSQL": r"postgres", "MongoDB": r"mongo",
    "Redis": r"redis", "Pandas": r"pandas", "NumPy": r"numpy", "Git": r"\bgit\b|github",
}


def _pause():
    time.sleep(random.uniform(2.0, 4.5))  # polite pacing between requests


def _text(html: str) -> str:
    return BeautifulSoup(html or "", "html.parser").get_text("\n", strip=True)


def _linkedin_search(role: str, location: str, remote_only: bool) -> list[dict]:
    jc = CFG["jobs"]
    params = {
        "keywords": role,
        "location": location,
        "f_TPR": f"r{int(jc.get('time_window_minutes', 60)) * 60}",  # only jobs posted in this window
        "f_E": ",".join(EXPERIENCE[e] for e in jc.get("experience", []) if e in EXPERIENCE),
        "f_JT": ",".join(JOB_TYPE[t] for t in jc.get("types", []) if t in JOB_TYPE),
        "sortBy": "DD",  # most recent first
    }
    if remote_only:
        params["f_WT"] = "2"
    jobs = []
    for page in range(int(jc.get("max_pages_per_query", 3))):
        params["start"] = page * PAGE_SIZE
        try:
            r = requests.get(LI_SEARCH, params={k: v for k, v in params.items() if v != ""}, headers=UA, timeout=30)
        except requests.RequestException as e:
            print(f"[jobs] network error searching '{role}' @ {location}: {type(e).__name__}; skipping")
            break
        if r.status_code == 429:
            print("[jobs] LinkedIn is rate-limiting; stopping this run early.")
            raise RateLimited()
        if r.status_code != 200:
            print(f"[jobs] LinkedIn search '{role}' @ {location}: HTTP {r.status_code}")
            break
        cards = BeautifulSoup(r.text, "html.parser").select("li")
        for card in cards:
            root = card.select_one("[data-entity-urn]")
            title = card.select_one(".base-search-card__title")
            if not (root and title):
                continue
            job_id = root["data-entity-urn"].rsplit(":", 1)[-1]
            company = card.select_one(".base-search-card__subtitle")
            loc = card.select_one(".job-search-card__location")
            posted = card.select_one("time")
            jobs.append({
                "source": "linkedin",
                "external_id": job_id,
                "title": title.get_text(strip=True),
                "company": company.get_text(strip=True) if company else "",
                "location": loc.get_text(strip=True) if loc else location,
                "url": f"https://www.linkedin.com/jobs/view/{job_id}/",
                "posted_at": posted.get("datetime", "") if posted else "",
                "work_mode": "Remote" if remote_only else "",
            })
        if len(cards) < PAGE_SIZE:
            break
        _pause()
    return jobs


class RateLimited(Exception):
    pass


def _linkedin_details(job_id: str) -> dict:
    try:
        r = requests.get(LI_DETAIL.format(id=job_id), headers=UA, timeout=30)
    except requests.RequestException as e:
        print(f"[jobs] network error fetching job {job_id}: {type(e).__name__}; saved without details")
        return {}
    if r.status_code == 429:
        raise RateLimited()
    if r.status_code != 200:
        return {}
    s = BeautifulSoup(r.text, "html.parser")

    def pick(sel: str) -> str:
        node = s.select_one(sel)
        return node.get_text(" ", strip=True) if node else ""

    criteria = {}
    for item in s.select(".description__job-criteria-item"):
        h, v = item.select_one("h3"), item.select_one("span")
        if h and v:
            criteria[h.get_text(strip=True).lower()] = v.get_text(strip=True)
    desc = s.select_one(".show-more-less-html__markup")
    company_link = s.select_one("a.topcard__org-name-link")
    apply = re.search(r'<code id="applyUrl"[^>]*><!--"(.*?)"-->', r.text)
    return {
        "description": desc.get_text("\n", strip=True) if desc else "",
        "seniority": criteria.get("seniority level", ""),
        "employment_type": criteria.get("employment type", ""),
        "industries": criteria.get("industries", ""),
        "job_function": criteria.get("job function", ""),
        "applicants": pick(".num-applicants__caption"),
        "salary": pick(".compensation__salary") or pick(".salary"),
        "posted_ago": pick(".posted-time-ago__text"),
        "company_url": company_link["href"].split("?")[0] if company_link else "",
        "apply_url": apply.group(1).replace("\\u0026", "&") if apply else "",
    }


def _remotive(role: str) -> list[dict]:
    try:
        r = requests.get("https://remotive.com/api/remote-jobs", params={"search": role, "limit": 30}, timeout=30)
    except requests.RequestException as e:
        print(f"[jobs] Remotive network error: {type(e).__name__}")
        return []
    if r.status_code != 200:
        print(f"[jobs] Remotive '{role}': HTTP {r.status_code}")
        return []
    cutoff = datetime.now(TZ) - timedelta(days=7)
    jobs = []
    for j in r.json().get("jobs", []):
        try:
            published = datetime.fromisoformat(j["publication_date"]).replace(tzinfo=TZ)
        except (KeyError, ValueError):
            published = None
        if published and published < cutoff:
            continue
        jobs.append({
            "source": "remotive",
            "external_id": str(j["id"]),
            "title": j.get("title", ""),
            "company": j.get("company_name", ""),
            "location": j.get("candidate_required_location") or "Anywhere",
            "url": j.get("url", ""),
            "posted_at": j.get("publication_date", ""),
            "description": _text(j.get("description", "")),
            "employment_type": (j.get("job_type") or "").replace("_", " ").title(),
            "salary": j.get("salary", ""),
            "work_mode": "Remote",
        })
    return jobs


def tech_stack(text: str) -> str:
    low = text.lower()
    return ", ".join(name for name, pattern in TECH.items() if re.search(pattern, low))


def experience_required(text: str) -> str:
    m = re.search(r"(\d{1,2})\s*(?:\+|-|–|to)?\s*(\d{1,2})?\s*\+?\s*(?:years?|yrs?)", text, re.I)
    if not m:
        return ""
    return f"{m.group(1)}-{m.group(2)} yrs" if m.group(2) else f"{m.group(1)}+ yrs"


def work_mode(job: dict) -> str:
    if job.get("work_mode"):
        return job["work_mode"]
    text = f"{job['title']} {job['location']} {job.get('description', '')[:1500]}".lower()
    for mode in ("remote", "hybrid"):
        if mode in text:
            return mode.title()
    if re.search(r"on-?site|in-office|work from office", text):
        return "On-site"
    return ""


def _passes_keywords(job: dict) -> bool:
    jc = CFG["jobs"]
    title = job["title"].lower()
    haystack = f"{title}\n{job.get('description', '')}".lower()
    if any(x.lower() in title for x in jc.get("exclude", [])):
        return False
    must = [m.lower() for m in jc.get("must_have_any", [])]
    return not must or any(re.search(rf"\b{re.escape(m)}\b", haystack) for m in must)


FIELDS = ["source", "external_id", "title", "company", "location", "url", "posted_at", "description",
          "seniority", "employment_type", "industries", "job_function", "applicants", "salary", "posted_ago",
          "company_url", "apply_url", "tech_stack", "experience", "work_mode", "status", "found_at"]


def collect(conn) -> int:
    """Fetches new postings into the DB. Returns how many were new."""
    jc = CFG["jobs"]
    found: list[dict] = []
    try:
        if jc["sources"].get("linkedin_public"):
            for role in jc["roles"]:
                for loc in jc["locations"]:
                    found += _linkedin_search(role, loc, remote_only=False)
                    _pause()
                if jc.get("remote"):
                    found += _linkedin_search(role, jc.get("remote_location", "India"), remote_only=True)
                    _pause()
        if jc["sources"].get("remotive"):
            for role in jc["roles"]:
                found += _remotive(role)
    except RateLimited:
        pass

    new, seen = 0, set()
    for job in found:
        key = (job["source"], job["external_id"])
        if key in seen or conn.execute(
            "SELECT 1 FROM jobs WHERE source = ? AND external_id = ?", key
        ).fetchone():
            continue
        seen.add(key)
        if new >= jc.get("max_new_per_run", 80):
            break
        if job["source"] == "linkedin":
            try:
                job.update(_linkedin_details(job["external_id"]))
            except RateLimited:
                print("[jobs] rate-limited while fetching details; saving what we have.")
                break
            _pause()
        full = f"{job['title']}\n{job.get('description', '')}"
        job["tech_stack"] = tech_stack(full)
        job["experience"] = experience_required(job.get("description", ""))
        job["work_mode"] = work_mode(job)
        job["status"] = "new" if _passes_keywords(job) else "filtered"
        job["found_at"] = now()
        conn.execute(
            f"INSERT OR IGNORE INTO jobs({', '.join(FIELDS)}) VALUES({', '.join('?' * len(FIELDS))})",
            [job.get(f, "") for f in FIELDS],
        )
        conn.commit()  # commit per job: never hold the DB write lock across slow network calls
        new += 1
    conn.commit()
    return new


class JobScore(BaseModel):
    job_id: int
    score: int
    verdict: Literal["strong", "possible", "weak"]
    reasons: str
    red_flags: str


class JobScores(BaseModel):
    scores: list[JobScore]


def score(conn) -> int:
    if not CFG["jobs"].get("ai_scoring", True):
        return 0
    rows = conn.execute("SELECT * FROM jobs WHERE status = 'new' ORDER BY id").fetchall()
    if not rows:
        return 0
    jc = CFG["jobs"]
    system = (
        "You screen job and internship postings for one candidate and score how well each fits, "
        "0-100. Be honest: penalise seniority mismatches, required skills the candidate lacks, "
        "and location/visa constraints. Never assume the candidate has a skill that isn't in "
        "their profile or resume. Keep reasons to one short sentence.\n\n"
        f"<candidate>\n{knowledge.candidate_profile()}\n</candidate>\n\n"
        f"Target roles: {', '.join(jc['roles'])}. Types: {', '.join(jc['types'])}. "
        f"Locations: {', '.join(jc['locations'])}{' + remote' if jc.get('remote') else ''}."
    )
    def run_batch(batch) -> JobScores | None:
        prompt = "Score each posting. Return one entry per job_id.\n\n" + "\n\n".join(
            f"<job job_id=\"{r['id']}\">\nTitle: {r['title']}\nCompany: {r['company']}\n"
            f"Location: {r['location']}\nSeniority: {r['seniority'] or '?'} · Type: {r['employment_type'] or '?'}\n"
            f"Description:\n{r['description'] or '(not available)'}\n</job>"
            for r in batch
        )
        try:
            return llm.structured(system, prompt, JobScores, CFG["llm"]["effort_scoring"])
        except llm.LLMError as e:
            print(f"[jobs] a scoring batch failed (those jobs stay unscored): {e}")
            return None

    batches = [rows[i : i + 6] for i in range(0, len(rows), 6)]
    scored = 0
    with ThreadPoolExecutor(max_workers=int(jc.get("scoring_parallel", 4))) as pool:
        for result in pool.map(run_batch, batches):
            for s in result.scores if result else []:
                cur = conn.execute(
                    "UPDATE jobs SET score = ?, verdict = ?, reasons = ?, status = 'scored' WHERE id = ? AND status = 'new'",
                    (max(0, min(100, s.score)), s.verdict, f"{s.reasons} Red flags: {s.red_flags or 'none'}", s.job_id),
                )
                scored += cur.rowcount
            conn.commit()
    return scored


def notify_matches(conn) -> int:
    min_score = CFG["jobs"]["min_score"]
    rows = conn.execute(
        "SELECT * FROM jobs WHERE status = 'scored' AND score >= ? ORDER BY score DESC", (min_score,)
    ).fetchall()
    conn.execute("UPDATE jobs SET status = 'notified' WHERE status = 'scored' AND score >= ?", (min_score,))
    conn.execute("UPDATE jobs SET status = 'low-fit' WHERE status = 'scored'")
    conn.commit()
    if not rows:
        return 0
    strong = sum(r["verdict"] == "strong" for r in rows)
    lines = [
        f"{r['score']} · {r['title']} — {r['company']} ({r['location']})\n   {r['url']}"
        for r in rows
    ]
    notify.send(
        f"🎯 {len(rows)} new job match{'es' if len(rows) != 1 else ''} ({strong} strong)",
        "\n\n".join(lines) + f"\n\nAll jobs are in {sheet.path().name}",
    )
    return len(rows)


def search(conn) -> dict:
    set_kv(conn, "last_job_search", now())
    new = collect(conn)
    added = sheet.sync(conn)  # rows appear right away; fit scores are filled in below
    scored = score(conn)
    sheet.sync(conn)
    sent = notify_matches(conn)
    return {"new": new, "scored": scored, "added_to_sheet": added, "notified": sent}


class CoverLetter(BaseModel):
    letter: str
    fit_summary: str
    gaps_to_address: list[str]


def cover_letter(conn, job_id: int) -> str:
    j = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    if j is None:
        raise ValueError(f"No job #{job_id}.")
    system = (
        "You write short, specific cover letters (under 250 words) in the candidate's own plain, "
        "human voice. Use only experience that appears in the candidate profile/resume — never "
        "invent projects, numbers, employers or skills. No clichés like 'I am excited to apply'.\n\n"
        f"<candidate>\n{knowledge.candidate_profile()}\n</candidate>"
    )
    prompt = (
        f"Job: {j['title']} at {j['company']} ({j['location']})\n{j['url']}\n\n"
        f"Description:\n{j['description'] or '(not available — keep the letter general to the role)'}"
    )
    c = llm.structured(system, prompt, CoverLetter, CFG["llm"]["effort_writing"])
    out_dir = DATA_DIR / "letters"
    out_dir.mkdir(exist_ok=True)
    text = (
        f"# {j['title']} — {j['company']}\n{j['url']}\n\n{c.letter}\n\n---\nFit: {c.fit_summary}\n"
        + ("Gaps to address: " + "; ".join(c.gaps_to_address) if c.gaps_to_address else "")
    )
    (out_dir / f"job_{job_id}.md").write_text(text)
    return text
