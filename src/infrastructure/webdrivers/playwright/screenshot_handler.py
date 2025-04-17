"""Screenshot handling for PlaywrightDriver."""

import logging
from typing import TYPE_CHECKING

from src.core.exceptions import WebDriverError

# Conditional import to avoid circular imports
if TYPE_CHECKING:
    from src.infrastructure.webdrivers.playwright.driver import PlaywrightDriver

# Import Playwright specifics - requires Playwright to be installed
try:
    from playwright.sync_api import Error as PlaywrightError
except ImportError:
    # Allow module to load but fail at runtime if Playwright is used without installation
    PlaywrightError = Exception  # Base exception fallback


logger = logging.getLogger(__name__)


class PlaywrightScreenshotHandler:
    """Handles screenshot operations for PlaywrightDriver."""

    def __init__(self, driver: 'PlaywrightDriver'):
        """
        Initialize the screenshot handler.

        Args:
            driver: The PlaywrightDriver instance.
        """
        self._driver = driver

    def take_screenshot(self, file_path: str) -> None:
        """Take a screenshot and save it."""
        logger.debug(f"Taking screenshot to path: {file_path}")
        try:
            page = self._driver._ensure_page()
            page.screenshot(path=file_path)
        except PlaywrightError as e:
            raise WebDriverError(f"Playwright failed to take screenshot to {file_path}: {e}") from e
        except IOError as e:
            raise WebDriverError(f"File system error saving screenshot to {file_path}: {e}") from e

    def take_element_screenshot(self, selector: str, file_path: str) -> None:
        """Take a screenshot of a specific element and save it."""
        logger.debug(f"Taking screenshot of element {selector} to path: {file_path}")
        try:
            context = self._driver._get_context()
            element = context.locator(selector)
            element.screenshot(path=file_path)
        except PlaywrightError as e:
            raise WebDriverError(f"Playwright failed to take element screenshot to {file_path}: {e}") from e
        except IOError as e:
            raise WebDriverError(f"File system error saving element screenshot to {file_path}: {e}") from e

    def take_full_page_screenshot(self, file_path: str) -> None:
        """Take a screenshot of the full page and save it."""
        logger.debug(f"Taking full page screenshot to path: {file_path}")
        try:
            page = self._driver._ensure_page()
            page.screenshot(path=file_path, full_page=True)
        except PlaywrightError as e:
            raise WebDriverError(f"Playwright failed to take full page screenshot to {file_path}: {e}") from e
        except IOError as e:
            raise WebDriverError(f"File system error saving full page screenshot to {file_path}: {e}") from e
