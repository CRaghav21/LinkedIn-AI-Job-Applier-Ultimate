# config/constants.py

# Import the comprehensive profile for use by LLM answerer and other modules
from config.profile import PROFILE

# ================================================================
# REAL PERSONAL DATA (used by auto‑filler in utils.py)
# ================================================================

NAME = "Raghavendra J C"
FIRST_NAME = "Raghavendra"
LAST_NAME = "J C"
PHONE = "+44 7551538278"          # or "07551538278"
EMAIL = "craghavendra910@gmail.com"
LINKEDIN = "https://www.linkedin.com/in/raghavendra-j-c-982b811a2"
GITHUB = "https://github.com/CRaghav21"
ZIP_CODE = "B19 3SJ"
ADDRESS = "Birmingham, UK"

# Professional summary
SUMMARY = (
    "Software and Data Professional with 3+ years of experience at Amazon and IBM, "
    "combining software development, data engineering, and automation expertise. "
    "Proven ability to build scalable automation systems, develop applications, and "
    "extract insights from large datasets using Python, SQL, and BI tools. "
    "Currently pursuing an MSc in Advanced Computer Science at University of Birmingham, "
    "with a focus on algorithms, intelligent systems, and software engineering. "
    "Seeking Software Developer / Data Engineer / ML Engineer roles."
)

# Work experience – list of dicts (each with title, company, location, start_date, end_date, description)
EXPERIENCE = [
    {
        "title": "Data Analyst",
        "company": "Amazon",
        "location": "Bangalore, India",
        "start_date": "2023-06",
        "end_date": "2025-05",
        "description": (
            "Designed and developed an internal workflow orchestration and automation platform using Python, "
            "enabling priority-based, sequential, non-sequential, and scheduled execution of business-critical "
            "reporting workflows. Architected end-to-end reporting pipelines integrating SQL databases, Excel datasets, "
            "internal reporting systems, APIs, and Amazon QuickSight dashboards. Built secure access controls with "
            "corporate email authentication and OTP verification. Automated report generation, validation, and "
            "distribution through Outlook integrations. Engineered ETL workflows to transform raw operational and "
            "financial data into actionable insights, KPI reports, and dashboards. Reduced daily reporting effort "
            "from approximately 5–6 hours to 1.5–2 hours. Supported reporting operations for 12 client accounts. "
            "Implemented monitoring, validation, logging, and error-handling mechanisms. Developed interactive "
            "dashboards using Power BI and Amazon QuickSight."
        )
    },
    {
        "title": "Application Developer",
        "company": "IBM",
        "location": "Bangalore, India",
        "start_date": "2022-04",
        "end_date": "2023-04",
        "description": (
            "Wrote, tested, and maintained C and C# code for various applications. Worked with databases (IBM Db2, "
            "SQL Server) for data manipulation and integration. Assisted in designing application components and "
            "systems. Documented code, technical specifications, and development processes. Built and debugged "
            "test cases under the application development lifecycle."
        )
    }
]

# Education – list of dicts (degree, institution, location, graduation_year, description optional)
EDUCATION = [
    {
        "degree": "MSc Advanced Computer Science",
        "institution": "University of Birmingham",
        "location": "Birmingham, UK",
        "graduation_year": "2026",
        "description": "Modules: Algorithms & Complexity, Intelligent Software Engineering, Interactive Intelligent Systems, Dependable and Distributed Systems, Advanced Networking, Human-Computer Interaction, Programming Language Principles."
    },
    {
        "degree": "Bachelor of Engineering – Computer Science",
        "institution": "Visvesvaraya Technological University",
        "location": "India",
        "graduation_year": "2021"
    }
]

# Skills – list of strings
SKILLS = [
    "Python", "C", "C#", "SQL",
    "Pandas", "NumPy", "NLTK", "TextBlob", "VADER",
    "Power BI", "Tableau", "Excel VBA", "R",
    "Algorithms", "Data Structures", "OOP", "SDLC", "Automation", "ETL",
    "Data Modeling", "Data Visualization", "ETL Pipelines", "API Integration"
]

# Projects – list of dicts (title, description, technologies, year, etc.)
PROJECTS = [
    {
        "title": "Automation System (Python GUI + Reporting Engine)",
        "company": "Amazon",
        "year": "2024–2025",
        "description": (
            "Built a standalone Python application for automated reporting with scheduling and zero manual intervention. "
            "Integrated Excel, databases, and dashboards into a unified system. Designed GUI using Tkinter with control "
            "features (start/stop/process monitoring). Reduced operational workload and improved reporting efficiency."
        )
    },
    {
        "title": "Sentiment Analysis System (NLP Project)",
        "company": "Amazon",
        "year": "2025",
        "description": (
            "Developed NLP pipeline using NLTK, VADER, TextBlob. Automated classification of customer feedback into "
            "categories. Built GUI-based tool for non-technical users. Implemented multi-threading for performance optimisation."
        )
    }
]

# Certifications – list of strings
CERTIFICATIONS = [
    "Power BI for Beginners – Simplilearn",
    "Game Development using PyGame – GUVI"
]

# Languages – list of strings (if any)
LANGUAGES = ["English", "Kannada", "Hindi"]

# ================================================================
# DUMMY DICT (kept for compatibility, now filled with real data)
# ================================================================

DUMMY_PERSONAL_INFO_MALE = {
    "name": "Raghavendra J C",
    "first_name": "Raghavendra",
    "last_name": "J C",
    "last_name_2": "J C",
    "phone": "+44 7551538278",
    "email": "craghavendra910@gmail.com",
    "linkedin": "https://www.linkedin.com/in/raghavendra-j-c-982b811a2",
    "github": "https://github.com/CRaghav21",
    "zip_code": "B19 3SJ",
    "address": "Birmingham, UK",
}

DUMMY_PERSONAL_INFO_FEMALE = DUMMY_PERSONAL_INFO_MALE.copy()  # same for now

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

# Per-model token pricing (input/output cost per token in USD)
# This is the full PRICE_DICT as shown in your snippet – keep it unchanged.
PRICE_DICT: dict[str, dict[str, float]] = {
    # Gemini
    "gemini-3.1-flash-lite-preview": {
        "input_cost_per_token": 0.075 / 1_000_000,
        "output_cost_per_token": 0.30 / 1_000_000,
    },
    "gemini-3-flash-preview": {
        "input_cost_per_token": 0.15 / 1_000_000,
        "output_cost_per_token": 0.60 / 1_000_000,
    },
    # OpenAI
    "gpt-4o-mini": {
        "input_cost_per_token": 0.15 / 1_000_000,
        "output_cost_per_token": 0.60 / 1_000_000,
    },
    "gpt-4o": {
        "input_cost_per_token": 2.50 / 1_000_000,
        "output_cost_per_token": 10.00 / 1_000_000,
    },
    "gpt-5-mini": {
        "input_cost_per_token": 0.15 / 1_000_000,
        "output_cost_per_token": 0.60 / 1_000_000,
    },
    "gpt-5-nano": {
        "input_cost_per_token": 0.10 / 1_000_000,
        "output_cost_per_token": 0.40 / 1_000_000,
    },
    # Anthropic
    "anthropic/claude-haiku-4-5": {
        "input_cost_per_token": 0.80 / 1_000_000,
        "output_cost_per_token": 4.00 / 1_000_000,
    },
    "anthropic/claude-sonnet-4": {
        "input_cost_per_token": 3.00 / 1_000_000,
        "output_cost_per_token": 15.00 / 1_000_000,
    },
    "anthropic/claude-sonnet-4-5": {
        "input_cost_per_token": 3.00 / 1_000_000,
        "output_cost_per_token": 15.00 / 1_000_000,
    },
    "anthropic/claude-sonnet-4-6": {
        "input_cost_per_token": 3.00 / 1_000_000,
        "output_cost_per_token": 15.00 / 1_000_000,
    },
    # DeepSeek
    "deepseek/deepseek-chat-v3.1": {
        "input_cost_per_token": 0.15 / 1_000_000,
        "output_cost_per_token": 0.75 / 1_000_000,
    },
    "deepseek/deepseek-chat-v3.2": {
        "input_cost_per_token": 0.26 / 1_000_000,
        "output_cost_per_token": 0.38 / 1_000_000,
    },
    "deepseek/deepseek-v4-flash": {
        "input_cost_per_token": 0.14 / 1_000_000,
        "output_cost_per_token": 0.28 / 1_000_000,
    },
    # Qwen
    "qwen/qwen3.5-flash-02-23": {
        "input_cost_per_token": 0.065 / 1_000_000,
        "output_cost_per_token": 0.26 / 1_000_000,
    },
    "qwen/qwen3.6-plus": {
        "input_cost_per_token": 0.325 / 1_000_000,
        "output_cost_per_token": 1.30 / 1_000_000,
    },
    # NVIDIA NIM
    "meta/llama-3.3-70b-instruct": {
        "input_cost_per_token": 0.27 / 1_000_000,
        "output_cost_per_token": 0.85 / 1_000_000,
    },
    "meta/llama-3.1-405b-instruct": {
        "input_cost_per_token": 1.00 / 1_000_000,
        "output_cost_per_token": 3.00 / 1_000_000,
    },
    "nvidia/llama-3.1-nemotron-70b-instruct": {
        "input_cost_per_token": 0.27 / 1_000_000,
        "output_cost_per_token": 0.85 / 1_000_000,
    },
    # Groq
    "llama-3.3-70b-versatile": {
        "input_cost_per_token": 0.59 / 1_000_000,
        "output_cost_per_token": 0.79 / 1_000_000,
    },
    "llama-3.1-8b-instant": {
        "input_cost_per_token": 0.05 / 1_000_000,
        "output_cost_per_token": 0.08 / 1_000_000,
    },
    "deepseek-r1-distill-llama-70b": {
        "input_cost_per_token": 0.75 / 1_000_000,
        "output_cost_per_token": 0.99 / 1_000_000,
    },
    # Cerebras
    "llama-3.3-70b": {
        "input_cost_per_token": 0.85 / 1_000_000,
        "output_cost_per_token": 1.20 / 1_000_000,
    },
    "llama-3.1-8b": {
        "input_cost_per_token": 0.10 / 1_000_000,
        "output_cost_per_token": 0.10 / 1_000_000,
    },
    "qwen-3-32b": {
        "input_cost_per_token": 0.45 / 1_000_000,
        "output_cost_per_token": 0.65 / 1_000_000,
    },
}


def cost_per_token(
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
    custom_cost_per_token: dict | None = None,
) -> tuple[float, float]:
    """Return (prompt_cost, completion_cost) for the given model and token counts."""
    rates = PRICE_DICT.get(model, custom_cost_per_token or CUSTOM_COST_PER_TOKEN)
    return (
        prompt_tokens * rates["input_cost_per_token"],
        completion_tokens * rates["output_cost_per_token"],
    )