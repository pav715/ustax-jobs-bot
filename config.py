import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
CHAT_ID   = os.environ.get("CHAT_ID", "")

# LinkedIn search keywords — broad US Tax coverage
KEYWORDS = [
    "US Tax",
    "US Taxation",
    "US Tax Analyst",
    "US Tax Associate",
    "US Tax Consultant",
    "Tax Preparation",
    "Tax Compliance",
    "Tax Reviewer",
    "Federal Tax",
    "International Tax",
    "Corporate Tax US",
    "Enrolled Agent",
    "Tax Return Preparer",
    "CPA Tax",
    "US Tax Manager",
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
