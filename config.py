import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8714105853:AAEBU3JWHAV8mk17MjSLTYh8W2QO2I-1cts")
CHAT_ID   = os.environ.get("CHAT_ID", "-1003570586532")

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
    # South (5)
    "Hyderabad",
    "Bangalore",
    "Chennai",
    "Kochi",
    "Visakhapatnam",
    # West & North (7)
    "Mumbai",
    "Pune",
    "Delhi",
    "Noida",
    "Gurgaon",
    "Ahmedabad",
    "Kolkata",
]

MAX_JOBS_PER_CYCLE = 15
