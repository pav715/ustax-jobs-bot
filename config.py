import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
CHAT_ID   = os.environ.get("CHAT_ID", "")

# TAX PREPARATION: 5 keywords for Phase 1
KEYWORDS = [
    "US Tax",
    "US Taxation",
    "Tax Preparation",
    "Tax Compliance",
    "Tax Reviewer",
]

# 12 CITIES - South First
LOCATIONS = [
    "Hyderabad",
    "Bangalore",
    "Chennai",
    "Kochi",
    "Visakhapatnam",
    "Mumbai",
    "Pune",
    "Delhi",
    "Noida",
    "Gurgaon",
    "Ahmedabad",
    "Kolkata",
]

MAX_JOBS_PER_CYCLE = 15
CHECK_INTERVAL_LABEL = "1 hour"
