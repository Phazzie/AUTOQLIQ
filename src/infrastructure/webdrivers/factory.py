"""Factory module for creating WebDriver instances."""

import logging
from typing import Any, Optional

# Core imports
from src.core.interfaces import IWebDriver
from src.core.exceptions import WebDriverError, ConfigError

# WebDriver implementations
from src.infrastructure.webdrivers.base import BrowserType
from src.infrastructure.webdrivers.selenium_driver import SeleniumWebDriver
# Removed Playwright import per YAGNI

# Import Selenium options classes if used directly here (or handled within SeleniumWebDriver)
# from selenium.webdriver import ChromeOptions, FirefoxOptions, EdgeOptions, SafariOptions

logger = logging.getLogger(__name__)


class WebDriverFactory:
    """
    Factory class for creating instances of IWebDriver implementations.

    Handles the creation of different WebDriver types (e.g., Selenium, Playwright)
    based on the specified browser type and options.
    """

    @staticmethod
    def create_driver(
        browser_type: BrowserType = BrowserType.CHROME, # Default to Chrome
        implicit_wait_seconds: int = 0,
        selenium_options: Optional[Any] = None, # e.g., ChromeOptions instance
        webdriver_path: Optional[str] = None # Optional path to the webdriver executable
    ) -> IWebDriver:
        """
        Creates a Selenium WebDriver implementation instance.

        Args:
            browser_type (BrowserType): The target browser (e.g., CHROME, FIREFOX). Defaults to CHROME.
            implicit_wait_seconds (int): Implicit wait time in seconds. Defaults to 0.
            selenium_options (Optional[Any]): Specific options object for Selenium (e.g., ChromeOptions).
            webdriver_path (Optional[str]): Explicit path to the WebDriver executable (e.g., chromedriver).
                                            If None, Selenium Manager or system PATH is used.

        Returns:
            IWebDriver: An instance conforming to the IWebDriver interface.

        Raises:
            ConfigError: If the browser_type is unsupported.
            WebDriverError: If the underlying driver fails to initialize.
        """
        logger.info(f"Creating Selenium driver for {browser_type.value} with implicit wait {implicit_wait_seconds}s")

        try:
            # SeleniumWebDriver handles driver creation internally
            return SeleniumWebDriver(
                browser_type=browser_type,
                implicit_wait_seconds=implicit_wait_seconds,
                selenium_options=selenium_options,
                webdriver_path=webdriver_path
            )
        except Exception as e:
             # Catch potential errors during instantiation
             error_msg = f"Failed to create Selenium driver for {browser_type.value}: {e}"
             logger.error(error_msg, exc_info=True)
             # Wrap unexpected errors in WebDriverError
             if not isinstance(e, (ConfigError, WebDriverError)):
                  raise WebDriverError(error_msg, driver_type="selenium", cause=e) from e
             raise # Re-raise ConfigError or WebDriverError