"""Element interaction handler for PlaywrightDriver.

This module provides specialized handling for element interactions in Playwright.
It encapsulates all element-related operations, improving separation of concerns
and making the main driver class more maintainable.

Playwright's approach to elements differs from Selenium:
1. It uses Locators instead of WebElements
2. It has built-in auto-waiting for elements
3. It provides more reliable element interactions
"""

import logging
from typing import Any, Optional, TYPE_CHECKING

from src.core.exceptions import WebDriverError, ValidationError

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


class PlaywrightElementHandler:
    """Handles element interactions for PlaywrightDriver.

    This handler class encapsulates all element-related operations for the PlaywrightDriver.
    It provides methods for finding, interacting with, and waiting for elements.

    The handler approach offers several benefits:
    1. Separation of concerns - element logic is isolated from other browser operations
    2. Improved maintainability - changes to element handling only affect this class
    3. Consistent error handling - all element operations follow the same error handling pattern
    4. Reusability - common element operations are implemented once and reused
    """

    def __init__(self, driver: 'PlaywrightDriver'):
        """
        Initialize the element handler.

        Args:
            driver: The PlaywrightDriver instance. This reference allows the handler
                   to access the current page or frame context for element operations.
        """
        self._driver = driver

    def find_element(self, selector: str) -> Any:
        """Find an element using a CSS selector.

        This method finds an element using Playwright's locator API. Unlike Selenium,
        Playwright doesn't have a direct equivalent to WebElement. Instead, it uses
        Locator objects that represent an element or a set of elements.

        We use the .first method to get the first matching element, and then check
        if it exists using count(). This approach ensures we fail fast if the element
        doesn't exist, similar to how Selenium's find_element behaves.

        Args:
            selector: CSS selector to find the element

        Returns:
            A Playwright Locator object representing the found element

        Raises:
            WebDriverError: If the element is not found or another error occurs
        """
        logger.debug(f"Finding element with selector: {selector}")
        try:
            context = self._driver._get_context()
            # Playwright's query_selector returns None if not found,
            # but IWebDriver expects an error. Use locator().first to mimic this.
            element = context.locator(selector).first
            # We need to trigger an action or check to see if it actually exists
            # or raise if it doesn't. count() is one way.
            if element.count() == 0:
                raise PlaywrightError(f"Element not found for selector: {selector}")
            # Return the Locator object itself, actions are performed on it
            return element
        except PlaywrightTimeoutError:  # May occur if default timeout is hit implicitly
            raise WebDriverError(f"Timeout finding element with selector: {selector}")
        except PlaywrightError as e:
            # Catch specific "not found" or other Playwright errors
            raise WebDriverError(f"Playwright failed to find element {selector}: {e}") from e

    def click_element(self, selector: str) -> None:
        """Click an element identified by the selector."""
        logger.debug(f"Clicking element with selector: {selector}")
        try:
            context = self._driver._get_context()
            context.click(selector)  # Playwright's click waits for element and actionability
        except PlaywrightTimeoutError:
            raise WebDriverError(f"Timeout clicking element with selector: {selector}")
        except PlaywrightError as e:
            raise WebDriverError(f"Playwright failed to click {selector}: {e}") from e

    def type_text(self, selector: str, text: str) -> None:
        """Type text into an element identified by the selector."""
        # Log length, not the text itself, for sensitive data
        logger.debug(f"Typing text of length {len(text)} into selector: {selector}")
        try:
            context = self._driver._get_context()
            context.fill(selector, text)  # fill clears and types, use type() for appending
        except PlaywrightTimeoutError:
            raise WebDriverError(f"Timeout typing into element with selector: {selector}")
        except PlaywrightError as e:
            raise WebDriverError(f"Playwright failed to type into {selector}: {e}") from e

    def is_element_present(self, selector: str) -> bool:
        """Check if an element is present on the page without raising an error."""
        logger.debug(f"Checking if element is present with selector: {selector}")
        if not isinstance(selector, str) or not selector:
            logger.warning("is_element_present called with empty selector.")
            return False

        try:
            context = self._driver._get_context()
            # Use count() to check if element exists without waiting
            original_timeout = context.get_default_timeout()
            context.set_default_timeout(0)  # Set timeout to 0 to avoid waiting
            try:
                count = context.locator(selector).count()
                return count > 0
            finally:
                # Restore original timeout
                context.set_default_timeout(original_timeout)
        except Exception as e:
            logger.error(f"Error checking element presence for {selector}: {e}")
            return False

    def wait_for_element(self, selector: str, timeout: int = 10) -> Any:
        """Wait explicitly for an element to be present on the page."""
        logger.debug(f"Waiting for element with selector: {selector}, timeout: {timeout}s")
        if not isinstance(selector, str) or not selector:
            raise ValidationError("Selector must be non-empty string.", field_name="selector")

        if not isinstance(timeout, (int, float)) or timeout <= 0:
            timeout = self._driver._DEFAULT_WAIT_TIMEOUT

        try:
            context = self._driver._get_context()
            # Convert timeout to milliseconds for Playwright
            timeout_ms = timeout * 1000
            # Wait for the element to be present
            locator = context.locator(selector)
            locator.wait_for(timeout=timeout_ms)
            return locator
        except PlaywrightTimeoutError:
            raise WebDriverError(f"Timeout waiting for element with selector: {selector}")
        except PlaywrightError as e:
            raise WebDriverError(f"Playwright failed to wait for element {selector}: {e}") from e

    def wait_for_element_visible(self, selector: str, timeout: int = 10) -> Any:
        """Wait for an element to be visible on the page."""
        logger.debug(f"Waiting for element to be visible with selector: {selector}, timeout: {timeout}s")
        if not isinstance(selector, str) or not selector:
            raise ValidationError("Selector must be non-empty string.", field_name="selector")

        if not isinstance(timeout, (int, float)) or timeout <= 0:
            timeout = self._driver._DEFAULT_WAIT_TIMEOUT

        try:
            context = self._driver._get_context()
            # Convert timeout to milliseconds for Playwright
            timeout_ms = timeout * 1000
            # Wait for the element to be visible
            locator = context.locator(selector)
            locator.wait_for(state="visible", timeout=timeout_ms)
            return locator
        except PlaywrightTimeoutError:
            raise WebDriverError(f"Timeout waiting for element to be visible with selector: {selector}")
        except PlaywrightError as e:
            raise WebDriverError(f"Playwright failed to wait for visible element {selector}: {e}") from e

    def get_element_text(self, selector: str) -> str:
        """Get the text content of an element."""
        logger.debug(f"Getting text from element with selector: {selector}")
        try:
            context = self._driver._get_context()
            return context.locator(selector).text_content() or ""
        except PlaywrightError as e:
            raise WebDriverError(f"Playwright failed to get text from element {selector}: {e}") from e

    def get_element_attribute(self, selector: str, attribute: str) -> Optional[str]:
        """Get the value of an attribute on an element."""
        logger.debug(f"Getting attribute '{attribute}' from element with selector: {selector}")
        if not isinstance(attribute, str) or not attribute:
            raise ValidationError("Attribute name must be non-empty string.", field_name="attribute")

        try:
            context = self._driver._get_context()
            return context.locator(selector).get_attribute(attribute)
        except PlaywrightError as e:
            raise WebDriverError(f"Playwright failed to get attribute '{attribute}' from element {selector}: {e}") from e

    def is_element_visible(self, selector: str) -> bool:
        """Check if an element is visible on the page."""
        logger.debug(f"Checking if element is visible with selector: {selector}")
        try:
            context = self._driver._get_context()
            # Use count() to check if element exists without waiting
            original_timeout = context.get_default_timeout()
            context.set_default_timeout(0)  # Set timeout to 0 to avoid waiting
            try:
                return context.locator(selector).is_visible()
            finally:
                # Restore original timeout
                context.set_default_timeout(original_timeout)
        except Exception as e:
            logger.error(f"Error checking element visibility for {selector}: {e}")
            return False

    def execute_script(self, script: str, *args: Any) -> Any:
        """Execute JavaScript in the current window/frame."""
        logger.debug(f"Executing script: {script[:50]}{'...' if len(script) > 50 else ''}")
        if not isinstance(script, str):
            raise ValidationError("Script must be a string.", field_name="script")

        try:
            context = self._driver._get_context()
            return context.evaluate(script, *args)
        except PlaywrightError as e:
            raise WebDriverError(f"Playwright failed to execute script: {e}") from e
