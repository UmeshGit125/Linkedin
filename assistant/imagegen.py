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


def provider() -> str:
    """IMAGE_PROVIDER = cloudflare | gemini | openai. Unset: guessed from IMAGE_API_BASE (older setups)."""
    p = env("IMAGE_PROVIDER").lower()
    if p:
        return p
    return "gemini" if "generativelanguage.googleapis.com" in env("IMAGE_API_BASE") else "openai"


def _cf_headers() -> dict:
    """An API token (Bearer) or, when CLOUDFLARE_API_EMAIL is set, the account's Global API Key."""
    key = env("CLOUDFLARE_API_TOKEN") or env("CLOUDFLARE_API_KEY")
    if env("CLOUDFLARE_API_EMAIL"):
        return {"X-Auth-Email": env("CLOUDFLARE_API_EMAIL"), "X-Auth-Key": key}
    return {"Authorization": f"Bearer {key}"}


def _cf_account() -> str:
    """CLOUDFLARE_ACCOUNT_ID, or the first account these credentials can see."""
    if env("CLOUDFLARE_ACCOUNT_ID"):
        return env("CLOUDFLARE_ACCOUNT_ID")
    r = requests.get("https://api.cloudflare.com/client/v4/accounts", headers=_cf_headers(), timeout=30)
    accounts = r.json().get("result") or [] if r.status_code == 200 else []
    if not accounts:
        raise RuntimeError(f"Cloudflare: could not find your account ({r.status_code}). Check CLOUDFLARE_API_KEY (and CLOUDFLARE_API_EMAIL if it is a Global API Key).")
    return accounts[0]["id"]


def enabled() -> bool:
    if provider() == "cloudflare":
        return bool(env("CLOUDFLARE_API_TOKEN") or env("CLOUDFLARE_API_KEY"))
    return bool(env("IMAGE_API_KEY"))


def _cloudflare(prompt: str, out_path: Path, timeout: int) -> Path:
    """Cloudflare Workers AI (free daily allowance). FLUX.1 schnell returns the image as base64 JSON."""
    model = env("CLOUDFLARE_IMAGE_MODEL", "@cf/black-forest-labs/flux-1-schnell")
    r = requests.post(
        f"https://api.cloudflare.com/client/v4/accounts/{_cf_account()}/ai/run/{model}",
        headers=_cf_headers(),
        json={"prompt": STYLE + prompt, "steps": 6},
        timeout=timeout,
    )
    if r.status_code != 200:
        raise RuntimeError(f"Cloudflare image error {r.status_code}: {r.text[:300]}")
    data = (r.json().get("result") or {}).get("image")
    if not data:
        raise RuntimeError("Cloudflare returned no image.")
    out_path.write_bytes(base64.b64decode(data))
    return out_path


def _gemini(prompt: str, out_path: Path, base: str, timeout: int) -> Path:
    """Google's native image call: Gemini image models answer generateContent with inline image data."""
    r = requests.post(
        f"{base.rstrip('/')}/models/{env('IMAGE_MODEL', 'gemini-2.5-flash-image')}:generateContent",
        headers={"x-goog-api-key": env("IMAGE_API_KEY")},
        json={"contents": [{"parts": [{"text": STYLE + prompt}]}], "generationConfig": {"responseModalities": ["IMAGE"]}},
        timeout=timeout,
    )
    if r.status_code != 200:
        raise RuntimeError(f"Image API error {r.status_code}: {r.text[:300]}")
    for cand in r.json().get("candidates", []):
        for part in cand.get("content", {}).get("parts", []):
            data = (part.get("inlineData") or part.get("inline_data") or {}).get("data")
            if data:
                out_path.write_bytes(base64.b64decode(data))
                return out_path
    raise RuntimeError("Gemini returned no image (it may have refused the prompt).")


def generate(prompt: str, out_path: Path) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cfg = CFG.get("image", {})
    base = env("IMAGE_API_BASE", "https://api.openai.com/v1")
    if provider() == "cloudflare":
        return _cloudflare(prompt, out_path, int(cfg.get("timeout_seconds", 180)))
    if provider() == "gemini":
        return _gemini(prompt, out_path, base, int(cfg.get("timeout_seconds", 180)))
    r = requests.post(
        base.rstrip("/") + "/images/generations",
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
