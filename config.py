import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8714105853:AAEBU3JWHAV8mk17MjSLTYh8W2QO2I-1cts")
CHAT_ID   = os.environ.get("CHAT_ID", "-1003570586532")  # Already correct

# Search core US Tax role titles - streamlined for better matching
# Filter by description (form numbers + US Tax keywords) to avoid Indian tax jobs
KEYWORDS = [
    # Tax Preparer Level
    "US Tax Preparer",
    "Tax Associate",
    "Tax Preparation Specialist",
    "Individual Tax Preparer",
    "Tax Return Preparer",

    # Tax Analyst Level
    "Tax Analyst",
    "Tax Compliance Analyst",
    "Tax Filing Analyst",
    "Tax Operations Analyst",
    "Tax Processing Analyst",

    # Senior / Reviewer Level
    "Senior Tax Associate",
    "Tax Reviewer",
    "Tax Senior",
    "Tax Quality Reviewer",
    "Tax Compliance Specialist",

    # Tax QA / E-File / Technical Level
    "Tax QA E-File Analyst",
    "Associate QA E-File Analyst",
    "Tax Software QA Analyst",
    "E-File Compliance Analyst",
    "XML Schema Analyst",
    "Tax Schema Developer",
    "ATS Analyst",
    "Tax Software Tester",
    "Regulatory QA Analyst",
    "Tax Compliance QA",
    "State Tax E-File Analyst",
    "Tax Form QA Analyst",
]

# India US-Tax delivery hubs + remote. "India" already covers smaller hubs
# (Kochi, Coimbatore, Ahmedabad, Noida, etc.) via LinkedIn's country search,
# and INDIA_LOCATION in run_once.py keeps those cities in the results.
LOCATIONS = [
    "Remote",
    "Hyderabad",
    "Bangalore",
    "Chennai",
    "Mumbai",
    "Pune",
    "Gurgaon",
    "Noida",
    "Delhi",
    "Kolkata",
    "Ahmedabad",
    "Jaipur",
    "Indore",
    "Chandigarh",
    "Kochi",
    "Coimbatore",
    "Lucknow",
]

MAX_JOBS_PER_CYCLE = 15
