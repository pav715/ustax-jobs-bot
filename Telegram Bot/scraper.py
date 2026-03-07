"""
Job scraper — uses requests + BeautifulSoup (no browser needed).
Sources: Naukri, LinkedIn public, Indeed India, Glassdoor
"""
import requests
import hashlib
import re
import time
import random
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import config

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def job_id(url, title, company):
    """Unique fingerprint for a job — used to detect duplicates."""
    raw = f"{url}{title}{company}".lower().strip()
    return hashlib.md5(raw.encode()).hexdigest()[:16]


def delay():
    # Short delay to be polite to servers but keep runs fast
    time.sleep(random.uniform(0.2, 0.5))


# ── NAUKRI ────────────────────────────────────────────────────────────
def scrape_naukri(keyword, location):
    jobs = []
    try:
        kw  = keyword.replace(" ", "%20")
        loc = location.replace(" ", "%20")
        url = (
            f"https://www.naukri.com/jobapi/v3/search?"
            f"noOfResults=20&urlType=search_by_keyword&searchType=adv"
            f"&keyword={kw}&location={loc}&experience=0"
            f"&jobAge={config.DAYS_OLD_MAX}&src=jobsearchDesk&latLong="
        )
        r = requests.get(url, headers={**HEADERS, "appid": "109", "systemid": "109"}, timeout=10)
        data = r.json()
        for j in data.get("jobDetails", []):
            title   = j.get("title", "").strip()
            company = j.get("companyName", "").strip()
            loc_str = ", ".join(j.get("placeholders", [{}])[0].get("label", "").split(",")[:2]) if j.get("placeholders") else location
            jurl    = f"https://www.naukri.com{j.get('jdURL', '')}"
            posted  = j.get("footerPlaceholderLabel", "")
            exp     = j.get("experienceText", "")
            skills  = ", ".join([s.get("label", "") for s in j.get("tagsAndSkills", [])[:5]])
            desc_html = j.get("jobDescription", "")
            desc    = BeautifulSoup(desc_html, "html.parser").get_text(" ", strip=True)[:300]

            jobs.append({
                "id":       job_id(jurl, title, company),
                "title":    title,
                "company":  company,
                "location": loc_str or location,
                "url":      jurl,
                "posted":   posted,
                "experience": exp,
                "skills":   skills or "Tax, Compliance, MS Excel",
                "description": desc,
                "source":   "Naukri",
                "fetched_at": datetime.now().isoformat(),
            })
    except Exception as e:
        print(f"  [Naukri] Error ({keyword}/{location}): {e}")
    return jobs


# ── INDEED INDIA (RSS) ────────────────────────────────────────────────
def scrape_indeed(keyword, location):
    jobs = []
    try:
        kw  = keyword.replace(" ", "+")
        loc = location.replace(" ", "+")
        url = f"https://in.indeed.com/rss?q={kw}&l={loc}&sort=date&fromage={config.DAYS_OLD_MAX}"
        r   = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.content, "xml")
        for item in soup.find_all("item")[:15]:
            title   = item.find("title").get_text(strip=True) if item.find("title") else ""
            link    = item.find("link").get_text(strip=True) if item.find("link") else ""
            company_tag = item.find("source")
            company = company_tag.get_text(strip=True) if company_tag else "Unknown"
            pub_date = item.find("pubDate")
            posted  = pub_date.get_text(strip=True) if pub_date else ""
            desc_tag = item.find("description")
            desc    = BeautifulSoup(desc_tag.get_text(), "html.parser").get_text(" ", strip=True)[:300] if desc_tag else ""

            # Strip job title prefix like "Tax Analyst - "
            title = re.sub(r"^[^-]+ - ", "", title).strip() if " - " in title[:50] else title

            jobs.append({
                "id":       job_id(link, title, company),
                "title":    title,
                "company":  company,
                "location": location,
                "url":      link,
                "posted":   posted,
                "experience": "",
                "skills":   "Tax, Compliance",
                "description": desc,
                "source":   "Indeed",
                "fetched_at": datetime.now().isoformat(),
            })
    except Exception as e:
        print(f"  [Indeed] Error ({keyword}/{location}): {e}")
    return jobs


# ── LINKEDIN (public search) ──────────────────────────────────────────
def scrape_linkedin(keyword, location):
    jobs = []
    try:
        kw  = keyword.replace(" ", "%20")
        loc = location.replace(" ", "%20")
        url = (
            f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?"
            f"keywords={kw}&location={loc}&f_TPR=r{config.DAYS_OLD_MAX * 86400}"
            f"&sortBy=DD&start=0"
        )
        r    = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.content, "html.parser")
        for card in soup.find_all("li")[:15]:
            try:
                title   = card.find("h3").get_text(strip=True) if card.find("h3") else ""
                company = card.find("h4").get_text(strip=True) if card.find("h4") else ""
                loc_tag = card.find("span", class_=re.compile("job-search-card__location"))
                loc_str = loc_tag.get_text(strip=True) if loc_tag else location
                link_tag = card.find("a", href=True)
                link    = link_tag["href"].split("?")[0] if link_tag else ""
                time_tag = card.find("time")
                posted  = time_tag["datetime"] if time_tag and time_tag.get("datetime") else ""
                if not title or not link:
                    continue
                jobs.append({
                    "id":       job_id(link, title, company),
                    "title":    title,
                    "company":  company,
                    "location": loc_str,
                    "url":      link,
                    "posted":   posted,
                    "experience": "",
                    "skills":   "Tax, Compliance",
                    "description": "",
                    "source":   "LinkedIn",
                    "fetched_at": datetime.now().isoformat(),
                })
            except Exception:
                pass
    except Exception as e:
        print(f"  [LinkedIn] Error ({keyword}/{location}): {e}")
    return jobs


# ── GLASSDOOR (public HTML) ───────────────────────────────────────────
def scrape_glassdoor(keyword, location):
    jobs = []
    try:
        kw  = keyword.replace(" ", "-").lower()
        url = f"https://www.glassdoor.co.in/Job/{location.lower()}-{kw}-jobs-SRCH_IL.0,{len(location)}_IC2940586_KO{len(location)+1},{len(location)+1+len(keyword)}.htm"
        r   = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.content, "html.parser")
        for card in soup.find_all("li", class_=re.compile("JobsList_jobListItem"))[:10]:
            try:
                title   = card.find("a", class_=re.compile("jobLink|JobCard_jobTitle")).get_text(strip=True)
                company = card.find("span", class_=re.compile("EmployerProfile|jobEmpolyerName")).get_text(strip=True)
                link_tag = card.find("a", href=True)
                link    = "https://www.glassdoor.co.in" + link_tag["href"] if link_tag else ""
                if not title or not link:
                    continue
                jobs.append({
                    "id":       job_id(link, title, company),
                    "title":    title,
                    "company":  company,
                    "location": location,
                    "url":      link,
                    "posted":   "",
                    "experience": "",
                    "skills":   "Tax, Compliance",
                    "description": "",
                    "source":   "Glassdoor",
                    "fetched_at": datetime.now().isoformat(),
                })
            except Exception:
                pass
    except Exception as e:
        print(f"  [Glassdoor] Error ({keyword}/{location}): {e}")
    return jobs


# ── COMPANY CAREER SITES (CONFIG-DRIVEN) ───────────────────────────────
def scrape_company_sites():
    """
    Scrape configured company career/job pages from config.COMPANY_SITES.

    This does NOT auto-discover “all” companies on the internet; instead,
    you manually list the companies you care about in config.COMPANY_SITES.
    """
    jobs = []
    for site in getattr(config, "COMPANY_SITES", []):
        name = site.get("name", "Company")
        url  = site.get("url")
        if not url:
            continue
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            if r.status_code != 200:
                continue
            soup = BeautifulSoup(r.text, "html.parser")

            # Very generic heuristic: look for links that contain “tax”
            # in their text or aria-label and that look like job links.
            for a in soup.find_all("a", href=True):
                text = a.get_text(" ", strip=True)
                aria = a.get("aria-label", "")
                label = f"{text} {aria}".lower()
                if "tax" not in label:
                    continue

                job_title = text or aria or "Tax Role"
                job_url   = a["href"]
                if job_url.startswith("/"):
                    # make absolute
                    from urllib.parse import urljoin
                    job_url = urljoin(url, job_url)

                jobs.append({
                    "id":       job_id(job_url, job_title, name),
                    "title":    job_title,
                    "company":  name,
                    "location": "India / Remote",
                    "url":      job_url,
                    "posted":   "",
                    "experience": "",
                    "skills":   "Tax, Compliance",
                    "description": "",
                    "source":   f"{name} Careers",
                    "fetched_at": datetime.now().isoformat(),
                })
        except Exception as e:
            print(f"  [Company] Error ({name}): {e}")
    return jobs


# ── MAIN SCRAPE FUNCTION ──────────────────────────────────────────────
def fetch_all_jobs():
    """
    Fetch all new jobs from fast, reliable sources.

    Simplified for speed:
    - Only use LinkedIn (other portals currently return 0 for your filters).
    - Use a single strong keyword "US Tax" across all configured LOCATIONS.
    - Still include any configured company career sites.
    """
    all_jobs = []
    seen_urls = set()

    # LinkedIn across all locations
    for location in config.LOCATIONS:
        try:
            results = scrape_linkedin("US Tax", location)
            for job in results:
                url = job.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    all_jobs.append(job)
        except Exception:
            pass
        delay()

    # Company career sites (independent of keyword/location loops)
    company_jobs = scrape_company_sites()
    for job in company_jobs:
        url = job.get("url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            all_jobs.append(job)

    # Sort newest first (by fetched_at as fallback)
    all_jobs.sort(key=lambda j: j.get("posted", "") or j.get("fetched_at", ""), reverse=True)
    return all_jobs
