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

US_TAX_TERMS = re.compile(
    r"("
    r"\btax\b.*\b(analyst|consultant|preparer|associate|advisor|manager|accountant|specialist|reviewer|intern|senior)\b|"
    r"\b(analyst|consultant|preparer|associate|advisor|manager|accountant|specialist|reviewer|intern|senior)\b.*\btax\b|"
    r"us\s*tax(ation)?|u\.s\.?\s*tax|united\s*states?\s*tax|"
    r"us\s*income\s*tax|us\s*federal\s*tax|"
    r"1040|1041|1120|1065|990|5500|1099|w-?2|"
    r"form\s*10(40|41|20|65|99)|"
    r"irs|internal\s*revenue|federal\s*tax|state\s*tax|"
    r"individual\s*tax(ation)?|corporate\s*tax(ation)?|"
    r"fiduciary\s*tax(ation)?|partnership\s*tax(ation)?|"
    r"tax\s*prep(arer|aration)?|tax\s*e.?fil|"
    r"tax\s*compliance|tax\s*consultant|"
    r"tax\s*software|tax\s*sme|tax\s*subject|"
    r"international\s*tax(ation)?|expat(riate)?\s*tax|"
    r"enrolled\s*agent|cpa\s*(us\s*)?tax|"
    r"lacerte|proseries|proconnect|ultratax|drake|"
    r"tax\s*returns?|"
    r"tax\s*operations?\s*analyst|tax\s*documentation|"
    r"global\s*compliance|gcr\s*consultant|"
    r"indirect\s*tax|sales\s*tax|vat\s*tax|excise\s*tax|"
    r"m&a\s*tax|merger\s*acquisition\s*tax|"
    r"transfer\s*pricing|"
    r"tax\s*technology|tax\s*automation|"
    r"direct\s*tax|property\s*casualty\s*tax|"
    r"us\s*taxation|us\s*entity\s*tax|"
    r"cross.?border\s*tax|"
    r"tax\s*specialist|tax\s*compliance\s*analyst|"
    r"corporate\s*tax|personal\s*tax|payroll\s*specialist|"
    r"tax\s*supervisor|tax\s*audit\s*manager|lead\s*tax|"
    r"tax\s*director|director\s*of\s*tax|"
    r"vice\s*president.*tax|vp\s*tax|"
    r"salt\s*tax|state\s*local\s*tax|"
    r"irc\s*provisions|internal\s*revenue\s*code|"
    r"tax\s*planning|tax.?loss\s*harvesting|retirement\s*planning|"
    r"estate\s*gift\s*tax|trust\s*taxation|"
    r"payroll\s*tax|fica\s*tax|unemployment\s*tax|"
    r"multi.?state\s*tax|nexus\s*tax|"
    r"tax\s*provision|deferred\s*tax|asc\s*740|"
    r"audit\s*support|workpaper|"
    r"gaap|ifrs|accounting\s*standard|"
    r"turbotax|taxtact|cch\s*axcess|onesource|"
    r"quickbooks|sap\s*tax|oracle\s*netsuite|"
    r"tableau|power\s*bi|"
    r"rpa|robotic\s*process\s*automation|"
    r"tax\s*research|tax\s*statutes|tax\s*guidance|"
    r"strategic\s*advisory"
    r")",
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


USA_LOCATION = re.compile(
    r"\b(usa|united\s*states?|u\.s\.a?\.?|"
    r"new\s*york|california|texas|florida|illinois|washington\s*dc|"
    r"massachusetts|new\s*jersey|georgia|ohio|virginia|pennsylvania|"
    r"north\s*carolina|michigan|arizona|colorado|"
    r"\bNY\b|\bCA\b|\bTX\b|\bFL\b|\bIL\b|\bNJ\b|\bGA\b|\bMA\b|"
    r"\bOH\b|\bVA\b|\bPA\b|\bNC\b|\bMI\b|\bAZ\b|\bCO\b|\bDC\b)\b",
    re.IGNORECASE,
)

INDIA_LOCATION = re.compile(
    r"india|hyderabad|bangalore|bengaluru|chennai|mumbai|pune|"
    r"delhi|gurugram|gurgaon|noida|kerala|tamil|kolkata|"
    r"ahmedabad|nagpur|indore|jaipur|bhopal|lucknow|chandigarh|"
    r"bhubaneswar|kochi|coimbatore|visakhapatnam|thiruvananthapuram|"
    r"remote|work\s*from\s*home",
    re.IGNORECASE,
)


def is_india_job(job):
    """Return True only if job is in India — reject USA locations."""
    loc = job.get("location", "")
    if USA_LOCATION.search(loc):
        return False
    if INDIA_LOCATION.search(loc):
        return True
    if not loc or loc.strip() == "":
        return True
    return False


def is_us_tax_job(job):
    title = job.get("title", "")
    company = job.get("company", "")
    desc  = job.get("description", "")
    full  = f"{title} {company} {desc}"
    if not US_TAX_TERMS.search(full):
        return False
    if BLOCKLIST.search(title):
        return False
    return True


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
            if not chat_id:
                continue

            api = f"https://api.telegram.org/bot{config.BOT_TOKEN}/sendMessage"

            if text.startswith("/status"):
                reply = (
                    f"🤖 *US Tax Jobs Bot — Status*\n\n"
                    f"{'⏸ PAUSED' if state.get('paused') else '✅ RUNNING'}\n\n"
                    f"📊 *Today ({stats['date']}):*\n"
                    f"• Jobs sent: *{stats['sent']}*\n"
                    f"• Companies: *{len(stats['companies'])}*\n"
                    f"⏱ Checks every *1 hour*\n"
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
                    criteria = soup.find_all("span", class_=re.compile(r"description__job-criteria-text"))
                    for c in criteria:
                        text = c.get_text(strip=True)
                        if re.search(r"year|experience|mid|senior|entry", text, re.IGNORECASE):
                            if not job.get("experience") or len(job["experience"]) < 3:
                                job["experience"] = text
    except Exception as e:
        log(f"  [Enrich] error: {e}")
    time.sleep(1.5)
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

    if not config.BOT_TOKEN:
        log("ERROR: BOT_TOKEN not set.")
        print("ERROR: BOT_TOKEN not set in config!")
        return
    if not config.CHAT_ID:
        log("ERROR: CHAT_ID not set.")
        print("ERROR: CHAT_ID not set in config!")
        return

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

    state["last_run_at"] = datetime.utcnow().isoformat()
    save_state(state)

    log(f"Fetch window: {since_seconds // 60} minutes")

    seen = load_seen()
    log(f"Loaded {len(seen)} previously seen jobs.")

    try:
        jobs = fetch_all_jobs(since_seconds=since_seconds)
    except Exception as e:
        log(f"Scrape error (will continue with empty list): {e}")
        jobs = []

    print(f"DEBUG: Total jobs scraped: {len(jobs)}")
    log(f"Total jobs scraped: {len(jobs)}")

    india_jobs = [j for j in jobs if is_india_job(j)]
    log(f"India location: {len(india_jobs)} out of {len(jobs)} total.")
    print(f"DEBUG: India jobs: {len(india_jobs)}")

    us_tax_jobs = [j for j in india_jobs if is_us_tax_job(j)]
    log(f"US Tax relevant: {len(us_tax_jobs)} out of {len(india_jobs)} India jobs.")
    print(f"DEBUG: US Tax jobs: {len(us_tax_jobs)}")

    if len(india_jobs) > 0 and len(us_tax_jobs) == 0:
        log(f"DEBUG: Checking first India job for filter match:")
        first_job = india_jobs[0]
        log(f"  Title: {first_job.get('title', '')}")
        log(f"  Company: {first_job.get('company', '')}")
        log(f"  Location: {first_job.get('location', '')}")
        log(f"  Matches US_TAX_TERMS: {bool(US_TAX_TERMS.search(f\"{first_job.get('title', '')} {first_job.get('company', '')} {first_job.get('description', '')}\"))}")
        log(f"  Matches BLOCKLIST: {bool(BLOCKLIST.search(first_job.get('title', '')))}")

    new_jobs = [j for j in us_tax_jobs if _dedup_key(j) not in seen]
    new_jobs.sort(key=lambda j: str(j.get("posted") or j.get("fetched_at") or ""))
    log(f"New jobs to send: {len(new_jobs)}")

    if not new_jobs:
        log("No new US Tax jobs this cycle.")
        save_seen(seen)
        save_stats(stats)
        return

    if len(new_jobs) > config.MAX_JOBS_PER_CYCLE:
        log(f"Capping to {config.MAX_JOBS_PER_CYCLE} jobs this cycle.")
        new_jobs = new_jobs[:config.MAX_JOBS_PER_CYCLE]

    sent = 0
    for job in new_jobs:
        job = enrich_job(job)
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
    log(f"Done. Sent {sent} new jobs. Today total: {stats['sent']}. Tracked: {len(seen)}")


if __name__ == "__main__":
    main()
