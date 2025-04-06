"""Selenium WebDriver implementation for AutoQliq."""
import logging
import os
from typing import Any, Optional, Union

# Selenium imports
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException
# Import Selenium options classes
from selenium.webdriver import ChromeOptions, FirefoxOptions, EdgeOptions, SafariOptions

# Core imports
from src.core.interfaces import IWebDriver
from src.core.exceptions import WebDriverError, ConfigError
# Infrastructure imports
from src.infrastructure.common.logging_utils import log_method_call
from src.infrastructure.webdrivers.error_handler import handle_driver_exceptions, map_webdriver_exception
from src.infrastructure.webdrivers.base import BrowserType

logger = logging.getLogger(__name__)


class SeleniumWebDriver(IWebDriver):
    """
    Implementation of IWebDriver using Selenium WebDriver.

    Wraps a Selenium WebDriver instance (like Chrome, Firefox) to provide
    browser automation capabilities conforming to the IWebDriver interface.
    Handles driver initialization.

    Attributes:
        driver (RemoteWebDriver): The underlying Selenium WebDriver instance.
        implicit_wait_seconds (int): The implicit wait time set on the driver.
        browser_type (BrowserType): The type of browser being used.
    """
    _DEFAULT_WAIT_TIMEOUT = 10 # Default explicit wait timeout in seconds

    def __init__(self,
                 browser_type: BrowserType = BrowserType.CHROME,
                 implicit_wait_seconds: int = 0,
                 selenium_options: Optional[Any] = None, # e.g. ChromeOptions()
                 webdriver_path: Optional[str] = None):
        """
        Initialize SeleniumWebDriver and the underlying Selenium driver.

        Args:
            browser_type (BrowserType): The target browser type. Defaults to CHROME.
            implicit_wait_seconds (int): Seconds to implicitly wait for elements. Defaults to 0.
            selenium_options (Optional[Any]): Pre-configured Selenium Options object (e.g., ChromeOptions).
                                              If None, default options are used.
            webdriver_path (Optional[str]): Explicit path to the WebDriver executable.
                                            If None, Selenium Manager or system PATH will be used.

        Raises:
            ConfigError: If the browser type is unsupported.
            WebDriverError: If the Selenium driver fails to initialize.
        """
        self.browser_type = browser_type
        self.implicit_wait_seconds = implicit_wait_seconds
        self.driver: Optional[RemoteWebDriver] = None # Initialize driver attribute
        logger.info(f"Initializing SeleniumWebDriver for: {self.browser_type.value}")

        try:
            options_instance = self._resolve_options(selenium_options)
            service_instance = self._create_service(webdriver_path)

            logger.info(f"Attempting to create Selenium WebDriver instance...")
            if browser_type == BrowserType.CHROME:
                self.driver = webdriver.Chrome(service=service_instance, options=options_instance)
            elif browser_type == BrowserType.FIREFOX:
                 self.driver = webdriver.Firefox(service=service_instance, options=options_instance)
            elif browser_type == BrowserType.EDGE:
                 self.driver = webdriver.Edge(service=service_instance, options=options_instance)
            elif browser_type == BrowserType.SAFARI:
                  # Safari often doesn't use a service object in the same way
                  if service_instance:
                       logger.warning("webdriver_path is typically ignored for Safari.")
                  self.driver = webdriver.Safari(options=options_instance) # Options might be limited
            else:
                # Should not happen if BrowserType enum is used correctly
                raise ConfigError(f"Unsupported browser type for SeleniumWebDriver: {browser_type}")

            logger.info(f"Successfully created Selenium {browser_type.value} WebDriver instance.")

            if self.implicit_wait_seconds > 0:
                self.driver.implicitly_wait(self.implicit_wait_seconds)
                logger.debug(f"Set implicit wait to {self.implicit_wait_seconds} seconds")

        except WebDriverException as e:
             # Catch Selenium's base exception for driver issues
             err_msg = f"Failed to initialize Selenium {browser_type.value} WebDriver: {e.msg}"
             logger.error(err_msg, exc_info=True)
             raise WebDriverError(err_msg, driver_type=self.browser_type.value, cause=e) from e
        except Exception as e:
             # Catch other potential errors (e.g., invalid path)
             err_msg = f"Unexpected error initializing SeleniumWebDriver: {e}"
             logger.error(err_msg, exc_info=True)
             raise WebDriverError(err_msg, driver_type=self.browser_type.value, cause=e) from e

    def _resolve_options(self, options_param: Optional[Any]) -> Optional[Any]:
        """Returns the appropriate options object or None."""
        if options_param:
             # Validate that the provided options match the browser type roughly
             expected_option_type = {
                  BrowserType.CHROME: ChromeOptions,
                  BrowserType.FIREFOX: FirefoxOptions,
                  BrowserType.EDGE: EdgeOptions,
                  BrowserType.SAFARI: SafariOptions
             }.get(self.browser_type)

             if expected_option_type and not isinstance(options_param, expected_option_type):
                  logger.warning(f"Provided selenium_options type ({type(options_param).__name__}) might not match browser type ({self.browser_type.value}). Attempting to use anyway.")
             return options_param
        else:
             # Return default options if none provided, or None if not applicable (e.g. Safari sometimes)
             logger.debug(f"No specific Selenium options provided for {self.browser_type.value}. Using defaults.")
             if self.browser_type == BrowserType.CHROME: return ChromeOptions()
             if self.browser_type == BrowserType.FIREFOX: return FirefoxOptions()
             if self.browser_type == BrowserType.EDGE: return EdgeOptions()
             # Safari might not need/use options object in basic cases
             if self.browser_type == BrowserType.SAFARI: return None # Or SafariOptions() if needed
             return None # Default for others


    def _create_service(self, webdriver_path: Optional[str]) -> Optional[Any]:
         """Creates a Selenium Service object if a path is provided."""
         from selenium.webdriver.chrome.service import Service as ChromeService
         from selenium.webdriver.firefox.service import Service as FirefoxService
         from selenium.webdriver.edge.service import Service as EdgeService
         # Safari does not use a service object

         service_map = {
              BrowserType.CHROME: ChromeService,
              BrowserType.FIREFOX: FirefoxService,
              BrowserType.EDGE: EdgeService
         }

         service_class = service_map.get(self.browser_type)

         if service_class and webdriver_path:
              if not os.path.exists(webdriver_path):
                   raise ConfigError(f"WebDriver executable not found at specified path: {webdriver_path}")
              logger.info(f"Using explicit webdriver path: {webdriver_path}")
              return service_class(executable_path=webdriver_path)
         elif webdriver_path:
              logger.warning(f"webdriver_path '{webdriver_path}' provided but not applicable for {self.browser_type.value}. Ignoring.")
              return None
         else:
              logger.debug(f"No explicit webdriver path provided. Using Selenium Manager or system PATH for {self.browser_type.value}.")
              return None # Let Selenium handle driver management


    def _ensure_driver(self) -> RemoteWebDriver:
        """Checks if the driver is initialized."""
        if self.driver is None:
            raise WebDriverError("WebDriver is not initialized or has been quit.")
        return self.driver

    # Apply decorators for consistent logging and error handling
    @log_method_call(logger)
    @handle_driver_exceptions("Failed to navigate to URL: {url}")
    def get(self, url: str) -> None:
        """Navigate to the specified URL."""
        if not isinstance(url, str) or not url:
            raise ValidationError("URL must be a non-empty string.", field_name="url")
        driver = self._ensure_driver()
        driver.get(url)

    @log_method_call(logger, log_result=False) # Don't log result of quit
    def quit(self) -> None:
        """Quit the WebDriver and close all associated windows."""
        driver = self.driver # Get ref before setting to None
        if driver:
            try:
                driver.quit()
                logger.info(f"Selenium WebDriver ({self.browser_type.value}) quit successfully.")
            except Exception as e:
                # Log error but don't raise, as quit is often called during cleanup
                logger.error(f"Error occurred while quitting Selenium WebDriver: {e}", exc_info=False)
            finally:
                 self.driver = None # Mark driver as None after attempting quit

    @log_method_call(logger)
    @handle_driver_exceptions("Failed to find element with selector: {selector}")
    def find_element(self, selector: str) -> WebElement:
        """Find a single element using a CSS selector."""
        if not isinstance(selector, str) or not selector:
            raise ValidationError("Selector must be a non-empty string.", field_name="selector")
        driver = self._ensure_driver()
        # If implicit wait is set, find_element uses it.
        # Otherwise, it fails immediately if not found.
        try:
            return driver.find_element(By.CSS_SELECTOR, selector)
        except NoSuchElementException as e:
             # Explicitly wrap NoSuchElementException
             raise WebDriverError(f"Element not found for selector: {selector}", cause=e) from e

    @log_method_call(logger, log_args=True)
    @handle_driver_exceptions("Failed to click element with selector: {selector}")
    def click_element(self, selector: str) -> None:
        """Find an element by CSS selector and click it."""
        # Consider adding explicit wait for clickability here if needed
        element = self.find_element(selector) # find_element raises WebDriverError if not found
        element.click()

    @log_method_call(logger, log_args=False) # Don't log text argument by default
    @handle_driver_exceptions("Failed to type text into element with selector: {selector}")
    def type_text(self, selector: str, text: str) -> None:
        """Find an element by CSS selector, clear it, and type text into it."""
        if not isinstance(text, str):
             raise ValidationError("Text to type must be a string.", field_name="text")
        element = self.find_element(selector) # find_element raises WebDriverError if not found
        # Explicitly clear before sending keys for more reliable typing
        element.clear()
        element.send_keys(text)
        logger.debug(f"Typed text (length {len(text)}) into element: {selector}")


    @log_method_call(logger)
    @handle_driver_exceptions("Failed to take screenshot to file: {file_path}")
    def take_screenshot(self, file_path: str) -> None:
        """Take a screenshot and save it to the specified file path."""
        if not isinstance(file_path, str) or not file_path:
            raise ValidationError("File path must be a non-empty string.", field_name="file_path")
        driver = self._ensure_driver()
        try:
            # Ensure directory exists
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                 os.makedirs(directory, exist_ok=True)

            if not driver.save_screenshot(file_path):
                 # save_screenshot returns False on failure in some cases
                 raise WebDriverError(f"WebDriver reported failure saving screenshot to {file_path}")
        except (IOError, OSError) as e:
             # Catch file system errors explicitly
             raise WebDriverError(f"File system error saving screenshot to {file_path}: {e}") from e

    # Make sure logging doesn't happen for is_element_present unless needed
    # @log_method_call(logger, level=logging.DEBUG) # Maybe too verbose
    def is_element_present(self, selector: str) -> bool:
        """Check if an element is present on the page using CSS selector."""
        if not isinstance(selector, str) or not selector:
            logger.warning("is_element_present called with invalid selector.")
            return False
        driver = self._ensure_driver()
        # Turn off implicit wait temporarily for this check if it's set
        original_implicit_wait = 0
        if self.implicit_wait_seconds > 0:
            try:
                 # Get current implicit wait (if possible, though Selenium doesn't expose getting it directly)
                 # For simplicity, just set to 0 and restore later. Store original value from init.
                 original_implicit_wait = self.implicit_wait_seconds
                 driver.implicitly_wait(0)
            except Exception:
                 logger.warning("Could not temporarily disable implicit wait for is_element_present.")

        present = False
        try:
            # Use find_elements which returns a list, empty if not found
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            present = len(elements) > 0
            logger.debug(f"Element '{selector}' presence check: {present}")
        except WebDriverException as e:
            # Log unexpected errors during the check but return False
            logger.error(f"WebDriverException checking presence of element '{selector}': {e}", exc_info=False)
            present = False
        finally:
             # Restore original implicit wait
             if original_implicit_wait > 0:
                  try:
                       driver.implicitly_wait(original_implicit_wait)
                  except Exception:
                       logger.warning("Could not restore original implicit wait after is_element_present.")
        return present


    @log_method_call(logger)
    @handle_driver_exceptions("Failed to get current URL")
    def get_current_url(self) -> str:
        """Get the current URL of the browser."""
        driver = self._ensure_driver()
        return driver.current_url

    # --- Optional IWebDriver Methods Implementation ---

    @log_method_call(logger)
    @handle_driver_exceptions("Failed waiting for element with selector: {selector}")
    def wait_for_element(self, selector: str, timeout: int = _DEFAULT_WAIT_TIMEOUT) -> WebElement:
        """Wait explicitly for an element to be present."""
        if not isinstance(selector, str) or not selector:
            raise ValidationError("Selector must be a non-empty string.", field_name="selector")
        if not isinstance(timeout, (int, float)) or timeout <= 0:
             logger.warning(f"Invalid timeout value {timeout}. Using default: {self._DEFAULT_WAIT_TIMEOUT}s")
             timeout = self._DEFAULT_WAIT_TIMEOUT
        driver = self._ensure_driver()
        wait = WebDriverWait(driver, timeout)
        try:
            # Wait for presence_of_element_located, which returns the element
            return wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
        except TimeoutException as e:
            raise WebDriverError(f"Timeout waiting for element: {selector}", cause=e) from e

    @log_method_call(logger)
    @handle_driver_exceptions("Failed to switch to frame: {frame_reference}")
    def switch_to_frame(self, frame_reference: Union[str, int, WebElement]) -> None:
        """Switch focus to a frame or iframe."""
        driver = self._ensure_driver()
        driver.switch_to.frame(frame_reference)

    @log_method_call(logger)
    @handle_driver_exceptions("Failed to switch to default content")
    def switch_to_default_content(self) -> None:
        """Switch focus back to the main document."""
        driver = self._ensure_driver()
        driver.switch_to.default_content()

    @log_method_call(logger)
    @handle_driver_exceptions("Failed to accept alert")
    def accept_alert(self) -> None:
        """Accept (click OK on) an alert, confirm, or prompt dialog."""
        driver = self._ensure_driver()
        driver.switch_to.alert.accept()

    @log_method_call(logger)
    @handle_driver_exceptions("Failed to dismiss alert")
    def dismiss_alert(self) -> None:
        """Dismiss (click Cancel on) an alert or confirm dialog."""
        driver = self._ensure_driver()
        driver.switch_to.alert.dismiss()

    @log_method_call(logger)
    @handle_driver_exceptions("Failed to get alert text")
    def get_alert_text(self) -> str:
        """Get the text content of an alert, confirm, or prompt dialog."""
        driver = self._ensure_driver()
        return driver.switch_to.alert.text

    # Context Manager Protocol
    def __enter__(self):
        """Enter context management."""
        logger.debug("Entering SeleniumWebDriver context")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context management, ensuring driver quits."""
        logger.debug("Exiting SeleniumWebDriver context")
        self.quit()