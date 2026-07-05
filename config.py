import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8714105853:AAEBU3JWHAV8mk17MjSLTYh8W2QO2I-1cts")
CHAT_ID   = os.environ.get("CHAT_ID", "-1003570586532")

# 7 search keywords - one from each category (positions 2,22,37,52,67,77,87)
# Filtering: if description has ANY 1 of these keywords → POST
KEYWORDS = [
    "form 1040nr",           # Position 2 (Tax Forms 1-20)
    "irs guidelines",        # Position 22 (IRS/Regulatory 21-35)
    "tax return preparation", # Position 37 (Preparation 36-50)
    "proseries",             # Position 52 (Software 51-65)
    "corporate tax",         # Position 67 (Entity Types 66-75)
    "1099 income",           # Position 77 (Income Types 76-85)
    "1040 preparation",      # Position 87 (Combinations 86-100)
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
