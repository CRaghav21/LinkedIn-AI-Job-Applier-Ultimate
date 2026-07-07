# config/constants_template.py
# ================================================================
#  ⚠️  COPY THIS FILE TO constants.py AND FILL IN YOUR PERSONAL DATA
#  DO NOT COMMIT constants.py TO GITHUB – IT CONTAINS SENSITIVE INFO
# ================================================================

# ================================================================
# REAL PERSONAL DATA (used by auto‑filler in utils.py)
# ================================================================

NAME = "Your Full Name"
FIRST_NAME = "Your First Name"
LAST_NAME = "Your Last Name"
PHONE = "+44 1234567890"
EMAIL = "your_email@example.com"
LINKEDIN = "https://linkedin.com/in/yourprofile"
GITHUB = "https://github.com/yourusername"
ZIP_CODE = "AB12 3CD"
ADDRESS = "Your City, UK"

# Professional summary
SUMMARY = (
    "Your professional summary. "
    "Describe your skills, experience, and career goals."
)

# Work experience – list of dicts (each with title, company, location, start_date, end_date, description)
EXPERIENCE = [
    {
        "title": "Your Job Title",
        "company": "Your Company",
        "location": "City, Country",
        "start_date": "YYYY-MM",
        "end_date": "YYYY-MM",
        "description": (
            "Describe your responsibilities and achievements."
        )
    },
    # Add more jobs
]

# Education – list of dicts (degree, institution, location, graduation_year, description optional)
EDUCATION = [
    {
        "degree": "Your Degree",
        "institution": "Your University",
        "location": "City, Country",
        "graduation_year": "YYYY",
        "description": "Relevant modules or coursework."
    },
    # Add more education
]

# Skills – list of strings
SKILLS = [
    "Python", "SQL", "C#", "Power BI", "Tableau",
    # ... add all your skills
]

# Projects – list of dicts (title, description, technologies, year, etc.)
PROJECTS = [
    {
        "title": "Project Title",
        "company": "Company/Personal",
        "year": "YYYY",
        "description": (
            "Describe your project and what you achieved."
        )
    },
    # Add more projects
]

# Certifications – list of strings
CERTIFICATIONS = [
    "Certification Name – Issuer",
    # ...
]

# Languages – list of strings
LANGUAGES = ["English", "Other Language"]

# ================================================================
# DUMMY DICT (kept for compatibility)
# ================================================================

DUMMY_PERSONAL_INFO_MALE = {
    "name": NAME,
    "first_name": FIRST_NAME,
    "last_name": LAST_NAME,
    "last_name_2": LAST_NAME,
    "phone": PHONE,
    "email": EMAIL,
    "linkedin": LINKEDIN,
    "github": GITHUB,
    "zip_code": ZIP_CODE,
    "address": ADDRESS,
}

DUMMY_PERSONAL_INFO_FEMALE = DUMMY_PERSONAL_INFO_MALE.copy()

# ================================================================
# PATHS AND DIRECTORIES (keep as is)
# ================================================================

SEARCH_CONFIG_FILE = "config/search_config.yaml"
OUTPUT_DIR_LINKEDIN = "data/output/linkedin"
OUTPUT_DIR_INDEED = "data/output/indeed"
DEBUG_DIR = "data/debug"
LOG_DIR = "logs"
RESUME_DIR = "data/resumes"
PHOTO_DIR = "data/photo"
COVER_LETTER_DIR = "data/cover_letters"
BROWSER_STORAGE_STATE = "browser_session/browser_state.json"
RESUME_TEXT_TEMPLATE_FILE = "examples/data/resumes/resume_text.txt"
APP_CONFIG_FILE = "config/app_config.yaml"

# ================================================================
# COST PER TOKEN (keep as is)
# ================================================================

CUSTOM_COST_PER_TOKEN = {
    "input_cost_per_token": 0.25 / 1_000_000,
    "output_cost_per_token": 1.50 / 1_000_000,
}

# Per-model token pricing – keep the full PRICE_DICT from your original file
# (You can copy it from your local constants.py or keep it short here)
PRICE_DICT = {
    # Gemini, OpenAI, Anthropic, etc.
    # If you don't want to paste the whole dictionary, you can leave this empty
    # but the bot will use CUSTOM_COST_PER_TOKEN as fallback.
    "gemini-3.1-flash-lite-preview": {
        "input_cost_per_token": 0.075 / 1_000_000,
        "output_cost_per_token": 0.30 / 1_000_000,
    },
    # ... add more models if needed
}

def cost_per_token(model, prompt_tokens, completion_tokens, custom_cost_per_token=None):
    rates = PRICE_DICT.get(model, custom_cost_per_token or CUSTOM_COST_PER_TOKEN)
    return (
        prompt_tokens * rates["input_cost_per_token"],
        completion_tokens * rates["output_cost_per_token"],
    )