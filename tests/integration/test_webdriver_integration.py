"""Integration tests for WebDriver implementations (Selenium)."""

import unittest
import os
import time
import warnings
import logging

# Assuming correct paths for imports
from src.infrastructure.webdrivers.factory import WebDriverFactory
from src.infrastructure.webdrivers.base import BrowserType
from src.infrastructure.webdrivers.selenium_driver import SeleniumWebDriver # Test specific implementation
from src.core.interfaces import IWebDriver
from src.core.exceptions import WebDriverError, ConfigError, ValidationError
# Configuration needed for potential driver paths
from src.config import config

# Target website for testing (relatively stable)
TEST_SITE_URL = "https://httpbin.org"
FORM_PAGE_URL = f"{TEST_SITE_URL}/forms/post"
DELAY_PAGE_URL = f"{TEST_SITE_URL}/delay/2" # Page that takes 2 seconds to load
ALERT_PAGE_URL = f"{TEST_SITE_URL}/basic-auth/user/passwd" # Requires basic auth, triggers alert if cancelled

# Check if running in an environment where a browser driver might not be available
DRIVER_AVAILABLE = os.environ.get("SKIP_WEBDRIVER_TESTS", "false").lower() != "true"
# Determine which browser to test based on config or default
BROWSER_TO_TEST_STR = config.default_browser
try:
    BROWSER_TO_TEST = BrowserType.from_string(BROWSER_TO_TEST_STR)
except ValueError:
     print(f"Warning: Invalid default_browser '{BROWSER_TO_TEST_STR}' in config. Defaulting to Chrome for tests.")
     BROWSER_TO_TEST = BrowserType.CHROME
     BROWSER_TO_TEST_STR = "chrome"


logger = logging.getLogger(__name__)

@unittest.skipUnless(DRIVER_AVAILABLE, f"WebDriver Integration Tests skipped (SKIP_WEBDRIVER_TESTS=true or driver for '{BROWSER_TO_TEST_STR}' unavailable/misconfigured)")
class TestWebDriverIntegration(unittest.TestCase):
    """Integration tests for SeleniumWebDriver against a live site."""

    driver: Optional[IWebDriver] = None
    webdriver_factory: WebDriverFactory

    @classmethod
    def setUpClass(cls):
        """Initialize WebDriver factory."""
        cls.webdriver_factory = WebDriverFactory()
        warnings.simplefilter("ignore", ResourceWarning)
        logger.info(f"--- Starting WebDriver Integration Tests ({BROWSER_TO_TEST_STR}) ---")

    def setUp(self):
        """Create a WebDriver instance for each test."""
        logger.debug(f"Setting up WebDriver for test: {self.id()}")
        try:
             self.driver = self.webdriver_factory.create_driver(
                 browser_type=BROWSER_TO_TEST,
                 implicit_wait_seconds=config.implicit_wait,
                 webdriver_path=config.get_driver_path(BROWSER_TO_TEST_STR)
             )
             logger.debug("WebDriver instance created.")
        except (WebDriverError, ConfigError, Exception) as e:
            logger.error(f"SETUP FAILED: Could not create WebDriver: {e}", exc_info=True)
            self.driver = None
            self.fail(f"WebDriver creation failed: {e}") # Fail test immediately

    def tearDown(self):
        """Quit the WebDriver instance after each test."""
        logger.debug(f"Tearing down WebDriver for test: {self.id()}")
        if self.driver:
            try: self.driver.quit()
            except Exception as e: logger.error(f"Warning: Error quitting WebDriver: {e}")
        self.driver = None

    @classmethod
    def tearDownClass(cls):
        logger.info(f"--- Finished WebDriver Integration Tests ({BROWSER_TO_TEST_STR}) ---")

    # --- Test Cases ---

    def test_navigation_get_and_url(self):
        """Test navigating to a URL and getting the current URL."""
        self.assertIsNotNone(self.driver)
        self.driver.get(TEST_SITE_URL); self.assertTrue(self.driver.get_current_url().startswith(TEST_SITE_URL))
        self.driver.get(FORM_PAGE_URL); self.assertTrue(self.driver.get_current_url().startswith(FORM_PAGE_URL))

    def test_find_element_present(self):
        """Test finding an existing element by CSS selector."""
        self.assertIsNotNone(self.driver); self.driver.get(TEST_SITE_URL)
        element = self.driver.find_element("h2") # Find first h2 element
        self.assertIsNotNone(element)
        if hasattr(element, 'tag_name'): self.assertEqual(element.tag_name.lower(), 'h2')

    def test_find_element_not_present_raises_error(self):
        """Test finding a non-existent element raises WebDriverError."""
        self.assertIsNotNone(self.driver); self.driver.get(TEST_SITE_URL)
        with self.assertRaisesRegex(WebDriverError, "Element not found"): self.driver.find_element("#non-existent-id")

    def test_is_element_present(self):
        """Test checking for element presence."""
        self.assertIsNotNone(self.driver); self.driver.get(TEST_SITE_URL)
        self.assertTrue(self.driver.is_element_present("h2"))
        self.assertFalse(self.driver.is_element_present("#non-existent-id"))

    def test_click_and_type(self):
        """Test clicking an element and typing text into form fields."""
        self.assertIsNotNone(self.driver); self.driver.get(FORM_PAGE_URL)
        name_sel, tel_sel, submit_sel = "form input[name='custname']", "form input[name='custtel']", "form button"
        self.driver.type_text(name_sel, "Integ Test Customer"); self.driver.type_text(tel_sel, "555-1111")
        self.driver.click_element(submit_sel); time.sleep(1) # Simple wait
        if isinstance(self.driver, SeleniumWebDriver):
            page_source = self.driver.driver.page_source
            self.assertIn("Integ Test Customer", page_source); self.assertIn("555-1111", page_source)
        else: self.skipTest("Cannot verify page source for non-Selenium driver")

    def test_execute_script(self):
         """Test executing simple JavaScript and getting return value."""
         self.assertIsNotNone(self.driver); self.driver.get(TEST_SITE_URL)
         title = self.driver.execute_script("return document.title;")
         self.assertIsInstance(title, str); self.assertIn("httpbin", title)
         result = self.driver.execute_script("return arguments[0] + arguments[1];", 10, 22); self.assertEqual(result, 32)
         # Test returning non-primitive
         result_obj = self.driver.execute_script("return {a: 1, b: 'hello'};")
         self.assertIsInstance(result_obj, dict); self.assertEqual(result_obj.get('a'), 1)

    def test_wait_for_element_success(self):
         """Test waiting for an element that appears."""
         self.assertIsNotNone(self.driver); self.driver.get(FORM_PAGE_URL)
         submit_sel = "form button"
         try:
             element = self.driver.wait_for_element(submit_sel, timeout=5)
             self.assertIsNotNone(element)
             if hasattr(element, 'tag_name'): self.assertEqual(element.tag_name.lower(), 'button')
         except WebDriverError as e: self.fail(f"wait_for_element failed unexpectedly: {e}")

    def test_wait_for_element_timeout(self):
         """Test waiting for an element that doesn't appear raises error."""
         self.assertIsNotNone(self.driver); self.driver.get(TEST_SITE_URL)
         with self.assertRaisesRegex(WebDriverError, "Timeout waiting for element"):
              self.driver.wait_for_element("#non-existent-wait-id", timeout=1)

    # @unittest.skip("Alert tests often unstable")
    # def test_alerts(self): ...
    # @unittest.skip("Frame tests require specific HTML")
    # def test_frames(self): ...

if __name__ == '__main__':
    if DRIVER_AVAILABLE:
        unittest.main(argv=['first-arg-is-ignored'], exit=False)
    else:
        print(f"Skipping WebDriver integration tests for {BROWSER_TO_TEST_STR}.")