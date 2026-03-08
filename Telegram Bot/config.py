import os

# ── Telegram ─────────────────────────────────────────────────────────
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
CHAT_ID   = os.environ.get("CHAT_ID", "")

# ── US Tax Job Keywords ───────────────────────────────────────────────
KEYWORDS = [
    # Core US Tax
    "US Tax",
    "US Taxation",
    "US Income Tax",
    "US Tax Laws",
    "Federal Tax Regulations",
    "State Tax Regulations",
    "IRS Regulations",

    # Tax Forms
    "Individual Taxation 1040",
    "Corporate Taxation 1120",
    "Fiduciary Taxation 1041",
    "Partnership Taxation 1065",
    "Tax Form 990",
    "Tax Form 5500",
    "Tax Preparation 1040",
    "Tax Preparation 1041",
    "Tax Preparation 1120",
    "Tax Preparation 1065",

    # Roles
    "Tax Analyst",
    "Tax Preparation",
    "Tax Reviewer",
    "Tax Consultant",
    "Tax Advisory",
    "Tax Compliance",
    "Tax Reporting",
    "Tax Research",
    "Tax Associate",
    "US Tax Associate",
    "Senior Tax Associate",
    "Senior Tax Analyst US Taxation",
    "Regulatory Tax Analyst",
    "Regulatory Analyst US Tax",
    "Tax Subject Matter Expert",
    "Tax SME",
    "Tax Content Analyst",

    # Technical / Software
    "Tax Software Specialist",
    "Tax Forms Processing",
    "Tax E-Filing Compliance",
    "ATS Acceptance Testing Tax",
    "Tax Schema Analysis",
    "Tax Business Rules",
    "Government Tax Liaison",

    # Other
    "Direct Tax",
    "State Tax Nexus",
    "Tax Calculation Accuracy",
    "Tax Policy Monitoring",
]

# ── Locations ─────────────────────────────────────────────────────────
LOCATIONS = [
    # Maharashtra
    "Mumbai",
    "Pune",
    "Nagpur",
    # Telangana
    "Hyderabad",
    # Karnataka
    "Bangalore",
    "Bengaluru",
    # Tamil Nadu
    "Chennai",
    "Coimbatore",
    # Kerala
    "Kochi",
    "Thiruvananthapuram",
    # Andhra Pradesh
    "Visakhapatnam",
    "Vijayawada",
]

# ── Timing ────────────────────────────────────────────────────────────
CHECK_INTERVAL_MINUTES = 5   # GitHub Actions cron: every 5 minutes

# ── Your Profile (used by AI for match scoring) ───────────────────────
USER_PROFILE = (
    # Experience: ~5.5 years in US Tax / Tax Software QA
    "Total Experience: 5 years 6 months in US Taxation and Tax Software QA/E-File. "

    # Current Role
    "Current: Filing Product Programmer 2 at Intuit (Sept 2024–Present), Hyderabad. "
    "Responsibilities: ATS test case preparation and submission to US State Authorities; "
    "comprehensive testing of Lacerte and ProSeries tax software; XML/XSD/EF schema analysis; "
    "tax form editing (state and federal); government liaison with state agencies; "
    "BRMS business rules implementation; production bug resolution (print and e-file). "

    # Previous: Thomson Reuters
    "Previous: Quality Assurance & E-File Analyst at Thomson Reuters (May 2022–Sept 2024, 2yr 5mo). "
    "Responsibilities: ATS submissions for 1041 (HI, IN, ME, NJ, WV) and 990 (FL) forms; "
    "Go-Systems software testing; XML/XSD schema updates; bug management via Visual Studio; "
    "Created BRMS Logic Writer AI chain — featured in Thomson Reuters All Company community. "
    "Awards: Surge Award 2024, Shine Award 2023 & 2024, Ignite Award 2022. "

    # Previous: H&R Block
    "Previous: Jr. Associate Regulatory Analyst at H&R Block India (Oct 2020–Mar 2022, 1yr 6mo). "
    "Responsibilities: Monitoring state and federal US tax regulatory changes; "
    "updating tax software for compliance; testing software updates; regulatory documentation. "

    # First role
    "Previous: US Tax Preparer at Advantage One Tax Consulting Inc. (Oct 2019–Apr 2020, 7mo). "
    "Responsibilities: Preparing individual tax returns, client interaction, e-filing, compliance. "

    # Key technical skills
    "Technical Skills: ATS acceptance testing, XML/XSD schemas, EF schema analysis, "
    "Go-Systems, Lacerte, ProSeries, BRMS, Visual Studio, AI chain development, Python. "
    "Tax Forms: 1041 (Fiduciary), 990 (Exempt Org), 1040 (Individual), state/federal forms. "
    "Domains: Tax software QA, e-file compliance, regulatory analysis, government liaison. "

    # Education
    "Education: B.Com (Computer Applications), St. Francis Xavier Degree College, 2019. "

    # Location & preferences
    "Location: Hyderabad, Telangana, India. "
    "Open to: On-site / Hybrid roles in Hyderabad, Bangalore, Chennai, Mumbai, Pune or South India."
)

# Only send jobs where AI match score >= this value (0 = send all)
MIN_MATCH_SCORE = 50

# Max jobs to send per cycle (prevents spam on first big batch)
MAX_JOBS_PER_CYCLE = 15

# ── India Job Portals (HTML scrape) ───────────────────────────────────
INDIA_PORTALS = [
    {"name": "Foundit",      "url": "https://www.foundit.in/srp/results?query=US+Tax&locations=India&experience=0&freshness=1"},
    {"name": "Shine",        "url": "https://www.shine.com/job-search/us-tax-jobs-in-india"},
    {"name": "TimesJobs",    "url": "https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&txtKeywords=US+Tax&sequence=2&startPage=1"},
    {"name": "AmbitionBox",  "url": "https://www.ambitionbox.com/jobs/search?q=US+Tax&location=India"},
]

# ── Company Career Sites (HTML scrape — companies not on Workday) ─────
COMPANY_SITES = [
    # ── Big 4 ──
    {"name": "EY",          "url": "https://careers.ey.com/ey/search/?q=US+Tax&location=India&startrow=0"},
    {"name": "KPMG India",  "url": "https://www.in.kpmg.com/careers/search-jobs.html#/?search=US+Tax"},
    # ── IT / BPO ──
    {"name": "Cognizant",   "url": "https://careers.cognizant.com/global-en/jobs/?keyword=US+Tax"},
    {"name": "WNS",         "url": "https://wnscareers.wns.com/jobs?keywords=US+Tax&location=India"},
    {"name": "EXL Service", "url": "https://careers.exlservice.com/jobs?keywords=US+Tax"},
    {"name": "Hexaware",    "url": "https://hexaware.com/careers/job-search/?search=US+Tax"},
    # ── Tax Software ──
    {"name": "Sovos",       "url": "https://careers.sovos.com/jobs?keywords=tax&location=India"},
    {"name": "Avalara",     "url": "https://careers.avalara.com/jobs?keywords=US+Tax"},
]
