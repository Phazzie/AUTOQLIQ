"""Cookie handling for PlaywrightDriver."""

import logging
from typing import Any, Dict, List, TYPE_CHECKING

from src.core.exceptions import WebDriverError

# Conditional import to avoid circular imports
if TYPE_CHECKING:
    from src.infrastructure.webdrivers.playwright.driver import PlaywrightDriver

# Import Playwright specifics - requires Playwright to be installed
try:
    from playwright.sync_api import Error as PlaywrightError, Page
except ImportError:
    # Allow module to load but fail at runtime if Playwright is used without installation
    PlaywrightError = Exception  # Base exception fallback
    Page = None  # Type placeholder


logger = logging.getLogger(__name__)


class PlaywrightCookieHandler:
    """Handles cookie operations for PlaywrightDriver."""

    def __init__(self, driver: 'PlaywrightDriver'):
        """
        Initialize the cookie handler.

        Args:
            driver: The PlaywrightDriver instance.
        """
        self._driver = driver

    def get_cookies(self) -> List[Dict[str, Any]]:
        """Get all cookies from the browser."""
        logger.debug("Getting all cookies")
        try:
            context = self._driver._get_context()
            if isinstance(context, Page):
                return context.context.cookies()
            else:  # Frame doesn't have direct access to cookies
                page = self._driver._ensure_page()
                return page.context.cookies()
        except PlaywrightError as e:
            raise WebDriverError(f"Playwright failed to get cookies: {e}") from e

    def add_cookie(self, cookie: Dict[str, Any]) -> None:
        """Add a cookie to the browser."""
        logger.debug(f"Adding cookie: {cookie.get('name')}")
        try:
            page = self._driver._ensure_page()
            page.context.add_cookies([cookie])
        except PlaywrightError as e:
            raise WebDriverError(f"Playwright failed to add cookie: {e}") from e

    def delete_all_cookies(self) -> None:
        """Delete all cookies."""
        logger.debug("Deleting all cookies")
        try:
            page = self._driver._ensure_page()
            page.context.clear_cookies()
        except PlaywrightError as e:
            raise WebDriverError(f"Playwright failed to delete all cookies: {e}") from e
