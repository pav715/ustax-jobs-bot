import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8714105853:AAEBU3JWHAV8mk17MjSLTYh8W2QO2I-1cts")
CHAT_ID   = os.environ.get("CHAT_ID", "-1003570586532")  # Already correct

# 18 keywords x 8 locations = 144 combinations (kept under ~150 for hourly runs).
# Near-duplicates merged: "Tax Analyst" covers "US Tax Analyst"; "Tax Associate"
# covers "US Tax Associate" / "Senior Tax Associate"; "1040 Tax" etc. anchor forms.
KEYWORDS = [
    "1040",
    "1041",
    "1065",
    "1120",
    "US Tax Preparer",
    "US Tax Analyst",
    "Enrolled Agent",
    "CPA Tax",
    "IRS",
]

# India US-Tax delivery hubs + remote. "India" already covers smaller hubs
# (Kochi, Coimbatore, Ahmedabad, Noida, etc.) via LinkedIn's country search,
# and INDIA_LOCATION in run_once.py keeps those cities in the results.
LOCATIONS = [
    "Remote",
]

MAX_JOBS_PER_CYCLE = 15
