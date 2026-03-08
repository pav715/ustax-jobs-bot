"""
Job scraper — LinkedIn (guest API) + company career sites.
Only these two work reliably from GitHub Actions cloud IPs.
"""
import requests
import hashlib
import re
import time
import random
from datetime import datetime
from urllib.parse import urljoin, quote
from bs4 import BeautifulSoup
import config

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection":      "keep-alive",
})

PRIORITY_KEYWORDS = [
    "US Tax",
    "US Taxation",
    "Tax Analyst",
    "Tax Compliance",
    "Tax Preparation",
    "Tax Consultant",
]

TAX_PATTERN = re.compile(
    r"\b(tax|taxation|1040|1041|1120|1065|990|5500|irs|fiduciary|"
    r"compliance|e.?fil|direct\s*tax)\b",
    re.IGNORECASE,
)


def job_id(url, title, company):
    raw = f"{url}{title}{company}".lower().strip()
    return hashlib.md5(raw.encode()).hexdigest()[:16]


def _delay():
    time.sleep(random.uniform(2.5, 4.0))


def _make_job(title, company, location, url, posted="", exp="", skills="", desc="", source=""):
    return {
        "id":          job_id(url, title, company),
        "title":       title,
        "company":     company,
        "location":    location,
        "url":         url,
        "posted":      posted,
        "experience":  exp,
        "skills":      skills,
        "description": desc,
        "source":      source,
        "fetched_at":  datetime.now().isoformat(),
    }


# ── LINKEDIN (guest API — works on cloud) ─────────────────────────────
def scrape_linkedin(keyword, location, since_seconds=86400):
    jobs = []
    try:
        url = (
            f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?"
            f"keywords={quote(keyword)}&location={quote(location)}"
            f"&f_TPR=r{since_seconds}&sortBy=DD&start=0"
        )
        r = SESSION.get(url, timeout=12)
        if r.status_code != 200:
            print(f"  [LinkedIn] HTTP {r.status_code} — '{keyword}' / {location}")
            return jobs

        soup = BeautifulSoup(r.content, "html.parser")
        for card in soup.find_all("li")[:15]:
            try:
                h3      = card.find("h3")
                h4      = card.find("h4")
                loc_tag = card.find("span", class_=re.compile("job-search-card__location"))
                a_tag   = card.find("a", href=True)
                t_tag   = card.find("time")
                title   = h3.get_text(strip=True) if h3 else ""
                company = h4.get_text(strip=True) if h4 else ""
                loc_str = loc_tag.get_text(strip=True) if loc_tag else location
                link    = a_tag["href"].split("?")[0] if a_tag else ""
                posted  = t_tag.get("datetime", "") if t_tag else ""
                if title and link:
                    jobs.append(_make_job(title, company, loc_str, link,
                                          posted=posted, source="LinkedIn"))
            except Exception:
                pass
    except Exception as e:
        print(f"  [LinkedIn] Error: {e}")

    print(f"  [LinkedIn] '{keyword}' / {location} → {len(jobs)} jobs")
    return jobs


# ── COMPANY CAREER SITES ───────────────────────────────────────────────
def scrape_company_sites():
    """Scrape configured company career pages for US Tax job links."""
    jobs = []
    for site in getattr(config, "COMPANY_SITES", []):
        name = site.get("name", "")
        url  = site.get("url", "")
        if not url:
            continue
        try:
            r = SESSION.get(url, timeout=15)
            if r.status_code != 200:
                print(f"  [Careers/{name}] HTTP {r.status_code}")
                _delay()
                continue

            soup  = BeautifulSoup(r.text, "html.parser")
            found = 0
            for a in soup.find_all("a", href=True):
                text  = a.get_text(" ", strip=True)
                aria  = a.get("aria-label", "")
                label = f"{text} {aria}"
                if not TAX_PATTERN.search(label):
                    continue
                if len(text) < 5 or len(text) > 150:
                    continue
                job_url = a["href"]
                if job_url.startswith("/"):
                    job_url = urljoin(url, job_url)
                if not job_url.startswith("http"):
                    continue
                jobs.append(_make_job(text, name, "India / Remote", job_url,
                                      skills="US Tax, Compliance",
                                      source=f"{name} Careers"))
                found += 1
                if found >= 10:
                    break
            print(f"  [Careers/{name}] → {found} jobs")
        except Exception as e:
            print(f"  [Careers/{name}] Error: {e}")
        _delay()
    return jobs


# ── MAIN ──────────────────────────────────────────────────────────────
def fetch_all_jobs(since_seconds=86400):
    """
    Fetch jobs from LinkedIn + company career sites.
    since_seconds: only fetch LinkedIn jobs posted in this window (default 1 day).
    Returns deduplicated list sorted newest first.
    """
    all_jobs  = []
    seen_urls = set()

    def add(results):
        for job in results:
            key = job.get("url") or job.get("id")
            if key and key not in seen_urls:
                seen_urls.add(key)
                all_jobs.append(job)

    # LinkedIn — keywords × locations, time-windowed
    print(f"\n[LinkedIn] Scanning (last {since_seconds // 60} min window)...")
    for kw in PRIORITY_KEYWORDS:
        for loc in config.LOCATIONS:
            add(scrape_linkedin(kw, loc, since_seconds))
            _delay()

    # Company career sites
    print(f"\n[Company Sites] Scanning {len(getattr(config, 'COMPANY_SITES', []))} companies...")
    add(scrape_company_sites())

    # Sort newest first
    all_jobs.sort(
        key=lambda j: j.get("posted") or j.get("fetched_at") or "",
        reverse=True
    )
    print(f"\n  Total unique jobs fetched: {len(all_jobs)}")
    return all_jobs
