import asyncio
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

from browser_use import Agent, Browser, ChatAnthropic, ChatGoogle, ChatOllama, ChatOpenAI, Tools
from browser_use.tools.views import UploadFileAction

from config.app_config import (
    APPLY_AGENT_MODEL,
    EXTERNAL_APPLY_AGENT_MODEL,
    EXTERNAL_APPLY_MAX_STEPS,
    EXTERNAL_APPLY_STEP_TIMEOUT,
    EXTERNAL_APPLY_TOTAL_TIMEOUT,
    HEADLESS_MODE,
    LLM_MODEL_TYPE,
)
from config.constants import CUSTOM_COST_PER_TOKEN, LOG_DIR, RESUME_DIR, cost_per_token
from config.logger_config import logger
from src.dashboard.runtime import emit_event
from src.pydantic_models.log_models import LLMCall
from src.utils.utils import append_yaml_file, get_ready_made_resume


class ApplyAgent:
    def __init__(
        self,
        api_key: str = None,
        browser_storage_state: str = None,
        llm_api_url: str = None,
        user_email: str = None,
        model_name: str = None,
        max_steps: int = None,
        step_timeout: int = None,
        total_timeout: int = None,
        resume_generator: Optional[Callable] = None,
    ) -> None:
        self.api_key = api_key
        self.user_email = user_email
        self.model = model_name or EXTERNAL_APPLY_AGENT_MODEL or APPLY_AGENT_MODEL
        self.model_type = LLM_MODEL_TYPE
        self.llm_api_url = llm_api_url
        self.llm = self.select_model_type(self.model_type, self.llm_api_url)
        self.calls_log = os.path.join(Path(LOG_DIR), "llm_api_calls.yaml")
        self.agent = None
        self.resume_readable = None
        self.resume_generator = resume_generator
        self.job_description = None
        self.max_steps = max_steps or EXTERNAL_APPLY_MAX_STEPS
        self.step_timeout = step_timeout or EXTERNAL_APPLY_STEP_TIMEOUT
        self.total_timeout = total_timeout or EXTERNAL_APPLY_TOTAL_TIMEOUT

        self.browser_storage_state = str(Path(browser_storage_state).absolute()) if browser_storage_state else None
        storage_state = (
            self.browser_storage_state if self.browser_storage_state and Path(self.browser_storage_state).exists() else None
        )
        if storage_state is None and self.browser_storage_state:
            logger.warning(
                f"Browser storage state file not found at {self.browser_storage_state}. "
                "Continuing without persisted cookies/localStorage."
            )
        self.storage_state = storage_state

        self.temp_dir = Path(tempfile.mkdtemp(prefix="apply_agent_resume_"))
        logger.debug(f"Created temporary directory for resumes: {self.temp_dir}")

    def __del__(self):
        try:
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
                logger.debug(f"Removed temporary directory: {self.temp_dir}")
        except Exception:
            pass

    def set_resume(self, resume_readable: str) -> None:
        self.resume_readable = resume_readable

    def set_resume_generator(self, generator: Callable) -> None:
        self.resume_generator = generator

    def set_job_description(self, job_description: str) -> None:
        self.job_description = job_description

    def _get_resume_pdf_path(self, job_title: str = "", company_name: str = "") -> Optional[str]:
        # If generator exists and job description is set, try custom generation
        if self.resume_generator and self.job_description and self.resume_readable:
            logger.info("Generating custom resume for this job...")
            try:
                pdf_path = self.resume_generator(
                    job_title=job_title,
                    company_name=company_name,
                    job_description=self.job_description,
                )
                if pdf_path and Path(pdf_path).exists():
                    logger.info(f"Custom resume generated: {pdf_path}")
                    return str(pdf_path)
                else:
                    logger.warning("Custom resume generation failed or returned invalid path. Using static resume.")
            except Exception as e:
                logger.error(f"Error generating custom resume: {e}")

        # Fallback: check for static resume.pdf in the resume directory
        static_pdf = Path(RESUME_DIR) / "resume.pdf"
        if static_pdf.exists():
            logger.info(f"Using static resume: {static_pdf}")
            return str(static_pdf)

        # If even that fails, return None (the agent will skip upload)
        logger.warning("No resume PDF found (neither custom nor static). Upload will be skipped.")
        return None

    def _create_browser(self) -> Browser:
        return Browser(
            headless=HEADLESS_MODE,
            storage_state=self.storage_state,
        )

    def select_model_type(self, model_type: str, llm_api_url: str):
        self.model_type = model_type
        if model_type == "gemini":
            if not self.api_key:
                raise ValueError("API key is required for Gemini model")
            llm = ChatGoogle(api_key=self.api_key, model=self.model)
        elif model_type == "openai":
            if not self.api_key:
                raise ValueError("API key is required for OpenAI model")
            llm = ChatOpenAI(api_key=self.api_key, model=self.model, reasoning_effort="minimal")
        elif model_type == "claude":
            if not self.api_key:
                raise ValueError("API key is required for Claude model")
            llm = ChatAnthropic(api_key=self.api_key, model=self.model)
        elif model_type == "ollama":
            if llm_api_url:
                os.environ["OLLAMA_BASE_URL"] = llm_api_url
            llm = ChatOllama(model=self.model)
        elif model_type == "openrouter":
            llm = ChatOpenAI(
                api_key=self.api_key,
                model=self.model,
                base_url="https://openrouter.ai/api/v1",
            )
        elif model_type == "nvidia_nim":
            if not self.api_key:
                raise ValueError("API key is required for NVIDIA NIM model")
            llm = ChatOpenAI(
                api_key=self.api_key,
                model=self.model,
                base_url="https://integrate.api.nvidia.com/v1",
            )
        elif model_type == "groq":
            if not self.api_key:
                raise ValueError("API key is required for Groq model")
            llm = ChatOpenAI(
                api_key=self.api_key,
                model=self.model,
                base_url="https://api.groq.com/openai/v1",
            )
        elif model_type == "cerebras":
            if not self.api_key:
                raise ValueError("API key is required for Cerebras model")
            llm = ChatOpenAI(
                api_key=self.api_key,
                model=self.model,
                base_url="https://api.cerebras.ai/v1",
            )
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
        return llm

    async def apply(self, job_url: str, job_title: str = "", company_name: str = "") -> None:
        resume_pdf_path = self._get_resume_pdf_path(job_title, company_name)
        emit_event("agent_apply_started", "External apply agent started", url=job_url)

        tools = Tools()

        @tools.action(
            description="Get an UploadFileAction for my resume PDF file (use with upload_file_to_element if needed)"
        )
        async def upload_resume(browser_session, index: int = 0):
            return UploadFileAction(path=resume_pdf_path, index=index)

        browser_storage_state = self.browser_storage_state

        @tools.action(
            description=(
                "Call this when the website requires email verification or confirmation "
                "before you can proceed. This pauses the task and asks the user to verify "
                "their email, then saves the browser session so the user won't need to "
                "log in again."
            )
        )
        async def wait_for_email_verification(browser_session):
            print("\n" + "=" * 60)
            print("EMAIL VERIFICATION REQUIRED")
            print("Please check your email and confirm your account.")
            print("Once done, press Enter to continue...")
            print("=" * 60 + "\n")
            await asyncio.get_event_loop().run_in_executor(None, input)
            await browser_session.export_storage_state(output_path=browser_storage_state)
            logger.info(f"Browser session saved to {browser_storage_state}")
            return "User confirmed email verification. Browser session saved. Proceeding with the application."

        task = f"""
        Your task is to apply to the job at: {job_url}

        **CRITICAL: This may be a Google Form, Workday, Lever, Greenhouse, or a custom company career page.**
        Treat every field you encounter as part of the application.

        ## Resume (source of truth)
        {self.resume_readable}

        ## Instructions
        1. Navigate to the URL and wait for the page to load completely.
        2. If a cookie consent banner appears, click "Accept" or "Allow" to dismiss it.
        3. If you see a "Sign in" or "Register" page:
           - Use my email: {self.user_email}
           - Use my password: {self.user_email.split("@")[0] + "123456" if self.user_email else "unknown"}
           - Complete the login/registration.
        4. Fill the application form from top to bottom:
           - For text inputs, use information from my resume.
           - For dropdowns, select the option that best matches my experience.
           - For radio buttons/checkboxes, choose the most appropriate based on my resume.
           - For file uploads (resume/CV), look for an upload button and upload the file at: {resume_pdf_path}
           - Do NOT skip required fields. If you can't find the answer, use "Not specified" or "N/A".
        5. **Google Forms specific**:
           - They often have "Short answer", "Paragraph", "Multiple choice", "Checkboxes", and "Dropdown" questions.
           - For "Full Name", use the name from my resume.
           - For "Email", use my email.
           - For "Resume/CV" upload, look for the file upload question and upload the PDF.
           - For "LinkedIn profile", you can enter my LinkedIn URL if available (or skip).
        6. **Workday / Lever / Greenhouse**:
           - These are multi‑step forms. Click "Next" or "Continue" after each section.
           - Watch for "Review" or "Submit" at the end.
        7. **Submit the form**:
           - Look for buttons labeled "Submit", "Apply", "Send", "Next", "Continue", or "Finish".
           - If there are multiple steps (e.g., "Next" -> "Next" -> "Submit"), go through all steps.
           - After submitting, wait for a confirmation message (e.g., "Application received", "Thank you").
        8. **Final Step**:
           - If the application is successful, you will see a confirmation page or message.
           - If you cannot apply (e.g., "Position filled", "Application closed"), finish the task.

        ## IMPORTANT RULES
        - You are not done until you have either submitted the application OR confirmed you cannot apply.
        - If you get stuck on a page for more than 2 minutes, try clicking the most obvious button and continue.
        - Do not open new tabs unless absolutely necessary.
        - Keep your actions deliberate and avoid unnecessary navigation.
        - If a field is optional, you may skip it if you cannot find the answer.

        ## FINAL OUTPUT
        At the end, provide a summary of:
        1. What actions you performed (detected fields, filled, submitted).
        2. Any questions encountered and how you answered them.
        3. Final status: "Success" or "Cannot apply".

        Good luck!
        """

        available_file_paths = [resume_pdf_path] if resume_pdf_path else []

        browser = self._create_browser()
        try:
            self.agent = Agent(
                task=task,
                browser=browser,
                llm=self.llm,
                tools=tools,
                use_vision=True,
                use_thinking=False,
                max_actions_per_step=3,
                save_conversation_path=Path(LOG_DIR).absolute() / "apply_agent_conversation",
                available_file_paths=available_file_paths,
            )
            # FIX: The newer browser_use version does not accept 'timeout' or 'step_timeout' in run()
            # We pass only max_steps; timeouts are either set during Agent init or globally.
            await self.agent.run(max_steps=self.max_steps)
        except TypeError as e:
            # Fallback: if even max_steps is rejected, try run() without arguments.
            if "max_steps" in str(e):
                logger.warning("max_steps not accepted in run(), calling run() without arguments.")
                await self.agent.run()
            else:
                raise
        finally:
            await browser.stop()

        self._log_token_usage(task)
        emit_event("agent_apply_completed", "External apply agent completed", url=job_url)

    def _log_token_usage(self, task: str) -> None:
        if not self.agent:
            logger.warning("Agent not initialized, cannot log token usage.")
            return
        try:
            token_usage = self.agent.token_cost_service.get_usage_tokens_for_model(self.model)
            input_tokens, output_tokens = token_usage.prompt_tokens, token_usage.completion_tokens
            total_tokens = input_tokens + output_tokens
            logger.info(
                f"Token usage - Input: {input_tokens}, Output: {output_tokens}, Total: {total_tokens}"
            )
            prompt_cost, completion_cost = cost_per_token(
                model=self.model.replace("google/", ""),
                prompt_tokens=input_tokens,
                completion_tokens=output_tokens,
                custom_cost_per_token=CUSTOM_COST_PER_TOKEN,
            )
            total_cost = prompt_cost + completion_cost
            logger.info(f"Total cost calculated: {total_cost}")

            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            try:
                log_entry = LLMCall(
                    model_name=self.model,
                    timestamp=current_time,
                    prompts={
                        "prompt_1": task,
                        "prompt_2": "<Some browser content>",
                    },
                    parsed_reply="<Some reply from agent>",
                    total_tokens=total_tokens,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    response_time_seconds=0.0,
                    total_cost=total_cost,
                )
                logger.debug(f"Log entry created: {log_entry}")
            except KeyError as e:
                logger.error(f"Error creating log entry: missing key {str(e)} in parsed_reply")
                raise

            append_yaml_file(Path(self.calls_log), log_entry.model_dump())
            return total_cost
        except Exception as e:
            logger.error(f"Failed to log token usage: {e}")

    async def apply_to_job(self, job_url: str, job_description: str = "", job_title: str = "", company_name: str = "") -> tuple[str, str]:
        self.set_job_description(job_description)
        try:
            await self.apply(job_url, job_title, company_name)
            return ("Success", "")
        except Exception as e:
            logger.error(f"Error applying to job: {e}")
            emit_event("agent_apply_failed", "External apply agent failed", url=job_url, error=str(e))
            return ("Error", str(e))


if __name__ == "__main__":
    """Test ApplyAgent functionality"""
    import traceback
    import dotenv
    from config.constants import BROWSER_STORAGE_STATE
    from src.pydantic_models.prompt_models import ResumeStructure
    from src.utils.utils import load_yaml_file

    async def test_apply_agent():
        logger.info("Starting ApplyAgent test...")
        try:
            secrets = dotenv.dotenv_values(".env")
            llm_api_key = secrets.get("llm_api_key", "")
            if not llm_api_key:
                logger.error("❌ LLM API key not found in .env file")
                return False

            apply_agent = ApplyAgent(
                api_key=llm_api_key,
                browser_storage_state=BROWSER_STORAGE_STATE,
                user_email=secrets.get("linkedin_email", ""),
                model_name="llama3.2:3b",
                max_steps=50,
                step_timeout=120,
            )
            logger.info("ApplyAgent initialized successfully")

            RESUME_STRUCTURED_FILE = Path(RESUME_DIR) / "structured_resume.yaml"
            RESUME_TEXT_FILE = Path(RESUME_DIR) / "resume_text.txt"

            if not RESUME_STRUCTURED_FILE.exists():
                logger.error(f"❌ Resume structured file not found: {RESUME_STRUCTURED_FILE}")
                return False
            if not RESUME_TEXT_FILE.exists():
                logger.error(f"❌ Resume text file not found: {RESUME_TEXT_FILE}")
                return False

            resume_structured = load_yaml_file(RESUME_STRUCTURED_FILE)
            resume_structured = ResumeStructure(**resume_structured).model_dump()
            with open(RESUME_TEXT_FILE, "r") as f:
                resume_text = f.read()

            apply_agent.set_resume(resume_text)
            logger.info("Resume and job data set successfully")

            vacancy_url = "https://app.searchwithjack.com/jobs/4372944?utm_source=linkedin-direct-apply-4372944&comet_source=linkedin"
            logger.info(f"Testing ApplyAgent.apply_to_job method with job: {vacancy_url}")
            await apply_agent.apply_to_job(vacancy_url)

            logger.info("✅ ApplyAgent test completed successfully!")
            return True
        except Exception as e:
            logger.error(f"❌ ApplyAgent test failed with error: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False

    success = asyncio.run(test_apply_agent())
    if success:
        print("✅ Test passed!")
    else:
        print("❌ Test failed!")