"""
Single-cycle runner for GitHub Actions.
Fetches jobs, filters US Tax only, sends new ones to Telegram, saves seen_jobs.json.
"""
import json
import os
import re
from datetime import datetime
import config
from scraper import fetch_all_jobs
from sender import send_job

SEEN_FILE = "seen_jobs.json"

# ── US Tax keywords — job title OR description must contain at least one ──
US_TAX_TERMS = re.compile(
    r"\b("
    # US Tax identity
    r"us\s*tax(ation)?|u\.s\.?\s*tax|united\s*states\s*tax|"
    r"us\s*income\s*tax|us\s*federal\s*tax|"

    # Federal tax forms
    r"1040|1041|1120|1065|990|5500|1099|W-2|W2|"
    r"form\s*10(40|41|20|65|99)|"
    r"schedule\s*[A-F]|"

    # IRS / Federal / State
    r"irs|internal\s*revenue|federal\s*tax|state\s*tax\s*returns?|"
    r"federal\s*returns?|state\s*filing|"

    # Tax types
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

# ── Hard blocklist — always reject these ─────────────────────────────
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
    """
    Allow job only if:
    1. Title OR description contains a US Tax term (form names, IRS, federal, etc.)
    2. Title does NOT match the hard blocklist
    """
    title = job.get("title", "")
    desc  = job.get("description", "")
    full  = f"{title} {desc}"

    # Must contain at least one US Tax term anywhere in title or description
    if not US_TAX_TERMS.search(full):
        return False

    # Reject if title contains blocked terms
    if BLOCKLIST.search(title):
        return False

    return True


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

    # SEED_MODE: mark all current jobs as seen WITHOUT sending
    # Used once to reset the baseline so only future NEW jobs are sent
    seed_mode = os.environ.get("SEED_MODE", "false").lower() == "true"
    if seed_mode:
        log("SEED MODE — marking all current jobs as seen (no messages sent).")

    seen = load_seen()
    log(f"Loaded {len(seen)} previously seen jobs.")

    try:
        jobs = fetch_all_jobs()
    except Exception as e:
        log(f"Scrape error: {e}")
        return

    # Filter: US Tax relevant only
    us_tax_jobs = [j for j in jobs if is_us_tax_job(j)]
    log(f"US Tax relevant: {len(us_tax_jobs)} out of {len(jobs)} total fetched.")

    if seed_mode:
        for job in us_tax_jobs:
            seen.add(job["id"])
        save_seen(seen)
        log(f"SEED DONE — marked {len(us_tax_jobs)} jobs as seen. Bot will only send NEW jobs from now.")
        return

    # Filter: not seen before
    new_jobs = [j for j in us_tax_jobs if j["id"] not in seen]
    log(f"New (not sent before): {len(new_jobs)}")

    if not new_jobs:
        log("No new US Tax jobs found this cycle.")
        save_seen(seen)
        return

    sent = 0
    for job in new_jobs:
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
    log(f"Done. Sent {sent} new US Tax jobs. Total tracked: {len(seen)}")


if __name__ == "__main__":
    main()
