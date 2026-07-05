import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8714105853:AAEBU3JWHAV8mk17MjSLTYh8W2QO2I-1cts")
CHAT_ID   = os.environ.get("CHAT_ID", "-1003570586532")  # Already correct

# 100 US Tax Preparation roles + 2 catchall
# Focus: Tax Preparation, Filing, Compliance, Analysis across all levels
KEYWORDS = [
    # Catchall - matches any "US Tax XXX" or "US Taxation XXX" role
    "US Tax",
    "US Taxation",

    # Tax Preparer (1-15)
    "US Tax Preparer",
    "Tax Preparer",
    "Senior Tax Preparer",
    "Individual Tax Preparer",
    "Tax Return Preparer",
    "Tax Preparation Specialist",
    "Tax Filing Specialist",
    "Tax Preparation Analyst",
    "Tax Return Specialist",
    "Federal Tax Preparer",
    "State Tax Preparer",
    "Tax Preparer Associate",
    "Tax Preparer Consultant",
    "Tax Filer",
    "Tax Filing Analyst",

    # Tax Analyst (16-30)
    "Tax Analyst",
    "US Tax Analyst",
    "Senior Tax Analyst",
    "Tax Compliance Analyst",
    "US Tax Compliance Analyst",
    "Federal Tax Analyst",
    "State Tax Analyst",
    "Tax Research Analyst",
    "Tax Technical Analyst",
    "Tax Data Analyst",
    "Tax Operations Analyst",
    "Tax Process Analyst",
    "Tax Reporting Analyst",
    "Tax Planning Analyst",
    "Tax Advisory Analyst",

    # Tax Reviewer (31-40)
    "Tax Reviewer",
    "Senior Tax Reviewer",
    "Tax Review Analyst",
    "Tax Quality Reviewer",
    "Tax Review Specialist",
    "Tax Return Reviewer",
    "Tax Compliance Reviewer",
    "Tax Audit Reviewer",
    "Tax Technical Reviewer",
    "Tax Senior Reviewer",

    # Tax Associate (41-50)
    "Tax Associate",
    "Senior Tax Associate",
    "Tax Associate Analyst",
    "US Tax Associate",
    "Tax Staff Associate",
    "Tax Associate Consultant",
    "Tax Associate Specialist",
    "Junior Tax Associate",
    "Tax Process Associate",
    "Tax Compliance Associate",

    # Tax Consultant (51-60)
    "Tax Consultant",
    "US Tax Consultant",
    "Senior Tax Consultant",
    "Tax Advisory Consultant",
    "Tax Compliance Consultant",
    "Tax Technology Consultant",
    "Tax Process Consultant",
    "Tax Planning Consultant",
    "Tax Transformation Consultant",
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
