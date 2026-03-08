"""
Telegram sender — formats and sends job posts to the channel.
"""
import requests
import re
import time
from datetime import datetime, date
import config

API = f"https://api.telegram.org/bot{config.BOT_TOKEN}"


def _escape(text):
    """Escape Telegram Markdown v1 special characters."""
    if not text:
        return ""
    for ch in ["_", "*", "`", "["]:
        text = text.replace(ch, f"\\{ch}")
    return text


def _post(text, chat_id=None):
    cid = chat_id or config.CHAT_ID
    if not cid:
        print("[Telegram] CHAT_ID not set.")
        return False
    try:
        r = requests.post(
            f"{API}/sendMessage",
            json={
                "chat_id":                  cid,
                "text":                     text,
                "parse_mode":               "Markdown",
                "disable_web_page_preview": False,
            },
            timeout=15,
        )
        if r.status_code == 200:
            return True

        # Fallback: plain text
        r2 = requests.post(
            f"{API}/sendMessage",
            json={
                "chat_id":                  cid,
                "text":                     re.sub(r"[*_`\[\]]", "", text),
                "disable_web_page_preview": False,
            },
            timeout=15,
        )
        return r2.status_code == 200

    except Exception as e:
        print(f"[Telegram] Send error: {e}")
        return False


def _urgency_tag(posted):
    """Return urgency label based on posting date."""
    if not posted:
        return ""
    try:
        posted_date = date.fromisoformat(str(posted)[:10])
        delta = (date.today() - posted_date).days
        if delta == 0:
            return "🔴 *URGENT — Posted Today!*\n"
        elif delta == 1:
            return "🟡 *Posted Yesterday*\n"
    except Exception:
        pass
    return ""



def _qualification(title):
    t = title.lower()
    if any(x in t for x in ["senior", "manager", "lead"]):
        return "Graduate / Post-Graduate (Accounting / Finance / Commerce)"
    elif any(x in t for x in ["software", "programmer", "developer"]):
        return "B.Com / B.Tech / BCA (Computer / Accounting preferred)"
    else:
        return "Graduate / Post-Graduate (Accounting / Finance preferred)"


def _experience(title, raw_exp):
    if raw_exp and len(raw_exp) > 2:
        return raw_exp
    t = title.lower()
    if any(x in t for x in ["senior", "manager", "lead"]):
        return "5+ Years (US Tax / Accounting)"
    elif any(x in t for x in ["associate", "junior", "jr"]):
        return "1-2 Years (US Tax / Accounting)"
    else:
        return "2-5 Years (US Tax / Accounting)"


def format_job(job):
    title   = job.get("title", "")
    company = job.get("company", "")
    loc     = job.get("location", "India / Remote")
    url     = job.get("url", "")
    source  = job.get("source", "")
    posted  = job.get("posted", "")

    qual   = job.get("_qualification") or _qualification(title)
    exp    = job.get("_experience")    or _experience(title, job.get("experience", ""))
    salary = job.get("_salary", "")

    # Location formatting
    if "remote" in loc.lower():
        loc_str = f"{loc} (Remote)"
    elif "hyderabad" in loc.lower():
        loc_str = "Hyderabad (Hybrid)"
    else:
        loc_str = loc

    safe_company = _escape(company)
    safe_title   = _escape(title)
    safe_loc     = _escape(loc_str)
    safe_qual    = _escape(qual)
    safe_exp     = _escape(exp)

    lines = []

    # Urgency tag
    urgency = _urgency_tag(posted)
    if urgency:
        lines.append(urgency.strip())
        lines.append("")

    # Header
    lines += [
        f"🔥 *Job Opportunity at {safe_company}*",
        "",
        f"💼 *Role:* {safe_title}",
        f"📍 *Location:* {safe_loc}",
        f"🎓 *Qualification:* {safe_qual}",
        f"👨‍💻 *Experience:* {safe_exp}",
    ]

    # Salary (if mentioned)
    if salary and salary.lower() not in ("not mentioned", ""):
        lines.append(f"💰 *Salary:* {_escape(salary)}")

    lines += [
        "",
        f"🔗 *Apply Here:*\n{url}",
    ]
    if source:
        lines.append(f"\n📋 _{_escape(source)}_")

    return "\n".join(lines)


def send_job(job):
    msg = format_job(job)
    ok  = _post(msg)
    if ok:
        time.sleep(2)
    return ok


def send_daily_summary(stats):
    """Send daily summary at 9 AM IST."""
    today    = stats.get("date", date.today().isoformat())
    sent     = stats.get("sent", 0)
    companies = stats.get("companies", {})

    lines = [
        "📊 *US Tax Jobs — Daily Summary*",
        f"📅 {today}",
        "",
        f"✅ *Jobs sent today:* {sent}",
        f"🏢 *Companies hired:* {len(companies)}",
    ]

    if companies:
        top = sorted(companies.items(), key=lambda x: x[1], reverse=True)[:5]
        lines.append("\n🏆 *Top Companies:*")
        for co, cnt in top:
            lines.append(f"  • {_escape(co)} — {cnt} job{'s' if cnt > 1 else ''}")

    lines += [
        "",
        "⏱ Bot checks every *10 minutes*",
        f"🕐 {datetime.now().strftime('%d %b %Y %H:%M IST')}",
    ]

    _post("\n".join(lines))


def send_and_pin_welcome():
    """
    Send a welcome/intro message to the channel and pin it.
    Call once — after that it stays pinned permanently.
    Requires the bot to have 'Pin Messages' admin permission.
    """
    msg = (
        "👋 *Welcome to US Tax Jobs India\\!*\n\n"
        "🎯 This channel posts *fresh US Tax job openings* every 10 minutes — "
        "automatically sourced from LinkedIn, Big 4 firms and top IT/BPO companies\\.\n\n"
        "💼 *Roles we cover:*\n"
        "• US Tax Preparer / Reviewer\n"
        "• Tax Analyst / Compliance Analyst\n"
        "• Tax Consultant / Associate\n"
        "• Tax Software / QA / E\\-file roles\n"
        "• Senior / Manager US Tax roles\n\n"
        "📍 *Locations:* Hyderabad, Bangalore, Chennai, Remote & more\n\n"
        "🔔 *Turn on notifications* so you never miss a job\\!\n\n"
        "✅ Good luck with your job search\\! 🚀"
    )

    api = f"https://api.telegram.org/bot{config.BOT_TOKEN}"

    # Step 1 — send the message
    try:
        r = requests.post(
            f"{api}/sendMessage",
            json={
                "chat_id":                  config.CHAT_ID,
                "text":                     msg,
                "parse_mode":               "MarkdownV2",
                "disable_web_page_preview": True,
            },
            timeout=15,
        )
        if r.status_code != 200:
            print(f"[Pin] Failed to send welcome message: {r.text}")
            return False

        message_id = r.json()["result"]["message_id"]
        print(f"[Pin] Welcome message sent (id={message_id})")

    except Exception as e:
        print(f"[Pin] Send error: {e}")
        return False

    # Step 2 — pin it (disable_notification=True so no alert spam)
    try:
        r2 = requests.post(
            f"{api}/pinChatMessage",
            json={
                "chat_id":              config.CHAT_ID,
                "message_id":          message_id,
                "disable_notification": True,
            },
            timeout=15,
        )
        if r2.status_code == 200:
            print(f"[Pin] Welcome message pinned successfully.")
            return True
        else:
            print(f"[Pin] Pin failed: {r2.text}")
            return False

    except Exception as e:
        print(f"[Pin] Pin error: {e}")
        return False


def send_fail_alert(error_msg=""):
    """Send alert if bot encounters a critical error."""
    msg = (
        "❌ *US Tax Jobs Bot — Error*\n\n"
        f"Something went wrong:\n`{_escape(str(error_msg)[:200])}`\n\n"
        "Please check GitHub Actions logs.\n"
        f"🕐 {datetime.now().strftime('%d %b %Y %H:%M')}"
    )
    _post(msg)
