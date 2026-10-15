"""Post images from an OpenAI-compatible image API (IMAGE_API_KEY / IMAGE_API_BASE / IMAGE_MODEL in .env)."""
import base64
from pathlib import Path

import requests

from .config import CFG, env

STYLE = (
    "Clean editorial illustration for a professional LinkedIn post about applied AI. "
    "Flat, modern, calm colour palette, lots of whitespace. No text, no letters, no logos, "
    "no real people or faces, no charts with invented numbers. Subject: "
)


def enabled() -> bool:
    return bool(env("IMAGE_API_KEY"))


def generate(prompt: str, out_path: Path) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cfg = CFG.get("image", {})
    r = requests.post(
        env("IMAGE_API_BASE", "https://api.openai.com/v1").rstrip("/") + "/images/generations",
        headers={"Authorization": f"Bearer {env('IMAGE_API_KEY')}"},
        json={"model": env("IMAGE_MODEL", "gpt-image-1"), "prompt": STYLE + prompt, "size": cfg.get("size", "1024x1024"), "n": 1},
        timeout=int(cfg.get("timeout_seconds", 180)),
    )
    if r.status_code != 200:
        raise RuntimeError(f"Image API error {r.status_code}: {r.text[:300]}")
    item = r.json()["data"][0]
    if item.get("b64_json"):
        out_path.write_bytes(base64.b64decode(item["b64_json"]))
    elif item.get("url"):
        img = requests.get(item["url"], timeout=60)
        img.raise_for_status()
        out_path.write_bytes(img.content)
    else:
        raise RuntimeError("Image API returned neither image data nor a URL.")
    return out_path
