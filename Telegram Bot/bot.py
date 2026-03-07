"""
US Tax Jobs — Telegram Bot
Runs 24/7, checks every 10 minutes, sends new jobs instantly.
No duplicates. Newest first.

Run: python bot.py
"""
import json
import os
import time
import re
import requests
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime
import config
from scraper import fetch_all_jobs
from sender import send_job, send_startup_message, send_no_jobs_today_message

SEEN_FILE = "seen_jobs.json"
LOG_FILE  = "bot.log"


# ── Seen jobs tracker ─────────────────────────────────────────────────
def load_seen():
    if os.path.exists(SEEN_FILE):
        try:
            with open(SEEN_FILE, "r") as f:
                return set(json.load(f))
        except Exception:
            pass
    return set()


def save_seen(seen_set):
    # Keep only last 5000 to avoid file bloat
    data = list(seen_set)[-5000:]
    with open(SEEN_FILE, "w") as f:
        json.dump(data, f)


# ── First-run initialization (no backlog) ──────────────────────────────
def initialize_seen_if_empty(seen):
    """
    If this is the first run (no seen jobs yet), preload all currently
    available jobs as 'already seen' so the bot starts sending ONLY
    new jobs from now on (no historical backlog spam).
    """
    if seen:
        return seen

    log("First run detected: preloading existing jobs as already seen (no backlog will be sent).")
    try:
        jobs = fetch_all_jobs()
        if not jobs:
            log("No jobs found during preload. Proceeding normally.")
            return seen

        for j in jobs:
            if "id" in j:
                seen.add(j["id"])

        save_seen(seen)
        log(f"Preload complete. Marked {len(seen)} jobs as already seen. Only new jobs will be posted going forward.")
    except Exception as e:
        log(f"Error during preload initialization: {e}")

    return seen


# ── Logging ───────────────────────────────────────────────────────────
def log(msg):
    ts  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


# ── Telegram setup ────────────────────────────────────────────────────
def setup_telegram():
    """Detect Chat ID on first run."""
    if config.CHAT_ID:
        return True

    log("CHAT_ID not set. Detecting from Telegram updates...")
    try:
        r = requests.get(
            f"https://api.telegram.org/bot{config.BOT_TOKEN}/getUpdates",
            timeout=15
        )
        data = r.json()
        for item in data.get("result", []):
            chat = (
                item.get("channel_post", {}).get("chat")
                or item.get("message", {}).get("chat")
                or {}
            )
            if chat.get("id"):
                chat_id = str(chat["id"])
                config.CHAT_ID = chat_id
                _save_chat_id(chat_id)
                log(f"Chat ID detected and saved: {chat_id}  ({chat.get('title','')})")
                return True

        log("No channel found. Add @USTaxjobs_bot as Admin to your channel, send a message, then restart.")
        return False
    except Exception as e:
        log(f"Telegram setup error: {e}")
        return False


def _save_chat_id(chat_id):
    """Write Chat ID into config.py automatically."""
    try:
        path = os.path.join(os.path.dirname(__file__), "config.py")
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        content = re.sub(
            r'CHAT_ID\s*=\s*"[^"]*"',
            f'CHAT_ID   = "{chat_id}"',
            content, count=1
        )
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
    except Exception:
        pass


# ── Helpers: date filtering ────────────────────────────────────────────
def _is_today(job):
    """Return True if the job was posted today (best-effort)."""
    today = datetime.now().date()

    # Try posted field first (LinkedIn ISO, Indeed RSS, etc.)
    posted = job.get("posted") or ""
    fetched = job.get("fetched_at") or ""

    # ISO-like datetime (e.g. 2026-03-07 or 2026-03-07T12:34:00)
    for value in (posted, fetched):
        if not value:
            continue
        iso = value.replace("Z", "").split("+")[0]
        try:
            dt = datetime.fromisoformat(iso)
            if dt.date() == today:
                return True
        except Exception:
            pass

    # RFC822 (Indeed RSS pubDate)
    if posted:
        try:
            dt = parsedate_to_datetime(posted)
            if dt.date() == today:
                return True
        except Exception:
            pass

    return False


def _location_allowed(loc_str):
    """
    Return True if the job location matches one of the configured
    priority locations/cities/states/remote.
    """
    loc = (loc_str or "").lower()
    allowed = [x.lower() for x in getattr(config, "LOCATIONS", [])]
    if not allowed or not loc:
        return True
    return any(a in loc for a in allowed)


def _is_within_days(job, days):
    """Return True if job posted date is within last `days` days (inclusive)."""
    today = datetime.now().date()
    cutoff = today - timedelta(days=days)

    posted = job.get("posted") or ""
    fetched = job.get("fetched_at") or ""

    # ISO-like
    for value in (posted, fetched):
        if not value:
            continue
        iso = value.replace("Z", "").split("+")[0]
        try:
            dt = datetime.fromisoformat(iso)
            if cutoff <= dt.date() <= today:
                return True
        except Exception:
            pass

    # RFC822 (Indeed)
    if posted:
        try:
            dt = parsedate_to_datetime(posted)
            if cutoff <= dt.date() <= today:
                return True
        except Exception:
            pass

    return False


# ── One scrape cycle ──────────────────────────────────────────────────
def run_cycle(seen):
    log(f"Checking for new jobs... ({len(config.KEYWORDS)} keywords x {len(config.LOCATIONS)} locations)")
    try:
        jobs = fetch_all_jobs()
    except Exception as e:
        log(f"Scrape error: {e}")
        return seen, 0

    # Prefer jobs from the last 2 days; if none, fall back to any jobs,
    # but always enforce the allowed locations filter.
    jobs_recent = [j for j in jobs if _is_within_days(j, 2) and _location_allowed(j.get("location", ""))]
    candidates = jobs_recent if jobs_recent else [j for j in jobs if _location_allowed(j.get("location", ""))]

    # Filter out already-seen jobs
    new_jobs = [j for j in candidates if j["id"] not in seen]

    if not new_jobs:
        if jobs_recent:
            log(f"No new unseen jobs from the last 2 days. Total tracked: {len(seen)}")
        else:
            log(f"No new unseen jobs (even when considering older ones). Total tracked: {len(seen)}")
        # On very first run with nothing to send, post a gentle update.
        if len(seen) == 0:
            send_no_jobs_today_message()
        return seen, 0

    if jobs_recent:
        log(f"Found {len(new_jobs)} new jobs from the last 2 days! Sending to Telegram...")
    else:
        log(f"Found {len(new_jobs)} new jobs (older than 2 days). Sending to Telegram...")

    sent = 0
    for job in new_jobs:   # already sorted newest first by scraper
        try:
            ok = send_job(job)
            if ok:
                seen.add(job["id"])
                sent += 1
                log(f"  Sent: [{job['source']}] {job['title']} @ {job['company']} | {job['location']}")
            else:
                log(f"  Failed to send: {job['title']}")
        except Exception as e:
            log(f"  Error sending job: {e}")

    save_seen(seen)
    log(f"Done. Sent {sent} new jobs. Total tracked: {len(seen)}")
    return seen, sent


# ── Main loop ─────────────────────────────────────────────────────────
def main():
    log("=" * 60)
    log("  US Tax Jobs Telegram Bot")
    log("  Bot: @USTaxjobs_bot")
    log(f"  Check interval: every {config.CHECK_INTERVAL_MINUTES} minutes")
    log("=" * 60)

    # Setup Telegram
    if not setup_telegram():
        log("Cannot start without CHAT_ID. Exiting.")
        return

    # Load seen jobs
    seen = load_seen()
    log(f"Loaded {len(seen)} previously seen jobs (no duplicates).")

    # Optional startup message to channel
    if getattr(config, "SHOW_STARTUP_MESSAGE", False):
        send_startup_message(len(config.KEYWORDS), len(config.LOCATIONS))

    # First run immediately (will only send jobs that appeared after preload)
    seen, sent = run_cycle(seen)

    interval = config.CHECK_INTERVAL_MINUTES * 60

    while True:
        next_check = datetime.now().strftime("%H:%M:%S")
        log(f"Sleeping {config.CHECK_INTERVAL_MINUTES} min... (next check after {next_check})")
        time.sleep(interval)
        seen, sent = run_cycle(seen)


# ── Utility: send at least one job now (demo) ──────────────────────────
def send_one_job_now():
    """
    Fetch jobs once and send at least one job to the channel,
    ignoring the 'today-only' filter and seen history.
    """
    log("Manual trigger: send_one_job_now()")
    try:
        jobs = fetch_all_jobs()
    except Exception as e:
        log(f"Manual send error (fetch_all_jobs): {e}")
        return

    if not jobs:
        log("Manual send: no jobs available from sources.")
        return

    job = jobs[0]
    ok = send_job(job)
    if ok:
        log(f"Manual send: Sent sample job [{job.get('source','')}] {job.get('title','')} @ {job.get('company','')}")
    else:
        log("Manual send: failed to send sample job.")


def send_all_today_jobs():
    """
    Fetch all jobs once and send every job from the last 2 days
    to the channel, completely ignoring seen-job history.
    Use this when you want to push ALL recent US Tax jobs (2-day window)
    into the channel in one shot.
    """
    log("Manual trigger: send_all_today_jobs()")
    try:
        jobs = fetch_all_jobs()
    except Exception as e:
        log(f"Manual send-all error (fetch_all_jobs): {e}")
        return

    if not jobs:
        log("Manual send-all: no jobs available from sources.")
        return

    today_jobs = [j for j in jobs if _is_within_days(j, 2) and _location_allowed(j.get("location", ""))]
    if not today_jobs:
        log("Manual send-all: no jobs found for the last 2 days.")
        return

    log(f"Manual send-all: sending {len(today_jobs)} jobs from the last 2 days...")
    sent = 0
    for job in today_jobs:
        ok = send_job(job)
        if ok:
            sent += 1
            log(f"  Manual sent: [{job.get('source','')}] {job.get('title','')} @ {job.get('company','')}")
        else:
            log(f"  Manual send failed: {job.get('title','')}")
    log(f"Manual send-all done. Sent {sent}/{len(today_jobs)} jobs from the last 2 days.")


def send_last_week_jobs():
    """
    Fetch all jobs once and send every job from the last 7 days
    (including today) to the channel, ignoring seen-job history.
    """
    log("Manual trigger: send_last_week_jobs()")
    try:
        jobs = fetch_all_jobs()
    except Exception as e:
        log(f"Manual send-last-week error (fetch_all_jobs): {e}")
        return

    if not jobs:
        log("Manual send-last-week: no jobs available from sources.")
        return

    week_jobs = [j for j in jobs if _is_within_days(j, 7) and _location_allowed(j.get("location", ""))]
    if not week_jobs:
        log("Manual send-last-week: no jobs found in last 7 days.")
        return

    log(f"Manual send-last-week: sending {len(week_jobs)} jobs from last 7 days...")
    sent = 0
    for job in week_jobs:
        ok = send_job(job)
        if ok:
            sent += 1
            log(f"  Manual sent: [{job.get('source','')}] {job.get('title','')} @ {job.get('company','')}")
        else:
            log(f"  Manual send failed: {job.get('title','')}")
    log(f"Manual send-last-week done. Sent {sent}/{len(week_jobs)} jobs.")


if __name__ == "__main__":
    main()
