"""
Single-cycle runner for GitHub Actions.
Fetches jobs, enriches with real description, filters US Tax only,
sends to Telegram with actual job info (not generic defaults).
AI-powered extraction via Google Gemini Flash (free tier).
"""
import json
import os
import re
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import config
from scraper import fetch_all_jobs, SESSION
from sender import send_job

# ── Gemini AI setup (optional — graceful fallback if key not set) ─────
GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")
_gemini_model = None

def _get_gemini():
    global _gemini_model
    if _gemini_model:
        return _gemini_model
    if not GEMINI_KEY:
        return None
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_KEY)
        _gemini_model = genai.GenerativeModel("gemini-2.0-flash")
        return _gemini_model
    except Exception as e:
        print(f"[AI] Gemini init failed: {e}")
        return None

SEEN_FILE = "seen_jobs.json"

# ── US Tax relevance filter ───────────────────────────────────────────
US_TAX_TERMS = re.compile(
    r"\b("
    r"us\s*tax(ation)?|u\.s\.?\s*tax|united\s*states\s*tax|"
    r"us\s*income\s*tax|us\s*federal\s*tax|"
    r"1040|1041|1120|1065|990|5500|1099|W-2|W2|"
    r"form\s*10(40|41|20|65|99)|"
    r"irs|internal\s*revenue|federal\s*tax|state\s*tax\s*returns?|"
    r"individual\s*tax(ation)?|corporate\s*tax(ation)?|"
    r"fiduciary\s*tax(ation)?|partnership\s*tax(ation)?|"
    r"tax\s*prep(arer|aration)|tax\s*e.?fil|"
    r"tax\s*compliance|tax\s*analyst|tax\s*consultant|"
    r"tax\s*reviewer|tax\s*associate|tax\s*advisor|"
    r"tax\s*software|tax\s*schema|tax\s*business\s*rules|"
    r"tax\s*sme|tax\s*subject\s*matter|"
    r"direct\s*tax|tax\s*returns?"
    r")\b",
    re.IGNORECASE,
)

BLOCKLIST = re.compile(
    r"\b("
    r"recruiter|recruitment|talent\s*acquisition|bench\s*sales|"
    r"us\s*it\s*recruiter|it\s*recruiter|"
    r"software\s*engineer(?!\s*tax)|software\s*developer(?!\s*tax)|"
    r"selenium|automation\s*tester|manual\s*tester|"
    r"\bgst\b|\bvat\b|goods\s*and\s*services\s*tax|"
    r"payroll(?!\s*tax)|accounts\s*payable|accounts\s*receivable|"
    r"statutory\s*audit|business\s*development|sales\s*executive"
    r")\b",
    re.IGNORECASE,
)


def is_us_tax_job(job):
    title = job.get("title", "")
    desc  = job.get("description", "")
    full  = f"{title} {desc}"
    if not US_TAX_TERMS.search(full):
        return False
    if BLOCKLIST.search(title):
        return False
    return True


# ── Fetch real job description ────────────────────────────────────────
def enrich_job(job):
    """
    Fetch the actual job description from the job page.
    Supports LinkedIn guest API. Falls back to existing description.
    """
    # Skip if already has good description
    if job.get("description") and len(job["description"]) > 300:
        return job

    url    = job.get("url", "")
    source = job.get("source", "")

    try:
        if "linkedin.com" in url:
            # Extract LinkedIn job ID from URL
            match = re.search(r'/(\d{8,})', url)
            if match:
                jid        = match.group(1)
                detail_url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{jid}"
                r = SESSION.get(detail_url, timeout=12)
                if r.status_code == 200:
                    soup = BeautifulSoup(r.content, "html.parser")
                    # Full description div
                    desc_div = (
                        soup.find("div", class_=re.compile(r"show-more-less-html|description__text")) or
                        soup.find("section", class_=re.compile(r"description"))
                    )
                    if desc_div:
                        job["description"] = desc_div.get_text(" ", strip=True)[:2000]

                    # Try to extract experience from criteria
                    criteria = soup.find_all("span", class_=re.compile(r"description__job-criteria-text"))
                    for i, c in enumerate(criteria):
                        text = c.get_text(strip=True)
                        if re.search(r"year|experience|mid|senior|entry", text, re.IGNORECASE):
                            if not job.get("experience") or len(job["experience"]) < 3:
                                job["experience"] = text

        elif "naukri.com" in url:
            r = SESSION.get(url, timeout=12)
            if r.status_code == 200:
                soup = BeautifulSoup(r.content, "html.parser")
                desc_div = soup.find("div", class_=re.compile(r"job-desc|jobDescription|dang-inner-html"))
                if desc_div:
                    job["description"] = desc_div.get_text(" ", strip=True)[:2000]

    except Exception as e:
        print(f"  [Enrich] {source} error: {e}")

    time.sleep(1.5)
    return job


# ── AI enrichment (Gemini Flash — free 1500 req/day) ─────────────────
def ai_enrich_job(job):
    """Use Gemini Flash to extract real job info from actual description."""
    model = _get_gemini()
    if not model:
        return job

    title = job.get("title", "")
    desc  = job.get("description", "")

    # Only use AI if we have a real description to work with
    if not desc or len(desc) < 100:
        return job

    prompt = f"""You are a job posting analyst. Extract info from this US Tax job posting.

Job Title: {title}
Job Description: {desc[:2500]}

Return ONLY a valid JSON object — no markdown, no explanation:
{{
  "responsibilities": ["point 1", "point 2", "point 3", "point 4", "point 5"],
  "skills": "skill1, skill2, skill3, skill4, skill5",
  "experience": "X-Y Years in US Tax / specific area",
  "qualification": "degree or certification required",
  "is_us_tax_job": true
}}

Rules:
- responsibilities: 5 specific bullets copied from this actual job (not generic)
- skills: extract real tools/knowledge (e.g. 1040, CCH, ProSeries, IRS, XML)
- experience: exact years from the description, or infer from seniority level
- qualification: B.Com / CA / CPA / MBA etc. from description
- is_us_tax_job: true if job involves US federal/state tax forms or IRS compliance"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()

        # Strip markdown code fences if Gemini wraps in ```json ... ```
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.strip()

        data = json.loads(text)

        if data.get("responsibilities"):
            job["_responsibilities"] = [r for r in data["responsibilities"] if r][:5]
        if data.get("skills"):
            job["_skills"] = data["skills"]
        if data.get("experience"):
            job["_experience"] = data["experience"]
        if data.get("qualification"):
            job["_qualification"] = data["qualification"]
        # Let AI override the US Tax filter if it says false
        if data.get("is_us_tax_job") is False:
            job["_ai_rejected"] = True

        log(f"  [AI] Enriched: {title[:55]}")

    except Exception as e:
        log(f"  [AI] Skipped '{title[:45]}': {e}")

    time.sleep(1)   # respect Gemini free-tier rate limit (15 RPM)
    return job


# ── Description parsers ───────────────────────────────────────────────
def extract_section(desc, *headers):
    """Extract bullet points under a section header from job description."""
    for header in headers:
        pattern = re.compile(
            rf"{header}\s*:?\s*\n(.*?)(?=\n[A-Z][^\n]{{3,}}:|\Z)",
            re.IGNORECASE | re.DOTALL
        )
        match = pattern.search(desc)
        if match:
            block = match.group(1)
            lines = [l.strip().lstrip("•·-–*▪►") .strip()
                     for l in re.split(r"[\n•·\|]", block) if len(l.strip()) > 20]
            if lines:
                return lines[:5]
    return []


def extract_experience(desc, title):
    """Extract years of experience from description."""
    # Look for patterns like "3+ years", "2-5 years", "minimum 3 years"
    patterns = [
        r"(\d+\+?\s*(?:to|-)\s*\d*\+?\s*years?\s*(?:of\s*)?(?:experience|exp)?[^\n.]*)",
        r"((?:minimum|min\.?|atleast|at\s*least)\s*\d+\+?\s*years?[^\n.]*)",
        r"(\d+\+?\s*years?\s*(?:of\s*)?(?:relevant\s*)?experience[^\n.]*)",
    ]
    for p in patterns:
        m = re.search(p, desc, re.IGNORECASE)
        if m:
            return m.group(1).strip()[:100]

    # Fallback based on title
    t = title.lower()
    if any(x in t for x in ["senior", "manager", "lead"]):
        return "5+ Years (US Tax)"
    elif any(x in t for x in ["associate", "junior", "jr"]):
        return "1-2 Years (US Tax)"
    return "2-5 Years (US Tax)"


def extract_skills(desc, title, raw_skills):
    """Extract skills from description."""
    if raw_skills and len(raw_skills) > 15:
        return raw_skills

    # Look for skills section in description
    skills_section = extract_section(desc,
        "skills", "required skills", "key skills",
        "technical skills", "qualifications", "requirements"
    )
    if skills_section:
        return ", ".join(skills_section[:4])

    # Look for skill keywords in description
    skill_terms = re.findall(
        r"\b(1040|1041|1120|1065|990|5500|"
        r"US Tax|IRS|federal tax|state tax|"
        r"tax software|MS Excel|QuickBooks|Lacerte|ProSeries|"
        r"CCH|GoSystem|UltraTax|Drake|"
        r"XML|XSD|e-file|ATS testing|"
        r"tax compliance|tax research|CPA|EA)\b",
        desc, re.IGNORECASE
    )
    if skill_terms:
        unique = list(dict.fromkeys([s.strip() for s in skill_terms]))
        return ", ".join(unique[:6])

    # Fallback
    t = title.lower()
    if any(x in t for x in ["preparer", "preparation"]):
        return "US Tax preparation, 1040/1041/1065/1120, Tax software, MS Excel"
    elif any(x in t for x in ["analyst", "compliance"]):
        return "US Tax, Federal/State regulations, IRS, Tax compliance, MS Excel"
    elif any(x in t for x in ["software", "testing", "qa"]):
        return "US Tax knowledge, Tax software, XML/XSD, ATS testing, QA"
    return "US Tax, Tax compliance, MS Excel, Analytical skills"


def extract_responsibilities(desc, title):
    """Extract actual responsibilities from description."""
    if desc and len(desc) > 100:
        # Try to find responsibilities section
        bullets = extract_section(desc,
            "responsibilities", "roles and responsibilities",
            "key responsibilities", "job responsibilities",
            "duties", "what you will do", "your role"
        )
        if bullets:
            return bullets

        # If no section found, split desc into meaningful sentences
        sents = [s.strip() for s in re.split(r"[.\n•·\|–-]", desc)
                 if len(s.strip()) > 35 and not re.match(r'^[\d\s,/-]+$', s.strip())]
        if len(sents) >= 3:
            return sents[:5]

    # Fallback by role
    t = title.lower()
    if any(x in t for x in ["preparer", "preparation"]):
        return [
            "Prepare US individual and business tax returns (1040, 1041, 1065, 1120)",
            "Collect client financial data and ensure accuracy of tax filings",
            "Ensure compliance with IRS and state tax regulations",
            "Research tax issues and advise on minimizing tax liability",
            "Track filing deadlines and maintain complete tax records",
        ]
    elif any(x in t for x in ["reviewer", "review"]):
        return [
            "Review US tax returns (1040, 1041, 1120, 1065) for accuracy and compliance",
            "Identify errors and discrepancies in tax filings",
            "Ensure all returns meet IRS and state filing requirements",
            "Provide feedback and guidance to preparers",
            "Maintain quality standards across all reviewed returns",
        ]
    elif any(x in t for x in ["analyst", "compliance", "regulatory"]):
        return [
            "Analyze US federal and state tax law changes and assess their impact",
            "Prepare and submit ATS test scenarios to state tax authorities",
            "Coordinate with development teams on regulatory updates",
            "Monitor IRS and state agency announcements for changes",
            "Support compliance with US federal and state tax requirements",
        ]
    elif any(x in t for x in ["software", "testing", "qa", "e-file", "efile"]):
        return [
            "Test US tax software for 1040, 1041, 1065, 1120 form accuracy",
            "Validate tax calculations against IRS rules and state requirements",
            "Create and execute test scenarios for e-file and print submissions",
            "Identify and report defects, coordinate fixes with development",
            "Support government agency approvals and ATS acceptance testing",
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


def extract_qualification(desc, title):
    """Extract qualification from description."""
    qual_match = re.search(
        r"(B\.?Com|B\.?Tech|MBA|CA|CPA|EA|Bachelor|Master|Graduate|Post.?Graduate)"
        r"[^\n.]{0,80}",
        desc, re.IGNORECASE
    )
    if qual_match:
        return qual_match.group(0).strip()[:120]

    t = title.lower()
    if any(x in t for x in ["senior", "manager", "lead"]):
        return "Graduate / Post-Graduate (Accounting / Finance / Commerce)"
    elif any(x in t for x in ["software", "developer"]):
        return "B.Com / B.Tech / BCA (Computer / Accounting preferred)"
    return "Graduate / Post-Graduate (Accounting / Finance preferred)"


# ── Seen jobs ─────────────────────────────────────────────────────────
def load_seen():
    if os.path.exists(SEEN_FILE):
        try:
            with open(SEEN_FILE, "r") as f:
                return set(json.load(f))
        except Exception:
            pass
    return set()


def save_seen(seen_set):
    data = list(seen_set)[-5000:]
    with open(SEEN_FILE, "w") as f:
        json.dump(data, f)


def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}")


# ── Main ──────────────────────────────────────────────────────────────
def main():
    log("=" * 50)
    log("US Tax Jobs Bot — Single Cycle")
    log("=" * 50)

    if not config.BOT_TOKEN:
        log("ERROR: BOT_TOKEN not set.")
        return
    if not config.CHAT_ID:
        log("ERROR: CHAT_ID not set.")
        return

    seen = load_seen()
    log(f"Loaded {len(seen)} previously seen jobs.")

    try:
        jobs = fetch_all_jobs()
    except Exception as e:
        log(f"Scrape error: {e}")
        return

    # Filter: US Tax relevant only
    us_tax_jobs = [j for j in jobs if is_us_tax_job(j)]
    log(f"US Tax relevant: {len(us_tax_jobs)} out of {len(jobs)} total.")

    # AUTO SEED: first run — mark all as seen, send nothing
    if len(seen) == 0 and len(us_tax_jobs) > 0:
        log("First run — seeding baseline. No messages sent.")
        for job in us_tax_jobs:
            seen.add(job["id"])
        save_seen(seen)
        log(f"Baseline set: {len(seen)} jobs. Next cycle sends only NEW jobs.")
        return

    # New jobs only
    new_jobs = [j for j in us_tax_jobs if j["id"] not in seen]
    log(f"New jobs to send: {len(new_jobs)}")

    if not new_jobs:
        log("No new US Tax jobs this cycle.")
        save_seen(seen)
        return

    # Enrich each new job with real description before sending
    use_ai = bool(GEMINI_KEY)
    log(f"Fetching real job descriptions... (AI {'ON' if use_ai else 'OFF — set GEMINI_API_KEY to enable'})")
    enriched = []
    for job in new_jobs:
        # Step 1: fetch actual description from LinkedIn
        job = enrich_job(job)
        desc  = job.get("description", "")
        title = job.get("title", "")

        # Step 2: AI extraction (uses real desc → accurate results)
        if use_ai:
            job = ai_enrich_job(job)

        # Step 3: regex fallback for any fields AI didn't fill
        if not job.get("_responsibilities"):
            job["_responsibilities"] = extract_responsibilities(desc, title)
        if not job.get("_skills"):
            job["_skills"]           = extract_skills(desc, title, job.get("skills", ""))
        if not job.get("_experience"):
            job["_experience"]       = extract_experience(desc, title)
        if not job.get("_qualification"):
            job["_qualification"]    = extract_qualification(desc, title)

        # Step 4: drop jobs AI flagged as not US Tax related
        if job.get("_ai_rejected"):
            log(f"  [AI] Rejected (not US Tax): {title}")
            seen.add(job["id"])   # mark seen so we don't recheck
            continue

        enriched.append(job)

    sent = 0
    for job in enriched:
        try:
            ok = send_job(job)
            if ok:
                seen.add(job["id"])
                sent += 1
                log(f"  Sent: [{job['source']}] {job['title']} @ {job['company']}")
            else:
                log(f"  Failed: {job['title']}")
        except Exception as e:
            log(f"  Error: {e}")

    save_seen(seen)
    log(f"Done. Sent {sent} new jobs. Total tracked: {len(seen)}")


if __name__ == "__main__":
    main()
