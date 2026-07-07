# config/profile_template.py
# ================================================================
#  ⚠️  COPY THIS FILE TO profile.py AND FILL IN YOUR PERSONAL DATA
#  DO NOT COMMIT profile.py TO GITHUB – IT CONTAINS SENSITIVE INFO
# ================================================================

from typing import Dict, List, Optional

PROFILE = {
    # ------------------------------------------------------------
    # PERSONAL INFORMATION
    # ------------------------------------------------------------
    "personal": {
        "full_name": "Your Full Name",
        "first_name": "Your First Name",
        "last_name": "Your Last Name",
        "email": "your_email@example.com",
        "phone": "+44 1234567890",
        "location": "Your City, United Kingdom",
        "nationality": "Your Nationality",
        "gender": "Male/Female/Other",
        "pronouns": "He/Him",
        "linkedin": "https://linkedin.com/in/yourprofile",
        "github": "https://github.com/yourusername",
    },

    # ------------------------------------------------------------
    # CURRENT STATUS & WORK AUTHORIZATION
    # ------------------------------------------------------------
    "status": {
        "current_status": "Your current employment/study status",
        "availability": "Your availability (e.g., Immediate, 1 month notice, etc.)",
        "reason_for_leaving": "Reason for leaving previous role (if applicable)",
        "visa_type": "UK Student Visa / Skilled Worker Visa / etc.",
        "right_to_work_uk": True,
        "visa_sponsorship_required": False,
        "future_authorization": "e.g., Eligible for PSW after graduation",
        "passport": "Your Passport Nationality",
        "driving_licence": False,
        "criminal_convictions": False,
    },

    # ------------------------------------------------------------
    # WORK PREFERENCES
    # ------------------------------------------------------------
    "work_preferences": {
        "willing_to_relocate": True,
        "willing_to_commute_long_distance": True,
        "preferred_work_mode": "any",
        "willing_to_work_onsite": True,
        "willing_to_work_remote": True,
        "willing_to_work_hybrid": True,
        "default_commute_answer": "Yes",
        "default_passport_answer": "No",

        "authorization_answers": {
            "legally authorized to work": "Yes",
            "sponsorship": "No",
            "work permit": "Yes",
            "right to work": "Yes",
            "visa sponsorship required": "No",
        },

        "default_experience_years": {
            # Example – replace with your own skill‑years mapping
            "python": 4,
            "sql": 4,
            "c": 3,
            "c#": 3,
            "power bi": 3,
            "tableau": 3,
            "excel": 5,
            "vba": 4,
            "etl": 4,
            "data analysis": 4,
            "data engineering": 4,
            "machine learning": 4,
            "nlp": 4,
            "automation": 5,
            "algorithms": 5,
            "data structures": 5,
            "oop": 4,
            "sdlc": 4,
            "rest apis": 4,
            "cloud": 3,
            "azure": 3,
            "aws": 3,
            "docker": 3,
        },
    },

    # ------------------------------------------------------------
    # EDUCATION
    # ------------------------------------------------------------
    "education": [
        {
            "degree": "Your Degree Name",
            "institution": "University Name",
            "location": "City, Country",
            "years": "Start–End",
            "modules": [
                "Module 1",
                "Module 2",
            ],
        },
        # Add more entries if needed
    ],

    # ------------------------------------------------------------
    # PROFESSIONAL EXPERIENCE
    # ------------------------------------------------------------
    "experience": [
        {
            "company": "Company Name",
            "title": "Job Title",
            "dates": "Start – End",
            "location": "City, Country",
            "responsibilities": [
                "Responsibility/achievement 1",
                "Responsibility/achievement 2",
            ],
            "achievement": "Key achievement (optional)",
        },
        # Add more entries
    ],

    # ------------------------------------------------------------
    # TECHNICAL SKILLS
    # ------------------------------------------------------------
    "skills": {
        "programming": ["Python", "SQL", "C#"],
        "data": ["ETL", "Power BI", "Tableau", "Excel", "VBA"],
        "machine_learning": ["NLTK", "VADER", "TextBlob", "NLP"],
        "software_engineering": ["OOP", "Algorithms", "Data Structures", "SDLC", "REST APIs", "Automation"],
    },

    # ------------------------------------------------------------
    # LANGUAGES
    # ------------------------------------------------------------
    "languages": ["English", "Other Language"],

    # ------------------------------------------------------------
    # LEADERSHIP (optional)
    # ------------------------------------------------------------
    "leadership": [
        {
            "role": "Role Title",
            "organization": "Organization Name",
            "responsibilities": [
                "Responsibility 1",
                "Responsibility 2",
            ],
        }
    ],

    # ------------------------------------------------------------
    # PROJECTS (optional)
    # ------------------------------------------------------------
    "projects": [
        {
            "name": "Project Name",
            "technologies": ["Tech1", "Tech2"],
            "description": "Brief description",
            "impact": "What you achieved",
        }
    ],

    # ------------------------------------------------------------
    # ACHIEVEMENTS (optional)
    # ------------------------------------------------------------
    "achievements": [
        {
            "name": "Achievement Title",
            "description": "What you did and why it matters",
        }
    ],

    # ------------------------------------------------------------
    # SALARY EXPECTATIONS
    # ------------------------------------------------------------
    "salary_expectations": {
        "Data Analyst": 45000,
        "Software Engineer": 50000,
        "default": 45000,
    },
    "salary_range": "£40,000–£50,000",
    "salary_single": "£45,000",
    "current_salary": "45000",

    # ------------------------------------------------------------
    # COMMON APPLICATION QUESTIONS
    # ------------------------------------------------------------
    "common_answers": {
        "interest_general": "Why you're interested in roles like this.",
        "notice_period": "Your notice period (e.g., Immediate, 1 month, etc.)",
        "remote_working": "Yes/No",
        "relocation": "Yes/No",
        "criminal_record": "No",
        "conflicts_of_interest": "None",
        "portfolio": "Links to your GitHub/LinkedIn",
        "visa_sponsorship": "No, I do not require sponsorship.",
        "right_to_work": "Yes, I have the right to work in the UK.",
        "commute_general": "Yes, I am willing to commute or relocate.",
    },

    # ------------------------------------------------------------
    # JOB SEARCH KEYWORDS (optional)
    # ------------------------------------------------------------
    "job_search_keywords": {
        "priority_1": [
            "Data Engineer", "Data Analyst", "Software Engineer",
        ],
        "priority_2": [],
        "priority_3": [],
        "priority_4": [],
    },

    # ------------------------------------------------------------
    # PROJECT SELECTION RULES (optional)
    # ------------------------------------------------------------
    "project_selection_rules": {
        "Python": "Your Python Project",
        "SQL": "Your SQL Project",
        # ... add more
    },
}