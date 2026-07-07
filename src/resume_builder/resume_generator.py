import re
from pathlib import Path
from string import Template
from typing import Any

from config.constants import RESUME_DIR
from config.logger_config import logger
from src.job_manager.resume_anonymizer import ResumeAnonymizer
from src.utils.utils import load_yaml_file


class ResumeGenerator:
    """Class for generating resumes"""

    def __init__(self, gpt_resume_generator: Any, resume_anonymizer: ResumeAnonymizer):
        self.gpt_resume_generator = gpt_resume_generator
        self.resume_anonymizer = resume_anonymizer
        self.html_template = """
                            <!DOCTYPE html>
                            <html lang="en">
                            <head>
                                <meta charset="UTF-8">
                                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                                <title>Resume</title>
                                <link href="https://fonts.googleapis.com/css2?family=Barlow:wght@400;600&display=swap" rel="stylesheet" />
                                <link href="https://fonts.googleapis.com/css2?family=Barlow:wght@400;600&display=swap" rel="stylesheet" />
                                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css" />
                                <link rel="stylesheet" href="$style_path">
                            </head>
                            $markdown
                            </body>
                            </html>
                            """

    def create_resume(
        self,
        style_path: str,
        temp_html_path: str,
    ):
        """Generate resume"""
        self._create_resume(style_path, temp_html_path)

    def _ensure_structured_data(self) -> None:
        """
        Ensure that the GPTAnswerer has structured data.
        If it's empty, load from structured_resume.yaml and set it.
        """
        structured = getattr(self.gpt_resume_generator, 'resume_structured', None)
        if not structured or not structured.get('experience_details') and not structured.get('education_details'):
            logger.warning("GPTAnswerer has no structured data or it's empty. Loading from YAML...")
            yaml_path = Path(RESUME_DIR) / "structured_resume.yaml"
            if yaml_path.exists():
                try:
                    loaded = load_yaml_file(yaml_path)
                    # Set it on the GPTAnswerer
                    self.gpt_resume_generator.resume_structured = loaded
                    # Also set resume_readable if needed (optional)
                    logger.info(f"Loaded structured resume from {yaml_path} with {len(loaded.get('experience_details', []))} experiences, {len(loaded.get('education_details', []))} educations, {len(loaded.get('skills', []))} skills.")
                except Exception as e:
                    logger.error(f"Failed to load structured_resume.yaml: {e}")
            else:
                logger.error(f"structured_resume.yaml not found at {yaml_path}. Cannot generate full resume.")
        else:
            # Log what we have
            exp_count = len(structured.get('experience_details', []))
            edu_count = len(structured.get('education_details', []))
            skill_count = len(structured.get('skills', []))
            logger.info(f"Structured resume already has: {exp_count} experiences, {edu_count} educations, {skill_count} skills.")

    def _create_resume(self, style_path: str, temp_html_path):
        """Helper method for generating resumes"""
        # Ensure structured data is present
        self._ensure_structured_data()

        template = Template(self.html_template)
        html_resume = self.gpt_resume_generator.generate_html_resume()
        deanonymized_html_resume = self.resume_anonymizer.deanonymize_text(html_resume)
        deanonymized_html_resume = self._normalize_anchor_hrefs(deanonymized_html_resume)
        message = template.substitute(markdown=deanonymized_html_resume, style_path=style_path)
        with open(temp_html_path, "w", encoding="utf-8") as temp_file:
            temp_file.write(message)

    @staticmethod
    def _normalize_anchor_hrefs(html: str) -> str:
        """
        Normalize common "bare" links produced by the LLM (e.g. href="github.com/...") into
        absolute URLs so Chromium/Playwright can embed clickable link annotations in the PDF.
        """

        def repl(match: re.Match) -> str:
            quote = match.group("q")
            href = match.group("href").strip()

            # Leave these as-is
            if re.match(r"^(https?://|mailto:|tel:|#|/|file:)", href, flags=re.IGNORECASE):
                return f"href={quote}{href}{quote}"

            # Promote common domains to https://
            if re.match(r"^(www\.)", href, flags=re.IGNORECASE):
                return f"href={quote}https://{href}{quote}"

            if re.match(r"^(github\.com/|linkedin\.com/)", href, flags=re.IGNORECASE):
                return f"href={quote}https://{href}{quote}"

            return f"href={quote}{href}{quote}"

        return re.sub(
            r'href=(?P<q>["\'])(?P<href>[^"\']+)(?P=q)',
            repl,
            html,
            flags=re.IGNORECASE,
        )