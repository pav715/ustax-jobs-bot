"""
Telegram sender — formats and sends job posts to the channel.
"""
import requests
import re
import time
from datetime import datetime
import config

API = f"https://api.telegram.org/bot{config.BOT_TOKEN}"


def _escape(text):
    """Escape Telegram Markdown special characters in plain text fields."""
    if not text:
        return ""
    # Escape chars that break Telegram Markdown v1
    for ch in ["_", "*", "`", "["]:
        text = text.replace(ch, f"\\{ch}")
    return text


def _post(text):
    if not config.CHAT_ID:
        print("[Telegram] CHAT_ID not set.")
        return False
    try:
        # Try Markdown first
        r = requests.post(
            f"{API}/sendMessage",
            json={
                "chat_id":                  config.CHAT_ID,
                "text":                     text,
                "parse_mode":               "Markdown",
                "disable_web_page_preview": False,
            },
            timeout=15,
        )
        if r.status_code == 200:
            return True

        # Fallback: send as plain text if Markdown fails (e.g. parse error)
        r2 = requests.post(
            f"{API}/sendMessage",
            json={
                "chat_id":                  config.CHAT_ID,
                "text":                     re.sub(r"[*_`\[\]]", "", text),
                "disable_web_page_preview": False,
            },
            timeout=15,
        )
        return r2.status_code == 200

    except Exception as e:
        print(f"[Telegram] Send error: {e}")
        return False


def _responsibilities(title, desc):
    """Extract from actual job description first, fall back to role-based defaults."""
    t = title.lower()

    # Use actual job description if it has enough content
    if desc and len(desc) > 80:
        sents = [s.strip() for s in re.split(r'[.\n•\|\-–]', desc) if len(s.strip()) > 30]
        sents = [s for s in sents if not re.match(r'^[\d\s,/-]+$', s)]
        if len(sents) >= 3:
            return sents[:5]

    # Role-based defaults — order matters (specific first)
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
    elif any(x in t for x in ["reviewer", "review"]):
        return [
            "Review US tax returns (1040, 1041, 1120, 1065) for accuracy and compliance",
            "Identify errors and discrepancies in tax filings",
            "Ensure all returns meet IRS and state filing requirements",
            "Provide feedback and guidance to tax preparers",
            "Maintain quality standards across all reviewed returns",
        ]
    elif any(x in t for x in ["analyst", "compliance", "regulatory"]):
        return [
            "Analyze US federal and state tax law changes and assess their impact",
            "Prepare and submit ATS test scenarios to US state tax authorities",
            "Coordinate with development teams to implement regulatory updates",
            "Monitor IRS and state agency announcements for changes",
            "Support compliance with US federal and state tax requirements",
        ]
    elif any(x in t for x in ["programmer", "developer", "software", "filing"]):
        return [
            "Develop and maintain US federal/state tax form software modules",
            "Analyze EF schema and business rule changes for print and e-file",
            "Liaise with government agencies to obtain annual form approvals",
            "Troubleshoot and resolve production issues in tax software",
            "Update XML schemas and business rules for compliance",
        ]
    elif any(x in t for x in ["senior", "manager", "lead"]):
        return [
            "Lead and mentor a team of US tax professionals",
            "Oversee tax compliance, preparation and quality review processes",
            "Review complex tax returns and regulatory submissions",
            "Manage relationships with IRS and state tax authorities",
            "Drive process improvements across tax operations",
        ]
    else:
        return [
            "Handle US tax preparation and compliance activities",
            "Review and validate tax returns (1040, 1041, 1065, 1120)",
            "Ensure accurate and timely filings per federal and state regulations",
            "Coordinate with clients and internal teams on tax matters",
            "Support e-file processes and IRS/state authority submissions",
        ]


def _skills(title, raw_skills):
    if raw_skills and len(raw_skills) > 10:
        return raw_skills
    t = title.lower()
    if any(x in t for x in ["qa", "quality", "testing", "e-file"]):
        return "US Tax knowledge, QA testing, XML/HTML, Analytical skills"
    elif any(x in t for x in ["preparer", "preparation"]):
        return "US Tax preparation, 1040/1041/1065/1120, Tax software, MS Excel"
    elif any(x in t for x in ["software", "programmer", "developer"]):
        return "Tax software, XML/XSD schemas, ATS testing, US Tax regulations"
    elif any(x in t for x in ["analyst", "compliance"]):
        return "US Tax, Federal/State regulations, IRS, Tax compliance, MS Excel"
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
    desc    = job.get("description", "")

    # Use real enriched fields from run_once.py if available, else fallback
    bullets = job.get("_responsibilities") or _responsibilities(title, desc)
    skills  = job.get("_skills")          or _skills(title, job.get("skills", ""))
    qual    = job.get("_qualification")   or _qualification(title)
    exp     = job.get("_experience")      or _experience(title, job.get("experience", ""))

    # Location formatting
    if "remote" in loc.lower():
        loc_str = f"{loc} (Remote)"
    elif "hyderabad" in loc.lower():
        loc_str = "Hyderabad (Hybrid)"
    else:
        loc_str = loc

    # Escape dynamic text to prevent Markdown breakage
    safe_company = _escape(company)
    safe_title   = _escape(title)
    safe_loc     = _escape(loc_str)
    safe_qual    = _escape(qual)
    safe_exp     = _escape(exp)
    safe_skills  = _escape(skills)

    lines = [
        f"🔥 *Job Opportunity at {safe_company}*",
        "",
        f"💼 *Role:* {safe_title}",
        f"📍 *Location:* {safe_loc}",
        f"🎓 *Qualification:* {safe_qual}",
        f"👨‍💻 *Experience:* {safe_exp}",
        "",
        "📌 *Roles & Responsibilities:*",
    ]
    for b in bullets:
        lines.append(f"• {_escape(b)}")
    lines += [
        "",
        f"🧠 *Skills:* {safe_skills}",
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


def send_startup_message(keyword_count, location_count):
    msg = (
        "🤖 *US Tax Jobs Bot Started!*\n\n"
        f"🔍 Monitoring *{keyword_count}* keywords\n"
        "📋 Forms: *1040, 1041, 1065, 1120, 990, 5500*\n"
        "💼 Roles: *Tax QA, E-File, Preparer, Analyst, Compliance*\n"
        f"📍 Locations: *Hyderabad, Bangalore, Chennai, Kerala, Remote*\n"
        f"⏱ Checks every *5 minutes*\n"
        "📬 New jobs only — no duplicates\n\n"
        f"🕐 {datetime.now().strftime('%d %b %Y %H:%M')}"
    )
    _post(msg)
