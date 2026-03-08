"""
Single-cycle runner for GitHub Actions.
Fetches jobs, enriches with real description, filters US Tax only,
sends to Telegram with actual job info.
AI-powered via Google Gemini Flash (free tier).
"""
import json
import os
import re
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime, date
import config
from scraper import fetch_all_jobs, SESSION
from sender import send_job, send_daily_summary, send_fail_alert, send_and_pin_welcome

# ── Gemini AI setup ───────────────────────────────────────────────────
GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")
_gemini_model = None

def _get_gemini():
    global _gemini_model
    if _gemini_model:
        return _gemini_model
    if not GEMINI_KEY:
        print("[AI] GEMINI_API_KEY not set — AI enrichment disabled.")
        return None
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_KEY)
        _gemini_model = genai.GenerativeModel("gemini-1.5-flash")
        print("[AI] Gemini 1.5 Flash initialized successfully.")
        return _gemini_model
    except Exception as e:
        print(f"[AI] Gemini init FAILED: {e}")
        return None

SEEN_FILE      = "seen_jobs.json"
STATS_FILE     = "stats.json"
STATE_FILE     = "bot_state.json"

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


# ── Bot state (pause/resume) ──────────────────────────────────────────
def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {"paused": False, "last_update_id": 0, "last_run_at": "", "welcome_pinned": False}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


# ── Daily stats ───────────────────────────────────────────────────────
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


def update_stats(stats, job):
    stats["sent"] += 1
    company = job.get("company", "Other")
    stats["companies"][company] = stats["companies"].get(company, 0) + 1


# ── Telegram command handler ──────────────────────────────────────────
def handle_commands(state, stats):
    """Check for Telegram commands and respond."""
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

            if text == "/status" or text.startswith("/status"):
                reply = (
                    f"🤖 *US Tax Jobs Bot — Status*\n\n"
                    f"{'⏸ PAUSED' if state.get('paused') else '✅ RUNNING'}\n\n"
                    f"📊 *Today ({stats['date']}):*\n"
                    f"• Jobs sent: *{stats['sent']}*\n"
                    f"• Companies: *{len(stats['companies'])}*\n"
                    f"⏱ Checks every *5 minutes*\n"
                    f"🕐 {datetime.now().strftime('%d %b %Y %H:%M IST')}"
                )
                requests.post(api, json={"chat_id": chat_id, "text": reply, "parse_mode": "Markdown"}, timeout=10)

            elif text == "/pause":
                state["paused"] = True
                requests.post(api, json={
                    "chat_id": chat_id,
                    "text": "⏸ *Bot paused.* Send /resume to restart notifications.",
                    "parse_mode": "Markdown"
                }, timeout=10)

            elif text == "/resume":
                state["paused"] = False
                requests.post(api, json={
                    "chat_id": chat_id,
                    "text": "▶️ *Bot resumed.* Notifications are back on.",
                    "parse_mode": "Markdown"
                }, timeout=10)

            elif text == "/top":
                if stats["companies"]:
                    top = sorted(stats["companies"].items(), key=lambda x: x[1], reverse=True)[:5]
                    lines = ["🏆 *Top Hiring Companies Today:*\n"]
                    for i, (co, cnt) in enumerate(top, 1):
                        lines.append(f"{i}. {co} — {cnt} job{'s' if cnt > 1 else ''}")
                    reply = "\n".join(lines)
                else:
                    reply = "📭 No jobs sent yet today."
                requests.post(api, json={"chat_id": chat_id, "text": reply, "parse_mode": "Markdown"}, timeout=10)

            elif text == "/help":
                reply = (
                    "🤖 *US Tax Jobs Bot — Commands*\n\n"
                    "/status — Bot status & today's count\n"
                    "/pause — Pause job notifications\n"
                    "/resume — Resume notifications\n"
                    "/top — Top hiring companies today\n"
                    "/help — Show this help"
                )
                requests.post(api, json={"chat_id": chat_id, "text": reply, "parse_mode": "Markdown"}, timeout=10)

    except Exception as e:
        log(f"[Commands] Error: {e}")

    return state


# ── Fetch real job description ────────────────────────────────────────
def enrich_job(job):
    if job.get("description") and len(job["description"]) > 300:
        return job

    url    = job.get("url", "")
    source = job.get("source", "")

    try:
        if "linkedin.com" in url:
            match = re.search(r'/(\d{8,})', url)
            if match:
                jid        = match.group(1)
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
        log(f"  [Enrich] {source} error: {e}")

    time.sleep(1.5)
    return job


# ── AI enrichment ─────────────────────────────────────────────────────
def ai_enrich_job(job):
    """Gemini Flash: extract job info + match score against candidate profile."""
    model = _get_gemini()
    if not model:
        return job

    title = job.get("title", "")
    desc  = job.get("description", "")

    if not desc or len(desc) < 100:
        return job

    prompt = f"""You are a US Tax recruitment expert. Analyze this job posting and score it against the candidate profile.

Job Title: {title}
Job Description: {desc[:2500]}

Candidate Profile:
{config.USER_PROFILE}

Return ONLY valid JSON — no markdown, no explanation:
{{
  "experience": "X-Y Years in specific area",
  "qualification": "exact degree/certification from job",
  "salary": "salary range if mentioned, else Not mentioned",
  "match_score": 85,
  "match_highlights": ["reason this matches candidate", "another strength"],
  "is_us_tax_job": true
}}

Rules:
- experience: exact years mentioned or infer from seniority
- qualification: B.Com / CA / CPA / MBA as stated in job
- salary: extract if mentioned (e.g. "12-18 LPA"), else "Not mentioned"
- match_score: 0-100 based on how well candidate profile matches this job
- match_highlights: 2-3 reasons why candidate is a good/poor fit
- is_us_tax_job: true only if job involves US federal/state tax (IRS, 1040, 1041 etc.)"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()

        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.strip()

        data = json.loads(text)

        if data.get("experience"):
            job["_experience"] = data["experience"]
        if data.get("qualification"):
            job["_qualification"] = data["qualification"]
        if data.get("salary"):
            job["_salary"] = data["salary"]
        if data.get("match_score") is not None:
            job["_match_score"] = int(data["match_score"])
        if data.get("match_highlights"):
            job["_match_highlights"] = data["match_highlights"]
        if data.get("is_us_tax_job") is False:
            job["_ai_rejected"] = True

        log(f"  [AI] {title[:45]} | Match: {job.get('_match_score', '?')}% | Salary: {job.get('_salary', '?')}")

    except Exception as e:
        log(f"  [AI] Skipped '{title[:40]}': {e}")

    time.sleep(1)
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

    # Load state and stats
    state = load_state()
    stats = load_stats()

    # ── Pin welcome message once (first run only) ─────────────────────
    if not state.get("welcome_pinned"):
        log("Pinning welcome message for the first time...")
        ok = send_and_pin_welcome()
        if ok:
            state["welcome_pinned"] = True
            save_state(state)

    # Handle Telegram commands (/status, /pause, /resume, /top, /help)
    state = handle_commands(state, stats)
    save_state(state)

    # Check if bot is paused
    if state.get("paused"):
        log("Bot is PAUSED. Send /resume to Telegram bot to restart.")
        return

    # Always fetch last 24 hours — seen_jobs.json handles deduplication
    # Previous approach (dynamic 5-min window) caused jobs to be missed all day
    now_utc = datetime.utcnow()
    since_seconds = 86400
    log(f"Fetch window: 24 hours (last run: {state.get('last_run_at') or 'never'})")

    # Record this run time for stats/logging
    state["last_run_at"] = now_utc.isoformat()
    save_state(state)

    # Daily summary at 9 AM IST (3:30 AM UTC)
    if now_utc.hour == 3 and 30 <= now_utc.minute < 40 and not stats.get("summary_sent"):
        send_daily_summary(stats)
        stats["summary_sent"] = True
        save_stats(stats)

    seen = load_seen()
    log(f"Loaded {len(seen)} previously seen jobs.")

    try:
        jobs = fetch_all_jobs(since_seconds=since_seconds)
    except Exception as e:
        log(f"Scrape error: {e}")
        send_fail_alert(f"Scrape error: {e}")
        return

    # Filter: US Tax relevant only
    us_tax_jobs = [j for j in jobs if is_us_tax_job(j)]
    log(f"US Tax relevant: {len(us_tax_jobs)} out of {len(jobs)} total.")

    # No date filter — LinkedIn filters by since_seconds=86400, seen_jobs.json deduplicates
    log(f"US Tax jobs ready to process: {len(us_tax_jobs)}")

    # New jobs only — sorted oldest-first so channel shows newest at top
    new_jobs = [j for j in us_tax_jobs if j["id"] not in seen]
    new_jobs.sort(key=lambda j: str(j.get("posted") or j.get("fetched_at") or ""))
    log(f"New jobs to send: {len(new_jobs)}")

    if not new_jobs:
        log("No new US Tax jobs this cycle.")
        save_seen(seen)
        save_stats(stats)
        return

    # Cap to prevent spam
    if len(new_jobs) > config.MAX_JOBS_PER_CYCLE:
        log(f"Capping to {config.MAX_JOBS_PER_CYCLE} jobs this cycle.")
        new_jobs = new_jobs[:config.MAX_JOBS_PER_CYCLE]

    use_ai = _get_gemini() is not None
    log(f"AI: {'ON (Gemini 1.5 Flash)' if use_ai else 'OFF — check GEMINI_API_KEY secret'}")

    enriched = []
    for job in new_jobs:
        # Step 1: fetch real description
        job = enrich_job(job)
        desc  = job.get("description", "")
        title = job.get("title", "")

        # Step 2: AI extraction + match score
        if use_ai:
            job = ai_enrich_job(job)

        # Step 3: regex fallback for fields still shown in message
        if not job.get("_experience"):
            job["_experience"]    = extract_experience(desc, title)
        if not job.get("_qualification"):
            job["_qualification"] = extract_qualification(desc, title)

        # Step 4: drop AI-rejected jobs
        if job.get("_ai_rejected"):
            log(f"  [AI] Rejected (not US Tax): {title}")
            seen.add(job["id"])
            continue

        # Step 5: drop low match score jobs
        score = job.get("_match_score", 100)
        if use_ai and score < config.MIN_MATCH_SCORE:
            log(f"  [AI] Low match ({score}%): {title}")
            seen.add(job["id"])
            continue

        enriched.append(job)

    # Sort by match score (highest first)
    enriched.sort(key=lambda j: j.get("_match_score", 0), reverse=True)

    sent = 0
    for job in enriched:
        try:
            ok = send_job(job)
            if ok:
                seen.add(job["id"])
                sent += 1
                update_stats(stats, job)
                log(f"  Sent [{job.get('_match_score', '?')}%]: {job['title']} @ {job['company']}")
            else:
                log(f"  Failed: {job['title']}")
        except Exception as e:
            log(f"  Error: {e}")

    save_seen(seen)
    save_stats(stats)
    log(f"Done. Sent {sent} new jobs. Today total: {stats['sent']}. Tracked: {len(seen)}")


if __name__ == "__main__":
    main()
