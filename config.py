import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8714105853:AAEBU3JWHAV8mk17MjSLTYh8W2QO2I-1cts")
CHAT_ID   = os.environ.get("CHAT_ID", "-1003570586532")

# PHASE 1: Positions 1-10 from each section (100% of 7 sections)
# Posts job if ANY keyword found in description
KEYWORDS = [
    # Position 1 from each section
    "Form 1040", "IRS", "Tax Preparation", "Lacerte", "Individual Tax", "W-2 Income", "1040 Preparation",
    # Position 2
    "Form 1040NR", "IRS Guidelines", "Tax Return Preparation", "ProSeries", "Corporate Tax", "1099 Income", "1040 Review",
    # Position 3
    "Form 1040SR", "IRS Regulations", "Tax Filing", "GoSystem", "Partnership Tax", "Rental Income", "1041 Preparation",
    # Position 4
    "Form 1041", "Department of Revenue", "Tax Review", "ONESOURCE", "S-Corporation", "Business Income", "1065 Review",
    # Position 5
    "Form 1120", "DOR", "Tax Reviewer", "UltraTax", "Fiduciary Tax", "Capital Gains", "1120 Preparation",
    # Position 6
    "Form 1120S", "Federal Tax", "Tax Return Review", "CCH Axcess", "Non-Resident Tax", "Dividend Income", "W-2 Processing",
    # Position 7
    "Form 1065", "State Tax", "Quality Review", "ProSystem fx", "Exempt Organization", "Interest Income", "1099 Processing",
    # Position 8
    "Form 990", "Tax Compliance", "Tax Advisory", "Drake", "Trust Tax", "Self-Employment Income", "IRS Compliance Review",
    # Position 9
    "Form 1099", "Tax Law", "Client Returns", "ATX", "Estate Tax", "Foreign Income", "Federal State Tax Preparation",
    # Position 10
    "W-2", "Tax Code", "Tax Planning", "TaxWise", "Self-Employed Tax", "Passive Income", "Individual Corporate Tax",
]

# India cities ONLY - metro + tier-2 cities
LOCATIONS = [
    "Bangalore", "Hyderabad", "Mumbai", "Delhi", "Pune", "Chennai", "Kolkata",
    "Gurgaon", "Noida", "Ahmedabad", "Chandigarh", "Jaipur", "Kochi", "Coimbatore", "Indore", "Lucknow",
]

MAX_JOBS_PER_CYCLE = 15
