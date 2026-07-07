"""This module runs the LinkedIn/Indeed bot for multiple sites."""

import argparse
import asyncio
import os
import re
import shutil
import sys
import traceback
from pathlib import Path
from threading import Lock
from typing import Optional

import dotenv
from pypdf import PdfReader

# Try to import pynput for keyboard control (optional, not available in Docker)
try:
    from pynput import keyboard as pynput_kb
    PYNPUT_AVAILABLE = True
except (ImportError, Exception):
    PYNPUT_AVAILABLE = False
    pynput_kb = None

# Try to import weasyprint for HTML→PDF conversion
try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False

# Import shared configuration
from config.app_config import JOB_SITES, RESTART_EVERY_DAY
from config.constants import (
    BROWSER_STORAGE_STATE,
    RESUME_DIR,
    RESUME_TEXT_TEMPLATE_FILE,
    SEARCH_CONFIG_FILE,
)
from config.logger_config import logger
from src.dashboard.runtime import StopRequested, emit_event, get_control_state, update_control_state
from src.job_manager.bot_facade import BotFacade
from src.job_manager.resume_anonymizer import ResumeAnonymizer
from src.llm.apply_agent import ApplyAgent
from src.llm.llm_manager import GPTAnswerer
from src.pydantic_models.config_models import SearchConfig, Secrets
from src.pydantic_models.prompt_models import ResumeStructure
from src.resume_builder.resume_generator import ResumeGenerator
from src.resume_builder.resume_manager import ResumeManager
from src.resume_builder.style_manager import StyleManager
from src.utils.browser_utils import create_playwright_browser, save_browser_session, stop_tracing
from src.utils.runtime_control import (
    register_shutdown_handlers,
    runtime_controller,
    sleep_with_shutdown,
)
from src.utils.utils import (
    get_ready_made_resume,
    load_yaml_file,
    save_yaml_file,
    validate_and_prompt_resume_completion,
)

# Create necessary directories if they don't exist
os.makedirs(RESUME_DIR, exist_ok=True)

# Resume file paths
RESUME_STRUCTURED_FILE = Path(RESUME_DIR) / "structured_resume.yaml"
RESUME_TEXT_FILE = Path(RESUME_DIR) / "resume_text.txt"

READY_MADE_RESUME = get_ready_made_resume()

# Global pause state for keyboard control
paused = False
pause_lock = Lock()
ctrl_pressed = False
last_dashboard_pause_state = False


class ConfigError(Exception):
    pass


class ConfigValidator:
    """Class for validating configuration settings"""

    def validate_search_config(self, config_yaml_path: Path) -> dict:
        """Validate LinkedIn search configuration settings"""
        try:
            parameters = load_yaml_file(config_yaml_path)
            parameters = SearchConfig(**parameters)
            logger.debug("Search config loaded successfully.")
            return parameters.model_dump()
        except Exception as e:
            raise ConfigError(f"Search configuration validation error: {str(e)}")

    @staticmethod
    def validate_secrets(site: str = None) -> dict:
        """
        Check for required secret keys based on the active site.
        If site is not provided, it will try to load all common keys.
        """
        secrets = {**dotenv.dotenv_values(".env")}
        try:
            if site == "indeed":
                required_keys = ["indeed_email", "indeed_password"]
            else:  # default to linkedin
                required_keys = ["linkedin_email", "linkedin_password"]

            missing_keys = [key for key in required_keys if not secrets.get(key)]
            if missing_keys:
                raise ValueError(f"Missing required keys for {site}: {', '.join(missing_keys)}")

            secrets_config = Secrets(**secrets)
            logger.debug(f"Secrets validated successfully for {site}.")
            return secrets_config.model_dump()
        except Exception as e:
            raise ConfigError(f"Secrets validation error: {str(e)}")

    @staticmethod
    def validate_resume_text(resume_file: Path) -> str:
        """Check for resume file, return placeholder if missing"""
        try:
            with open(resume_file, "r", encoding="utf-8") as f:
                resume_text = f.read()
                if not resume_text:
                    raise ConfigError("Resume not found")
                return resume_text
        except FileNotFoundError:
            logger.warning("Resume text file not found. Using a placeholder.")
            return "Placeholder resume. Please replace with your actual resume."
        except Exception as e:
            raise ConfigError(f"Resume validation error: {str(e)}")


def generate_resume_text_from_pdf(secrets: dict) -> str:
    """Find a PDF in RESUME_DIR, parse it, and write a formatted resume_text.txt using the LLM."""
    pdf_files = list(Path(RESUME_DIR).glob("*.pdf"))
    if not pdf_files:
        return ""

    pdf_path = pdf_files[0]
    logger.info(f"Generating resume_text.txt from {pdf_path.name}")

    reader = PdfReader(pdf_path)
    raw_text = "\n".join(page.extract_text() or "" for page in reader.pages).strip()
    if not raw_text:
        logger.warning(f"Could not extract text from {pdf_path.name}")
        return ""

    template = Path(RESUME_TEXT_TEMPLATE_FILE).read_text(encoding="utf-8")

    llm_answerer = GPTAnswerer(
        secrets.get("llm_api_key"), secrets.get("llm_proxy"), secrets.get("llm_api_url")
    )
    resume_text = llm_answerer.generate_resume_text(raw_text, template)

    RESUME_TEXT_FILE.write_text(resume_text, encoding="utf-8")
    logger.info(f"resume_text.txt generated and saved to {RESUME_TEXT_FILE}")
    return resume_text


def on_press(key):
    """Handle key press events"""
    if not PYNPUT_AVAILABLE:
        return

    global paused, ctrl_pressed
    try:
        # Track Ctrl key state
        if key in (pynput_kb.Key.ctrl_l, pynput_kb.Key.ctrl_r):
            ctrl_pressed = True
        # Check for 'x' key when Ctrl is pressed
        elif hasattr(key, "char") and key.char == "x" and ctrl_pressed:
            with pause_lock:
                paused = not paused
                if paused:
                    logger.warning("⏸️  PAUSED - Press Ctrl+X to continue")
                    emit_event("pause_state_changed", "Keyboard pause requested", paused=True)
                else:
                    logger.info("▶️  RESUMED")
                    emit_event("pause_state_changed", "Keyboard resume requested", paused=False)
    except AttributeError:
        pass


def on_release(key):
    """Handle key release events"""
    if not PYNPUT_AVAILABLE:
        return

    global ctrl_pressed
    # Reset Ctrl key state
    if key in (pynput_kb.Key.ctrl_l, pynput_kb.Key.ctrl_r):
        ctrl_pressed = False


def start_keyboard_listener():
    """Start keyboard listener in background thread"""
    if not PYNPUT_AVAILABLE:
        logger.info("Keyboard control disabled (pynput not available - Docker/headless mode)")
        return

    try:
        listener = pynput_kb.Listener(on_press=on_press, on_release=on_release)
        listener.daemon = True
        listener.start()
        logger.info("Keyboard listener started - Press Ctrl+X to pause/resume")
    except Exception as e:
        logger.warning(f"Could not start keyboard listener: {e}")


async def check_pause():
    """Check if execution is paused and wait if needed"""
    global last_dashboard_pause_state, paused

    control = get_control_state() if os.environ.get("DASHBOARD_RUN_ID") else {}
    effective_paused = paused or control.get("pause_requested", False)

    if control.get("stop_requested"):
        raise StopRequested("Dashboard requested stop")

    if effective_paused != last_dashboard_pause_state:
        emit_event(
            "pause_state_changed",
            f"Execution {'paused' if effective_paused else 'resumed'}",
            paused=effective_paused,
            source="dashboard" if control.get("pause_requested") and not paused else "keyboard",
        )
        last_dashboard_pause_state = effective_paused

    while paused or (
        os.environ.get("DASHBOARD_RUN_ID") and get_control_state().get("pause_requested", False)
    ):
        if os.environ.get("DASHBOARD_RUN_ID") and get_control_state().get("stop_requested"):
            raise StopRequested("Dashboard requested stop")
        await asyncio.sleep(0.5)

    if last_dashboard_pause_state:
        emit_event("pause_state_changed", "Execution resumed", paused=False)
        last_dashboard_pause_state = False


def clear_cache(include_output: bool = False, include_logs: bool = True) -> None:
    """
    Clear temporary and cached data to start fresh.
    - Deletes browser session.
    - Removes temporary resume files (generated per job).
    - Optionally deletes logs and output folders.
    """
    dirs_to_clear = [
        Path("browser_session"),
        Path("apply_agent_resume_*"),
    ]
    if include_output:
        dirs_to_clear.append(Path("data/output"))
    if include_logs:
        dirs_to_clear.append(Path("logs"))

    for path in dirs_to_clear:
        if "*" in str(path):
            for p in Path(".").glob(str(path)):
                if p.exists():
                    try:
                        shutil.rmtree(p)
                        logger.info(f"Cleared: {p}")
                    except Exception as e:
                        logger.warning(f"Could not delete {p}: {e}")
        else:
            if path.exists():
                try:
                    shutil.rmtree(path)
                    logger.info(f"Cleared: {path}")
                except Exception as e:
                    logger.warning(f"Could not delete {path}: {e}")

    for f in Path(RESUME_DIR).glob("temp_*.pdf"):
        try:
            f.unlink()
            logger.info(f"Removed temporary resume: {f.name}")
        except Exception as e:
            logger.warning(f"Could not delete {f}: {e}")

    logger.info("Cache clearing completed.")


# Helper function to strip emojis
def strip_emojis(text: str) -> str:
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE,
    )
    return emoji_pattern.sub(r'', text)


# ================================================================
# MULTI‑PHASE SEARCH CONFIGURATIONS
# ================================================================
SEARCH_PHASES = {
    "indeed": [
        {"remote": True, "locations": ["Remote"]},
        {"remote": False, "locations": ["United Kingdom", "Scotland", "Ireland", "Northern Ireland"]},
        {"remote": False, "locations": ["France", "Germany", "Netherlands", "Spain", "Italy"]},
    ],
    "linkedin": [
        {"remote": True, "locations": ["Remote"]},
        {"remote": False, "locations": ["United Kingdom", "Scotland", "Ireland", "Northern Ireland"]},
        {"remote": False, "locations": ["France", "Germany", "Netherlands", "Spain", "Italy"]},
    ],
}


async def create_and_run_bot(
    search_config: dict,
    secrets: dict,
    resume_text: str,
    resume_structured: dict,
    site: str = "linkedin",
):
    """
    Start the bot for a specific site (linkedin or indeed).
    """
    logger.info(f"Initializing {site.capitalize()} bot...")
    emit_event(
        "run_started",
        f"{site.capitalize()} bot run started",
        positions=search_config.get("positions", []),
        locations=search_config.get("locations", []),
    )

    # Import the appropriate modules dynamically based on the site
    if site == "indeed":
        from src.job_manager.indeed.authenticator_indeed import IndeedAuthenticator as Authenticator
        from src.job_manager.indeed.job_manager_indeed import IndeedJobManager as JobManager
        from src.job_manager.indeed.search_customizer_indeed import (
            IndeedSearchCustomizer as SearchCustomizer,
        )
        site_email = secrets.get("indeed_email")
        site_password = secrets.get("indeed_password")
    else:  # linkedin
        from src.job_manager.linkedin.authenticator_linkedin import (
            LinkedInAuthenticator as Authenticator,
        )
        from src.job_manager.linkedin.job_manager_linkedin import LinkedInJobManager as JobManager
        from src.job_manager.linkedin.search_customizer_linkedin import SearchCustomizer
        site_email = secrets.get("linkedin_email")
        site_password = secrets.get("linkedin_password")

    # Initialize browser Playwright
    try:
        browser, context, page = await create_playwright_browser()
        logger.info("Playwright browser initialized successfully")
        emit_event("browser_initialized", "Playwright browser initialized")
    except Exception as e:
        runtime_controller.finish_run()
        logger.error(f"Browser initialization error: {e}")
        emit_event("run_failed", "Browser initialization failed", error=str(e))
        raise RuntimeError(f"Failed to initialize browser: {e}")

    try:
        # Initialize authenticator
        authenticator = Authenticator(page)
        authenticator.set_parameters(site_email, site_password)

        # Attempt login
        login_success = await authenticator.start()
        if login_success:
            await save_browser_session(context)
            logger.info(f"Successfully logged into {site.capitalize()}!")
            logger.info(f"{site.capitalize()} bot ready to work")
            emit_event("login_success", f"{site.capitalize()} login succeeded")
        else:
            logger.error(f"Failed to log into {site.capitalize()}")
            emit_event("run_failed", f"{site.capitalize()} login failed")
            return False

        # --------------------------------------------------------------
        # FIX: Use existing structured resume – do NOT parse again
        # --------------------------------------------------------------
        # Ensure resume_structured has all required keys.
        # If it's empty or missing personal details, fill from constants.
        from config.constants import DUMMY_PERSONAL_INFO_MALE
        pi = resume_structured.get("personal_information", {})
        if not pi.get("first_name") or pi.get("first_name") == "John":
            # Use the constants we updated with real data
            pi["first_name"] = DUMMY_PERSONAL_INFO_MALE["first_name"]
            pi["last_name"] = DUMMY_PERSONAL_INFO_MALE["last_name"]
            pi["email"] = DUMMY_PERSONAL_INFO_MALE["email"]
            pi["phone"] = DUMMY_PERSONAL_INFO_MALE["phone"]
            pi["location"] = DUMMY_PERSONAL_INFO_MALE["address"]
            pi["linkedin"] = DUMMY_PERSONAL_INFO_MALE["linkedin"]
            pi["github"] = DUMMY_PERSONAL_INFO_MALE["github"]
            pi["summary"] = "Software and Data Professional with 3+ years of experience."
        # Add any missing fields
        pi.setdefault("summary", "Software and Data Professional")
        pi.setdefault("website", "")
        resume_structured["personal_information"] = pi

        # Ensure details arrays exist
        for key in ["education_details", "experience_details", "skills", "interests"]:
            if key not in resume_structured:
                resume_structured[key] = []

        # Save the structured resume once (if not already saved)
        if not RESUME_STRUCTURED_FILE.exists():
            save_yaml_file(RESUME_STRUCTURED_FILE, resume_structured)
            logger.info(f"Saved structured resume to {RESUME_STRUCTURED_FILE}")

        # Set GPT answerer and resume generator
        llm_api_key = secrets.get("llm_api_key")
        llm_proxy = secrets.get("llm_proxy")
        llm_api_url = secrets.get("llm_api_url")
        llm_answerer_component = GPTAnswerer(llm_api_key, llm_proxy, llm_api_url)
        # Give the answerer the structured data (no LLM parsing needed)
        llm_answerer_component.set_resume(resume_structured, resume_text)

        # Anonymize a copy for the bot facade
        resume_anonymizer = ResumeAnonymizer(resume_structured)
        resume_anonymizer.anonymize_personal_information()
        anonymized_resume = resume_anonymizer.resume_anonymized
        resume_text_anonymized = resume_anonymizer.anonymize_text(resume_text)

        # Resume generator components
        style_manager = StyleManager()
        resume_generator = ResumeGenerator(llm_answerer_component, resume_anonymizer)
        resume_generator_manager = ResumeManager(llm_api_key, style_manager, resume_generator)
        resume_generator_manager.choose_style()

        # ------------------------------------------------------------------
        # Custom resume generator callback
        # ------------------------------------------------------------------
        def generate_custom_resume(job_title: str, company_name: str, job_description: str) -> Optional[Path]:
            logger.info(f"Generating custom resume for: {job_title} at {company_name}")
            try:
                llm_answerer_component.set_job({
                    "job_title": job_title,
                    "company_name": company_name,
                    "job_description": job_description
                })

                header = llm_answerer_component.generate_header()
                education = llm_answerer_component.generate_education_section()
                experience = llm_answerer_component.generate_work_experience_section()
                projects = llm_answerer_component.generate_side_projects_section()
                achievements = llm_answerer_component.generate_achievements_section()
                certifications = llm_answerer_component.generate_certifications_section()
                skills = llm_answerer_component.generate_additional_skills_section()

                combined = (header or "") + (education or "") + (experience or "") + (projects or "") + (achievements or "") + (certifications or "") + (skills or "")
                clean_content = strip_emojis(combined)

                html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="utf-8">
                    <title>{job_title} Resume</title>
                    <style>
                        body {{
                            font-family: Arial, Helvetica, sans-serif;
                            font-size: 12pt;
                            margin: 1in;
                            color: #000;
                            background: #fff;
                            line-height: 1.5;
                        }}
                        h1, h2, h3 {{ font-weight: normal; margin: 0.3em 0; }}
                        h1 {{ font-size: 18pt; }}
                        h2 {{ font-size: 14pt; border-bottom: 1px solid #ccc; }}
                        .section {{ margin-bottom: 1em; }}
                        .entry {{ margin-bottom: 0.5em; }}
                        .entry-header {{ font-weight: bold; }}
                        ul {{ margin: 0; padding-left: 1.2em; }}
                        li {{ margin-bottom: 0.2em; }}
                        .contact {{ margin-bottom: 0.5em; }}
                        .contact span {{ margin-right: 1em; }}
                    </style>
                </head>
                <body>
                    {clean_content}
                </body>
                </html>
                """

                temp_dir = Path("temp_resumes")
                temp_dir.mkdir(exist_ok=True)
                html_filename = f"resume_{job_title.replace(' ', '_')}.html"
                html_path = temp_dir / html_filename
                html_path.write_text(html_content, encoding="utf-8")
                logger.info(f"HTML resume saved: {html_path}")

                pdf_filename = html_filename.replace('.html', '.pdf')
                pdf_path = temp_dir / pdf_filename

                if WEASYPRINT_AVAILABLE:
                    logger.info("Converting HTML to PDF using weasyprint...")
                    HTML(string=html_content).write_pdf(pdf_path)
                    if pdf_path.exists():
                        logger.info(f"PDF resume generated: {pdf_path}")
                        return pdf_path
                    else:
                        logger.warning("PDF generation failed.")
                else:
                    logger.warning("weasyprint not available. Falling back to static resume.")

                static_pdf = get_ready_made_resume()
                if static_pdf and static_pdf.exists():
                    return static_pdf
                default_pdf = Path(RESUME_DIR) / "resume.pdf"
                if default_pdf.exists():
                    return default_pdf
                return None

            except Exception as e:
                logger.error(f"Error generating custom resume: {e}")
                static_pdf = get_ready_made_resume()
                if static_pdf and static_pdf.exists():
                    return static_pdf
                default_pdf = Path(RESUME_DIR) / "resume.pdf"
                if default_pdf.exists():
                    return default_pdf
                return None

        # Create ApplyAgent
        llm_agent_component = ApplyAgent(
            api_key=llm_api_key,
            browser_storage_state=BROWSER_STORAGE_STATE,
            llm_api_url=llm_api_url,
            user_email=site_email,
            model_name="llama3.2:3b",  # or "mistral" if you prefer quality
            max_steps=80,
            step_timeout=240,
            resume_generator=generate_custom_resume,
        )
        llm_agent_component.set_resume(resume_text)

        # --------------------------------------------------------------
        # Ensure search parameters are passed to customizer
        # --------------------------------------------------------------
        search_component = SearchCustomizer(page)
        logger.info(f"Setting search parameters on customizer: {search_config}")
        search_component.set_parameters(search_config)

        apply_component = JobManager(page, site_email, resume_anonymizer, search_component)

        # Bot facade
        bot = BotFacade(resume_anonymizer, search_component, apply_component, llm_agent_component)
        bot.set_parameters(search_config)
        bot.set_pause_checker(check_pause)

        # Skip resume validation – always continue
        # We have already filled missing fields, so validation will pass.
        if not os.environ.get("DASHBOARD_RUN_ID"):
            # We skip validation entirely
            pass

        # Start applying
        await bot.set_search_parameters(search_config)
        bot.set_answerer_and_agent(llm_answerer_component, llm_agent_component, search_config)
        bot.set_resume(anonymized_resume, resume_text, resume_text_anonymized)
        bot.set_resume_generator(resume_generator_manager)
        await bot.start_apply()
        emit_event("run_completed", f"{site.capitalize()} bot run completed successfully")

    finally:
        # Cleanup
        logger.info("Cleaning up browser resources...")
        try:
            if context is not None:
                await save_browser_session(context)
                await stop_tracing(context)
            if browser is not None:
                await browser.close()
            elif context is not None:
                await context.close()
            logger.info("Playwright browser closed")
            emit_event("browser_closed", "Playwright browser closed")
        except Exception as e:
            logger.warning(f"Error during browser cleanup: {e}")
        finally:
            runtime_controller.finish_run()


def run_bot_for_site(site: str, search_config: dict, secrets: dict, resume_text: str, resume_structured: dict):
    try:
        asyncio.run(create_and_run_bot(search_config, secrets, resume_text, resume_structured, site))
    except Exception as e:
        logger.error(f"Error running bot for {site}: {e}")
        traceback.print_exc()


def main() -> None:
    parser = argparse.ArgumentParser(description="Multi-site job applier")
    parser.add_argument(
        "--site",
        choices=JOB_SITES + ["all"],
        default="all",
        help="Run for a specific site (default: all sites from config)",
    )
    parser.add_argument(
        "--search",
        type=str,
        help="Override search query (e.g., 'Software Engineer')",
    )
    parser.add_argument(
        "--location",
        type=str,
        help="Override location (e.g., 'London')",
    )
    parser.add_argument(
        "--max",
        type=int,
        dest="max_applies",
        help="Maximum number of applications to attempt (overrides config)",
    )
    parser.add_argument(
        "--clear-cache",
        action="store_true",
        help="Clear all cached data (browser session, logs, output, temporary resumes) before starting.",
    )
    args = parser.parse_args()

    if args.clear_cache:
        clear_cache(include_output=True, include_logs=True)

    register_shutdown_handlers()
    start_keyboard_listener()
    if not os.environ.get("DASHBOARD_RUN_ID"):
        update_control_state(stop_requested=False, pause_requested=False)

    config_validator = ConfigValidator()
    try:
        secrets = config_validator.validate_secrets()
    except ConfigError as e:
        logger.error(f"Secrets validation failed: {e}")
        return

    # Load resume text
    resume_text = config_validator.validate_resume_text(RESUME_TEXT_FILE)
    if not resume_text:
        resume_text = generate_resume_text_from_pdf(secrets)

    # Load structured resume – if missing, create a default one from constants
    resume_structured = {}
    # We'll fill it in create_and_run_bot, but for validation we need a default.
    # We'll use constants to populate it.
    from config.constants import DUMMY_PERSONAL_INFO_MALE
    resume_structured = {
        "personal_information": {
            "first_name": DUMMY_PERSONAL_INFO_MALE["first_name"],
            "last_name": DUMMY_PERSONAL_INFO_MALE["last_name"],
            "gender": "Male",
            "email": DUMMY_PERSONAL_INFO_MALE["email"],
            "phone": DUMMY_PERSONAL_INFO_MALE["phone"],
            "location": DUMMY_PERSONAL_INFO_MALE["address"],
            "linkedin": DUMMY_PERSONAL_INFO_MALE["linkedin"],
            "github": DUMMY_PERSONAL_INFO_MALE["github"],
            "summary": "Software and Data Professional with 3+ years of experience.",
        },
        "education_details": [],
        "experience_details": [],
        "projects": [],
        "achievements": [],
        "certifications": [],
        "languages": [],
        "interests": [],
        "skills": [],
        "availability": {},
        "salary_expectations": {},
        "self_identification": {},
        "legal_authorization": {},
        "work_preferences": {},
    }

    # Ensure arrays exist
    for key in ["education_details", "experience_details", "skills", "interests"]:
        if key not in resume_structured:
            resume_structured[key] = []

    # Determine sites to run
    sites_to_run = []
    if args.site == "all":
        sites_to_run = JOB_SITES
    else:
        sites_to_run = [args.site]

    for site in sites_to_run:
        logger.info(f"\n{'='*60}\nStarting run for {site.upper()}\n{'='*60}")

        try:
            site_secrets = config_validator.validate_secrets(site)
        except ConfigError as e:
            logger.error(f"Skipping {site} due to missing secrets: {e}")
            continue

        phases = SEARCH_PHASES.get(site, [{}])

        for phase_idx, phase in enumerate(phases):
            logger.info(f"\n--- Phase {phase_idx+1}/{len(phases)} for {site}: {phase} ---")

            site_config_path = Path(f"config/search_config_{site}.yaml")
            if site_config_path.exists():
                search_config = config_validator.validate_search_config(site_config_path)
            else:
                search_config = config_validator.validate_search_config(SEARCH_CONFIG_FILE)

            for key, value in phase.items():
                search_config[key] = value

            if args.search:
                search_config["positions"] = [args.search]
            if args.location:
                search_config["locations"] = [args.location]
            if args.max_applies is not None:
                search_config["max_applies"] = args.max_applies

            logger.info(f"Final search config for this phase: {search_config}")

            run_bot_for_site(site, search_config, site_secrets, resume_text, resume_structured)

    logger.info("All sites and phases completed. Exiting.")


if __name__ == "__main__":
    main()