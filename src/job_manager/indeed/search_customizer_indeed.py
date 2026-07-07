import urllib.parse
from typing import Any, Dict

from src.job_manager.search_customizer import BaseSearchCustomizer
from src.utils.utils import async_pause
from config.logger_config import logger


class IndeedSearchCustomizer(BaseSearchCustomizer):
    def __init__(self, page):
        self.page = page
        self.parameters = {}
        logger.info("IndeedSearchCustomizer initialized")

    def set_parameters(self, parameters: Dict[str, Any]):
        """Store the search parameters for later use."""
        # Only overwrite if the new dict is not empty
        if parameters:
            self.parameters = parameters
            logger.info(f"IndeedSearchCustomizer parameters set: {parameters}")
        else:
            logger.warning("Received empty parameters; keeping existing.")

    async def set_search_params(self) -> None:
        """
        Apply the stored search parameters to Indeed (UK version).
        """
        if not self.parameters:
            logger.warning("No search parameters set; using defaults.")
            query = "Python remote"
            location = "Remote"
            remote = True
        else:
            # Build query
            positions = self.parameters.get("positions", [])
            if isinstance(positions, list):
                # Take first 3 terms to keep URL short
                if len(positions) > 3:
                    positions = positions[:3]
                query = " OR ".join(positions)
            else:
                query = positions

            # Location: use first location if any, else "Remote" if remote is True
            locations = self.parameters.get("locations", [])
            remote = self.parameters.get("remote", False)
            if remote:
                location = "Remote"
            elif locations:
                location = locations[0]
            else:
                location = ""

        base_url = "https://uk.indeed.com/jobs"
        params = {"q": query}
        if location:
            params["l"] = location
        if remote:
            params["remote"] = "1"

        date_config = self.parameters.get("date", {})
        if date_config.get("week", False):
            params["fromage"] = "7"

        url = f"{base_url}?{urllib.parse.urlencode(params)}"
        logger.info(f"Navigating to Indeed search: {url}")

        await self.page.goto(url, wait_until="domcontentloaded")
        await async_pause(2, 3)

        logger.info("Indeed search parameters applied successfully")

    def is_job_blacklisted(self, job_title: str, company_name: str, location: str) -> bool:
        return False