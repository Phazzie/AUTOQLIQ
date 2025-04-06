"""Tests for the WebDriverFactory class."""
import unittest
from unittest.mock import patch, MagicMock

from src.core.interfaces import IWebDriver
from src.infrastructure.webdrivers.browser_type import BrowserType
from src.infrastructure.webdrivers.factory import WebDriverFactory
from src.infrastructure.webdrivers.selenium_driver import SeleniumWebDriver

class TestWebDriverFactory(unittest.TestCase):
    """Test cases for the WebDriverFactory class."""

    @patch("src.infrastructure.webdrivers.factory.webdriver.Chrome")
    def test_create_chrome_driver(self, mock_chrome):
        """Test that _create_chrome_driver creates a Chrome WebDriver."""
        # Set up mock
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        
        # Create a Chrome driver
        driver = WebDriverFactory._create_chrome_driver({})
        
        # Check that the driver is of the correct type
        self.assertEqual(driver, mock_driver)
        
        # Check that Chrome was called
        mock_chrome.assert_called_once()

    @patch("src.infrastructure.webdrivers.factory.webdriver.Firefox")
    def test_create_firefox_driver(self, mock_firefox):
        """Test that _create_firefox_driver creates a Firefox WebDriver."""
        # Set up mock
        mock_driver = MagicMock()
        mock_firefox.return_value = mock_driver
        
        # Create a Firefox driver
        driver = WebDriverFactory._create_firefox_driver({})
        
        # Check that the driver is of the correct type
        self.assertEqual(driver, mock_driver)
        
        # Check that Firefox was called
        mock_firefox.assert_called_once()

    @patch("src.infrastructure.webdrivers.factory.webdriver.Edge")
    def test_create_edge_driver(self, mock_edge):
        """Test that _create_edge_driver creates an Edge WebDriver."""
        # Set up mock
        mock_driver = MagicMock()
        mock_edge.return_value = mock_driver
        
        # Create an Edge driver
        driver = WebDriverFactory._create_edge_driver({})
        
        # Check that the driver is of the correct type
        self.assertEqual(driver, mock_driver)
        
        # Check that Edge was called
        mock_edge.assert_called_once()

    @patch("src.infrastructure.webdrivers.factory.WebDriverFactory._create_chrome_driver")
    def test_create_driver_chrome(self, mock_create_chrome):
        """Test that create_driver creates a Chrome WebDriver."""
        # Set up mock
        mock_driver = MagicMock()
        mock_create_chrome.return_value = mock_driver
        
        # Create a driver
        driver = WebDriverFactory.create_driver(BrowserType.CHROME)
        
        # Check that the driver is of the correct type
        self.assertEqual(driver, mock_driver)
        
        # Check that _create_chrome_driver was called with the correct options
        mock_create_chrome.assert_called_once_with({})

    @patch("src.infrastructure.webdrivers.factory.WebDriverFactory._create_firefox_driver")
    def test_create_driver_firefox(self, mock_create_firefox):
        """Test that create_driver creates a Firefox WebDriver."""
        # Set up mock
        mock_driver = MagicMock()
        mock_create_firefox.return_value = mock_driver
        
        # Create a driver
        driver = WebDriverFactory.create_driver(BrowserType.FIREFOX)
        
        # Check that the driver is of the correct type
        self.assertEqual(driver, mock_driver)
        
        # Check that _create_firefox_driver was called with the correct options
        mock_create_firefox.assert_called_once_with({})

    @patch("src.infrastructure.webdrivers.factory.WebDriverFactory._create_edge_driver")
    def test_create_driver_edge(self, mock_create_edge):
        """Test that create_driver creates an Edge WebDriver."""
        # Set up mock
        mock_driver = MagicMock()
        mock_create_edge.return_value = mock_driver
        
        # Create a driver
        driver = WebDriverFactory.create_driver(BrowserType.EDGE)
        
        # Check that the driver is of the correct type
        self.assertEqual(driver, mock_driver)
        
        # Check that _create_edge_driver was called with the correct options
        mock_create_edge.assert_called_once_with({})

    def test_create_driver_unsupported(self):
        """Test that create_driver raises ValueError for unsupported browser types."""
        # Create a driver with an unsupported browser type
        with self.assertRaises(ValueError):
            # Create a mock browser type that is not supported
            unsupported_browser_type = MagicMock()
            unsupported_browser_type.value = "unsupported"
            WebDriverFactory.create_driver(unsupported_browser_type)

    @patch("src.infrastructure.webdrivers.factory.WebDriverFactory.create_driver")
    @patch("src.infrastructure.webdrivers.factory.SeleniumWebDriver")
    def test_create_selenium_webdriver(self, mock_selenium_webdriver, mock_create_driver):
        """Test that create_selenium_webdriver creates a SeleniumWebDriver."""
        # Set up mocks
        mock_driver = MagicMock()
        mock_create_driver.return_value = mock_driver
        mock_selenium_instance = MagicMock()
        mock_selenium_webdriver.return_value = mock_selenium_instance
        
        # Create a SeleniumWebDriver
        driver = WebDriverFactory.create_selenium_webdriver(BrowserType.CHROME)
        
        # Check that the driver is the mock instance
        self.assertEqual(driver, mock_selenium_instance)
        
        # Check that create_driver was called with the correct options
        mock_create_driver.assert_called_once_with(BrowserType.CHROME, {})
        
        # Check that SeleniumWebDriver was called with the correct driver
        mock_selenium_webdriver.assert_called_once_with(driver=mock_driver)

if __name__ == "__main__":
    unittest.main()
