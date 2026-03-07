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
    "Pune",
    "Ahmedabad",
    "Gujarat",
    "Kerala",
    "Mumbai",
    "Chennai",
    "Tamil Nadu",
    "Remote",
]

# ── Timing ────────────────────────────────────────────────────────────
CHECK_INTERVAL_MINUTES = 1   # local; GitHub Actions minimum is 5 min

# ── Filters ──────────────────────────────────────────────────────────
DAYS_OLD_MAX = 2

# ── Messaging ────────────────────────────────────────────────────────
SHOW_STARTUP_MESSAGE = False

# ── Company Career Sites ──────────────────────────────────────────────
# Big 4 & Accounting Firms
# IT / BPO / GCC companies
# Tax Software companies
# US captive centers in India
COMPANY_SITES = [
    # ── Big 4 ──
    {"name": "Deloitte",            "url": "https://apply.deloitte.com/careers/SearchJobs/US%20Tax?3_104_3=India"},
    {"name": "EY",                  "url": "https://careers.ey.com/ey/search/?q=US+Tax&location=India"},
    {"name": "KPMG India",          "url": "https://kpmg.com/in/en/home/careers/job-search.html?keyword=US+Tax"},
    {"name": "PwC India",           "url": "https://www.pwc.in/careers/experienced-join-us.html"},

    # ── Mid-Tier Accounting ──
    {"name": "Grant Thornton",      "url": "https://www.grantthornton.in/careers/current-openings/?search=US+Tax"},
    {"name": "RSM",                 "url": "https://rsmus.wd1.myworkdayjobs.com/en-US/RSM/jobs?q=US+Tax"},
    {"name": "BDO",                 "url": "https://www.bdo.in/en-gb/careers/job-openings"},
    {"name": "Mazars",              "url": "https://careers.mazars.com/jobs?q=US+Tax&l=India"},
    {"name": "Forvis Mazars",       "url": "https://careers.forvismazars.com/jobs?q=US+Tax&l=India"},
    {"name": "CohnReznick",         "url": "https://cohnreznick.wd1.myworkdayjobs.com/en-US/CohnReznick_Careers/jobs?q=US+Tax"},
    {"name": "Moss Adams",          "url": "https://mossadams.wd1.myworkdayjobs.com/en-US/MossAdams/jobs?q=US+Tax"},
    {"name": "Baker Tilly",         "url": "https://bakertilly.wd1.myworkdayjobs.com/en-US/bakertillyus/jobs?q=US+Tax"},
    {"name": "Plante Moran",        "url": "https://plantemoran.wd1.myworkdayjobs.com/en-US/PlanteAndMoran/jobs?q=tax"},
    {"name": "Citrin Cooperman",    "url": "https://citrincooperman.wd1.myworkdayjobs.com/en-US/CitrinCoopermanCareers/jobs?q=US+Tax"},

    # ── IT / BPO / GCC ──
    {"name": "Wipro",               "url": "https://careers.wipro.com/careers-home/jobs?q=US+Tax&l=India"},
    {"name": "Infosys BPM",         "url": "https://www.infosysbpm.com/careers/job-search.html?keyword=US+Tax"},
    {"name": "TCS",                 "url": "https://ibegin.tcs.com/iBegin/jobs?keyword=US+Tax&location=India"},
    {"name": "HCL Technologies",    "url": "https://www.hcltech.com/careers/search-jobs?keyword=US+Tax"},
    {"name": "Cognizant",           "url": "https://careers.cognizant.com/global/en/search-results?keywords=US+Tax&location=India"},
    {"name": "Accenture",           "url": "https://www.accenture.com/in-en/careers/jobsearch?jk=US+Tax&l=India"},
    {"name": "Capgemini",           "url": "https://www.capgemini.com/in-en/careers/job-search/?search_term=US+Tax&country=India"},
    {"name": "Genpact",             "url": "https://jobs.genpact.com/jobs?q=US+Tax&l=India"},
    {"name": "WNS Global",          "url": "https://www.wns.com/careers/job-search?keyword=US+Tax"},
    {"name": "EXL Service",         "url": "https://jobs.exlservice.com/jobs?q=US+Tax&l=India"},
    {"name": "Mphasis",             "url": "https://careers.mphasis.com/jobs?q=US+Tax"},
    {"name": "Conduent",            "url": "https://jobs.conduent.com/jobs?q=US+Tax&l=India"},
    {"name": "Syntel",              "url": "https://www.syntelinc.com/en-us/careers/open-positions?keyword=US+Tax"},
    {"name": "Hexaware",            "url": "https://hexaware.com/careers/?search=US+Tax"},
    {"name": "Firstsource",         "url": "https://jobs.firstsource.com/jobs?q=US+Tax"},
    {"name": "iGate / Mastech",     "url": "https://mastechdigital.com/careers/?search=tax"},

    # ── Tax Software Companies ──
    {"name": "Wolters Kluwer",      "url": "https://careers.wolterskluwer.com/jobs?q=US+Tax&l=India"},
    {"name": "Thomson Reuters",     "url": "https://thomsonreuters.wd5.myworkdayjobs.com/en-US/External_Career_Site/jobs?q=US+Tax"},
    {"name": "Vertex Inc",          "url": "https://vertexinc.wd1.myworkdayjobs.com/en-US/vertex_careers/jobs?q=tax"},
    {"name": "H&R Block",           "url": "https://www.hrblock.com/corporate/careers/jobs/?keyword=tax+preparation"},
    {"name": "Jackson Hewitt",      "url": "https://www.jacksonhewitt.com/tax-help/about-us/careers/?q=tax"},
    {"name": "Drake Software",      "url": "https://drakesoftware.com/company/careers/"},
    {"name": "Avalara",             "url": "https://avalara.wd1.myworkdayjobs.com/en-US/Avalara/jobs?q=tax"},
    {"name": "Ryan LLC",            "url": "https://ryan.wd5.myworkdayjobs.com/en-US/Ryan/jobs?q=US+Tax"},
    {"name": "Sovos",               "url": "https://sovos.com/careers/open-positions/?search=tax"},
    {"name": "Bloomberg Tax",       "url": "https://careers.bloombergindustry.com/jobs?q=US+Tax"},

    # ── US Captives / GCC in India ──
    {"name": "Goldman Sachs",       "url": "https://higher.gs.com/roles?q=tax&l=India"},
    {"name": "JPMorgan Chase",      "url": "https://jpmc.fa.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1001/jobs?keyword=US+Tax"},
    {"name": "Citibank India",      "url": "https://jobs.citi.com/jobs?q=US+Tax&l=India"},
    {"name": "Bank of America",     "url": "https://careers.bankofamerica.com/en-us/search-jobs/India/282/0/6252001/22.3511/78.6677/50/jobs?q=US+Tax"},
    {"name": "Wells Fargo",         "url": "https://www.wellsfargojobs.com/en/jobs/?keyword=US+Tax&location=India"},
    {"name": "American Express",    "url": "https://aexp.eightfold.ai/careers?query=US+Tax&location=India"},
    {"name": "State Street",        "url": "https://statestreet.wd1.myworkdayjobs.com/en-US/Global/jobs?q=US+Tax&locations=India"},
    {"name": "BNY Mellon",          "url": "https://bnymellon.wd1.myworkdayjobs.com/en-US/BNY_Mellon_Careers/jobs?q=US+Tax&locations=India"},
    {"name": "Northern Trust",      "url": "https://northerntrust.wd5.myworkdayjobs.com/en-US/Careers/jobs?q=US+Tax&locations=India"},
]
