"""Official LinkedIn API: OAuth sign-in and publishing posts as you.

Uses only the "Share on LinkedIn" (w_member_social) and OpenID Connect products,
which LinkedIn grants self-serve to any developer app. No scraping, no browser bot.
"""
import json
import re
import secrets
import time
import webbrowser
from datetime import date
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlencode, urlparse

import requests

from .config import DATA_DIR, env

AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
USERINFO_URL = "https://api.linkedin.com/v2/userinfo"
POSTS_URL = "https://api.linkedin.com/rest/posts"
REDIRECT_URI = "http://localhost:8765/callback"
SCOPES = "openid profile w_member_social"
TOKEN_FILE = DATA_DIR / "linkedin_token.json"


class LinkedInError(RuntimeError):
    pass


def _api_version() -> str:
    """LinkedIn's versioned API wants YYYYMM; versions retire after ~1 year, so use two months back."""
    if env("LINKEDIN_API_VERSION"):
        return env("LINKEDIN_API_VERSION")
    d = date.today()
    month = d.month - 2
    year = d.year + (month - 1) // 12
    month = (month - 1) % 12 + 1
    return f"{year}{month:02d}"


def authorize() -> dict:
    client_id, client_secret = env("LINKEDIN_CLIENT_ID"), env("LINKEDIN_CLIENT_SECRET")
    if not (client_id and client_secret):
        raise LinkedInError("Set LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET in .env first.")

    state = secrets.token_urlsafe(16)
    result: dict = {}

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            qs = parse_qs(urlparse(self.path).query)
            result.update({k: v[0] for k, v in qs.items()})
            ok = "code" in qs and qs.get("state", [""])[0] == state
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            msg = "Signed in. You can close this tab." if ok else "Sign-in failed. Check the terminal."
            self.wfile.write(f"<h2>{msg}</h2>".encode())

        def log_message(self, *args):
            pass

    url = AUTH_URL + "?" + urlencode(
        {"response_type": "code", "client_id": client_id, "redirect_uri": REDIRECT_URI, "state": state, "scope": SCOPES}
    )
    print(f"Opening LinkedIn sign-in in your browser. If it doesn't open, visit:\n{url}\n")
    webbrowser.open(url)
    server = HTTPServer(("localhost", 8765), Handler)
    server.timeout = 300
    server.handle_request()
    server.server_close()

    if result.get("state") != state or "code" not in result:
        raise LinkedInError(f"Sign-in did not complete: {result.get('error_description') or result or 'timed out'}")

    r = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "authorization_code",
            "code": result["code"],
            "redirect_uri": REDIRECT_URI,
            "client_id": client_id,
            "client_secret": client_secret,
        },
        timeout=30,
    )
    if r.status_code != 200:
        raise LinkedInError(f"Token exchange failed ({r.status_code}): {r.text}")
    tok = r.json()

    me = requests.get(USERINFO_URL, headers={"Authorization": f"Bearer {tok['access_token']}"}, timeout=30)
    if me.status_code != 200:
        raise LinkedInError(f"Could not read your profile ({me.status_code}): {me.text}")
    info = me.json()

    saved = {
        "access_token": tok["access_token"],
        "expires_at": int(time.time()) + int(tok.get("expires_in", 0)),
        "person_urn": f"urn:li:person:{info['sub']}",
        "name": info.get("name", ""),
    }
    TOKEN_FILE.write_text(json.dumps(saved, indent=2))
    TOKEN_FILE.chmod(0o600)
    return saved


def token() -> dict:
    if not TOKEN_FILE.exists():
        raise LinkedInError("Not connected to LinkedIn yet. Run: uv run assistant auth")
    tok = json.loads(TOKEN_FILE.read_text())
    if tok["expires_at"] < time.time():
        raise LinkedInError("LinkedIn sign-in expired (tokens last 60 days). Run: uv run assistant auth")
    return tok


def days_until_expiry() -> int | None:
    if not TOKEN_FILE.exists():
        return None
    return int((json.loads(TOKEN_FILE.read_text())["expires_at"] - time.time()) // 86400)


# Characters that LinkedIn's "little text" format treats as markup in post commentary.
# Unescaped, they silently truncate or mangle the published post.
_RESERVED = re.compile(r"([\\|{}@\[\]()<>#*_~])")
_HASHTAG = re.compile(r"(?<![\w#])#(\w+)")


def to_commentary(body: str, hashtags: list[str]) -> str:
    def escape(segment: str) -> str:
        return _RESERVED.sub(r"\\\1", segment)

    out, last = [], 0
    for m in _HASHTAG.finditer(body):
        out.append(escape(body[last : m.start()]))
        out.append("{hashtag|\\#|" + m.group(1) + "}")
        last = m.end()
    out.append(escape(body[last:]))
    text = "".join(out).rstrip()

    tags = [t.lstrip("#").strip() for t in hashtags if t.strip()]
    tags = [t for t in tags if f"#{t}".lower() not in body.lower()]
    if tags:
        text += "\n\n" + " ".join("{hashtag|\\#|" + t + "}" for t in tags)
    return text


def publish(body: str, hashtags: list[str]) -> str:
    """Publishes a text post. Returns the post URN (urn:li:share:... / urn:li:ugcPost:...)."""
    tok = token()
    payload = {
        "author": tok["person_urn"],
        "commentary": to_commentary(body, hashtags),
        "visibility": "PUBLIC",
        "distribution": {"feedDistribution": "MAIN_FEED", "targetEntities": [], "thirdPartyDistributionChannels": []},
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    }
    r = requests.post(
        POSTS_URL,
        headers={
            "Authorization": f"Bearer {tok['access_token']}",
            "LinkedIn-Version": _api_version(),
            "X-Restli-Protocol-Version": "2.0.0",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=30,
    )
    if r.status_code != 201:
        raise LinkedInError(f"LinkedIn rejected the post ({r.status_code}): {r.text}")
    urn = r.headers.get("x-restli-id", "")
    if not urn:
        raise LinkedInError("LinkedIn accepted the post but returned no post id — check your profile.")
    return urn


def post_url(urn: str) -> str:
    return f"https://www.linkedin.com/feed/update/{urn}/"
