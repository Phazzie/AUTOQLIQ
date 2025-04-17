"""Network handling for PlaywrightDriver."""

import logging
from typing import Any, Callable, Optional, TYPE_CHECKING

from src.core.exceptions import WebDriverError

# Conditional import to avoid circular imports
if TYPE_CHECKING:
    from src.infrastructure.webdrivers.playwright.driver import PlaywrightDriver

# Import Playwright specifics - requires Playwright to be installed
try:
    from playwright.sync_api import Error as PlaywrightError, TimeoutError as PlaywrightTimeoutError
except ImportError:
    # Allow module to load but fail at runtime if Playwright is used without installation
    PlaywrightError = Exception  # Base exception fallback
    PlaywrightTimeoutError = Exception  # Base exception fallback


logger = logging.getLogger(__name__)


class PlaywrightNetworkHandler:
    """Handles network operations for PlaywrightDriver."""

    def __init__(self, driver: 'PlaywrightDriver'):
        """
        Initialize the network handler.

        Args:
            driver: The PlaywrightDriver instance.
        """
        self._driver = driver

    def add_route_handler(self, url_pattern: str, handler: Callable) -> None:
        """
        Add a route handler to intercept network requests.

        Args:
            url_pattern: URL pattern to match for interception (supports glob patterns)
            handler: Callback function that takes a Route and Request object and handles the request
                     The signature should be: handler(route, request) -> None
                     The handler must call either route.fulfill(), route.continue_() or route.abort()
        """
        logger.debug(f"Adding route handler for URL pattern: {url_pattern}")
        try:
            page = self._driver._ensure_page()
            page.route(url_pattern, handler)
        except PlaywrightError as e:
            raise WebDriverError(f"Playwright failed to add route handler: {e}") from e

    def remove_route_handler(self, url_pattern: str, handler: Optional[Callable] = None) -> None:
        """
        Remove a previously added route handler.

        Args:
            url_pattern: URL pattern that was used to add the handler
            handler: The handler function to remove. If None, removes all handlers for the pattern.
        """
        logger.debug(f"Removing route handler for URL pattern: {url_pattern}")
        try:
            page = self._driver._ensure_page()
            if handler:
                page.unroute(url_pattern, handler)
            else:
                page.unroute(url_pattern)
        except PlaywrightError as e:
            raise WebDriverError(f"Playwright failed to remove route handler: {e}") from e

    def wait_for_request(self, url_pattern: str, timeout: int = 10) -> Any:
        """
        Wait for a request matching the given URL pattern.

        Args:
            url_pattern: URL pattern to match (supports glob patterns)
            timeout: Maximum time to wait in seconds

        Returns:
            The Request object that matched the pattern
        """
        logger.debug(f"Waiting for request matching pattern: {url_pattern}")
        try:
            page = self._driver._ensure_page()
            return page.wait_for_request(url_pattern, timeout=timeout * 1000)
        except PlaywrightTimeoutError:
            raise WebDriverError(f"Timeout waiting for request matching: {url_pattern}")
        except PlaywrightError as e:
            raise WebDriverError(f"Playwright failed to wait for request: {e}") from e

    def wait_for_response(self, url_pattern: str, timeout: int = 10) -> Any:
        """
        Wait for a response matching the given URL pattern.

        Args:
            url_pattern: URL pattern to match (supports glob patterns)
            timeout: Maximum time to wait in seconds

        Returns:
            The Response object that matched the pattern
        """
        logger.debug(f"Waiting for response matching pattern: {url_pattern}")
        try:
            page = self._driver._ensure_page()
            return page.wait_for_response(url_pattern, timeout=timeout * 1000)
        except PlaywrightTimeoutError:
            raise WebDriverError(f"Timeout waiting for response matching: {url_pattern}")
        except PlaywrightError as e:
            raise WebDriverError(f"Playwright failed to wait for response: {e}") from e
