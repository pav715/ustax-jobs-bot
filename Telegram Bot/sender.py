"""
Telegram sender — formats and sends job posts to the channel.
"""
import requests
import re
import time
from datetime import datetime
import config

API = f"https://api.telegram.org/bot{config.BOT_TOKEN}"


def _post(text):
    if not config.CHAT_ID:
        print("[Telegram] CHAT_ID not set.")
        return False
    try:
        r = requests.post(
            f"{API}/sendMessage",
            json={
                "chat_id":    config.CHAT_ID,
                "text":       text,
                "parse_mode": "Markdown",
                "disable_web_page_preview": False,
            },
            timeout=15,
        )
        return r.status_code == 200
    except Exception as e:
        print(f"[Telegram] Send error: {e}")
        return False


def _responsibilities(title, desc):
    """Pick role-specific bullet points based on job title."""
    t = title.lower()

    if desc:
        sents = [s.strip() for s in re.split(r'[.\n•\-]', desc) if len(s.strip()) > 25]
        if len(sents) >= 4:
            return sents[:5]

    # Role-based defaults
    if any(x in t for x in ["qa", "quality", "e-file", "efile", "testing"]):
        return [
            "Perform QA testing for US tax software (1040, 1041, 1065, 1120 forms)",
            "Test tax calculations and validate software outputs",
            "Identify and report bugs/issues and coordinate with developers",
            "Create test scenarios and support e-file approvals with US state agencies",
            "Ensure tax products meet compliance and quality standards",
        ]
    elif any(x in t for x in ["preparer", "preparation"]):
        return [
            "Prepare and file US individual/business tax returns (1040, 1041, 1065, 1120)",
            "Collect and organize financial information from clients",
            "Ensure all returns comply with US federal and state tax laws",
            "Provide strategic tax advice to minimize liabilities and maximize refunds",
            "Maintain detailed records of all tax filings and client interactions",
        ]
    elif any(x in t for x in ["analyst", "compliance", "regulatory"]):
        return [
            "Monitor US federal and state tax regulations for software impact",
            "Analyze and implement tax regulatory changes into software",
            "Prepare and submit ATS test scenarios to US state authorities",
            "Coordinate with development teams to align with government requirements",
            "Support users and clients on regulatory updates and tax filings",
        ]
    elif any(x in t for x in ["programmer", "developer", "software", "filing"]):
        return [
            "Develop and maintain US state/federal tax form software",
            "Analyze EF schema changes and create test scenarios for print/e-file",
            "Liaise with government agencies to obtain form approvals annually",
            "Troubleshoot and resolve bugs in production tax software",
            "Update and maintain XML schemas and business rules for tax compliance",
        ]
    elif any(x in t for x in ["manager", "senior", "lead"]):
        return [
            "Lead a team of tax analysts and QA specialists",
            "Oversee US tax compliance and regulatory filing processes",
            "Review and approve tax returns and software test cases",
            "Build relationships with US state tax authorities",
            "Drive process improvements and best practices in tax operations",
        ]
    else:
        return [
            "Handle US tax preparation and compliance activities",
            "Review and validate tax returns (1040, 1041, 1065, 1120)",
            "Ensure accurate and timely tax filings per US regulations",
            "Maintain tax documentation and coordinate with stakeholders",
            "Support e-file processes and government authority submissions",
        ]


def _skills(title, raw_skills):
    """Return relevant skills string."""
    if raw_skills and len(raw_skills) > 10:
        return raw_skills
    t = title.lower()
    if any(x in t for x in ["qa", "quality", "testing", "e-file"]):
        return "US Tax knowledge, QA testing, XML/HTML, analytical skills, good communication"
    elif any(x in t for x in ["preparer", "preparation"]):
        return "US Tax preparation, 1040/1041/1065/1120, Tax software, Client communication"
    elif any(x in t for x in ["software", "programmer", "developer"]):
        return "Tax software development, XML/XSD schemas, ATS testing, US Tax regulations"
    else:
        return "US Tax, Compliance, Tax software, Analytical skills, MS Excel"


def _qualification(title):
    t = title.lower()
    if any(x in t for x in ["senior", "manager", "lead"]):
        return "Graduate / Post-Graduate (Accounting / Finance / Commerce)"
    elif any(x in t for x in ["software", "programmer", "developer"]):
        return "B.Com / B.Tech / BCA (Computer / Accounting preferred)"
    else:
        return "Graduate / Post-Graduate (Accounting / Finance preferred)"


def _experience(title, raw_exp):
    if raw_exp and len(raw_exp) > 1:
        return raw_exp
    t = title.lower()
    if any(x in t for x in ["senior", "manager", "lead"]):
        return "5+ Years (US Tax / Accounting)"
    elif any(x in t for x in ["associate", "junior", "jr"]):
        return "1–2 Years (US Tax / Accounting)"
    else:
        return "2–5 Years (US Tax / Accounting)"


def format_job(job):
    title   = job.get("title", "")
    company = job.get("company", "")
    loc     = job.get("location", "India / Remote")
    url     = job.get("url", "")
    source  = job.get("source", "")
    posted  = job.get("posted", "")
    desc    = job.get("description", "")

    bullets  = _responsibilities(title, desc)
    skills   = _skills(title, job.get("skills", ""))
    qual     = _qualification(title)
    exp      = _experience(title, job.get("experience", ""))

    # Location formatting
    if "remote" in loc.lower():
        loc_str = f"{loc} (Remote)"
    elif "hyderabad" in loc.lower():
        loc_str = "Hyderabad (Hybrid)"
    else:
        loc_str = loc

    lines = [
        f"🔥 *Job Opportunity at {company}*",
        "",
        f"💼 *Role:* {title}",
        f"📍 *Location:* {loc_str}",
        f"🎓 *Qualification:* {qual}",
        f"👨‍💻 *Experience:* {exp}",
        "",
        "📌 *Roles & Responsibilities:*",
    ]
    for b in bullets:
        lines.append(f"• {b}")
    lines += [
        "",
        f"🧠 *Skills:* {skills}",
        f"🔗 *Apply Here:*\n{url}",
    ]
    if source:
        lines.append(f"\n📋 _{source}_")
    return "\n".join(lines)


def send_job(job):
    msg = format_job(job)
    ok  = _post(msg)
    if ok:
        time.sleep(2)
    return ok


def send_startup_message(keyword_count, location_count):
    msg = (
        "🤖 *US Tax Jobs Bot Started!*\n\n"
        f"🔍 Monitoring *{keyword_count}* keywords\n"
        "📋 Forms: *1040, 1041, 1065, 1120, 990, 5500*\n"
        "💼 Roles: *Tax QA, E-File, Preparer, Analyst, Software Testing*\n"
        f"📍 Locations: *Hyderabad, Bangalore, India, Remote*\n"
        f"⏱ Checks every *{config.CHECK_INTERVAL_MINUTES} minutes*\n"
        "📬 New jobs posted here instantly — newest first, no duplicates\n\n"
        f"🕐 {datetime.now().strftime('%d %b %Y %H:%M')}"
    )
    _post(msg)
