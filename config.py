import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8714105853:AAEBU3JWHAV8mk17MjSLTYh8W2QO2I-1cts")
CHAT_ID   = os.environ.get("CHAT_ID", "-1003570586532")

# Search keywords organized by POSITION (1-20) across all 7 sections
# Bot checks position-wise: if description has keywords from same position → POST
KEYWORDS = [
    # POSITION 1 from each section
    "Form 1040", "IRS", "Tax Preparation", "Lacerte", "Individual Tax", "W-2 Income", "1040 Preparation",
    # POSITION 2
    "Form 1040NR", "IRS Guidelines", "Tax Return Preparation", "ProSeries", "Corporate Tax", "1099 Income", "1040 Review",
    # POSITION 3
    "Form 1040SR", "IRS Regulations", "Tax Filing", "GoSystem", "Partnership Tax", "Rental Income", "1041 Preparation",
    # POSITION 4
    "Form 1041", "Department of Revenue", "Tax Review", "ONESOURCE", "S-Corporation", "Business Income", "1065 Review",
    # POSITION 5
    "Form 1120", "DOR", "Tax Reviewer", "UltraTax", "Fiduciary Tax", "Capital Gains", "1120 Preparation",
    # POSITION 6
    "Form 1120S", "Federal Tax", "Tax Return Review", "CCH Axcess", "Non-Resident Tax", "Dividend Income", "W-2 Processing",
    # POSITION 7
    "Form 1065", "State Tax", "Quality Review", "ProSystem fx", "Exempt Organization", "Interest Income", "1099 Processing",
    # POSITION 8
    "Form 990", "Tax Compliance", "Tax Advisory", "Drake", "Trust Tax", "Self-Employment Income", "IRS Compliance Review",
    # POSITION 9
    "Form 1099", "Tax Law", "Client Returns", "ATX", "Estate Tax", "Foreign Income", "Federal State Tax Preparation",
    # POSITION 10
    "W-2", "Tax Code", "Tax Planning", "TaxWise", "Self-Employed Tax", "Passive Income", "Individual Corporate Tax",
    # POSITION 11
    "Schedule A", "Tax Reform", "Tax Research", "TaxAct", "", "", "Tax Return QA",
    # POSITION 12
    "Schedule B", "Tax Withholding", "Tax Compliance Review", "TaxSlayer", "", "", "Tax Software Review",
    # POSITION 13
    "Schedule C", "Tax Liability", "Return Review", "ProConnect", "", "", "Multi-State Tax Filing",
    # POSITION 14
    "Schedule D", "Tax Deductions", "Tax Processing", "CrossLink", "", "", "Tax Deadline Compliance",
    # POSITION 15
    "Schedule E", "Tax Credits", "Tax Engagement", "H&R Block Software", "", "", "Client Tax Advisory",
]

# India cities ONLY - metro + tier-2 cities
LOCATIONS = [
    # Metro cities (Tier-1)
    "Bangalore",
    "Hyderabad",
    "Mumbai",
    "Delhi",
    "Pune",
    "Chennai",
    "Kolkata",
    # State capitals & major cities (Tier-2)
    "Gurgaon",
    "Noida",
    "Ahmedabad",
    "Chandigarh",
    "Jaipur",
    "Kochi",
    "Coimbatore",
    "Indore",
    "Lucknow",
]

MAX_JOBS_PER_CYCLE = 15
