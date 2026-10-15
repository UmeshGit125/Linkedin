import json
import sqlite3
from datetime import datetime

from .config import DATA_DIR, TZ

SCHEMA = """
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY,
    created_at TEXT NOT NULL,
    slot TEXT NOT NULL,              -- tofu | mofu | authority
    post_type TEXT,
    topic TEXT,
    hook TEXT,
    body TEXT NOT NULL,
    hashtags TEXT,
    first_comment TEXT,              -- prepared text, or NULL when not needed
    why TEXT,
    source TEXT,
    originality TEXT,
    confidence TEXT,
    status TEXT NOT NULL,            -- draft | ready | blocked | approved | published | rejected | failed
    verification TEXT,               -- JSON from the verification gate
    scheduled_for TEXT,
    published_at TEXT,
    linkedin_urn TEXT,
    metrics TEXT,                    -- JSON, entered after publishing
    error TEXT
);
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY,
    source TEXT NOT NULL,
    external_id TEXT NOT NULL,
    title TEXT NOT NULL,
    company TEXT,
    location TEXT,
    url TEXT,
    posted_at TEXT,
    description TEXT,
    score INTEGER,
    verdict TEXT,
    reasons TEXT,
    status TEXT NOT NULL,            -- new | filtered | scored | notified | interested | applied | interview | rejected | ignored
    found_at TEXT NOT NULL,
    UNIQUE(source, external_id)
);
CREATE TABLE IF NOT EXISTS comment_drafts (
    id INTEGER PRIMARY KEY,
    created_at TEXT NOT NULL,
    target_url TEXT,
    target_author TEXT,
    target_text TEXT NOT NULL,
    worth_commenting INTEGER,
    comment TEXT,
    reasoning TEXT,
    status TEXT NOT NULL             -- drafted | posted | skipped
);
CREATE TABLE IF NOT EXISTS watchlist (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    url TEXT,
    added_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS kv (key TEXT PRIMARY KEY, value TEXT);
"""


def now() -> str:
    return datetime.now(TZ).isoformat(timespec="seconds")


# Columns added after the first release; created on existing databases automatically.
JOB_EXTRA_COLUMNS = [
    "seniority TEXT", "employment_type TEXT", "industries TEXT", "job_function TEXT", "applicants TEXT",
    "salary TEXT", "posted_ago TEXT", "company_url TEXT", "apply_url TEXT", "tech_stack TEXT",
    "experience TEXT", "work_mode TEXT", "in_sheet INTEGER NOT NULL DEFAULT 0", "score_in_sheet INTEGER NOT NULL DEFAULT 0",
    "match_in_sheet INTEGER NOT NULL DEFAULT 0",
]


POST_EXTRA_COLUMNS = ["image_prompt TEXT", "alt_text TEXT", "image_path TEXT", "parent_id INTEGER"]
COMMENT_EXTRA_COLUMNS = ["options TEXT"]


def _migrate(conn, table: str, columns: list[str]) -> None:
    existing = {r["name"] for r in conn.execute(f"PRAGMA table_info({table})")}
    for col in columns:
        if col.split()[0] not in existing:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {col}")


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DATA_DIR / "assistant.db", timeout=30)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    _migrate(conn, "jobs", JOB_EXTRA_COLUMNS)
    _migrate(conn, "posts", POST_EXTRA_COLUMNS)
    _migrate(conn, "comment_drafts", COMMENT_EXTRA_COLUMNS)
    conn.commit()
    return conn


def get_kv(conn, key: str, default=None):
    row = conn.execute("SELECT value FROM kv WHERE key = ?", (key,)).fetchone()
    return json.loads(row["value"]) if row else default


def set_kv(conn, key: str, value) -> None:
    conn.execute(
        "INSERT INTO kv(key, value) VALUES(?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, json.dumps(value)),
    )
    conn.commit()
