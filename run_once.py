"""Single-cycle runner for GitHub Actions — LinkedIn only. Updated: 2026-07-04"""
import json
import os
import re
import time
import sys
import requests
from bs4 import BeautifulSoup
from datetime import datetime, date, timedelta
import config

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
from scraper import fetch_all_jobs, SESSION
from sender import send_job, send_daily_summary, send_fail_alert

SEEN_FILE  = "seen_jobs.json"
STATS_FILE = "stats.json"
STATE_FILE = "bot_state.json"

US_TAX_KEYWORDS = [
    "us tax", "us taxation", "u.s. tax", "federal tax", "international tax",
    "cross border tax", "cross-border tax", "expat tax", "us expat",
    "form 1040", "form 1041", "form 1120", "form 1065", "form 990", "form 5500",
    "form 1120s", "form 1065", "schedule k-1", "schedule c", "schedule e", "schedule d",
    "w-2", "1099", "1099-r", "1099-int", "1099-div", "1099-misc",
    "irs", "dor", "tax preparation", "tax preparer", "tax return", "tax filing",
    "tax review", "tax reviewer", "tax compliance", "tax analyst", "tax associate",
    "tax consultant", "tax manager", "tax specialist", "tax advisor", "tax senior",
    "tax lead", "tax director", "tax executive", "tax preparer", "tax return preparer",
    "lacerte", "proseries", "ultratax", "drake tax", "cch axcess", "atx", "gosystem",
    "intuit", "turbotax", "h&r block", "enrolled agent", "cpa", "cpa tax",
    "state tax", "multi-state", "multi state", "state and local", "salt",
    "partnership tax", "corporate tax", "individual tax", "s corp", "c corp",
    "estate tax", "gift tax", "trust tax", "fiduciary", "nonprofit tax",
    "tax provision", "asc 740", "transfer pricing us", "us transfer pricing",
    "withholding tax", "payroll tax us", "sales tax us", "use tax",
    "tax technology", "tax software", "tax operations", "tax support",
    "remote tax", "virtual tax", "outsourced tax", "kpmg tax", "ey tax", "pwc tax", "deloitte tax",
]

INDIA_LOCATION_KEYWORDS = [
    "india", "hyderabad", "bangalore", "bengaluru", "chennai", "mumbai", "pune", "delhi",
    "gurgaon", "gurugram", "noida", "kolkata", "ahmedabad", "jaipur", "indore", "chandigarh",
    "kochi", "coimbatore", "lucknow", "visakhapatnam", "vizag",
]

FOREIGN_LOCATION_KEYWORDS = [
    "usa", "united states", "u.s.", "canada", "uk", "united kingdom", "australia", "europe",
    "egypt", "middle east", "africa", "singapore", "malaysia", "sweden", "sverige", "japan",
    "dubai", "germany", "france",
]

BLOCKLIST = re.compile(
    r"\b("
    r"recruiter|recruitment|talent\s*acquisition|bench\s*sales|"
    r"us\s*it\s*recruiter|it\s*recruiter|"
    r"software\s*engineer(?!\s*tax)|software\s*developer(?!\s*tax)|"
    r"selenium|automation\s*tester|manual\s*tester|"
    r"payroll(?!\s*tax)|accounts\s*payable|accounts\s*receivable|"
    r"statutory\s*audit|business\s*development|sales\s*executive|"
    # Indian tax roles - GST (1-10)
    r"\bgst\b|goods\s*and\s*services\s*tax|gstn|gst\s*compliance|gst\s*specialist|gst\s*manager|gst\s*consultant|gst\s*filing|gst\s*returns|gst\s*audit|gst\s*advisory|"
    # Income Tax India (11-20)
    r"income\s*tax\s*(?!withholding)|income\s*tax\s*consultant|income\s*tax\s*executive|"
    r"direct\s*tax(?!\s*analyst\s*(?:us|federal|state))|india\s*tax|domestic\s*tax|indian\s*tax|"
    # TDS / TCS (21-25)
    r"\btds\b|\btcs\b|tax\s*deducted|tax\s*collected|tds\s*analyst|tds\s*filing|"
    # Indirect Tax India (26-35)
    r"indirect\s*tax(?!\s*analyst\s*(?:us|federal))|"
    r"\bvat\b(?!\s*us)|service\s*tax|excise\s*duty|customs\s*duty|"
    r"transfer\s*pricing|tax\s*litigation|"
    # CA / Finance Related (36-45)
    r"chartered\s*accountant|ca\s*article|ca\s*analyst|"
    r"(?<!us\s)(?<!federal\s)finance\s*analyst(?!\s*us)|accounts\s*analyst|^accountant$|"
    r"financial\s*analyst(?!\s*(?:us|tax))|finance\s*executive|accounts\s*executive|"
    # Other Indian Tax (46-50)
    r"tax\s*auditor|statutory\s*compliance|tax\s*compliance\s*executive(?!\s*us)"
    r")\b",
    re.IGNORECASE,
)

# STRICT: Reject all Indian tax roles - no US Tax jobs should have these keywords
# Title match — US Tax roles (primary accept rule)
US_TAX_TITLE = re.compile(
    r"\b("
    r"u\.?\s*s\.?\s*tax(?:ation)?|us\s*tax(?:ation)?|"
    r"federal\s*tax|international\s*tax|cross[\s-]*border\s*tax|expat\s*tax|"
    r"us\s*corporate\s*tax|us\s*individual\s*tax|partnership\s*tax|"
    r"enrolled\s*agent|"
    r"(?:us|u\.s\.|federal)\s*tax\s*(?:analyst|associate|consultant|manager|senior|lead|specialist|advisor|preparer|reviewer|director|executive)|"
    r"tax\s*(?:analyst|associate|consultant|manager|senior|lead|specialist|advisor|preparer|reviewer|director|executive).{0,30}(?:us|u\.s\.|federal|international|expat)|"
    r"tax\s*prepar(?:er|ation)|tax\s*compliance|tax\s*review(?:er|ing)|"
    r"tax\s*return\s*prepar|cpa\s*(?:us\s*)?tax|tax\s*cpa|"
    r"lacerte|proseries|ultratax|drake\s*tax|h\s*&\s*r\s*block|"
    r"state\s*(?:and\s*)?local\s*tax|multi[\s-]*state\s*tax|salt\s*tax"
    r")\b",
    re.IGNORECASE,
)

INDIAN_TAX_BLOCKLIST = re.compile(
    r"\b("
    # GST Related (1-10)
    r"gst\s*analyst|gst\s*compliance|gst\s*executive|gst\s*specialist|gst\s*manager|"
    r"gst\s*consultant|gst\s*filing|gst\s*returns|gst\s*audit|gst\s*advisory|"
    # Income Tax India (11-20)
    r"income\s*tax\s*analyst|income\s*tax\s*consultant|income\s*tax\s*executive|"
    r"direct\s*tax\s*analyst|direct\s*tax\s*consultant|direct\s*tax\s*manager|"
    r"india\s*tax\s*analyst|india\s*tax\s*consultant|domestic\s*tax|"
    # TDS / TCS (21-25)
    r"tds\s*analyst|tds\s*compliance|tcs\s*analyst|tds\s*executive|tds\s*filing|"
    # Indirect Tax India (26-35)
    r"indirect\s*tax\s*analyst|indirect\s*tax\s*consultant|indirect\s*tax\s*manager|"
    r"vat\s*analyst|service\s*tax|excise\s*duty|customs\s*duty|"
    r"tax\s*litigation|indirect\s*tax\s*specialist|"
    # Other Indian Tax (46-50)
    r"tax\s*auditor|tax\s*litigation\s*specialist|transfer\s*pricing|"
    r"tax\s*compliance\s*executive|statutory\s*compliance|"
    # Keywords that indicate Indian context
    r"itr|itr-1|itr-2|itr-3|itr-4|itr-5|itr-6|itr-7|"
    r"form\s*16|form\s*16a|form\s*24q|"
    r"pan\s*number|aadhar|aadhaar|cin|gstin|"
    r"goods\s*and\s*services\s*tax|section\s*80|fy20[0-9]{2}|ay20[0-9]{2}|"
    r"tds|tcs|advance\s*tax|challan|saral|"
    r"indian\s*tax|india\s*tax|ato"
    r")\b",
    re.IGNORECASE,
)




def _keyword_hits(text, keywords):
    hits = []
    for kw in keywords:
        if len(kw) <= 4:
            if re.search(rf"\b{re.escape(kw)}\b", text):
                hits.append(kw)
        elif kw in text:
            hits.append(kw)
    return hits


def is_india_location(job):
    """Return True only for India on-site or India-tied remote jobs."""
    loc = (job.get("location") or "").lower()
    title = (job.get("title") or "").lower()

    if any(kw in loc for kw in FOREIGN_LOCATION_KEYWORDS):
        return False

    if any(kw in loc for kw in INDIA_LOCATION_KEYWORDS):
        return True

    if "remote" in loc:
        context = f"{loc} {title}"
        return "india" in context or any(kw in context for kw in INDIA_LOCATION_KEYWORDS)

    return False


def _passes_early_filter(title, company, role_title_pattern):
    title_l = (title or "").lower()
    company_l = (company or "").lower()
    if INDIAN_TAX_BLOCKLIST.search(title_l) or INDIAN_TAX_BLOCKLIST.search(company_l):
        return False
    if role_title_pattern.search(title_l):
        if BLOCKLIST.search(title_l) or BLOCKLIST.search(company_l):
            return False
        return True
    if BLOCKLIST.search(title_l) or BLOCKLIST.search(company_l):
        return False
    return True


def is_us_tax_job(job):
    """Accept US Tax titled roles first; then keyword match in full text."""
    desc = (job.get("description") or "").lower()
    title = (job.get("title") or "").lower()
    company = (job.get("company") or "").lower()
    blob = f"{title} {company} {desc}"

    if INDIAN_TAX_BLOCKLIST.search(title) or INDIAN_TAX_BLOCKLIST.search(company):
        return False

    if US_TAX_TITLE.search(title):
        if BLOCKLIST.search(title) or BLOCKLIST.search(company):
            return False
        print(f"DEBUG: '{job.get('title')}' @ {job.get('company')} matched: us tax title")
        return True

    if BLOCKLIST.search(blob):
        return False
    if INDIAN_TAX_BLOCKLIST.search(blob):
        return False

    matched = _keyword_hits(blob, US_TAX_KEYWORDS)
    if len(matched) >= 1:
        print(f"DEBUG: '{job.get('title')}' @ {job.get('company')} matched: {matched}")
        return True
    return False


def _mark_run_complete(state):
    state["last_run_at"] = datetime.utcnow().isoformat()
    save_state(state)


def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {"paused": False, "last_update_id": 0, "last_run_at": ""}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def load_stats():
    today = date.today().isoformat()
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE) as f:
                s = json.load(f)
            if s.get("date") == today:
                return s
        except Exception:
            pass
    return {"date": today, "sent": 0, "companies": {}, "summary_sent": False}


def save_stats(stats):
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f)


def load_seen():
    """Load seen job IDs. Handles [], {}, and corrupt files gracefully."""
    if os.path.exists(SEEN_FILE):
        try:
            with open(SEEN_FILE, "r") as f:
                data = json.load(f)
            if isinstance(data, list):
                return set(data)
            if isinstance(data, dict):
                return set(data.keys()) if data else set()
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


def _dedup_key(job):
    """Title+company fingerprint — blocks the same job even if LinkedIn
    gives it a new URL each scrape (prevents channel spam)."""
    title   = (job.get("title") or "").lower().strip()
    company = (job.get("company") or "").lower().strip()
    return f"{title}|{company}"


def handle_commands(state, stats):
    if not config.BOT_TOKEN:
        return state
    try:
        offset = state.get("last_update_id", 0) + 1
        r = requests.get(
            f"https://api.telegram.org/bot{config.BOT_TOKEN}/getUpdates",
            params={"offset": offset, "timeout": 5, "limit": 10},
            timeout=10,
        )
        if r.status_code != 200:
            return state

        updates = r.json().get("result", [])
        for update in updates:
            state["last_update_id"] = update["update_id"]
            msg = (update.get("message") or update.get("channel_post") or {})
            text = msg.get("text", "").strip().lower()
            chat_id = str(msg.get("chat", {}).get("id", ""))
            if not chat_id or chat_id != str(config.CHAT_ID):
                continue

            api = f"https://api.telegram.org/bot{config.BOT_TOKEN}/sendMessage"

            if text.startswith("/status"):
                reply = (
                    f"🤖 *US Tax Jobs Bot — Status*\n\n"
                    f"{'⏸ PAUSED' if state.get('paused') else '✅ RUNNING'}\n\n"
                    f"📊 *Today ({stats['date']}):*\n"
                    f"• Jobs sent: *{stats['sent']}*\n"
                    f"• Companies: *{len(stats['companies'])}*\n"
                    f"⏱ Checks every *{config.CHECK_INTERVAL_LABEL}*\n"
                    f"🕐 {datetime.now().strftime('%d %b %Y %H:%M IST')}"
                )
                requests.post(api, json={"chat_id": chat_id, "text": reply, "parse_mode": "Markdown"}, timeout=10)
            elif text == "/pause":
                state["paused"] = True
                requests.post(api, json={"chat_id": chat_id, "text": "⏸ *Bot paused.* Send /resume to restart.", "parse_mode": "Markdown"}, timeout=10)
            elif text == "/resume":
                state["paused"] = False
                requests.post(api, json={"chat_id": chat_id, "text": "▶️ *Bot resumed.* Notifications are back on.", "parse_mode": "Markdown"}, timeout=10)
            elif text == "/help":
                reply = "🤖 *Commands:*\n/status — Bot status\n/pause — Pause\n/resume — Resume\n/help — Help"
                requests.post(api, json={"chat_id": chat_id, "text": reply, "parse_mode": "Markdown"}, timeout=10)
    except Exception as e:
        log(f"[Commands] Error: {e}")
    return state


def enrich_job(job):
    """Fetch full job description from LinkedIn detail page."""
    if job.get("description") and len(job["description"]) > 300:
        return job
    url = job.get("url", "")
    fetched = False
    try:
        if "linkedin.com" in url:
            match = re.search(r'/(\d{8,})', url)
            if match:
                jid = match.group(1)
                detail_url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{jid}"
                r = SESSION.get(detail_url, timeout=12)
                if r.status_code == 200:
                    soup = BeautifulSoup(r.content, "html.parser")
                    desc_div = (
                        soup.find("div", class_=re.compile(r"show-more-less-html|description__text")) or
                        soup.find("section", class_=re.compile(r"description"))
                    )
                    if desc_div:
                        job["description"] = desc_div.get_text(" ", strip=True)[:2000]
                        fetched = True
                    criteria = soup.find_all("span", class_=re.compile(r"description__job-criteria-text"))
                    for c in criteria:
                        text = c.get_text(strip=True)
                        if re.search(r"year|experience|mid|senior|entry", text, re.IGNORECASE):
                            if not job.get("experience") or len(job["experience"]) < 3:
                                job["experience"] = text
    except Exception as e:
        log(f"  [Enrich] error: {e}")
    if fetched:
        time.sleep(1.0)
    return job


def extract_experience(desc, title):
    patterns = [
        r"(\d+\+?\s*(?:to|-)\s*\d*\+?\s*years?\s*(?:of\s*)?(?:experience|exp)?[^\n.]*)",
        r"((?:minimum|min\.?|atleast|at\s*least)\s*\d+\+?\s*years?[^\n.]*)",
        r"(\d+\+?\s*years?\s*(?:of\s*)?(?:relevant\s*)?experience[^\n.]*)",
    ]
    for p in patterns:
        m = re.search(p, desc, re.IGNORECASE)
        if m:
            return m.group(1).strip()[:100]
    t = title.lower()
    if any(x in t for x in ["senior", "manager", "lead"]):
        return "5+ Years (US Tax)"
    elif any(x in t for x in ["associate", "junior", "jr"]):
        return "1-2 Years (US Tax)"
    return "2-5 Years (US Tax)"


def extract_qualification(desc, title):
    qual_match = re.search(
        r"(B\.?Com|B\.?Tech|MBA|CA|CPA|EA|Bachelor|Master|Graduate|Post.?Graduate)[^\n.]{0,80}",
        desc, re.IGNORECASE,
    )
    if qual_match:
        return qual_match.group(0).strip()[:120]
    return "Graduate / Post-Graduate (Accounting / Finance preferred)"


def main():
    log("=" * 50)
    log("US Tax Jobs Bot — LinkedIn Only")
    log("=" * 50)

    if not config.BOT_TOKEN or not config.CHAT_ID:
        log("ERROR: BOT_TOKEN or CHAT_ID not set in environment.")
        sys.exit(1)

    log(f"BOT_TOKEN present: {len(config.BOT_TOKEN)} chars")
    log(f"CHAT_ID: {config.CHAT_ID}")

    state = load_state()
    stats = load_stats()

    state = handle_commands(state, stats)
    save_state(state)

    if state.get("paused"):
        log("Bot is PAUSED. Send /resume to restart.")
        return

    # Calculate time window: only fetch jobs since last run (+ 5 min buffer)
    last_run = state.get("last_run_at", "")
    if last_run:
        try:
            last_dt = datetime.fromisoformat(last_run)
            elapsed = (datetime.utcnow() - last_dt).total_seconds()
            since_seconds = int(elapsed) + 300  # add 5 min buffer
        except Exception:
            since_seconds = 2400  # fallback: 40 minutes
    else:
        since_seconds = 2400  # first run: 40 minutes

    # Cap: minimum 30 min, maximum 2 hours
    since_seconds = max(1800, min(since_seconds, 7200))

    log(f"Fetch window: {since_seconds // 60} minutes")

    seen = load_seen()
    log(f"Loaded {len(seen)} previously seen jobs.")

    try:
        jobs = fetch_all_jobs(since_seconds=since_seconds)
    except Exception as e:
        log(f"Scrape error: {e}")
        send_fail_alert(str(e))
        sys.exit(1)

    if os.environ.get("SEED_MODE", "").lower() == "true":
        for job in jobs:
            seen.add(_dedup_key(job))
        save_seen(seen)
        _mark_run_complete(state)
        log(f"Seed mode: marked {len(jobs)} jobs as seen, sent 0.")
        return

    print(f"DEBUG: Total jobs scraped: {len(jobs)}")
    log(f"Total jobs scraped: {len(jobs)}")

    india_jobs = [j for j in jobs if is_india_location(j)]
    log(f"India/Remote: {len(india_jobs)} out of {len(jobs)} total.")

    us_tax_jobs = []
    for job in india_jobs:
        if not _passes_early_filter(job.get("title"), job.get("company"), US_TAX_TITLE):
            continue
        job = enrich_job(job)
        if is_us_tax_job(job):
            us_tax_jobs.append(job)

    log(f"US Tax relevant: {len(us_tax_jobs)} out of {len(india_jobs)} India jobs.")

    new_jobs = [j for j in us_tax_jobs if _dedup_key(j) not in seen]
    new_jobs.sort(key=lambda j: str(j.get("posted") or j.get("fetched_at") or ""))
    log(f"New jobs to send: {len(new_jobs)}")

    if not new_jobs:
        log("No new US Tax jobs this cycle.")
        save_seen(seen)
        save_stats(stats)
        _mark_run_complete(state)
        return

    if len(new_jobs) > config.MAX_JOBS_PER_CYCLE:
        log(f"Capping to {config.MAX_JOBS_PER_CYCLE} jobs this cycle.")
        new_jobs = new_jobs[:config.MAX_JOBS_PER_CYCLE]

    sent = 0
    for job in new_jobs:
        desc  = job.get("description", "")
        title = job.get("title", "")
        if not job.get("_experience"):
            job["_experience"] = extract_experience(desc, title)
        if not job.get("_qualification"):
            job["_qualification"] = extract_qualification(desc, title)

        try:
            ok = send_job(job)
            if ok:
                seen.add(_dedup_key(job))
                sent += 1
                stats["sent"] += 1
                company = job.get("company", "Other")
                stats["companies"][company] = stats["companies"].get(company, 0) + 1
                log(f"  Sent: {job['title']} @ {job['company']}")
            else:
                log(f"  Failed: {job['title']}")
        except Exception as e:
            log(f"  Error: {e}")

    save_seen(seen)
    save_stats(stats)
    _mark_run_complete(state)
    log(f"Done. Sent {sent} new jobs. Today total: {stats['sent']}. Tracked: {len(seen)}")


if __name__ == "__main__":
    main()
