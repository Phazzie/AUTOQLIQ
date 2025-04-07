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
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException, JavascriptException

# Core imports
from src.core.interfaces import IWebDriver
from src.core.exceptions import WebDriverError, ConfigError, ValidationError

# Infrastructure imports
from src.infrastructure.common.logging_utils import log_method_call
from src.infrastructure.webdrivers.error_handler import handle_driver_exceptions, map_webdriver_exception
from src.infrastructure.webdrivers.base import BrowserType

# Import Selenium options classes
from selenium.webdriver import ChromeOptions, FirefoxOptions, EdgeOptions, SafariOptions

logger = logging.getLogger(__name__)


class SeleniumWebDriver(IWebDriver):
    """
    Implementation of IWebDriver using Selenium WebDriver.
    Handles driver initialization and wraps Selenium methods.
    """
    _DEFAULT_WAIT_TIMEOUT = 10 # Default explicit wait timeout in seconds

    def __init__(self,
                 browser_type: BrowserType = BrowserType.CHROME,
                 implicit_wait_seconds: int = 0,
                 selenium_options: Optional[Any] = None,
                 webdriver_path: Optional[str] = None):
        """Initialize SeleniumWebDriver and the underlying Selenium driver."""
        self.browser_type = browser_type
        self.implicit_wait_seconds = implicit_wait_seconds
        self.driver: Optional[RemoteWebDriver] = None
        logger.info(f"Initializing SeleniumWebDriver for: {self.browser_type.value}")

        try:
            options_instance = self._resolve_options(selenium_options)
            service_instance = self._create_service(webdriver_path)

            logger.info(f"Attempting to create Selenium WebDriver instance...")
            driver_map = { BrowserType.CHROME: webdriver.Chrome, BrowserType.FIREFOX: webdriver.Firefox,
                           BrowserType.EDGE: webdriver.Edge, BrowserType.SAFARI: webdriver.Safari }
            driver_class = driver_map.get(browser_type)
            if driver_class is None: raise ConfigError(f"Unsupported browser: {browser_type}")

            if browser_type == BrowserType.SAFARI:
                 if service_instance: logger.warning("webdriver_path ignored for Safari.")
                 self.driver = driver_class(options=options_instance)
            else:
                 self.driver = driver_class(service=service_instance, options=options_instance)

            logger.info(f"Successfully created Selenium {browser_type.value} WebDriver instance.")
            if self.implicit_wait_seconds > 0:
                self.driver.implicitly_wait(self.implicit_wait_seconds)
                logger.debug(f"Set implicit wait to {self.implicit_wait_seconds} seconds")

        except WebDriverException as e:
             err_msg = f"Failed initialize Selenium {browser_type.value}: {e.msg}"
             logger.error(err_msg, exc_info=True)
             raise WebDriverError(err_msg, driver_type=self.browser_type.value, cause=e) from e
        except Exception as e:
             err_msg = f"Unexpected error initializing SeleniumWebDriver: {e}"
             logger.error(err_msg, exc_info=True)
             raise WebDriverError(err_msg, driver_type=self.browser_type.value, cause=e) from e

    def _resolve_options(self, options_param: Optional[Any]) -> Optional[Any]:
        """Returns the appropriate options object or None."""
        if options_param:
             expected_type = { BrowserType.CHROME: ChromeOptions, BrowserType.FIREFOX: FirefoxOptions,
                               BrowserType.EDGE: EdgeOptions, BrowserType.SAFARI: SafariOptions }.get(self.browser_type)
             if expected_type and not isinstance(options_param, expected_type):
                  logger.warning(f"Provided options type ({type(options_param).__name__}) might not match browser ({self.browser_type.value}).")
             return options_param
        else:
             logger.debug(f"No specific Selenium options provided for {self.browser_type.value}. Using defaults.")
             if self.browser_type == BrowserType.CHROME: return ChromeOptions()
             if self.browser_type == BrowserType.FIREFOX: return FirefoxOptions()
             if self.browser_type == BrowserType.EDGE: return EdgeOptions()
             if self.browser_type == BrowserType.SAFARI: return SafariOptions()
             return None

    def _create_service(self, webdriver_path: Optional[str]) -> Optional[Any]:
         """Creates a Selenium Service object if a path is provided."""
         from selenium.webdriver.chrome.service import Service as ChromeService
         from selenium.webdriver.firefox.service import Service as FirefoxService
         from selenium.webdriver.edge.service import Service as EdgeService
         service_map = { BrowserType.CHROME: ChromeService, BrowserType.FIREFOX: FirefoxService, BrowserType.EDGE: EdgeService }
         service_class = service_map.get(self.browser_type)
         if service_class and webdriver_path:
              if not os.path.exists(webdriver_path): raise ConfigError(f"WebDriver executable not found: {webdriver_path}")
              logger.info(f"Using explicit webdriver path: {webdriver_path}")
              return service_class(executable_path=webdriver_path)
         elif webdriver_path: logger.warning(f"webdriver_path '{webdriver_path}' ignored for {self.browser_type.value}.")
         else: logger.debug(f"Using Selenium Manager or system PATH for {self.browser_type.value}.")
         return None

    def _ensure_driver(self) -> RemoteWebDriver:
        """Checks if the driver is initialized."""
        if self.driver is None: raise WebDriverError("WebDriver not initialized or has been quit.")
        return self.driver

    @log_method_call(logger)
    @handle_driver_exceptions("Failed to navigate to URL: {url}")
    def get(self, url: str) -> None:
        if not isinstance(url, str) or not url: raise ValidationError("URL must be non-empty string.", field_name="url")
        driver = self._ensure_driver(); driver.get(url)

    @log_method_call(logger, log_result=False)
    def quit(self) -> None:
        driver = self.driver
        if driver:
            try: driver.quit(); logger.info(f"Selenium WebDriver ({self.browser_type.value}) quit.")
            except Exception as e: logger.error(f"Error quitting Selenium WebDriver: {e}", exc_info=False)
            finally: self.driver = None

    @log_method_call(logger)
    @handle_driver_exceptions("Failed to find element with selector: {selector}")
    def find_element(self, selector: str) -> WebElement:
        if not isinstance(selector, str) or not selector: raise ValidationError("Selector must be non-empty string.", field_name="selector")
        driver = self._ensure_driver()
        try: return driver.find_element(By.CSS_SELECTOR, selector)
        except NoSuchElementException as e: raise WebDriverError(f"Element not found for selector: {selector}", cause=e) from e

    @log_method_call(logger, log_args=True)
    @handle_driver_exceptions("Failed to click element with selector: {selector}")
    def click_element(self, selector: str) -> None:
        element = self.find_element(selector); element.click()

    @log_method_call(logger, log_args=False)
    @handle_driver_exceptions("Failed to type text into element with selector: {selector}")
    def type_text(self, selector: str, text: str) -> None:
        if not isinstance(text, str): raise ValidationError("Text must be string.", field_name="text")
        element = self.find_element(selector); element.clear(); element.send_keys(text)
        logger.debug(f"Typed text (length {len(text)}) into element: {selector}")

    @log_method_call(logger)
    @handle_driver_exceptions("Failed to take screenshot to file: {file_path}")
    def take_screenshot(self, file_path: str) -> None:
        if not isinstance(file_path, str) or not file_path: raise ValidationError("File path must be non-empty string.", field_name="file_path")
        driver = self._ensure_driver()
        try:
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory): os.makedirs(directory, exist_ok=True)
            if not driver.save_screenshot(file_path): raise WebDriverError(f"WebDriver failed saving screenshot to {file_path}")
        except (IOError, OSError) as e: raise WebDriverError(f"File system error saving screenshot to {file_path}: {e}") from e

    def is_element_present(self, selector: str) -> bool:
        if not isinstance(selector, str) or not selector: logger.warning("is_element_present empty selector."); return False
        driver = self._ensure_driver(); original_wait = self.implicit_wait_seconds; present = False
        try:
             if original_wait > 0: driver.implicitly_wait(0)
             elements = driver.find_elements(By.CSS_SELECTOR, selector); present = len(elements) > 0
        except WebDriverException as e: logger.error(f"Error checking presence of '{selector}': {e}"); present = False
        finally:
             if original_wait > 0:
                  try: driver.implicitly_wait(original_wait)
                  except Exception: logger.warning("Could not restore implicit wait.")
        return present

    @log_method_call(logger)
    @handle_driver_exceptions("Failed to get current URL")
    def get_current_url(self) -> str:
        driver = self._ensure_driver(); return driver.current_url

    @log_method_call(logger)
    @handle_driver_exceptions("Failed to execute script")
    def execute_script(self, script: str, *args: Any) -> Any:
        """Executes JavaScript."""
        if not isinstance(script, str): raise ValidationError("Script must be a string.", field_name="script")
        driver = self._ensure_driver()
        try: return driver.execute_script(script, *args)
        except JavascriptException as e: raise WebDriverError(f"JavaScript execution error: {e.msg}", cause=e) from e

    @log_method_call(logger)
    @handle_driver_exceptions("Failed waiting for element with selector: {selector}")
    def wait_for_element(self, selector: str, timeout: int = _DEFAULT_WAIT_TIMEOUT) -> WebElement:
        """Wait explicitly for an element to be present."""
        if not isinstance(selector, str) or not selector: raise ValidationError("Selector must be non-empty string.", field_name="selector")
        if not isinstance(timeout, (int, float)) or timeout <= 0: timeout = self._DEFAULT_WAIT_TIMEOUT
        driver = self._ensure_driver(); wait = WebDriverWait(driver, timeout)
        try: return wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
        except TimeoutException as e: raise WebDriverError(f"Timeout waiting for element: {selector}", cause=e) from e

    @log_method_call(logger)
    @handle_driver_exceptions("Failed to switch to frame: {frame_reference}")
    def switch_to_frame(self, frame_reference: Union[str, int, WebElement]) -> None:
        driver = self._ensure_driver(); driver.switch_to.frame(frame_reference)

    @log_method_call(logger)
    @handle_driver_exceptions("Failed to switch to default content")
    def switch_to_default_content(self) -> None:
        driver = self._ensure_driver(); driver.switch_to.default_content()

    @log_method_call(logger)
    @handle_driver_exceptions("Failed to accept alert")
    def accept_alert(self) -> None:
        driver = self._ensure_driver(); driver.switch_to.alert.accept()

    @log_method_call(logger)
    @handle_driver_exceptions("Failed to dismiss alert")
    def dismiss_alert(self) -> None:
        driver = self._ensure_driver(); driver.switch_to.alert.dismiss()

    @log_method_call(logger)
    @handle_driver_exceptions("Failed to get alert text")
    def get_alert_text(self) -> str:
        driver = self._ensure_driver(); return driver.switch_to.alert.text

    def __enter__(self): return self
    def __exit__(self, exc_type, exc_val, exc_tb): self.quit()