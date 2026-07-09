import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
CHAT_ID   = os.environ.get("CHAT_ID", "")

# LinkedIn search — broad US Tax coverage
KEYWORDS = [
    "US Tax",
    "US Taxation",
    "US Tax Analyst",
    "US Tax Associate",
    "US Tax Consultant",
    "US Tax Manager",
    "US Tax Senior",
    "Tax Preparation",
    "Tax Preparer",
    "Tax Compliance",
    "Tax Reviewer",
    "Tax Return Preparer",
    "Federal Tax",
    "International Tax",
    "Corporate Tax US",
    "Individual Tax US",
    "Partnership Tax",
    "S Corp Tax",
    "Enrolled Agent",
    "CPA Tax",
    "CPA US Tax",
    "Tax Analyst US",
    "State Tax US",
    "Multi State Tax",
    "Expat Tax",
    "Cross Border Tax",
    "H&R Block Tax",
    "Lacerte Tax",
    "ProSeries Tax",
    "GoSystem Tax",
    "CCH Axcess Tax",
    "Thomson Reuters Tax",
    "Tax Operations",
    "Tax Support Analyst",
]

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
