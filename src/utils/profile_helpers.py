# src/utils/profile_helpers.py
"""
Helper functions to access candidate profile data for dynamic form filling.
"""

from datetime import datetime, timedelta
from config.profile import PROFILE


def get_salary_for_role(role: str) -> int:
    """
    Return the expected salary (in GBP) for a given job role.
    Falls back to default if role not found.
    """
    return PROFILE["salary_expectations"].get(role, PROFILE["salary_expectations"]["default"])


def get_salary_range(role: str = None) -> str:
    """
    Return a salary range string for the given role, or the default range.
    """
    if role and role in PROFILE["salary_expectations"]:
        base = PROFILE["salary_expectations"][role]
        # Return a ±5k range around the base
        return f"£{base-5000:,}–£{base+5000:,}"
    return PROFILE.get("salary_range", "£40,000–£50,000")


def get_salary_single(role: str = None) -> str:
    """
    Return a single salary figure for the given role, or default.
    """
    if role and role in PROFILE["salary_expectations"]:
        return f"£{PROFILE['salary_expectations'][role]:,}"
    return PROFILE.get("salary_single", "£45,000")


def get_interview_availability(start_date: datetime = None) -> list[str]:
    """
    Generate three weekday availability windows starting from start_date.
    If start_date is None, use today.
    """
    if start_date is None:
        start_date = datetime.now()

    # We'll produce 3 weekdays from the next 7 days
    windows = PROFILE["interview_availability_rules"]["availability_windows"]
    # Prefer the first three windows
    available_windows = windows[:3]

    # Find the next 3 weekdays (Mon-Fri)
    dates = []
    cursor = start_date
    while len(dates) < 3:
        cursor += timedelta(days=1)
        if cursor.weekday() < 5:  # Monday=0, Friday=4
            dates.append(cursor)

    # Format: "Tuesday, 10:00 AM–12:00 PM"
    result = []
    for i, date in enumerate(dates):
        window = available_windows[i % len(available_windows)]
        day_name = date.strftime("%A")
        result.append(f"{day_name}: {window}")

    return result


def get_answer_for_question(question_text: str) -> str:
    """
    Return a pre-defined answer for common questions based on the profile.
    This can be expanded.
    """
    q = question_text.lower()
    common = PROFILE.get("common_answers", {})

    # Check for specific keywords
    if "sponsor" in q or "visa" in q:
        return "No, I do not require visa sponsorship. I hold a UK Student Visa and am eligible for the Graduate Route after my MSc."
    if "right to work" in q or "authorization" in q:
        return "Yes, I have the right to work in the UK on a Student Visa (up to 20 hours/week during term time, full-time during holidays)."
    if "salary" in q or "compensation" in q:
        return common.get("salary_single", "£45,000")
    if "notice" in q or "available to start" in q or "start date" in q:
        return common.get("notice_period", "Immediate.")
    if "remote" in q or "work from home" in q:
        return common.get("remote_working", "Yes. Open to Remote, Hybrid, or On-site.")
    if "relocate" in q or "relocation" in q:
        return common.get("relocation", "Yes. Open to relocation anywhere within the UK.")
    if "criminal" in q or "conviction" in q:
        return common.get("criminal_record", "No.")
    if "conflict" in q or "interest" in q:
        return common.get("conflicts_of_interest", "None.")
    if "portfolio" in q or "github" in q:
        return common.get("portfolio", "GitHub: https://github.com/CRaghav21 | LinkedIn: https://www.linkedin.com/in/raghavendra-j-c-982b811a2")
    if "why are you interested" in q or "motivation" in q:
        return common.get("interest_general", "I enjoy solving business problems using software, data engineering and automation...")

    # If no match, return None so the LLM handles it.
    return None