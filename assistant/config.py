import os
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
LOG_DIR = ROOT / "logs"

load_dotenv(ROOT / ".env")


def load() -> dict:
    with open(ROOT / "config.yaml") as f:
        cfg = yaml.safe_load(f)
    DATA_DIR.mkdir(exist_ok=True)
    LOG_DIR.mkdir(exist_ok=True)
    return cfg


CFG = load()
TZ = ZoneInfo(CFG.get("timezone", "Asia/Kolkata"))
DOCS_DIR = ROOT / CFG.get("docs_dir", "Docs")


def env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()
