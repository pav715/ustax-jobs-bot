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

# ── US Tax relevance filter ───────────────────────────────────────────
# Job title or description must match at least one of these
US_TAX_FILTER = re.compile(
    r"\b("
    r"us\s*tax|us\s*taxation|u\.s\.?\s*tax|united\s*states\s*tax|"
    r"1040|1041|1120|1065|990|5500|"
    r"irs|federal\s*tax|state\s*tax|"
    r"us\s*income\s*tax|fiduciary\s*tax|partnership\s*tax|"
    r"tax\s*prep(arer|aration)|"
    r"tax\s*software|tax\s*e.?fil|e.?filing\s*tax|"
    r"tax\s*compliance|tax\s*analyst|tax\s*consultant|"
    r"tax\s*reviewer|tax\s*advisor|tax\s*associate|"
    r"direct\s*tax|indirect\s*tax|"
    r"tax\s*forms?|tax\s*returns?|"
    r"tax\s*schema|tax\s*business\s*rules|"
    r"form\s*10(40|41|20|65)|"
    r"tax\s*sme|tax\s*subject\s*matter"
    r")\b",
    re.IGNORECASE,
)


def is_us_tax_job(job):
    """Return True if job is US Tax related."""
    title = job.get("title", "")
    desc  = job.get("description", "")
    check = f"{title} {desc}"
    return bool(US_TAX_FILTER.search(check))


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
