"""Simple test for PlaywrightDriver implementation."""

import unittest
from src.infrastructure.webdrivers import WebDriverFactory, BrowserType

# Test against a public website
TEST_SITE_URL = "https://example.com"

class TestPlaywrightSimple(unittest.TestCase):
    """Simple test for PlaywrightDriver."""
    
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

if __name__ == "__main__":
    unittest.main()
