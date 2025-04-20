"""Integration tests for Firefox WebDriver implementation."""

import unittest
import os
import time
import warnings
import logging

from src.infrastructure.webdrivers.factory import WebDriverFactory
from src.infrastructure.webdrivers.base import BrowserType
from src.infrastructure.webdrivers.selenium_driver import SeleniumWebDriver
from src.core.interfaces import IWebDriver
from src.core.exceptions import WebDriverError, ConfigError, ValidationError

# Configuration needed for potential driver paths
from src.config import config

# Skip tests if running in an environment where Firefox might not be available
FIREFOX_AVAILABLE = os.environ.get("SKIP_FIREFOX_TESTS", "false").lower() != "true"

logger = logging.getLogger(__name__)

@unittest.skipIf(not FIREFOX_AVAILABLE, "Firefox tests skipped due to SKIP_FIREFOX_TESTS=true")
class TestFirefoxDriverIntegration(unittest.TestCase):
    """Integration tests for Firefox WebDriver implementation."""
    
    def setUp(self):
        """Set up test environment before each test."""
        # Suppress ResourceWarning about unclosed sockets
        warnings.simplefilter("ignore", ResourceWarning)
        
        # Get Firefox driver path from config if available
        self.firefox_driver_path = getattr(config, 'firefox_driver_path', None)
        if self.firefox_driver_path and not os.path.exists(self.firefox_driver_path):
            logger.warning(f"Firefox driver path in config does not exist: {self.firefox_driver_path}")
            self.firefox_driver_path = None
        
        # Create Firefox driver
        try:
            self.driver = WebDriverFactory.create_driver(
                browser_type=BrowserType.FIREFOX,
                webdriver_path=self.firefox_driver_path,
                headless=True  # Use headless mode for CI environments
            )
        except (WebDriverError, ConfigError) as e:
            self.skipTest(f"Failed to create Firefox driver: {e}")
    
    def tearDown(self):
        """Clean up after each test."""
        if hasattr(self, 'driver') and self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                logger.warning(f"Error quitting driver: {e}")
    
    def test_firefox_navigation(self):
        """Test basic navigation in Firefox."""
        # Navigate to a test page
        self.driver.get("https://example.com")
        
        # Verify navigation was successful
        self.assertEqual(self.driver.get_title(), "Example Domain")
        self.assertTrue("example.com" in self.driver.get_current_url())
    
    def test_firefox_find_element(self):
        """Test finding elements in Firefox."""
        # Navigate to a test page
        self.driver.get("https://example.com")
        
        # Find an element
        heading = self.driver.find_element("h1")
        
        # Verify element was found
        self.assertIsNotNone(heading)
        self.assertEqual(heading.text, "Example Domain")
    
    def test_firefox_is_element_present(self):
        """Test checking if elements are present in Firefox."""
        # Navigate to a test page
        self.driver.get("https://example.com")
        
        # Check if elements are present
        self.assertTrue(self.driver.is_element_present("h1"))
        self.assertFalse(self.driver.is_element_present("h6"))
    
    def test_firefox_execute_script(self):
        """Test executing JavaScript in Firefox."""
        # Navigate to a test page
        self.driver.get("https://example.com")
        
        # Execute JavaScript to get the page title
        title = self.driver.execute_script("return document.title;")
        
        # Verify script execution was successful
        self.assertEqual(title, "Example Domain")
    
    def test_firefox_wait_for_element(self):
        """Test waiting for elements in Firefox."""
        # Navigate to a test page
        self.driver.get("https://example.com")
        
        # Wait for an element
        element = self.driver.wait_for_element("p", timeout=5)
        
        # Verify element was found
        self.assertIsNotNone(element)
        self.assertTrue("for use in illustrative examples" in element.text)

if __name__ == '__main__':
    unittest.main()
