import smtplib
import subprocess
from email.message import EmailMessage

import requests

from .config import CFG, env


def _desktop(title: str, message: str) -> None:
    def q(s: str) -> str:
        return s.replace("\\", "\\\\").replace('"', '\\"')

    first_line = message.splitlines()[0] if message else ""
    script = f'display notification "{q(first_line[:200])}" with title "{q(title)}" sound name "Glass"'
    subprocess.run(["osascript", "-e", script], check=False, capture_output=True)


def _telegram(title: str, message: str) -> bool:
    token, chat_id = env("TELEGRAM_BOT_TOKEN"), env("TELEGRAM_CHAT_ID")
    if not (token and chat_id):
        return False
    text = f"{title}\n\n{message}"
    # Telegram caps messages at 4096 chars; send in pieces rather than dropping content.
    for i in range(0, len(text), 4000):
        r = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": text[i : i + 4000], "disable_web_page_preview": True},
            timeout=20,
        )
        r.raise_for_status()
    return True


def _email(title: str, message: str) -> bool:
    user, password, to = env("SMTP_USER"), env("SMTP_PASSWORD"), env("NOTIFY_EMAIL_TO")
    if not (user and password and to):
        return False
    msg = EmailMessage()
    msg["Subject"], msg["From"], msg["To"] = title, user, to
    msg.set_content(message)
    with smtplib.SMTP(env("SMTP_HOST", "smtp.gmail.com"), int(env("SMTP_PORT", "587"))) as s:
        s.starttls()
        s.login(user, password)
        s.send_message(msg)
    return True


def send(title: str, message: str) -> list[str]:
    """Sends through every enabled channel. Returns the channels that delivered."""
    opts, sent = CFG.get("notify", {}), []
    if opts.get("desktop", True):
        _desktop(title, message)
        sent.append("desktop")
    for name, fn in (("telegram", _telegram), ("email", _email)):
        if opts.get(name):
            try:
                if fn(title, message):
                    sent.append(name)
            except Exception as e:  # a broken channel must not stop the others
                print(f"[notify] {name} failed: {e}")
    return sent


def telegram_find_chat_id() -> str | None:
    token = env("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("Set TELEGRAM_BOT_TOKEN in .env first.")
    r = requests.get(f"https://api.telegram.org/bot{token}/getUpdates", timeout=20)
    r.raise_for_status()
    for update in reversed(r.json().get("result", [])):
        chat = (update.get("message") or {}).get("chat")
        if chat:
            return str(chat["id"])
    return None
