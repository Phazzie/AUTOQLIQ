"""Integration tests for PlaywrightDriver implementation."""

import os
import unittest
from pathlib import Path

from src.core.exceptions import WebDriverError
from src.infrastructure.webdrivers.base import BrowserType
from src.infrastructure.webdrivers.factory import WebDriverFactory


class TestPlaywrightIntegration(unittest.TestCase):
    """Integration tests for PlaywrightDriver.
    
    These tests require Playwright to be installed.
    Skip tests if Playwright is not available.
    """

    @classmethod
    def setUpClass(cls):
        """Check if Playwright is available before running tests."""
        cls.playwright_available = WebDriverFactory.is_playwright_available()
        if not cls.playwright_available:
            print("Playwright is not installed. Skipping integration tests.")
        
        # Create a directory for screenshots if it doesn't exist
        cls.screenshot_dir = Path(__file__).parent / "screenshots"
        cls.screenshot_dir.mkdir(exist_ok=True)

    def setUp(self):
        """Set up a new browser instance for each test."""
        if not self.playwright_available:
            self.skipTest("Playwright is not installed")
            
        self.driver = WebDriverFactory.create_driver(
            browser_type=BrowserType.CHROME,
            driver_type="playwright",
            implicit_wait_seconds=5
        )

    def tearDown(self):
        """Close the browser after each test."""
        if hasattr(self, 'driver'):
            self.driver.quit()

    def test_navigation(self):
        """Test basic navigation functionality."""
        # Navigate to a website
        self.driver.get("https://example.com")
        
        # Check that we're on the right page
        self.assertIn("example.com", self.driver.get_current_url())
        
        # Check page title
        title = self.driver.execute_script("return document.title")
        self.assertEqual("Example Domain", title)

    def test_find_element(self):
        """Test finding elements on a page."""
        # Navigate to a website
        self.driver.get("https://example.com")
        
        # Find an element
        h1 = self.driver.find_element("h1")
        self.assertIsNotNone(h1)
        
        # Check element text
        text = self.driver.get_element_text("h1")
        self.assertEqual("Example Domain", text)

    def test_is_element_present(self):
        """Test checking if elements are present."""
        # Navigate to a website
        self.driver.get("https://example.com")
        
        # Check for existing element
        self.assertTrue(self.driver.is_element_present("h1"))
        
        # Check for non-existing element
        self.assertFalse(self.driver.is_element_present("h5"))

    def test_wait_for_element(self):
        """Test waiting for elements to appear."""
        # Navigate to a website
        self.driver.get("https://example.com")
        
        # Wait for an element that exists immediately
        element = self.driver.wait_for_element("h1")
        self.assertIsNotNone(element)
        
        # Test timeout for non-existent element
        with self.assertRaises(WebDriverError):
            self.driver.wait_for_element("non-existent-element", timeout=1)

    def test_execute_script(self):
        """Test executing JavaScript."""
        # Navigate to a website
        self.driver.get("https://example.com")
        
        # Execute script to get page title
        title = self.driver.execute_script("return document.title")
        self.assertEqual("Example Domain", title)
        
        # Execute script to modify the page
        self.driver.execute_script("document.querySelector('h1').textContent = 'Modified Title'")
        
        # Check that the modification worked
        text = self.driver.get_element_text("h1")
        self.assertEqual("Modified Title", text)

    def test_screenshots(self):
        """Test taking screenshots."""
        # Navigate to a website
        self.driver.get("https://example.com")
        
        # Take a regular screenshot
        screenshot_path = self.screenshot_dir / "regular_screenshot.png"
        self.driver.take_screenshot(str(screenshot_path))
        self.assertTrue(screenshot_path.exists())
        
        # Take a full page screenshot
        full_screenshot_path = self.screenshot_dir / "full_page_screenshot.png"
        self.driver.take_full_page_screenshot(str(full_screenshot_path))
        self.assertTrue(full_screenshot_path.exists())
        
        # Take an element screenshot
        element_screenshot_path = self.screenshot_dir / "element_screenshot.png"
        self.driver.take_element_screenshot("h1", str(element_screenshot_path))
        self.assertTrue(element_screenshot_path.exists())

    def test_element_properties(self):
        """Test getting element properties."""
        # Navigate to a website
        self.driver.get("https://example.com")
        
        # Check element visibility
        self.assertTrue(self.driver.is_element_visible("h1"))
        
        # Get element attribute
        # Add a custom attribute with JavaScript
        self.driver.execute_script("document.querySelector('h1').setAttribute('data-test', 'test-value')")
        attr_value = self.driver.get_element_attribute("h1", "data-test")
        self.assertEqual("test-value", attr_value)

    def test_cookies(self):
        """Test cookie handling."""
        # Navigate to a website
        self.driver.get("https://example.com")
        
        # Add a cookie
        cookie = {
            "name": "test_cookie",
            "value": "test_value",
            "url": "https://example.com"
        }
        self.driver.add_cookie(cookie)
        
        # Get all cookies
        cookies = self.driver.get_cookies()
        
        # Check if our cookie is in the list
        cookie_found = False
        for c in cookies:
            if c["name"] == "test_cookie" and c["value"] == "test_value":
                cookie_found = True
                break
        self.assertTrue(cookie_found)
        
        # Delete all cookies
        self.driver.delete_all_cookies()
        
        # Check that cookies are gone
        cookies = self.driver.get_cookies()
        cookie_found = False
        for c in cookies:
            if c["name"] == "test_cookie":
                cookie_found = True
                break
        self.assertFalse(cookie_found)


if __name__ == '__main__':
    unittest.main()
