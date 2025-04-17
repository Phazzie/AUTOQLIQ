"""Main PlaywrightDriver class implementing IWebDriver interface.

This module provides a Playwright-based implementation of the IWebDriver interface,
offering an alternative to Selenium with better performance and reliability for
modern web applications. The implementation follows a modular design with specialized
handler classes for different aspects of browser automation.
"""

import logging
from typing import Any, Dict, Optional, Union, List

# Core imports
from src.core.interfaces import IWebDriver
from src.core.exceptions import WebDriverError, ValidationError

# Infrastructure imports
from src.infrastructure.webdrivers.base import BrowserType

# Handler imports
from src.infrastructure.webdrivers.playwright.element_handler import PlaywrightElementHandler
from src.infrastructure.webdrivers.playwright.network_handler import PlaywrightNetworkHandler
from src.infrastructure.webdrivers.playwright.cookie_handler import PlaywrightCookieHandler
from src.infrastructure.webdrivers.playwright.dialog_handler import PlaywrightDialogHandler
from src.infrastructure.webdrivers.playwright.screenshot_handler import PlaywrightScreenshotHandler

# Import Playwright specifics - requires Playwright to be installed
# We use a try/except block to handle the case where Playwright is not installed
# This allows the module to be imported without errors, but will raise appropriate
# exceptions if someone tries to actually use the PlaywrightDriver without installing Playwright
try:
    from playwright.sync_api import sync_playwright, Browser, Page, Frame, Error as PlaywrightError, TimeoutError as PlaywrightTimeoutError
except ImportError:
    # Allow module to load but fail at runtime if Playwright is used without installation
    # This approach enables better error messages and allows the application to start
    # even if Playwright is not installed, as long as it's not actually used
    sync_playwright = None
    Browser = None
    Page = None
    Frame = None
    PlaywrightError = Exception  # Base exception fallback
    PlaywrightTimeoutError = Exception  # Base exception fallback
    logging.getLogger(__name__).warning("Playwright library not found. PlaywrightDriver will not function.")


logger = logging.getLogger(__name__)


class PlaywrightDriver(IWebDriver):
    """
    Implementation of IWebDriver using Playwright (Synchronous API).

    This class provides a complete implementation of the IWebDriver interface using
    Playwright's synchronous API. It follows a modular design with specialized handler
    classes for different aspects of browser automation (elements, dialogs, screenshots, etc.).
    This approach improves maintainability and separation of concerns.

    The implementation leverages Playwright's built-in auto-waiting and reliability features
    to provide a more robust alternative to Selenium, particularly for modern web applications
    with complex dynamic content.

    Attributes:
        browser_type (BrowserType): The type of browser being controlled.
        launch_options (Optional[Dict[str, Any]]): Options used for launching the browser.
        implicit_wait_seconds (int): Default timeout for actions (in milliseconds for Playwright).
        playwright_context: The Playwright context manager instance.
        browser (Optional[Browser]): The Playwright Browser instance.
        page (Optional[Page]): The current Playwright Page instance.
        _current_frame (Optional[Frame]): The current frame if switched from main page.
    """

    _DEFAULT_WAIT_TIMEOUT = 10  # Default explicit wait timeout in seconds

    def __init__(self,
                 browser_type: BrowserType = BrowserType.CHROME,
                 launch_options: Optional[Dict[str, Any]] = None,
                 implicit_wait_seconds: int = 0):
        """
        Initialize PlaywrightDriver and launch the browser.

        Args:
            browser_type: The browser to launch (CHROME, FIREFOX, etc.).
            launch_options: Dictionary of options for `browser_type.launch()`.
            implicit_wait_seconds: Default timeout for operations.

        Raises:
            WebDriverError: If Playwright is not installed or browser launch fails.
            ValueError: If the browser type is unsupported by Playwright.
        """
        if sync_playwright is None:
            raise WebDriverError("Playwright library is not installed. Please run `pip install playwright` and `playwright install`.")

        self.browser_type = browser_type
        self.launch_options = launch_options or {}
        # Playwright uses milliseconds for timeouts
        self.default_timeout_ms = implicit_wait_seconds * 1000
        self._playwright = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self._current_frame: Optional[Frame] = None
        logger.info(f"Initializing Playwright driver for {browser_type.value}")

        try:
            self._playwright = sync_playwright().start()
            browser_launcher = self._get_browser_launcher()
            self.browser = browser_launcher.launch(**self.launch_options)
            self.page = self.browser.new_page()
            if self.default_timeout_ms > 0:
                self.page.set_default_timeout(self.default_timeout_ms)
            logger.info(f"Playwright {browser_type.value} browser launched successfully.")

            # Initialize handlers
            self._element_handler = PlaywrightElementHandler(self)
            self._network_handler = PlaywrightNetworkHandler(self)
            self._cookie_handler = PlaywrightCookieHandler(self)
            self._dialog_handler = PlaywrightDialogHandler(self)
            self._screenshot_handler = PlaywrightScreenshotHandler(self)

        except PlaywrightError as e:
            err_msg = f"Failed to launch Playwright {browser_type.value}: {e}"
            logger.error(err_msg, exc_info=True)
            self.quit()  # Attempt cleanup
            raise WebDriverError(err_msg) from e
        except Exception as e:
            err_msg = f"An unexpected error occurred during Playwright initialization: {e}"
            logger.error(err_msg, exc_info=True)
            self.quit()  # Attempt cleanup
            raise WebDriverError(err_msg) from e

    def _get_browser_launcher(self) -> Any:
        """Get the appropriate Playwright browser launcher based on BrowserType.

        This method maps AutoQliq's BrowserType enum to Playwright's browser launchers.
        Playwright uses different naming conventions than Selenium:
        - Chromium instead of Chrome (covers Chrome, Edge, and other Chromium-based browsers)
        - WebKit instead of Safari

        Returns:
            The appropriate Playwright browser launcher object

        Raises:
            ValueError: If the browser type is not supported by Playwright
        """
        if self.browser_type == BrowserType.CHROME:
            return self._playwright.chromium
        elif self.browser_type == BrowserType.FIREFOX:
            return self._playwright.firefox
        elif self.browser_type == BrowserType.SAFARI:  # Playwright uses 'webkit' for Safari
            return self._playwright.webkit
        # Note: Playwright doesn't map directly to 'EDGE' like Selenium.
        # Chromium is typically used for Edge since modern Edge is Chromium-based
        elif self.browser_type == BrowserType.EDGE:
            logger.warning("Mapping Edge to Playwright's Chromium since modern Edge is Chromium-based.")
            return self._playwright.chromium
        else:
            raise ValueError(f"Unsupported browser type for Playwright: {self.browser_type}")

    def _ensure_page(self) -> Page:
        """Ensure the page object is available.

        This helper method checks if the page object exists before operations,
        providing a clear error message if the page has been closed or not initialized.

        Returns:
            The Playwright Page object

        Raises:
            WebDriverError: If the page is None (not initialized or closed)
        """
        if self.page is None:
            raise WebDriverError("Playwright page is not initialized or has been closed.")
        return self.page

    def _get_context(self) -> Union[Page, Frame]:
        """Get the current context (page or frame) for operations.

        This method returns either the current frame (if we've switched to one)
        or the main page. This allows operations to work correctly regardless of
        whether we're in the main page or a frame.

        Returns:
            Either the current frame or the main page, depending on context
        """
        page = self._ensure_page()
        return self._current_frame if self._current_frame is not None else page

    # --- Core IWebDriver Method Implementations ---

    def get(self, url: str) -> None:
        """Navigate to the specified URL."""
        logger.debug(f"Navigating to URL: {url}")
        try:
            page = self._ensure_page()
            page.goto(url)
        except PlaywrightError as e:
            raise WebDriverError(f"Playwright failed to navigate to {url}: {e}") from e

    def quit(self) -> None:
        """Close the browser and stop the Playwright instance.

        This method performs a graceful shutdown of all Playwright resources.
        It attempts to close the browser and stop the Playwright instance,
        handling any errors that might occur during the process.

        Unlike Selenium, which might leave orphaned browser processes,
        Playwright's cleanup is more thorough, but we still handle potential
        errors to ensure resources are released properly.
        """
        logger.info("Quitting Playwright driver.")
        if self.browser:
            try:
                self.browser.close()
                logger.debug("Playwright browser closed.")
            except PlaywrightError as e:
                # Log but don't raise - we want to continue cleanup
                logger.error(f"Error closing Playwright browser: {e}")
        if self._playwright:
            try:
                self._playwright.stop()
                logger.debug("Playwright context stopped.")
            except Exception as e:  # Can raise errors if already stopped
                # Log but don't raise - we want to complete cleanup
                logger.error(f"Error stopping Playwright context: {e}")
        # Clear references to allow garbage collection
        self.page = None
        self.browser = None
        self._playwright = None

    def get_current_url(self) -> str:
        """Get the current URL."""
        try:
            page = self._ensure_page()
            return page.url
        except PlaywrightError as e:
            raise WebDriverError(f"Playwright failed to get current URL: {e}") from e

    # --- Element Interaction Methods (delegated to ElementHandler) ---

    def find_element(self, selector: str) -> Any:
        """Find an element using a CSS selector."""
        return self._element_handler.find_element(selector)

    def click_element(self, selector: str) -> None:
        """Click an element identified by the selector."""
        self._element_handler.click_element(selector)

    def type_text(self, selector: str, text: str) -> None:
        """Type text into an element identified by the selector."""
        self._element_handler.type_text(selector, text)

    def is_element_present(self, selector: str) -> bool:
        """Check if an element is present on the page without raising an error."""
        return self._element_handler.is_element_present(selector)

    def wait_for_element(self, selector: str, timeout: int = 10) -> Any:
        """Wait explicitly for an element to be present on the page."""
        return self._element_handler.wait_for_element(selector, timeout)

    def wait_for_element_visible(self, selector: str, timeout: int = 10) -> Any:
        """Wait for an element to be visible on the page."""
        return self._element_handler.wait_for_element_visible(selector, timeout)

    def get_element_text(self, selector: str) -> str:
        """Get the text content of an element."""
        return self._element_handler.get_element_text(selector)

    def get_element_attribute(self, selector: str, attribute: str) -> Optional[str]:
        """Get the value of an attribute on an element."""
        return self._element_handler.get_element_attribute(selector, attribute)

    def is_element_visible(self, selector: str) -> bool:
        """Check if an element is visible on the page."""
        return self._element_handler.is_element_visible(selector)

    def execute_script(self, script: str, *args: Any) -> Any:
        """Execute JavaScript in the current window/frame."""
        return self._element_handler.execute_script(script, *args)

    # --- Frame Handling Methods ---

    def switch_to_frame(self, frame_reference: Union[str, int, Any]) -> None:
        """Switch focus to a frame or iframe."""
        logger.debug(f"Switching to frame: {frame_reference}")
        try:
            page = self._ensure_page()

            if isinstance(frame_reference, int):
                # Switch by frame index
                frames = page.frames
                if frame_reference < 0 or frame_reference >= len(frames):
                    raise WebDriverError(f"Frame index out of range: {frame_reference}")
                self._current_frame = frames[frame_reference]
            elif isinstance(frame_reference, str):
                # Switch by frame name or id
                frame = page.frame(name=frame_reference)
                if frame is None:
                    # Try to find by selector if name doesn't work
                    element = page.locator(f"iframe[name='{frame_reference}'],iframe[id='{frame_reference}']").first
                    if element.count() == 0:
                        raise WebDriverError(f"Frame not found with name/id: {frame_reference}")
                    frame = element.content_frame()
                    if frame is None:
                        raise WebDriverError(f"Could not access frame content: {frame_reference}")
                self._current_frame = frame
            else:
                # Assume it's a locator or element
                if hasattr(frame_reference, "content_frame"):
                    frame = frame_reference.content_frame()
                    if frame is None:
                        raise WebDriverError("Could not access frame content from element")
                    self._current_frame = frame
                else:
                    raise WebDriverError(f"Unsupported frame reference type: {type(frame_reference)}")
        except PlaywrightError as e:
            raise WebDriverError(f"Playwright failed to switch to frame {frame_reference}: {e}") from e

    def switch_to_default_content(self) -> None:
        """Switch focus back to the main frame."""
        logger.debug("Switching to default content")
        try:
            self._current_frame = None  # Reset current frame to use page directly
        except PlaywrightError as e:
            raise WebDriverError(f"Playwright failed to switch to default content: {e}") from e

    # --- Dialog Handling Methods (delegated to DialogHandler) ---

    def accept_alert(self) -> None:
        """Accept the currently displayed alert dialog."""
        self._dialog_handler.accept_alert()

    def dismiss_alert(self) -> None:
        """Dismiss the currently displayed alert dialog."""
        self._dialog_handler.dismiss_alert()

    def get_alert_text(self) -> str:
        """Get the text of the currently displayed alert dialog."""
        return self._dialog_handler.get_alert_text()

    # --- Screenshot Methods (delegated to ScreenshotHandler) ---

    def take_screenshot(self, file_path: str) -> None:
        """Take a screenshot and save it."""
        self._screenshot_handler.take_screenshot(file_path)

    def take_element_screenshot(self, selector: str, file_path: str) -> None:
        """Take a screenshot of a specific element and save it."""
        self._screenshot_handler.take_element_screenshot(selector, file_path)

    def take_full_page_screenshot(self, file_path: str) -> None:
        """Take a screenshot of the full page and save it."""
        self._screenshot_handler.take_full_page_screenshot(file_path)

    # --- Cookie Handling Methods (delegated to CookieHandler) ---

    def get_cookies(self) -> List[Dict[str, Any]]:
        """Get all cookies from the browser."""
        return self._cookie_handler.get_cookies()

    def add_cookie(self, cookie: Dict[str, Any]) -> None:
        """Add a cookie to the browser."""
        self._cookie_handler.add_cookie(cookie)

    def delete_all_cookies(self) -> None:
        """Delete all cookies."""
        self._cookie_handler.delete_all_cookies()

    # --- Network Interception Methods (delegated to NetworkHandler) ---

    def add_route_handler(self, url_pattern: str, handler: Any) -> None:
        """Add a route handler to intercept network requests."""
        self._network_handler.add_route_handler(url_pattern, handler)

    def remove_route_handler(self, url_pattern: str, handler: Optional[Any] = None) -> None:
        """Remove a previously added route handler."""
        self._network_handler.remove_route_handler(url_pattern, handler)

    def wait_for_request(self, url_pattern: str, timeout: int = 10) -> Any:
        """Wait for a request matching the given URL pattern."""
        return self._network_handler.wait_for_request(url_pattern, timeout)

    def wait_for_response(self, url_pattern: str, timeout: int = 10) -> Any:
        """Wait for a response matching the given URL pattern."""
        return self._network_handler.wait_for_response(url_pattern, timeout)
