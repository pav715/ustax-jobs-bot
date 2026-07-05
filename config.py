import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8714105853:AAEBU3JWHAV8mk17MjSLTYh8W2QO2I-1cts")
CHAT_ID   = os.environ.get("CHAT_ID", "-1003570586532")  # Already correct

# Search exact US Tax role titles to catch all variants
# Filter by description (form numbers + US Tax keywords) to avoid Indian tax jobs
KEYWORDS = [
    # Tax Preparer Level
    "US Tax Preparer",
    "Tax Associate",
    "Tax Analyst",
    "Tax Preparation Specialist",
    "Tax Return Preparer",
    "Individual Tax Preparer",
    "Corporate Tax Preparer",
    "Tax Preparation Analyst",
    "Tax Filing Specialist",
    "Tax Return Specialist",

    # Tax Analyst/Reviewer Level
    "Senior Tax Analyst",
    "Tax Reviewer",
    "Tax Review Analyst",
    "Tax Quality Reviewer",
    "US Tax Compliance Analyst",
    "Federal Tax Analyst",
    "State Tax Analyst",
    "Tax Research Analyst",
    "Tax Technical Analyst",

    # Tax Manager/Senior Level
    "Tax Manager",
    "Senior Tax Associate",
    "Tax Senior",
    "Tax Consultant",
    "Tax Advisory Consultant",
    "Tax Compliance Manager",
    "Tax Operations Manager",
    "Tax Process Manager",
    "US Tax Manager",
    "Tax Engagement Manager",

    # US Tax Testing Level
    "US Tax QA Analyst",
    "US Tax Software Tester",
    "US Tax Quality Assurance Analyst",
    "US Tax Compliance Tester",
    "US Tax Software QA Engineer",
    "US Tax Form Tester",
    "US Tax Regulatory QA Analyst",
    "US Tax E-File QA Analyst",
    "US Tax Software Test Analyst",
    "US Tax Product QA Analyst",
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
