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


def send(title: str, message: str, telegram: bool = True) -> list[str]:
    """Sends through every enabled channel. Returns the channels that delivered."""
    opts, sent = CFG.get("notify", {}), []
    if opts.get("desktop", True):
        _desktop(title, message)
        sent.append("desktop")
    for name, fn in (("telegram", _telegram), ("email", _email)):
        if name == "telegram" and not telegram:
            continue
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


# ---- Telegram with buttons (used by the bot, the daily draft and job cards) -------------------

def btn(text: str, data: str) -> dict:
    return {"text": text, "callback_data": data}


def link(text: str, url: str) -> dict:
    return {"text": text, "url": url}


def tg_api(method: str, timeout: int = 30, **payload) -> dict:
    token = env("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set in .env.")
    r = requests.post(f"https://api.telegram.org/bot{token}/{method}", json=payload, timeout=timeout)
    data = r.json() if r.content else {}
    if not data.get("ok"):
        raise RuntimeError(f"Telegram {method} failed: {data.get('description') or r.status_code}")
    return data["result"]


def tg_send(text: str, buttons: list[list[dict]] | None = None) -> None:
    """Plain-text message to your chat; long text is split and the buttons go on the last piece."""
    chat_id = env("TELEGRAM_CHAT_ID")
    pieces = [text[i : i + 3900] for i in range(0, len(text), 3900)] or [""]
    for i, piece in enumerate(pieces):
        payload = {"chat_id": chat_id, "text": piece or "(empty)", "disable_web_page_preview": True}
        if buttons and i == len(pieces) - 1:
            payload["reply_markup"] = {"inline_keyboard": buttons}
        tg_api("sendMessage", **payload)


def tg_photo(path: str, caption: str = "") -> None:
    token = env("TELEGRAM_BOT_TOKEN")
    with open(path, "rb") as f:
        r = requests.post(
            f"https://api.telegram.org/bot{token}/sendPhoto",
            data={"chat_id": env("TELEGRAM_CHAT_ID"), "caption": caption[:1000]},
            files={"photo": f},
            timeout=60,
        )
    if r.status_code != 200:
        raise RuntimeError(f"Telegram sendPhoto failed: {r.text[:200]}")


def tg_clear_buttons(chat_id, message_id) -> None:
    try:
        tg_api("editMessageReplyMarkup", chat_id=chat_id, message_id=message_id, reply_markup={"inline_keyboard": []})
    except RuntimeError:
        pass


def tg_answer(callback_id: str, text: str = "") -> None:
    try:
        tg_api("answerCallbackQuery", callback_query_id=callback_id, text=text)
    except RuntimeError:
        pass


def send_job_card(j) -> None:
    lines = [
        f"🎯 {j['score']} · {j['title']}" + ("  [Y Combinator]" if j["source"] == "yc" else ""),
        f"{j['company']} — {j['location']}" + (f" · {j['work_mode']}" if j["work_mode"] else ""),
    ]
    if j["source"] == "yc" and j["industries"]:
        lines.append(j["industries"])
    if j["salary"]:
        lines.append(f"Pay: {j['salary']}")
    if j["tech_stack"]:
        lines.append(f"Stack: {j['tech_stack']}")
    if j["experience"]:
        lines.append(f"Experience: {j['experience']}")
    if j["reasons"]:
        lines.append(f"\n{j['reasons'][:500]}")
    tg_send("\n".join(lines), job_buttons(j))


def job_buttons(j) -> list[list[dict]]:
    return [
        [link("Open & apply ↗", j["apply_url"] or j["url"])],
        [btn("📝 Cover letter", f"jc:{j['id']}"), btn("📄 Tailor resume", f"jr:{j['id']}")],
        [btn("✅ Applied", f"ja:{j['id']}"), btn("🙈 Skip", f"jx:{j['id']}")],
    ]


def job_marked_buttons(j) -> list[list[dict]]:
    """After Applied/Skip: keep the link and offer Undo, so a mis-tap never loses anything."""
    return [[link("Open job ↗", j["apply_url"] or j["url"]), btn("↩ Undo", f"ju:{j['id']}")]]
