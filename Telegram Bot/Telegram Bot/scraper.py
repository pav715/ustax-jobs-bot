"""
Job scraper — LinkedIn + Google Jobs + Indeed + Naukri + India portals + company sites.
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
    # Use title+company only — same job from multiple sources gets the same ID
    # This prevents LinkedIn + Indeed + Naukri all posting the same role
    raw = f"{title}{company}".lower().strip()
    return hashlib.md5(raw.encode()).hexdigest()[:16]


def _delay():
    time.sleep(random.uniform(1.0, 2.0))


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


# ── GOOGLE JOBS via JobSpy ────────────────────────────────────────────
JOBSPY_KEYWORDS = ["US Tax", "Tax Analyst", "Tax Compliance", "US Taxation"]
JOBSPY_LOCATIONS = ["Hyderabad", "Bangalore", "Chennai", "Mumbai", "Pune", "Kochi", "Visakhapatnam"]


def scrape_jobspy():
    """
    Scrape Google Jobs + Glassdoor using python-jobspy (free, open source).
    Returns jobs posted in last 24 hours.
    """
    jobs = []
    try:
        from jobspy import scrape_jobs
    except ImportError:
        print("  [JobSpy] Not installed — skipping")
        return jobs

    for keyword in JOBSPY_KEYWORDS:
        for location in JOBSPY_LOCATIONS:
            try:
                results = scrape_jobs(
                    site_name=["google"],
                    search_term=keyword,
                    location=location,
                    results_wanted=10,
                    hours_old=24,
                    country_indeed="India",
                    verbose=0,
                )
                for _, row in results.iterrows():
                    try:
                        title   = str(row.get("title", "") or "")
                        company = str(row.get("company", "") or "")
                        loc_str = str(row.get("location", location) or location)
                        link    = str(row.get("job_url", "") or "")
                        posted  = str(row.get("date_posted", "") or "")
                        source  = str(row.get("site", "Google Jobs") or "Google Jobs").title()

                        if title and link:
                            jobs.append(_make_job(title, company, loc_str, link,
                                                  posted=posted, source=source))
                    except Exception:
                        pass
                print(f"  [JobSpy] '{keyword}' / {location} → {len(results)} jobs")
            except Exception as e:
                print(f"  [JobSpy] '{keyword}' / {location} error: {e}")
            _delay()

    return jobs


# ── INDEED.CO.IN ──────────────────────────────────────────────────────
INDEED_KEYWORDS = [
    "US Tax",
    "Tax Analyst",
    "Tax Compliance",
    "1040",
    "US Taxation",
]
INDEED_LOCATIONS = ["Hyderabad", "Bangalore", "Chennai", "Mumbai", "Pune", "Nagpur", "Kochi", "Visakhapatnam"]


def scrape_indeed(keyword, location):
    """Scrape Indeed.co.in for US Tax jobs posted in last 1 day."""
    jobs = []
    try:
        url = (
            f"https://www.indeed.co.in/jobs?"
            f"q={quote(keyword)}&l={quote(location)}"
            f"&fromage=1&sort=date"
        )
        r = SESSION.get(url, timeout=15)
        if r.status_code != 200:
            print(f"  [Indeed] HTTP {r.status_code} — '{keyword}' / {location}")
            return jobs

        soup = BeautifulSoup(r.text, "html.parser")

        # Try multiple card selectors (Indeed occasionally changes class names)
        cards = soup.find_all("div", class_=re.compile("job_seen_beacon"))
        if not cards:
            cards = soup.find_all("div", attrs={"data-jk": True})

        for card in cards[:10]:
            try:
                # Title
                title_tag = card.find("h2", class_=re.compile("jobTitle"))
                title = title_tag.get_text(strip=True) if title_tag else ""

                # Company
                co_tag = card.find("span", class_=re.compile("companyName"))
                company = co_tag.get_text(strip=True) if co_tag else ""

                # Location
                loc_tag = card.find("div", class_=re.compile("companyLocation"))
                loc_str = loc_tag.get_text(strip=True) if loc_tag else location

                # Job URL via data-jk key
                a_tag = card.find("a", attrs={"data-jk": True})
                if not a_tag and title_tag:
                    a_tag = title_tag.find("a")
                jk   = a_tag.get("data-jk", "") if a_tag else ""
                link = f"https://www.indeed.co.in/viewjob?jk={jk}" if jk else (
                    a_tag["href"] if a_tag and a_tag.get("href", "").startswith("http") else ""
                )

                # Posted date (relative text like "1 day ago")
                date_tag = card.find("span", class_=re.compile(r"^date"))
                posted = date_tag.get_text(strip=True) if date_tag else ""

                if title and link:
                    jobs.append(_make_job(title, company, loc_str, link,
                                          posted=posted, source="Indeed"))
            except Exception:
                pass
    except Exception as e:
        print(f"  [Indeed] Error: {e}")

    print(f"  [Indeed] '{keyword}' / {location} → {len(jobs)} jobs")
    return jobs


# ── NAUKRI.COM ────────────────────────────────────────────────────────
NAUKRI_KEYWORDS = [
    "US Tax",
    "US Taxation",
    "Tax Analyst",
    "Tax Compliance",
]
NAUKRI_LOCATIONS = ["hyderabad", "bangalore", "chennai", "mumbai", "pune", "nagpur", "kochi", "visakhapatnam", "vijayawada"]


def scrape_naukri(keyword, location="hyderabad"):
    """Scrape Naukri.com search results for US Tax jobs."""
    jobs = []
    try:
        slug = re.sub(r"[^a-z0-9]+", "-", keyword.lower()).strip("-")
        url  = (
            f"https://www.naukri.com/{slug}-jobs-in-{location}"
            f"?experience=0&jobAge=1"
        )
        r = SESSION.get(url, timeout=15)
        if r.status_code != 200:
            print(f"  [Naukri] HTTP {r.status_code} — '{keyword}' / {location}")
            return jobs

        soup = BeautifulSoup(r.text, "html.parser")

        # Naukri uses article tags with class "jobTuple" or similar
        cards = (
            soup.find_all("article", class_=re.compile("jobTuple|job-tuple")) or
            soup.find_all("div", class_=re.compile("jobTuple|srp-jobtuple"))
        )

        for card in cards[:10]:
            try:
                # Title
                title_tag = card.find("a", class_=re.compile("title"))
                title = title_tag.get_text(strip=True) if title_tag else ""
                link  = title_tag["href"] if title_tag and title_tag.get("href") else ""
                if link and link.startswith("/"):
                    link = f"https://www.naukri.com{link}"

                # Company
                co_tag = card.find("a", class_=re.compile("subTitle|company"))
                company = co_tag.get_text(strip=True) if co_tag else ""

                # Location
                loc_tag = card.find("li", class_=re.compile("location"))
                loc_str = loc_tag.get_text(strip=True) if loc_tag else location.title()

                # Posted — Naukri shows "X days ago" in a span
                date_tag = card.find("span", class_=re.compile("date|ago"))
                posted = date_tag.get_text(strip=True) if date_tag else ""

                if title and link:
                    jobs.append(_make_job(title, company, loc_str, link,
                                          posted=posted, source="Naukri"))
            except Exception:
                pass
    except Exception as e:
        print(f"  [Naukri] Error: {e}")

    print(f"  [Naukri] '{keyword}' / {location} → {len(jobs)} jobs")
    return jobs


# ── INDIA JOB PORTALS (Foundit, Shine, TimesJobs, AmbitionBox) ────────
def scrape_india_portals():
    """Scrape India job portals configured in config.INDIA_PORTALS."""
    jobs = []
    for site in getattr(config, "INDIA_PORTALS", []):
        name = site.get("name", "")
        url  = site.get("url", "")
        if not url:
            continue
        try:
            r = SESSION.get(url, timeout=15)
            if r.status_code != 200:
                print(f"  [India/{name}] HTTP {r.status_code}")
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
                jobs.append(_make_job(text, name, "India", job_url,
                                      source=name))
                found += 1
                if found >= 10:
                    break
            print(f"  [India/{name}] → {found} jobs")
        except Exception as e:
            print(f"  [India/{name}] Error: {e}")
        _delay()
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
    Fetch jobs from LinkedIn + Indeed + Naukri + company career sites.
    since_seconds: only fetch LinkedIn jobs posted in this window (default 1 day).
    Returns deduplicated list sorted newest first.
    """
    all_jobs   = []
    seen_urls  = set()
    seen_ids   = set()

    def add(results):
        for job in results:
            jid = job.get("id", "")
            url = job.get("url", "")
            # Skip if same title+company already seen this cycle (from another source)
            if jid and jid in seen_ids:
                continue
            # Skip if exact same URL already seen
            if url and url in seen_urls:
                continue
            if jid:
                seen_ids.add(jid)
            if url:
                seen_urls.add(url)
            all_jobs.append(job)

    # LinkedIn — keywords × locations, time-windowed
    print(f"\n[LinkedIn] Scanning (last {since_seconds // 60} min window)...")
    for kw in PRIORITY_KEYWORDS:
        for loc in config.LOCATIONS:
            add(scrape_linkedin(kw, loc, since_seconds))
            _delay()

    # Google Jobs via JobSpy
    print(f"\n[JobSpy] Scanning Google Jobs...")
    add(scrape_jobspy())

    # Indeed.co.in — last 1 day
    print(f"\n[Indeed] Scanning...")
    for kw in INDEED_KEYWORDS:
        for loc in INDEED_LOCATIONS:
            add(scrape_indeed(kw, loc))
            _delay()

    # Naukri.com — last 1 day
    print(f"\n[Naukri] Scanning...")
    for kw in NAUKRI_KEYWORDS:
        for loc in NAUKRI_LOCATIONS:
            add(scrape_naukri(kw, loc))
            _delay()

    # India job portals — Foundit, Shine, TimesJobs, AmbitionBox
    india_portals = getattr(config, "INDIA_PORTALS", [])
    print(f"\n[India Portals] Scanning {len(india_portals)} portals...")
    add(scrape_india_portals())

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
