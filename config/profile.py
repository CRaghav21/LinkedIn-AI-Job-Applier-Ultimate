# config/profile.py
# This file contains all personal/professional data used by the bot.
# It is the single source of truth for candidate information.

from typing import Dict, List, Optional

PROFILE = {
    # ------------------------------------------------------------
    # PERSONAL INFORMATION
    # ------------------------------------------------------------
    "personal": {
        "full_name": "Raghavendra J C",
        "first_name": "Raghavendra",
        "last_name": "J C",
        "email": "craghavendra910@gmail.com",
        "phone": "+44 7551538278",
        "location": "Birmingham, United Kingdom",
        "nationality": "Indian",
        "gender": "Male",
        "pronouns": "He/Him",
        "linkedin": "https://www.linkedin.com/in/raghavendra-j-c-982b811a2",
        "github": "https://github.com/CRaghav21",
    },

    # ------------------------------------------------------------
    # CURRENT STATUS & WORK AUTHORIZATION
    # ------------------------------------------------------------
    "status": {
        "current_status": "Full-time MSc Advanced Computer Science student at the University of Birmingham.",
        "availability": (
            "Available immediately. "
            "Part-time (up to 20 hours/week) during university term time in accordance with Student visa conditions. "
            "Full-time during university holidays. Full-time after course completion."
        ),
        "reason_for_leaving": "Relocated to the UK to pursue an MSc in Advanced Computer Science and further develop expertise in Software Engineering, Data Engineering and Artificial Intelligence.",
        "visa_type": "UK Student Visa",
        "right_to_work_uk": True,
        "visa_sponsorship_required": False,
        "future_authorization": "Eligible to apply for the UK Graduate Route (PSW) visa after successful completion of MSc.",
        "passport": "Indian Passport",
        "driving_licence": False,
        "criminal_convictions": False,
    },

    # ------------------------------------------------------------
    # WORK PREFERENCES – ALL SET TO TRUE (apply to every job)
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

        # --- Hardcoded answers for authorization questions ---
        "authorization_answers": {
            "legally authorized to work": "Yes",
            "sponsorship": "No",
            "work permit": "Yes",
            "right to work": "Yes",
            "visa sponsorship required": "No",
        },

        # --- Default years for numeric experience questions ---
        "default_experience_years": {
            # Core skills
            "python": 4,
            "sql": 4,
            "c": 3,
            "c#": 3,
            "java": 3,
            "javascript": 3,
            # Data & BI
            "power bi": 3,
            "tableau": 3,
            "excel": 5,
            "vba": 4,
            "etl": 4,
            "data analysis": 4,
            "data engineering": 4,
            "data modeling": 4,
            # ML / NLP / AI
            "machine learning": 4,
            "nlp": 4,
            "natural language processing": 4,
            "nltk": 4,
            "vader": 4,
            "textblob": 4,
            "artificial intelligence": 4,
            "ai": 4,
            "deep learning": 4,
            "llm": 4,
            # Automation
            "automation": 5,
            "workflow automation": 5,
            # Other
            "algorithms": 5,
            "data structures": 5,
            "oop": 4,
            "sdlc": 4,
            "rest apis": 4,
            "cloud": 3,
            "azure": 3,
            "aws": 3,
            "gcp": 3,
            "docker": 3,
            "kubernetes": 3,
        },
    },

    # ------------------------------------------------------------
    # EDUCATION
    # ------------------------------------------------------------
    "education": [
        {
            "degree": "MSc Advanced Computer Science",
            "institution": "University of Birmingham",
            "location": "Birmingham, UK",          # <-- fixed comma after this line
            "years": "2025–2026",
            "modules": [
                "Algorithms & Complexity",
                "Intelligent Software Engineering",
                "Interactive Intelligent Systems",
                "Distributed Systems",
                "Advanced Networking",
                "Human Computer Interaction"
            ],
        },
        {
            "degree": "Bachelor of Engineering (Computer Science)",
            "institution": "Visvesvaraya Technological University",
            "location": "India",
            "years": "2017–2021",
            "modules": [],
        },
    ],

    # ------------------------------------------------------------
    # PROFESSIONAL EXPERIENCE
    # ------------------------------------------------------------
    "experience": [
        {
            "company": "Amazon",
            "title": "Data Analyst",
            "dates": "June 2023 – May 2025",
            "location": "India",
            "responsibilities": [
                "Built enterprise reporting automation systems using Python.",
                "Developed ETL pipelines integrating SQL databases, APIs, Excel datasets and reporting systems.",
                "Reduced daily reporting effort from approximately 5–6 hours to 1.5–2 hours (60% reduction).",
                "Created Power BI and Tableau dashboards.",
                "Automated reporting workflows using Python and Excel VBA.",
                "Performed large-scale business data analysis.",
                "Delivered management reporting.",
                "Improved reporting quality through automated validation.",
                "Worked closely with cross-functional stakeholders.",
            ],
            "achievement": "Reduced reporting effort by approximately 60% through development of an internal automation orchestration platform.",
        },
        {
            "company": "IBM",
            "title": "Application Developer",
            "dates": "April 2022 – April 2023",
            "location": "India",
            "responsibilities": [
                "Developed applications using C and C#.",
                "Backend development using SQL Server and Db2.",
                "Debugging and testing.",
                "Technical documentation.",
                "Participated throughout the Software Development Life Cycle (SDLC).",
            ],
            "achievement": "",
        },
    ],

    # ------------------------------------------------------------
    # TECHNICAL SKILLS
    # ------------------------------------------------------------
    "skills": {
        "programming": ["Python", "SQL", "C", "C#"],
        "data": ["ETL", "Power BI", "Tableau", "Excel", "VBA", "Pandas", "NumPy"],
        "machine_learning": ["NLTK", "VADER", "TextBlob", "NLP"],
        "software_engineering": ["OOP", "Algorithms", "Data Structures", "SDLC", "REST APIs", "Automation"],
    },

    # ------------------------------------------------------------
    # LANGUAGES
    # ------------------------------------------------------------
    "languages": ["English", "Kannada", "Hindi"],

    # ------------------------------------------------------------
    # LEADERSHIP
    # ------------------------------------------------------------
    "leadership": [
        {
            "role": "Vice President",
            "organization": "Computer Society of India",
            "responsibilities": [
                "Technical event management",
                "Student mentoring",
                "Leadership",
                "Publications",
                "Team coordination",
            ],
        }
    ],

    # ------------------------------------------------------------
    # PROJECTS (Knowledge Base)
    # ------------------------------------------------------------
    "projects": [
        {
            "name": "Automation Orchestration Platform",
            "technologies": ["Python", "SQL", "Power BI", "Tableau", "Excel VBA", "Tkinter", "ETL", "Workflow Automation"],
            "description": "Designed and developed an enterprise automation platform integrating SQL databases, dashboards, Excel datasets and internal reporting systems.",
            "features": [
                "Workflow scheduling",
                "Automated reporting",
                "Data validation",
                "Dashboard integration",
                "Reporting automation",
                "GUI",
                "Monitoring",
            ],
            "impact": "Reduced manual operational effort by approximately 60%.",
            "best_suited_for": [
                "Data Engineer", "Data Analyst", "Business Analyst", "BI Developer",
                "Python Developer", "Reporting Analyst", "Automation Engineer", "Software Engineer"
            ],
        },
        {
            "name": "Sentiment Analysis Tool",
            "technologies": ["Python", "NLTK", "TextBlob", "VADER", "Tkinter", "Excel"],
            "description": "Developed an NLP application that analyses customer feedback, calculates sentiment scores, classifies feedback into categories and exports structured reports.",
            "best_suited_for": [
                "Machine Learning Engineer", "AI Engineer", "Data Scientist",
                "Python Developer", "NLP Engineer", "Research roles"
            ],
        },
    ],

    # ------------------------------------------------------------
    # ACHIEVEMENTS
    # ------------------------------------------------------------
    "achievements": [
        {
            "name": "UKFinnovator 2026",
            "event": "Imperial College London",
            "challenge": "Cambridge Spark RegTech Challenge",
            "result": "Top 4 Finalist",
            "responsibilities": [
                "Designed overall system architecture.",
                "Integrated AI components.",
                "Developed dashboards and visualisations.",
                "Built AI-powered compliance workflows.",
            ],
            "platform_features": [
                "Compliance review automation",
                "KYB verification",
                "Sanctions screening",
                "AI dashboards",
            ],
            "highlight_for": ["AI", "Software Engineering", "Data Engineering", "Machine Learning", "FinTech", "RegTech", "Consulting", "Research"],
        }
    ],

    # ------------------------------------------------------------
    # SALARY EXPECTATIONS (per role)
    # ------------------------------------------------------------
    "salary_expectations": {
        "Graduate Software Engineer": 40000,
        "Graduate Data Engineer": 40000,
        "Graduate Data Analyst": 38000,
        "Data Analyst": 45000,
        "Business Analyst": 45000,
        "Business Performance Analyst": 45000,
        "BI Analyst": 45000,
        "Reporting Analyst": 42000,
        "Data Engineer": 50000,
        "ETL Developer": 50000,
        "Analytics Engineer": 50000,
        "Python Developer": 50000,
        "Software Engineer": 50000,
        "Application Developer": 48000,
        "AI Engineer": 50000,
        "Machine Learning Engineer": 50000,
        "Data Consultant": 45000,
        "Technology Consultant": 45000,
        "Research Software Engineer": 42000,
        "default": 45000,
    },
    "salary_range": "£40,000–£50,000",
    "salary_single": "£45,000",
    "current_salary": "45000",   # Most recent salary (Amazon)

    # ------------------------------------------------------------
    # INTERVIEW AVAILABILITY
    # ------------------------------------------------------------
    "interview_availability_rules": {
        "days": "Monday–Friday",
        "timezone": "UK",
        "availability_windows": ["10:00 AM–12:00 PM", "2:00 PM–4:00 PM", "9:30 AM–11:30 AM"],
    },

    # ------------------------------------------------------------
    # COMMON APPLICATION QUESTIONS (with direct answers)
    # ------------------------------------------------------------
    "common_answers": {
        "interest_general": (
            "I enjoy solving business problems using software, data engineering and automation. "
            "My experience at Amazon and IBM has enabled me to build scalable reporting systems, "
            "automate business processes and deliver data-driven insights. "
            "I'm now applying these skills through my MSc in Advanced Computer Science and am "
            "excited to contribute while continuing to grow professionally."
        ),
        "notice_period": (
            "Immediate. Available to start immediately. "
            "Can work part-time during term time (up to 20 hours per week) and full-time during "
            "university holidays in accordance with Student visa conditions."
        ),
        "remote_working": "Yes. Open to Remote, Hybrid, or On-site.",
        "relocation": "Yes. Open to relocation anywhere within the UK.",
        "criminal_record": "No.",
        "conflicts_of_interest": "None.",
        "portfolio": "GitHub: https://github.com/CRaghav21  |  LinkedIn: https://www.linkedin.com/in/raghavendra-j-c-982b811a2",
        "visa_sponsorship": "No, I do not require visa sponsorship. I hold a UK Student Visa and am eligible for the Graduate Route after my MSc.",
        "right_to_work": "Yes, I have the right to work in the UK on a Student Visa (up to 20 hours/week during term time, full-time during holidays).",
        "commute_general": "Yes, I am willing to commute or relocate as required.",
    },

    # ------------------------------------------------------------
    # JOB SEARCH KEYWORDS (priority groups)
    # ------------------------------------------------------------
    "job_search_keywords": {
        "priority_1": [
            "Data Engineer", "Data Analyst", "Business Data Analyst", "Business Performance Analyst",
            "Business Intelligence Analyst", "BI Analyst", "Reporting Analyst", "MI Analyst",
            "Performance Analyst", "Analytics Engineer", "ETL Developer", "SQL Developer",
            "Python Developer", "Software Engineer", "Software Developer", "Backend Developer",
            "Application Developer", "Automation Engineer", "AI Engineer", "Machine Learning Engineer",
            "Data Consultant", "Technology Consultant", "Research Software Engineer",
        ],
        "priority_2": [
            "Graduate Software Engineer", "Graduate Data Engineer", "Graduate Data Analyst",
            "Graduate Business Analyst", "Graduate Technology Consultant", "Graduate AI Consultant",
            "Graduate ML Engineer", "Graduate BI Developer",
        ],
        "priority_3": [
            "Software Engineering Intern", "Data Engineering Intern", "AI Intern",
            "ML Intern", "Python Developer Intern", "Research Intern", "Performance Engineer Intern",
        ],
        "priority_4": [
            "Research Assistant", "Teaching Assistant", "Graduate Teaching Assistant",
            "Student Success Tutor", "Academic Services Administrator", "Registry Administrator",
            "Customer Service Officer", "IT Support Analyst", "Administrative Assistant",
            "Data Analyst",
        ],
    },

    # ------------------------------------------------------------
    # PROJECT SELECTION RULES (for tailoring resumes)
    # ------------------------------------------------------------
    "project_selection_rules": {
        "Python": "Automation Platform",
        "SQL": "Automation Platform",
        "Power BI": "Automation Platform",
        "Tableau": "Automation Platform",
        "ETL": "Automation Platform",
        "Dashboards": "Automation Platform",
        "Reporting": "Automation Platform",
        "Automation": "Automation Platform",
        "Machine Learning": "Sentiment Analysis Tool",
        "NLP": "Sentiment Analysis Tool",
        "AI": "Sentiment Analysis Tool + UKFinnovator",
        "LLM": "UKFinnovator",
        "FinTech": "UKFinnovator",
        "RegTech": "UKFinnovator",
        "Software Engineering": "IBM + Automation Platform",
        "Backend": "IBM",
        "Research": "MSc + Sentiment Analysis + UKFinnovator",
        "Consulting": "Amazon + UKFinnovator",
        "Leadership": "Vice President, Computer Society of India",
    },
}