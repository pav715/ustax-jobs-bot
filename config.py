import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8714105853:AAEBU3JWHAV8mk17MjSLTYh8W2QO2I-1cts")
CHAT_ID   = os.environ.get("CHAT_ID", "-1003570586532")

# ALL 100 keywords (positions 1-100) - comprehensive coverage
# If description has ANY 1 keyword → POST (broader net)
KEYWORDS = [
    # Tax Forms (1-20)
    "form 1040", "form 1040nr", "form 1040sr", "form 1041", "form 1120",
    "form 1120s", "form 1065", "form 990", "form 1099", "w-2",
    "schedule a", "schedule b", "schedule c", "schedule d", "schedule e",
    "schedule f", "schedule k-1", "schedule se", "form 2441", "form 8863",
    # IRS / Regulatory (21-35)
    "irs", "irs guidelines", "irs regulations", "department of revenue", "dor",
    "federal tax", "state tax", "tax compliance", "tax law", "tax code",
    "tax reform", "tax withholding", "tax liability", "tax deductions", "tax credits",
    # Preparation Keywords (36-50)
    "tax preparation", "tax return preparation", "tax filing", "tax review", "tax reviewer",
    "tax return review", "quality review", "tax advisory", "client returns", "tax planning",
    "tax research", "tax compliance review", "return review", "tax processing", "tax engagement",
    # Software (51-65)
    "lacerte", "proseries", "gosystem", "onesource", "ultratax",
    "cch axcess", "prosystem fx", "drake", "atx", "taxwise",
    "taxact", "taxslayer", "proconnect", "crosslink", "h&r block software",
    # Entity Types (66-75)
    "individual tax", "corporate tax", "partnership tax", "s-corporation", "fiduciary tax",
    "non-resident tax", "exempt organization", "trust tax", "estate tax", "self-employed tax",
    # Income Types (76-85)
    "w-2 income", "1099 income", "rental income", "business income", "capital gains",
    "dividend income", "interest income", "self-employment income", "foreign income", "passive income",
    # Combination Keywords (86-100)
    "1040 preparation", "1040 review", "1041 preparation", "1065 review", "1120 preparation",
    "w-2 processing", "1099 processing", "irs compliance review", "federal state tax preparation",
    "individual corporate tax", "tax return qa", "tax software review", "multi-state tax filing",
    "tax deadline compliance", "client tax advisory",
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
