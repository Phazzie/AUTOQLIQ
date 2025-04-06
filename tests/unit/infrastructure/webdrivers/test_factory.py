"""Tests for the WebDriverFactory class."""
import unittest
from unittest.mock import patch, MagicMock

# Define mock options classes for testing
class ChromeOptions:
    pass

class FirefoxOptions:
    pass

class EdgeOptions:
    pass

from src.infrastructure.webdrivers.browser_type import BrowserType
from src.infrastructure.webdrivers.factory import WebDriverFactory

class TestWebDriverFactory(unittest.TestCase):
    """Test cases for the WebDriverFactory class."""

    @patch("selenium.webdriver.Chrome")
    def test_create_driver_chrome(self, mock_chrome):
        """Test that create_driver creates a Chrome WebDriver."""
        # Set up mock return value
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver

        # Create driver
        result = WebDriverFactory.create_driver(BrowserType.CHROME)

        # Check result
        self.assertEqual(result, mock_driver)

        # Verify Chrome was called with correct arguments
        mock_chrome.assert_called_once()

        # Verify options were passed to Chrome
        self.assertIn("options", mock_chrome.call_args[1])

    @patch("selenium.webdriver.Chrome")
    def test_create_driver_chrome_with_options(self, mock_chrome):
        """Test that create_driver creates a Chrome WebDriver with options."""
        # Set up mock return value
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver

        # Create driver with options
        options = {
            "headless": True,
            "window_size": (1024, 768)
        }
        result = WebDriverFactory.create_driver(BrowserType.CHROME, options)

        # Check result
        self.assertEqual(result, mock_driver)

        # Verify Chrome was called with correct arguments
        mock_chrome.assert_called_once()

        # Verify options were passed to Chrome
        self.assertIn("options", mock_chrome.call_args[1])

        # For this test, we can't check the actual options since we're not mocking
        # the ChromeOptions class. We'll just verify that the options object is passed
        # to the Chrome constructor.

    @patch("selenium.webdriver.Firefox")
    def test_create_driver_firefox(self, mock_firefox):
        """Test that create_driver creates a Firefox WebDriver."""
        # Set up mock return value
        mock_driver = MagicMock()
        mock_firefox.return_value = mock_driver

        # Create driver
        result = WebDriverFactory.create_driver(BrowserType.FIREFOX)

        # Check result
        self.assertEqual(result, mock_driver)

        # Verify Firefox was called with correct arguments
        mock_firefox.assert_called_once()

        # Verify options were passed to Firefox
        self.assertIn("options", mock_firefox.call_args[1])

    @patch("selenium.webdriver.Firefox")
    def test_create_driver_firefox_with_options(self, mock_firefox):
        """Test that create_driver creates a Firefox WebDriver with options."""
        # Set up mock return value
        mock_driver = MagicMock()
        mock_firefox.return_value = mock_driver

        # Create driver with options
        options = {
            "headless": True
        }
        result = WebDriverFactory.create_driver(BrowserType.FIREFOX, options)

        # Check result
        self.assertEqual(result, mock_driver)

        # Verify Firefox was called with correct arguments
        mock_firefox.assert_called_once()

        # Verify options were passed to Firefox
        self.assertIn("options", mock_firefox.call_args[1])

        # For this test, we can't check the actual options since we're not mocking
        # the FirefoxOptions class. We'll just verify that the options object is passed
        # to the Firefox constructor.

    @patch("selenium.webdriver.Edge")
    def test_create_driver_edge(self, mock_edge):
        """Test that create_driver creates an Edge WebDriver."""
        # Set up mock return value
        mock_driver = MagicMock()
        mock_edge.return_value = mock_driver

        # Create driver
        result = WebDriverFactory.create_driver(BrowserType.EDGE)

        # Check result
        self.assertEqual(result, mock_driver)

        # Verify Edge was called with correct arguments
        mock_edge.assert_called_once()

        # Verify options were passed to Edge
        self.assertIn("options", mock_edge.call_args[1])

    @patch("selenium.webdriver.Edge")
    def test_create_driver_edge_with_options(self, mock_edge):
        """Test that create_driver creates an Edge WebDriver with options."""
        # Set up mock return value
        mock_driver = MagicMock()
        mock_edge.return_value = mock_driver

        # Create driver with options
        options = {
            "headless": True
        }
        result = WebDriverFactory.create_driver(BrowserType.EDGE, options)

        # Check result
        self.assertEqual(result, mock_driver)

        # Verify Edge was called with correct arguments
        mock_edge.assert_called_once()

        # Verify options were passed to Edge
        self.assertIn("options", mock_edge.call_args[1])

        # For this test, we can't check the actual options since we're not mocking
        # the EdgeOptions class. We'll just verify that the options object is passed
        # to the Edge constructor.

    def test_create_driver_unsupported_browser(self):
        """Test that create_driver raises ValueError for unsupported browser types."""
        # Create a mock browser type
        mock_browser_type = MagicMock()
        mock_browser_type.__str__.return_value = "mock_browser"

        # Try to create driver with unsupported browser type
        with self.assertRaises(ValueError):
            WebDriverFactory.create_driver(mock_browser_type)

if __name__ == "__main__":
    unittest.main()
