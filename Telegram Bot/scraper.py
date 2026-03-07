"""
Job scraper — Naukri, LinkedIn, Indeed, Glassdoor, Google Jobs + company career sites.
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

# Priority keywords used for job board scans (fast, high-signal)
PRIORITY_KEYWORDS = [
    "US Tax",
    "US Taxation",
    "Tax Analyst",
    "Tax Compliance",
    "Tax Preparation",
    "Tax Consultant",
]

# Tax-related match pattern for filtering career site links
TAX_PATTERN = re.compile(
    r"\b(tax|taxation|1040|1041|1120|1065|990|5500|irs|fiduciary|"
    r"compliance|e.?fil|e.?filing|indirect tax|direct tax)\b",
    re.IGNORECASE,
)


def job_id(url, title, company):
    raw = f"{url}{title}{company}".lower().strip()
    return hashlib.md5(raw.encode()).hexdigest()[:16]


def _delay():
    time.sleep(random.uniform(2.5, 4.0))


def _log(source, keyword, location, count):
    print(f"  [{source}] '{keyword}' / {location} → {count} jobs")


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


# ── NAUKRI ────────────────────────────────────────────────────────────
def scrape_naukri(keyword, location):
    jobs = []
    try:
        url = (
            f"https://www.naukri.com/jobapi/v3/search?"
            f"noOfResults=20&urlType=search_by_keyword&searchType=adv"
            f"&keyword={quote(keyword)}&location={quote(location)}&experience=0"
            f"&src=jobsearchDesk&latLong="
        )
        r = SESSION.get(url, headers={
            "User-Agent":   "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "appid":        "109",
            "systemid":     "109",
            "Referer":      "https://www.naukri.com/",
            "Accept":       "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Origin":       "https://www.naukri.com",
        }, timeout=12)

        if r.status_code != 200:
            print(f"  [Naukri] HTTP {r.status_code}")
            return jobs

        for j in r.json().get("jobDetails", []):
            title   = j.get("title", "").strip()
            company = j.get("companyName", "").strip()
            jurl    = "https://www.naukri.com" + j.get("jdURL", "")
            placeholders = j.get("placeholders", [])
            loc_str = placeholders[0].get("label", location) if placeholders else location
            desc    = BeautifulSoup(j.get("jobDescription", ""), "html.parser").get_text(" ", strip=True)[:300]
            skills  = ", ".join([s.get("label", "") for s in j.get("tagsAndSkills", [])[:5]])
            if title:
                jobs.append(_make_job(
                    title, company, loc_str, jurl,
                    posted=j.get("footerPlaceholderLabel", ""),
                    exp=j.get("experienceText", ""),
                    skills=skills, desc=desc, source="Naukri"
                ))
    except Exception as e:
        print(f"  [Naukri] Error: {e}")
    _log("Naukri", keyword, location, len(jobs))
    return jobs


# ── INDEED INDIA (RSS) ─────────────────────────────────────────────────
def scrape_indeed(keyword, location):
    jobs = []
    try:
        url = (
            f"https://in.indeed.com/rss?"
            f"q={quote(keyword)}&l={quote(location)}"
            f"&sort=date&fromage={config.DAYS_OLD_MAX}"
        )
        r = SESSION.get(url, timeout=12)
        if r.status_code != 200:
            print(f"  [Indeed] HTTP {r.status_code}")
            return jobs

        soup = BeautifulSoup(r.content, "xml")
        for item in soup.find_all("item")[:15]:
            try:
                title_raw = item.find("title").get_text(strip=True) if item.find("title") else ""
                link      = item.find("link").get_text(strip=True)  if item.find("link")  else ""
                pub_date  = item.find("pubDate").get_text(strip=True) if item.find("pubDate") else ""
                desc_tag  = item.find("description")
                desc      = BeautifulSoup(desc_tag.get_text(), "html.parser").get_text(" ", strip=True)[:300] if desc_tag else ""
                if " - " in title_raw:
                    parts = title_raw.split(" - ")
                    title, company = parts[0].strip(), parts[-1].strip()
                else:
                    title, company = title_raw, "Unknown"
                if title and link:
                    jobs.append(_make_job(title, company, location, link, posted=pub_date, desc=desc, source="Indeed"))
            except Exception:
                pass
    except Exception as e:
        print(f"  [Indeed] Error: {e}")
    _log("Indeed", keyword, location, len(jobs))
    return jobs


# ── LINKEDIN (guest API) ───────────────────────────────────────────────
def scrape_linkedin(keyword, location):
    jobs = []
    try:
        url = (
            f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?"
            f"keywords={quote(keyword)}&location={quote(location)}"
            f"&f_TPR=r{config.DAYS_OLD_MAX * 86400}&sortBy=DD&start=0"
        )
        r = SESSION.get(url, timeout=12)
        if r.status_code != 200:
            print(f"  [LinkedIn] HTTP {r.status_code}")
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
                    jobs.append(_make_job(title, company, loc_str, link, posted=posted, source="LinkedIn"))
            except Exception:
                pass
    except Exception as e:
        print(f"  [LinkedIn] Error: {e}")
    _log("LinkedIn", keyword, location, len(jobs))
    return jobs


# ── GLASSDOOR ──────────────────────────────────────────────────────────
def scrape_glassdoor(keyword, location):
    jobs = []
    try:
        url = (
            f"https://www.glassdoor.co.in/Job/jobs.htm?"
            f"sc.keyword={quote(keyword)}&locT=N&locId=115&"
            f"fromAge={config.DAYS_OLD_MAX}&minSalary=0&includeNoSalaryJobs=true"
        )
        r = SESSION.get(url, headers={**dict(SESSION.headers), "Referer": "https://www.glassdoor.co.in/"}, timeout=12)
        if r.status_code != 200:
            print(f"  [Glassdoor] HTTP {r.status_code}")
            return jobs

        soup = BeautifulSoup(r.content, "html.parser")
        cards = (
            soup.find_all("li", class_=re.compile(r"JobsList_jobListItem|react-job-listing")) or
            soup.find_all("article", attrs={"data-test": re.compile(r"jobListing")})
        )
        for card in cards[:10]:
            try:
                title_el   = card.find(attrs={"data-test": re.compile(r"job-title")}) or \
                             card.find(["a", "span"], class_=re.compile(r"jobTitle|JobCard_jobTitle"))
                company_el = card.find(attrs={"data-test": re.compile(r"employer-name")}) or \
                             card.find(["span", "div"], class_=re.compile(r"employerName|EmployerProfile"))
                link_el    = card.find("a", href=True)
                title   = title_el.get_text(strip=True)   if title_el   else ""
                company = company_el.get_text(strip=True) if company_el else ""
                link    = link_el["href"]                 if link_el    else ""
                if link and link.startswith("/"):
                    link = "https://www.glassdoor.co.in" + link
                if title and link:
                    jobs.append(_make_job(title, company, location, link, source="Glassdoor"))
            except Exception:
                pass
    except Exception as e:
        print(f"  [Glassdoor] Error: {e}")
    _log("Glassdoor", keyword, location, len(jobs))
    return jobs


# ── GOOGLE JOBS ────────────────────────────────────────────────────────
def scrape_google_jobs(keyword, location):
    """Scrape Google Jobs search widget for job listings."""
    jobs = []
    try:
        query = f"{keyword} jobs {location} India"
        url   = f"https://www.google.com/search?q={quote(query)}&ibp=htl;jobs&hl=en&gl=in"
        headers = {
            **dict(SESSION.headers),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Referer": "https://www.google.com/",
        }
        r = SESSION.get(url, headers=headers, timeout=15)
        if r.status_code != 200:
            print(f"  [Google Jobs] HTTP {r.status_code}")
            return jobs

        soup = BeautifulSoup(r.content, "html.parser")

        # Google Jobs widget card selectors (multiple fallbacks)
        cards = (
            soup.find_all("div", class_=re.compile(r"gws-plugins-horizon-jobs__li-ed")) or
            soup.find_all("div", attrs={"data-ved": True, "class": re.compile(r"iFjolb|gws-plugins")}) or
            soup.find_all("li", class_=re.compile(r"iFjolb"))
        )

        for card in cards[:10]:
            try:
                title_el   = card.find(class_=re.compile(r"BjJfJf|sH3znd|jGbdBd"))
                company_el = card.find(class_=re.compile(r"vNEEBe|nJlQNd|sCuL3"))
                loc_el     = card.find(class_=re.compile(r"Qk80Jf|ShLq6|location"))
                link_el    = card.find("a", href=True)

                title   = title_el.get_text(strip=True)   if title_el   else ""
                company = company_el.get_text(strip=True) if company_el else ""
                loc_str = loc_el.get_text(strip=True)     if loc_el     else location
                link    = link_el["href"]                 if link_el    else ""

                # Google wraps job links in /search?q=... — use a stable fingerprint
                if not title:
                    continue
                job_url = link if link.startswith("http") else f"https://www.google.com{link}"
                jobs.append(_make_job(title, company, loc_str, job_url, source="Google Jobs"))
            except Exception:
                pass
    except Exception as e:
        print(f"  [Google Jobs] Error: {e}")
    _log("Google Jobs", keyword, location, len(jobs))
    return jobs


# ── COMPANY CAREER SITES ───────────────────────────────────────────────
def scrape_company_sites():
    """Scrape all configured company career pages for US Tax job links."""
    jobs = []
    for site in getattr(config, "COMPANY_SITES", []):
        name = site.get("name", "Company")
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
                if len(text) < 5 or len(text) > 200:
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
def fetch_all_jobs():
    """
    Fetch jobs from all sources. Deduplicates by URL. Returns newest first.

    Portals:
      - LinkedIn:     PRIORITY_KEYWORDS × all LOCATIONS
      - Naukri:       PRIORITY_KEYWORDS × all LOCATIONS
      - Indeed:       PRIORITY_KEYWORDS × all LOCATIONS
      - Google Jobs:  top 5 keywords × top 3 locations
      - Glassdoor:    top 3 keywords × top 3 locations (bot-protected)
      - Company sites: all 50 companies in COMPANY_SITES
    """
    all_jobs  = []
    seen_urls = set()

    def add(results):
        for job in results:
            key = job.get("url") or job.get("id")
            if key and key not in seen_urls:
                seen_urls.add(key)
                all_jobs.append(job)

    # LinkedIn
    print("\n[LinkedIn] Scanning all keywords × locations...")
    for kw in PRIORITY_KEYWORDS:
        for loc in config.LOCATIONS:
            add(scrape_linkedin(kw, loc))
            _delay()

    # Naukri
    print("\n[Naukri] Scanning all keywords × locations...")
    for kw in PRIORITY_KEYWORDS:
        for loc in config.LOCATIONS:
            add(scrape_naukri(kw, loc))
            _delay()

    # Indeed
    print("\n[Indeed] Scanning all keywords × locations...")
    for kw in PRIORITY_KEYWORDS:
        for loc in config.LOCATIONS:
            add(scrape_indeed(kw, loc))
            _delay()

    # Google Jobs — top 5 keywords × top 3 locations
    print("\n[Google Jobs] Scanning...")
    for kw in PRIORITY_KEYWORDS[:5]:
        for loc in config.LOCATIONS[:3]:
            add(scrape_google_jobs(kw, loc))
            _delay()

    # Glassdoor — limited (heavy bot protection)
    print("\n[Glassdoor] Scanning (limited)...")
    for kw in PRIORITY_KEYWORDS[:3]:
        for loc in config.LOCATIONS[:3]:
            add(scrape_glassdoor(kw, loc))
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
