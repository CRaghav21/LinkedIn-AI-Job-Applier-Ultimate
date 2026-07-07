import os
import sys
import tempfile
import webbrowser
import re
from pathlib import Path

import inquirer

from config.app_config import RESUME_STYLE, READY_MADE_RESUME_PATH, UPLOAD_RESUME
from config.constants import RESUME_DIR
from config.logger_config import logger
from src.utils.browser_utils import HTML_to_PDF
from src.utils.utils import load_yaml_file, save_yaml_file


class ResumeManager:
    """Class interface with resume generator"""

    def __init__(self, api_key, style_manager, resume_generator):
        lib_directory = Path(__file__).resolve().parent
        styles_directory = lib_directory / "resume_style"
        self.style_manager = style_manager
        self.style_manager.set_styles_directory(styles_directory)
        self.resume_generator = resume_generator
        self.selected_style = None

    def prompt_user(self, choices: list[str], message: str) -> str:
        questions = [
            inquirer.List("selection", message=message, choices=choices),
        ]
        return inquirer.prompt(questions)["selection"]

    def is_interactive_mode(self) -> bool:
        return sys.stdin.isatty()

    def choose_default_style(self):
        styles = self.style_manager.get_styles()
        if not styles:
            logger.warning("No available styles, using fallback default style")
            self.selected_style = "default"
            return
        default_style = list(styles.keys())[0]
        self.selected_style = default_style
        logger.info(f"Non-interactive mode: Using default resume style '{default_style}'")

    def choose_style(self):
        # If RESUME_STYLE is set and exists, use it
        if RESUME_STYLE is not None:
            styles = self.style_manager.get_styles()
            if styles and RESUME_STYLE in styles:
                self.selected_style = RESUME_STYLE
                logger.info(f"Using resume style from config: '{RESUME_STYLE}'")
                return
            else:
                logger.warning(
                    f"Configured style '{RESUME_STYLE}' not found. "
                    f"Available styles: {list(styles.keys()) if styles else 'none'}. Falling back to default."
                )

        if os.environ.get("DASHBOARD_RUN_ID"):
            logger.info("Dashboard run detected, using default resume style")
            self.choose_default_style()
            return

        if not self.is_interactive_mode():
            logger.info("Running in non-interactive mode (Docker/headless)")
            self.choose_default_style()
            return

        # Interactive mode – prompt user
        styles = self.style_manager.get_styles()
        if not styles:
            logger.warning("No available styles, using fallback default style")
            self.selected_style = "default"
            return

        final_style_choice = "Create your own style in CSS"
        formatted_choices = self.style_manager.format_choices(styles)
        formatted_choices.append(final_style_choice)

        try:
            selected_choice = self.prompt_user(
                formatted_choices, "Which resume style would you like to use?"
            )
            if selected_choice == final_style_choice:
                tutorial_url = "https://github.com/feder-cr/lib_resume_builder_AIHawk/blob/main/how_to_contribute/web_designer.md"
                logger.info("\nOpening tutorial in your browser...")
                webbrowser.open(tutorial_url)
                exit()
            else:
                self.selected_style = selected_choice.split(" (")[0]
        except Exception as e:
            logger.warning(f"Could not get interactive input: {e}")
            logger.info("Falling back to default style selection")
            self.choose_default_style()

    def _clean_resume_html(self, html_content: str) -> str:
        """
        Post‑process the generated HTML to fix common LLM mistakes:
        - Remove invented grades (e.g., "Grade: 85%").
        - Correct education years (Bachelor: 2017–2021; Master: 2025–Present).
        - Remove placeholder links like [Link].
        """
        # Remove any "Grade: X%" pattern (case‑insensitive) from the education section
        html_content = re.sub(
            r'(<[^>]*>)?\s*Grade:\s*[^<]+(?:\s*<[^>]*>)?',
            '',
            html_content,
            flags=re.IGNORECASE
        )

        # Correct Bachelor's years: 2021–2025 -> 2017–2021
        html_content = re.sub(
            r'Bachelor[^<]*?2021\s*[–\-]\s*2025',
            'Bachelor of Engineering – Computer Science  2017 – 2021',
            html_content,
            flags=re.IGNORECASE
        )

        # Correct Master's years: 2026–2027 or 2026–Present -> 2025 – Present
        html_content = re.sub(
            r'MSc[^<]*?2026\s*[–\-]\s*(2027|Present)',
            'MSc Advanced Computer Science  2025 – Present',
            html_content,
            flags=re.IGNORECASE
        )

        # Remove [Link] placeholders
        html_content = html_content.replace('[Link]', '')

        # Remove double spaces created by replacements
        html_content = re.sub(r'\s+', ' ', html_content)

        return html_content

    def _validate_resume_html(self, html_content: str) -> bool:
        """
        Validate the generated HTML for common errors:
        - Wrong education years.
        - Invented grades.
        - Placeholder links [Link].
        - Missing sections.
        Logs warnings and returns True if no critical errors, False otherwise.
        """
        errors = []
        warnings = []

        # 1. Check education years
        # Bachelor's should be 2017–2021
        if re.search(r"Bachelor.*2021\s*[–\-]\s*2025", html_content, re.IGNORECASE):
            errors.append("Bachelor's degree shows wrong years (should be 2017–2021).")
        if re.search(r"Bachelor.*2021\s*[–\-]\s*Present", html_content, re.IGNORECASE):
            errors.append("Bachelor's degree shows wrong years (should be 2017–2021).")

        # Master's should be 2025–Present (or 2025–2026)
        if not re.search(r"MSc.*2025", html_content, re.IGNORECASE):
            warnings.append("Master's degree start year 2025 not found.")

        # 2. Check for invented grades – we now remove them, so no need to warn
        # 3. Check for placeholder links
        if "[Link]" in html_content:
            errors.append("Project links contain placeholder [Link] – please remove or replace with real links.")

        # 4. Check that both education entries exist
        if not re.search(r"University of Birmingham", html_content, re.IGNORECASE):
            errors.append("Missing University of Birmingham (Master's).")
        if not re.search(r"Visvesvaraya Technological University", html_content, re.IGNORECASE):
            errors.append("Missing Visvesvaraya Technological University (Bachelor's).")

        # 5. Check for experience entries
        if not re.search(r"Amazon", html_content, re.IGNORECASE):
            warnings.append("Amazon experience not found.")
        if not re.search(r"IBM", html_content, re.IGNORECASE):
            warnings.append("IBM experience not found.")

        # 6. Check that projects are present
        if not re.search(r"Automation System", html_content, re.IGNORECASE):
            warnings.append("Project 'Automation System' not found.")
        if not re.search(r"Sentiment Analysis", html_content, re.IGNORECASE):
            warnings.append("Project 'Sentiment Analysis' not found.")

        # Log issues
        if errors:
            for err in errors:
                logger.error(f"Resume validation ERROR: {err}")
        if warnings:
            for warn in warnings:
                logger.warning(f"Resume validation WARNING: {warn}")

        return len(errors) == 0  # Return True if no errors (warnings are okay)

    async def pdf_base64(self) -> str:
        """
        Create PDF file from generated HTML template.
        If a ready-made resume is configured and exists, return its base64 directly.
        """
        # 1. Ready-made resume check
        if UPLOAD_RESUME and READY_MADE_RESUME_PATH:
            ready_path = Path(READY_MADE_RESUME_PATH)
            if ready_path.exists() and ready_path.is_file():
                logger.info(f"Using ready-made resume from {ready_path}")
                import base64
                with open(ready_path, "rb") as f:
                    pdf_bytes = f.read()
                return base64.b64encode(pdf_bytes).decode("utf-8")
            else:
                logger.warning(
                    f"Ready-made resume path '{READY_MADE_RESUME_PATH}' does not exist or is not a file. "
                    "Proceeding with generation."
                )

        # 2. ALWAYS load the latest structured data from profile – ignore existing YAML
        from config.profile import PROFILE
        logger.info("Loading fresh structured resume data from profile (overwriting any existing YAML).")

        # Flatten all skills from the skills dictionary
        all_skills = []
        for category_skills in PROFILE["skills"].values():
            if isinstance(category_skills, list):
                all_skills.extend(category_skills)

        # Build the structured resume dictionary from profile
        structured = {
            "personal_information": {
                "first_name": PROFILE["personal"]["first_name"],
                "last_name": PROFILE["personal"]["last_name"],
                "email": PROFILE["personal"]["email"],
                "phone": PROFILE["personal"]["phone"],
                "location": PROFILE["personal"]["location"],
                "linkedin": PROFILE["personal"]["linkedin"],
                "github": PROFILE["personal"]["github"],
                "summary": PROFILE.get("common_answers", {}).get("interest_general", ""),
            },
            "education_details": PROFILE["education"],
            "experience_details": PROFILE["experience"],
            "projects": PROFILE["projects"],
            "skills": all_skills,
            "languages": PROFILE["languages"],
            "achievements": PROFILE["achievements"],
            "certifications": PROFILE.get("certifications", []),
	    "interests": [],   # <-- add this line
        }

        # Save this fresh data to YAML for future runs (optional)
        structured_file = Path(RESUME_DIR) / "structured_resume.yaml"
        save_yaml_file(structured_file, structured)
        logger.info("Fresh structured resume saved to YAML from profile.")

        # Inject the fresh data into the generator
        if hasattr(self.resume_generator, 'resume_structured'):
            self.resume_generator.resume_structured = structured
        elif hasattr(self.resume_generator, 'structured_resume'):
            self.resume_generator.structured_resume = structured
        elif hasattr(self.resume_generator, 'gpt_answerer') and hasattr(self.resume_generator.gpt_answerer, 'resume_structured'):
            self.resume_generator.gpt_answerer.resume_structured = structured
        else:
            logger.warning("Could not inject structured data into resume generator.")

        # Log the number of experience entries and bullet points for debugging
        exp_count = len(structured.get('experience_details', []))
        total_bullets = sum(len(exp.get('responsibilities', [])) for exp in structured.get('experience_details', []))
        logger.info(f"Loaded {exp_count} experience entries with {total_bullets} total bullet points from profile.")

        # 3. Choose style
        if self.selected_style is None:
            self.choose_style()
            if self.selected_style is None:
                raise ValueError("No resume style selected and unable to choose a default.")

        style_path = self.style_manager.get_style_path(self.selected_style)
        if not style_path or not style_path.exists():
            logger.warning(
                f"Selected style '{self.selected_style}' not found at '{style_path}'. "
                "Falling back to first available style."
            )
            styles = self.style_manager.get_styles()
            if styles:
                fallback_style = list(styles.keys())[0]
                self.selected_style = fallback_style
                style_path = self.style_manager.get_style_path(fallback_style)
                logger.info(f"Using fallback style '{fallback_style}'")
            else:
                raise FileNotFoundError("No resume styles available. Please add a style to the resume_style directory.")

        # 4. Generate HTML
        with tempfile.NamedTemporaryFile(
            delete=False, mode="w", suffix=".html", encoding="utf-8"
        ) as temp_html_file:
            temp_html_path = temp_html_file.name
            self.resume_generator.create_resume(style_path, temp_html_path)

        # 5. Read the HTML content
        with open(temp_html_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        # 6. Clean the HTML (remove grades, fix years, remove [Link])
        cleaned_html = self._clean_resume_html(html_content)

        # 7. Write cleaned HTML back
        with open(temp_html_path, "w", encoding="utf-8") as f:
            f.write(cleaned_html)

        # 8. Validate
        is_valid = self._validate_resume_html(cleaned_html)
        if not is_valid:
            logger.warning("Resume validation found errors. The PDF may still be generated, but please review.")

        # 9. Convert to PDF
        pdf_base64 = await HTML_to_PDF(temp_html_path)
        os.remove(temp_html_path)
        return pdf_base64


if __name__ == "__main__":
    """Simple test to generate a resume"""
    import asyncio
    import base64
    import dotenv

    from config.constants import RESUME_DIR
    from src.job_manager.resume_anonymizer import ResumeAnonymizer
    from src.llm.llm_manager import GPTAnswerer
    from src.resume_builder.resume_generator import ResumeGenerator
    from src.resume_builder.style_manager import StyleManager
    from src.utils.utils import load_yaml_file

    async def test_resume_generation():
        logger.info("Starting resume generation test...")
        try:
            secrets = dotenv.dotenv_values(".env")
            llm_api_key = secrets.get("llm_api_key", "")
            llm_proxy = secrets.get("llm_proxy", "")

            resume_structured_file = Path(RESUME_DIR) / "structured_resume.yaml"
            resume_text_file = Path(RESUME_DIR) / "resume_text.txt"

            with open(resume_text_file, "r", encoding="utf-8") as f:
                resume_text = f.read()

            try:
                resume_structured = load_yaml_file(resume_structured_file)
            except Exception as e:
                if not str(e).startswith("File not found"):
                    raise
                from src.pydantic_models.prompt_models import ResumeStructure
                from src.utils.utils import save_yaml_file

                logger.info("Structured resume not found, generating from resume text...")
                gpt_answerer_for_parse = GPTAnswerer(llm_api_key, llm_proxy)
                resume_structured = gpt_answerer_for_parse.parse_resume(resume_text)
                resume_structured = ResumeStructure(**resume_structured).model_dump()
                save_yaml_file(resume_structured_file, resume_structured)
                logger.info(f"Structured resume saved to {resume_structured_file}")

            resume_anonymizer = ResumeAnonymizer(resume_structured)
            resume_anonymizer.anonymize_personal_information()
            resume_structured = resume_anonymizer.resume_anonymized
            resume_text = resume_anonymizer.anonymize_text(resume_text)

            gpt_answerer = GPTAnswerer(llm_api_key, llm_proxy)
            gpt_answerer.set_resume(resume_structured, resume_text)

            test_job = {
                "job_title": "BrowserUse consultant engineer position",
                "company_name": "Teemo AI",
                "job_description": "We are looking for a BrowserUse consultant engineer with experience in BrowserUse, Chrome Extensions, and cloud technologies.",
            }
            gpt_answerer.set_job(test_job)

            style_manager = StyleManager()
            resume_generator = ResumeGenerator(gpt_answerer, resume_anonymizer)

            resume_manager = ResumeManager(llm_api_key, style_manager, resume_generator)
            resume_manager.choose_style()

            logger.info("Generating PDF resume...")
            pdf_base64 = await resume_manager.pdf_base64()

            output_file = Path("test_generated_resume.pdf")
            with open(output_file, "wb") as f:
                f.write(base64.b64decode(pdf_base64))

            logger.info(f"✅ Resume generated successfully! Saved to: {output_file}")
            logger.info(f"PDF size: {len(pdf_base64)} characters")
            return True

        except FileNotFoundError as e:
            logger.error(f"❌ Required file not found: {e}")
            logger.error("Make sure you have:")
            logger.error("1. data/secrets/secrets.yaml with LLM API key")
            logger.error("2. data/resume/resume.txt with your resume text")
            logger.error("3. data/resume/structured_resume.yaml with structured resume data")
            return False
        except Exception as e:
            logger.error(f"❌ Resume generation test failed: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False

    success = asyncio.run(test_resume_generation())
    if success:
        print("✅ Resume generation test passed!")
    else:
        print("❌ Resume generation test failed!")