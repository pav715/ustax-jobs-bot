import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8714105853:AAEBU3JWHAV8mk17MjSLTYh8W2QO2I-1cts")
CHAT_ID   = os.environ.get("CHAT_ID", "-1003570586532")  # Already correct

# Broad search terms - filter by description keywords (3+ matches required)
# These are just to get initial results - ACTUAL filtering happens by description
KEYWORDS = [
    "tax",
    "job",
]
    "Tax Digital Consultant",

    # Tax Senior / Manager (61-75)
    "Tax Senior",
    "US Tax Senior",
    "Senior Tax Specialist",
    "Tax Manager",
    "US Tax Manager",
    "Senior Tax Manager",
    "Tax Compliance Manager",
    "Tax Operations Manager",
    "Tax Planning Manager",
    "Tax Reporting Manager",
    "Tax Supervisor",
    "Tax Team Lead",
    "Tax Practice Manager",
    "Tax Engagement Manager",
    "Tax Process Manager",

    # Tax Specialist (76-85)
    "Tax Specialist",
    "US Tax Specialist",
    "Senior Tax Specialist",
    "Tax Compliance Specialist",
    "Tax Filing Specialist",
    "Tax Regulatory Specialist",
    "Tax Operations Specialist",
    "Tax Technology Specialist",
    "Tax Research Specialist",
    "Tax Advisory Specialist",

    # US Taxation (86-100)
    "US Taxation Analyst",
    "US Taxation Associate",
    "US Taxation Consultant",
    "US Taxation Specialist",
    "US Taxation Manager",
    "US Taxation Senior",
    "US Individual Tax Analyst",
    "US Corporate Tax Analyst",
    "US Partnership Tax Analyst",
    "US International Tax Analyst",
    "US Indirect Tax Analyst",
    "US Direct Tax Analyst",
    "US Tax Compliance Specialist",
    "US Tax Filing Analyst",
    "US Tax Operations Analyst",
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
