"""Basic integration tests for PlaywrightDriver implementation."""

import unittest
import os
import time
from typing import Optional

from src.infrastructure.webdrivers import WebDriverFactory, BrowserType
from src.infrastructure.webdrivers.playwright_driver import PlaywrightDriver
from src.core.interfaces import IWebDriver
from src.core.exceptions import WebDriverError

# Test against a public website
TEST_SITE_URL = "https://example.com"


class TestPlaywrightBasic(unittest.TestCase):
    """Basic integration tests for PlaywrightDriver."""
    
    def setUp(self):
        """Set up a new browser instance for each test."""
        try:
            self.driver = WebDriverFactory.create_driver(
                browser_type=BrowserType.CHROME,
                driver_type="playwright",
                implicit_wait_seconds=5
            )
        except Exception as e:
            self.skipTest(f"Playwright not available: {e}")
    
    def tearDown(self):
        """Close the browser after each test."""
        if hasattr(self, 'driver') and self.driver:
            self.driver.quit()
    
    def test_navigation(self):
        """Test basic navigation functionality."""
        # Navigate to a website
        self.driver.get(TEST_SITE_URL)
        
        # Check that we're on the right page
        self.assertIn("example.com", self.driver.get_current_url())
        
        # Check page title using JavaScript
        title = self.driver.execute_script("return document.title")
        self.assertEqual("Example Domain", title)
    
    def test_find_element(self):
        """Test finding elements on a page."""
        # Navigate to a website
        self.driver.get(TEST_SITE_URL)
        
        # Find an element
        h1 = self.driver.find_element("h1")
        self.assertIsNotNone(h1)
        
        # Check element text
        text = self.driver.get_element_text("h1")
        self.assertEqual("Example Domain", text)
    
    def test_is_element_present(self):
        """Test checking if elements are present."""
        # Navigate to a website
        self.driver.get(TEST_SITE_URL)
        
        # Check for existing element
        self.assertTrue(self.driver.is_element_present("h1"))
        
        # Check for non-existing element
        self.assertFalse(self.driver.is_element_present("h5"))
    
    def test_wait_for_element(self):
        """Test waiting for elements to appear."""
        # Navigate to a website
        self.driver.get(TEST_SITE_URL)
        
        # Wait for an element that exists immediately
        element = self.driver.wait_for_element("h1")
        self.assertIsNotNone(element)
        
        # Test timeout for non-existent element
        with self.assertRaises(WebDriverError):
            self.driver.wait_for_element("non-existent-element", timeout=1)
    
    def test_execute_script(self):
        """Test executing JavaScript."""
        # Navigate to a website
        self.driver.get(TEST_SITE_URL)
        
        # Execute script to get page title
        title = self.driver.execute_script("return document.title")
        self.assertEqual("Example Domain", title)
        
        # Execute script to modify the page
        self.driver.execute_script("document.querySelector('h1').textContent = 'Modified Title'")
        
        # Verify the modification
        modified_text = self.driver.get_element_text("h1")
        self.assertEqual("Modified Title", modified_text)
    
    def test_screenshot(self):
        """Test taking screenshots."""
        # Navigate to a website
        self.driver.get(TEST_SITE_URL)
        
        # Take a screenshot
        screenshot_path = "playwright_test_screenshot.png"
        try:
            self.driver.take_screenshot(screenshot_path)
            
            # Verify the screenshot was created
            self.assertTrue(os.path.exists(screenshot_path))
            self.assertTrue(os.path.getsize(screenshot_path) > 0)
        finally:
            # Clean up
            if os.path.exists(screenshot_path):
                os.remove(screenshot_path)


if __name__ == "__main__":
    unittest.main()
