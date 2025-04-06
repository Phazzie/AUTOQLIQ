"""Tests for the BrowserType enum."""
import unittest

from src.infrastructure.webdrivers.browser_type import BrowserType

class TestBrowserType(unittest.TestCase):
    """Test cases for the BrowserType enum."""

    def test_browser_type_values(self):
        """Test that BrowserType enum has the expected values."""
        self.assertEqual(BrowserType.CHROME.value, "chrome")
        self.assertEqual(BrowserType.FIREFOX.value, "firefox")
        self.assertEqual(BrowserType.EDGE.value, "edge")

    def test_browser_type_equality(self):
        """Test that BrowserType enum values can be compared."""
        self.assertEqual(BrowserType.CHROME, BrowserType.CHROME)
        self.assertNotEqual(BrowserType.CHROME, BrowserType.FIREFOX)
        self.assertNotEqual(BrowserType.CHROME, BrowserType.EDGE)

if __name__ == "__main__":
    unittest.main()
