import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8714105853:AAEBU3JWHAV8mk17MjSLTYh8W2QO2I-1cts")
CHAT_ID   = os.environ.get("CHAT_ID", "-1003570586532")  # Already correct

# 18 keywords x 8 locations = 144 combinations (kept under ~150 for hourly runs).
# Near-duplicates merged: "Tax Analyst" covers "US Tax Analyst"; "Tax Associate"
# covers "US Tax Associate" / "Senior Tax Associate"; "1040 Tax" etc. anchor forms.
KEYWORDS = [
    "US Tax",
    "US Taxation",
    "Tax Analyst",
    "Tax Associate",
    "Tax Preparer",
    "US Tax Reviewer",
    "Tax Consultant",
    "Tax Compliance",
    "Federal Tax",
    "Tax Senior",
    "Enrolled Agent",
    "International Tax",
    "Expat Tax",
    "Partnership Tax",
    "Corporate Tax US",
    "1040 Tax",
    "1065 Tax",
    "1120 Tax",
]

# India US-Tax delivery hubs + remote. "India" already covers smaller hubs
# (Kochi, Coimbatore, Ahmedabad, Noida, etc.) via LinkedIn's country search,
# and INDIA_LOCATION in run_once.py keeps those cities in the results.
LOCATIONS = [
    "India",
    "Hyderabad",
    "Bangalore",
    "Chennai",
    "Mumbai",
    "Pune",
    "Gurgaon",
    "Remote",
]

MAX_JOBS_PER_CYCLE = 15
