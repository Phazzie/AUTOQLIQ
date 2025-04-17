"""Dialog handling for PlaywrightDriver."""

import logging
import concurrent.futures
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


class PlaywrightDialogHandler:
    """Handles dialog interactions for PlaywrightDriver."""

    def __init__(self, driver: 'PlaywrightDriver'):
        """
        Initialize the dialog handler.

        Args:
            driver: The PlaywrightDriver instance.
        """
        self._driver = driver

    def accept_alert(self) -> None:
        """Accept the currently displayed alert dialog."""
        logger.debug("Accepting alert")
        try:
            page = self._driver._ensure_page()
            # Set up dialog handler before the alert appears
            page.once("dialog", lambda dialog: dialog.accept())
        except PlaywrightError as e:
            raise WebDriverError(f"Playwright failed to accept alert: {e}") from e

    def dismiss_alert(self) -> None:
        """Dismiss the currently displayed alert dialog."""
        logger.debug("Dismissing alert")
        try:
            page = self._driver._ensure_page()
            # Set up dialog handler before the alert appears
            page.once("dialog", lambda dialog: dialog.dismiss())
        except PlaywrightError as e:
            raise WebDriverError(f"Playwright failed to dismiss alert: {e}") from e

    def get_alert_text(self) -> str:
        """Get the text of the currently displayed alert dialog."""
        logger.debug("Getting alert text")
        try:
            page = self._driver._ensure_page()
            # This is tricky with Playwright as we need to handle the dialog when it appears
            # We'll use a custom approach with a future
            future = concurrent.futures.Future()

            def handle_dialog(dialog):
                text = dialog.message
                future.set_result(text)
                dialog.accept()  # We need to handle the dialog

            page.once("dialog", handle_dialog)

            # Wait for the future to complete (timeout after a reasonable time)
            # Note: This assumes the alert is already present or will appear soon
            try:
                return future.result(timeout=5)  # 5 second timeout
            except concurrent.futures.TimeoutError:
                raise WebDriverError("Timed out waiting for alert")
        except PlaywrightError as e:
            raise WebDriverError(f"Playwright failed to get alert text: {e}") from e
