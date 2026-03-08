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

# ── Workday ATS Companies ─────────────────────────────────────────────
# Format: tenant = subdomain, path = career site path, wd = workday instance number
# API: POST https://{tenant}.wd{wd}.myworkdayjobs.com/wday/cxs/{tenant}/{path}/jobs
WORKDAY_COMPANIES = [
    # ── Tax Software ──
    {"name": "Thomson Reuters",   "tenant": "thomsonreuters",  "path": "External_Career_Site",   "wd": 1},
    {"name": "Intuit",            "tenant": "intuit",          "path": "Intuit_Careers",         "wd": 1},
    {"name": "H&R Block",         "tenant": "hrblock",         "path": "External",               "wd": 5},
    {"name": "Wolters Kluwer",    "tenant": "wolterskluwer",   "path": "wkcareers",              "wd": 5},
    {"name": "Vertex Inc",        "tenant": "vertexinc",       "path": "Vertex_Careers",         "wd": 1},
    {"name": "Ryan LLC",          "tenant": "ryan",            "path": "Ryan_Careers",           "wd": 1},
    # ── Big 4 / Accounting ──
    {"name": "Deloitte",          "tenant": "deloitte",        "path": "Deloitte-Careers",       "wd": 1},
    {"name": "KPMG",              "tenant": "kpmg",            "path": "campus",                 "wd": 3},
    {"name": "Grant Thornton",    "tenant": "grantthornton",   "path": "GrantThorntonCareers",   "wd": 1},
    {"name": "RSM",               "tenant": "rsm",             "path": "RSM_Careers",            "wd": 1},
    # ── IT / BPO ──
    {"name": "Cognizant",         "tenant": "cognizant",       "path": "Cognizant_Careers",      "wd": 1},
    {"name": "Genpact",           "tenant": "genpact",         "path": "Genpact_Careers",        "wd": 1},
    {"name": "Wipro",             "tenant": "wipro",           "path": "External",               "wd": 3},
    {"name": "Accenture",         "tenant": "accenture",       "path": "AccentureJobs",          "wd": 3},
    {"name": "Mphasis",           "tenant": "mphasis",         "path": "Mphasis_Careers",        "wd": 1},
    # ── Financial Services (US captives in India — large tax teams) ──
    {"name": "BNY Mellon",        "tenant": "bnymellon",       "path": "Global",                 "wd": 1},
    {"name": "State Street",      "tenant": "statestreet",     "path": "Global",                 "wd": 1},
    {"name": "Northern Trust",    "tenant": "northerntrust",   "path": "NT",                     "wd": 5},
    {"name": "Vanguard",          "tenant": "vanguard",        "path": "vanguard",               "wd": 5},
    {"name": "Fidelity",          "tenant": "fidelity",        "path": "Fidelity",               "wd": 5},
    {"name": "Wells Fargo",       "tenant": "wellsfargo",      "path": "WellsFargoJobs",         "wd": 5},
    {"name": "Citi",              "tenant": "citi",            "path": "Citi_Careers",           "wd": 5},
    {"name": "BlackRock",         "tenant": "blackrock",       "path": "BlackRock",              "wd": 1},
    {"name": "Morgan Stanley",    "tenant": "morganstanley",   "path": "morganstanley",          "wd": 1},
    {"name": "Charles Schwab",    "tenant": "charlesschwab",   "path": "Careers",                "wd": 1},
]

# ── Company Career Sites ──────────────────────────────────────────────
# Big 4 & Accounting Firms
# IT / BPO / GCC companies
# Tax Software companies
# US captive centers in India
COMPANY_SITES = [
    # ── Big 4 (verified working) ──
    {"name": "Deloitte",        "url": "https://apply.deloitte.com/careers/SearchJobs/US%20Tax?3_104_3=India"},
    {"name": "EY",              "url": "https://careers.ey.com/ey/search/?q=US+Tax&location=India&startrow=0"},
    {"name": "KPMG",            "url": "https://www.kpmgcareers.in/job-search-results/?keyword=US+Tax"},
    {"name": "PwC",             "url": "https://www.pwc.in/careers/experienced-join-us/search-jobs.html?q=US+Tax"},

    # ── IT / BPO ──
    {"name": "Wipro",           "url": "https://careers.wipro.com/careers-home/jobs?q=US+Tax"},
    {"name": "Cognizant",       "url": "https://careers.cognizant.com/global/en/search-results?keywords=US+Tax"},
    {"name": "Genpact",         "url": "https://www.genpact.com/careers/results?keyword=US+Tax&location=India"},
    {"name": "WNS",             "url": "https://www.wns.com/careers/job-search?keyword=US+Tax"},
    {"name": "EXL Service",     "url": "https://www.exlservice.com/careers/job-search?keyword=US+Tax"},
    {"name": "Hexaware",        "url": "https://hexaware.com/careers/?search=tax"},

    # ── Tax Software ──
    {"name": "Wolters Kluwer",  "url": "https://careers.wolterskluwer.com/jobs?q=US+Tax&location=India"},
    {"name": "Sovos",           "url": "https://sovos.com/careers/open-positions/?search=tax"},
    {"name": "Avalara",         "url": "https://www.avalara.com/us/en/about/jobs/job-listing.html?keyword=tax"},
]
