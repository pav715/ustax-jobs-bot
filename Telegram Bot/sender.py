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
    """Extract from actual job description first, fall back to role-based defaults."""
    t = title.lower()

    # Use actual job description if it has enough content
    if desc and len(desc) > 80:
        # Split by sentence endings, bullets, newlines
        sents = [s.strip() for s in re.split(r'[.\n•\|\-–]', desc) if len(s.strip()) > 30]
        # Filter out noise (very short fragments, just dates, just numbers)
        sents = [s for s in sents if not re.match(r'^[\d\s,/-]+$', s)]
        if len(sents) >= 3:
            return sents[:5]

    # Role-based defaults when no description available
    if any(x in t for x in ["qa", "quality", "e-file", "efile", "testing"]):
        return [
            "Perform QA testing for US tax software (1040, 1041, 1065, 1120 forms)",
            "Test tax calculations and validate software outputs against IRS rules",
            "Identify and report bugs, coordinate fixes with development teams",
            "Create test scenarios and support e-file approvals with US state agencies",
            "Ensure tax products meet compliance and quality standards",
        ]
    elif any(x in t for x in ["preparer", "preparation"]):
        return [
            "Prepare and review US individual/business tax returns (1040, 1041, 1065, 1120)",
            "Collect and organize client financial data for accurate tax filing",
            "Ensure all returns comply with US federal and state tax laws",
            "Research tax issues and advise on minimizing liabilities",
            "Maintain records of all filings and track deadlines",
        ]
    elif any(x in t for x in ["analyst", "compliance", "regulatory"]):
        return [
            "Analyze US federal and state tax law changes and assess software impact",
            "Prepare and submit ATS test scenarios to US state tax authorities",
            "Coordinate with development teams to implement regulatory updates",
            "Monitor IRS and state agency announcements for form and rule changes",
            "Support clients and internal teams on US tax compliance matters",
        ]
    elif any(x in t for x in ["programmer", "developer", "software", "filing"]):
        return [
            "Develop and maintain US federal/state tax form software modules",
            "Analyze EF schema and business rule changes for print and e-file",
            "Liaise with government agencies to obtain annual form approvals",
            "Troubleshoot and resolve production issues in tax software",
            "Update XML schemas and business rules for compliance",
        ]
    elif any(x in t for x in ["manager", "senior", "lead"]):
        return [
            "Lead and mentor a team of tax analysts and QA professionals",
            "Oversee US tax compliance, regulatory filing, and software processes",
            "Review and approve tax returns, test cases, and regulatory submissions",
            "Build and maintain relationships with US state tax authorities",
            "Drive continuous improvement in tax operations and processes",
        ]
    elif any(x in t for x in ["reviewer", "review"]):
        return [
            "Review US individual and business tax returns for accuracy (1040, 1041, 1120, 1065)",
            "Identify errors, discrepancies, and compliance issues in tax filings",
            "Provide feedback and guidance to tax preparers",
            "Ensure returns meet IRS and state filing requirements",
            "Maintain quality standards across all reviewed returns",
        ]
    else:
        return [
            "Handle US tax preparation and compliance activities",
            "Review and validate tax returns (1040, 1041, 1065, 1120)",
            "Ensure accurate and timely filings per US federal and state regulations",
            "Maintain tax documentation and coordinate with internal stakeholders",
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
