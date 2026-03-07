"""
Single-cycle runner for GitHub Actions.
Fetches jobs, sends new ones to Telegram, saves seen_jobs.json, exits.
"""
import json
import os
from datetime import datetime
import config
from scraper import fetch_all_jobs
from sender import send_job

SEEN_FILE = "seen_jobs.json"


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
        log("ERROR: BOT_TOKEN not set. Add it as a GitHub Secret.")
        return
    if not config.CHAT_ID:
        log("ERROR: CHAT_ID not set. Add it as a GitHub Secret.")
        return

    seen = load_seen()
    log(f"Loaded {len(seen)} previously seen jobs.")

    try:
        jobs = fetch_all_jobs()
    except Exception as e:
        log(f"Scrape error: {e}")
        return

    new_jobs = [j for j in jobs if j["id"] not in seen]
    log(f"Found {len(new_jobs)} new jobs out of {len(jobs)} total.")

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
    log(f"Done. Sent {sent} new jobs. Total tracked: {len(seen)}")


if __name__ == "__main__":
    main()
