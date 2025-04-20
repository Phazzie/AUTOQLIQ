"""Factory module for creating WebDriver instances."""

import logging
from typing import Any, Dict, Optional

# Assuming IWebDriver is defined in core interfaces
from src.core.interfaces import IWebDriver
from src.core.exceptions import WebDriverError, ConfigError
from src.infrastructure.webdrivers.base import BrowserType
from src.infrastructure.webdrivers.selenium_driver import SeleniumWebDriver
# from src.infrastructure.webdrivers.playwright_driver import PlaywrightDriver # Keep commented if not implemented

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
        driver_type: str = "selenium", # Or 'playwright'
        implicit_wait_seconds: int = 0,
        selenium_options: Optional[Any] = None, # e.g., ChromeOptions instance
        playwright_options: Optional[Dict[str, Any]] = None, # Options for Playwright launch
        webdriver_path: Optional[str] = None, # Optional path to the webdriver executable
        headless: bool = False # Whether to run in headless mode
    ) -> IWebDriver:
        """
        Creates an IWebDriver implementation instance.

        Args:
            browser_type (BrowserType): The target browser (e.g., CHROME, FIREFOX). Defaults to CHROME.
            driver_type (str): The underlying driver library ('selenium' or 'playwright'). Defaults to 'selenium'.
            implicit_wait_seconds (int): Implicit wait time in seconds. Defaults to 0.
            selenium_options (Optional[Any]): Specific options object for Selenium (e.g., ChromeOptions).
            playwright_options (Optional[Dict[str, Any]]): Dictionary of options for Playwright launch.
            webdriver_path (Optional[str]): Explicit path to the WebDriver executable (e.g., chromedriver).
                                            If None, Selenium Manager or system PATH is used.
            headless (bool): Whether to run the browser in headless mode (no GUI). Defaults to False.

        Returns:
            IWebDriver: An instance conforming to the IWebDriver interface.

        Raises:
            ConfigError: If the driver_type or browser_type is unsupported.
            WebDriverError: If the underlying driver fails to initialize.
        """
        headless_str = "headless mode" if headless else "normal mode"
        logger.info(f"Requesting {driver_type} driver for {browser_type.value} with implicit wait {implicit_wait_seconds}s in {headless_str}")

        try:
            if driver_type.lower() == "selenium":
                # SeleniumWebDriver now handles driver creation internally
                return SeleniumWebDriver(
                    browser_type=browser_type,
                    implicit_wait_seconds=implicit_wait_seconds,
                    selenium_options=selenium_options,
                    webdriver_path=webdriver_path,
                    headless=headless
                )
            elif driver_type.lower() == "playwright":
                # Ensure Playwright is installed before attempting to use
                try:
                    from src.infrastructure.webdrivers.playwright_driver import PlaywrightDriver
                    # PlaywrightDriver handles its own browser launching internally
                    # Ensure headless is included in launch options if specified
                    if playwright_options is None:
                        playwright_options = {}
                    if headless and 'headless' not in playwright_options:
                        playwright_options['headless'] = True

                    return PlaywrightDriver(
                        browser_type=browser_type,
                        launch_options=playwright_options,
                        implicit_wait_seconds=implicit_wait_seconds
                    )
                except ImportError:
                    logger.error("Playwright library not found. Please install it (`pip install playwright` and `playwright install`) to use the Playwright driver.")
                    raise ConfigError("Playwright library not found.")
                except Exception as e:
                    err_msg = f"Failed to create Playwright {browser_type.value} WebDriver: {e}"
                    logger.error(err_msg, exc_info=True)
                    raise WebDriverError(err_msg, driver_type="playwright") from e
            else:
                raise ConfigError(f"Unsupported driver type: {driver_type}. Choose 'selenium' or 'playwright'.")
        except Exception as e:
             # Catch potential errors during instantiation
             error_msg = f"Failed to create {driver_type} driver for {browser_type.value}: {e}"
             logger.error(error_msg, exc_info=True)
             # Wrap unexpected errors in WebDriverError
             if not isinstance(e, (ConfigError, WebDriverError)):
                  raise WebDriverError(error_msg, driver_type=driver_type, cause=e) from e
             raise # Re-raise ConfigError or WebDriverError