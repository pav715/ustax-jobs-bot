# ── Telegram ─────────────────────────────────────────────────────────
BOT_TOKEN = "8534310272:AAEJKeBKc7t92nb5xd_XNNVWrYIeOvqlIH0"
CHAT_ID   = "-1003570586532"   # auto-filled on first run

# ── US Tax Job Keywords ───────────────────────────────────────────────
KEYWORDS = [
    "US Tax",
    "US Taxation",
    "Individual Taxation 1040",
    "Corporate Taxation 1120",
    "Fiduciary Taxation 1041",
    "Tax Preparation",
    "Tax Reviewer",
    "Tax Analyst",
    "Regulatory Tax Analyst",
    "Tax Compliance",
    "Federal Tax Regulations",
    "State Tax Regulations",
    "US Tax Laws",
    "Tax Advisory",
    "Tax Consultant",
    "Tax Reporting",
    "IRS Regulations",
    "Tax Research",
    "Tax Software Specialist",
    "Tax Forms Processing",
    "Government Tax Liaison",
    "Tax E-Filing Compliance",
    "ATS Acceptance Testing Tax",
    "Tax Schema Analysis",
    "Tax Business Rules",
    "Tax Policy Monitoring",
    "Direct Tax",
    "State Tax Nexus",
    "Tax Calculation Accuracy",
    "US Income Tax",
    "Senior Tax Analyst US Taxation",
    "US Tax Associate",
    "Senior Tax Associate",
    "Tax Content Analyst",
    "Regulatory Analyst US Tax",
    "Tax Subject Matter Expert",
    "Tax SME",
]

# ── Locations (priority order) ────────────────────────────────────────
# Only jobs from these cities/states/remote should be posted.
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
# Check every 1 minute so updates come quickly
CHECK_INTERVAL_MINUTES = 1

# ── Filters ──────────────────────────────────────────────────────────
# Limit to roughly "last 2 days" of jobs from portals.
DAYS_OLD_MAX = 2

# ── UI / messaging options ───────────────────────────────────────────
# If True, bot sends a "Bot Started" message each time it starts.
# You said you do NOT want this, so keep it False.
SHOW_STARTUP_MESSAGE = False

# ── Company career sites (optional) ──────────────────────────────────
# Add specific companies you care about here. The scraper will visit
# these pages and try to extract US Tax jobs in addition to job boards.
# Example entry:
# {
#     "name": "Example Tax Co",
#     "url": "https://careers.example.com/jobs?search=US+Tax",
# }
COMPANY_SITES = [
    # Fill this with your target companies' careers/job URLs.
]
