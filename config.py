import os

# ── Telegram ─────────────────────────────────────────────────────────
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8534310272:AAEJKeBKc7t92nb5xd_XNNVWrYIeOvqlIH0")
CHAT_ID   = os.environ.get("CHAT_ID", "-1003570586532")

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
    "Hyderabad",
    "Bangalore",
    "Bengaluru",
    "Chennai",
    "Tamil Nadu",
    "Kerala",
    "Remote",
]

# ── Timing ────────────────────────────────────────────────────────────
CHECK_INTERVAL_MINUTES = 5   # GitHub Actions cron: every 5 minutes

# ── Your Profile (used by AI for match scoring) ───────────────────────
USER_PROFILE = (
    "6 years US Tax experience: Tax Preparer → H&R Block → Thomson Reuters → "
    "Intuit (current: Filing Product Programmer 2). "
    "Skills: 1040, 1041, 1120, 1065, 990, 5500, IRS, XML/XSD schemas, "
    "ATS acceptance testing, E-file approvals, Tax software development, Python. "
    "Location: Hyderabad, India. Education: B.Com Computer 2019."
)

# Only send jobs where AI match score >= this value (0 = send all)
MIN_MATCH_SCORE = 50

# Max jobs to send per cycle (prevents spam on first big batch)
MAX_JOBS_PER_CYCLE = 15

# ── Workday ATS Companies (verified URLs from myworkdayjobs.com) ──────
# API: POST https://{tenant}.wd{wd}.myworkdayjobs.com/wday/cxs/{tenant}/{path}/jobs
WORKDAY_COMPANIES = [
    # ── Tax Software (verified) ──
    {"name": "Thomson Reuters",   "tenant": "thomsonreuters",  "path": "External_Career_Site",   "wd": 5},
    {"name": "Intuit",            "tenant": "intuit",          "path": "Intuit_Careers",         "wd": 1},
    {"name": "H&R Block",         "tenant": "hrblock",         "path": "External",               "wd": 5},
    {"name": "Wolters Kluwer",    "tenant": "wolterskluwer",   "path": "wkcareers",              "wd": 5},
    {"name": "Vertex Inc",        "tenant": "vertexinc",       "path": "Vertex_Careers",         "wd": 1},
    {"name": "Ryan LLC",          "tenant": "ryan",            "path": "RyanCareers",            "wd": 1},
    # ── Big 4 / Accounting ──
    {"name": "Deloitte",          "tenant": "deloitte",        "path": "Deloitte-Careers",       "wd": 1},
    {"name": "PwC",               "tenant": "pwc",             "path": "Global_Campus_Careers",  "wd": 3},
    {"name": "Grant Thornton",    "tenant": "grantthornton",   "path": "GrantThorntonCareers",   "wd": 1},
    {"name": "RSM",               "tenant": "rsm",             "path": "RSM_Careers",            "wd": 1},
    # ── IT / BPO (verified) ──
    {"name": "Accenture",         "tenant": "accenture",       "path": "AccentureCareers",       "wd": 103},
    {"name": "Genpact",           "tenant": "genpact",         "path": "Genpact_Careers",        "wd": 1},
    {"name": "Wipro",             "tenant": "wipro",           "path": "External",               "wd": 3},
    {"name": "Mphasis",           "tenant": "mphasis",         "path": "Mphasis_Careers",        "wd": 1},
    # ── Financial Services — US captives with large India tax teams (verified) ──
    {"name": "Fidelity",          "tenant": "fmr",             "path": "FidelityCareers",        "wd": 1},
    {"name": "Northern Trust",    "tenant": "ntrs",            "path": "northerntrust",          "wd": 1},
    {"name": "Vanguard",          "tenant": "vanguard",        "path": "vanguard_external",      "wd": 5},
    {"name": "BNY Mellon",        "tenant": "bnymellon",       "path": "Global",                 "wd": 1},
    {"name": "State Street",      "tenant": "statestreet",     "path": "Global",                 "wd": 1},
    {"name": "Wells Fargo",       "tenant": "wellsfargo",      "path": "WellsFargoJobs",         "wd": 5},
    {"name": "Citi",              "tenant": "citi",            "path": "Citi_Careers",           "wd": 5},
    {"name": "BlackRock",         "tenant": "blackrock",       "path": "BlackRock",              "wd": 1},
    {"name": "Morgan Stanley",    "tenant": "morganstanley",   "path": "morganstanley",          "wd": 1},
    {"name": "Charles Schwab",    "tenant": "charlesschwab",   "path": "Careers",                "wd": 1},
]

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
