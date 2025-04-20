"""Unit tests for the enhanced SeleniumWebDriver implementation."""

import unittest
from unittest.mock import MagicMock, patch
import os

from src.infrastructure.webdrivers.selenium_driver import SeleniumWebDriver
from src.infrastructure.webdrivers.base import BrowserType
from src.core.exceptions import WebDriverError, ConfigError, ValidationError

class TestSeleniumWebDriverEnhanced(unittest.TestCase):
    """Test cases for the enhanced SeleniumWebDriver implementation."""

    @patch('src.infrastructure.webdrivers.selenium_driver.webdriver')
    def test_firefox_driver_initialization(self, mock_webdriver):
        """Test that Firefox driver is initialized correctly."""
        # Mock Firefox driver
        mock_firefox_driver = MagicMock()
        mock_webdriver.Firefox.return_value = mock_firefox_driver
        
        # Create Firefox driver
        driver = SeleniumWebDriver(browser_type=BrowserType.FIREFOX)
        
        # Verify Firefox driver was created
        mock_webdriver.Firefox.assert_called_once()
        self.assertEqual(driver.browser_type, BrowserType.FIREFOX)
        self.assertIsNotNone(driver.driver)
    
    @patch('src.infrastructure.webdrivers.selenium_driver.webdriver')
    def test_headless_mode_chrome(self, mock_webdriver):
        """Test that headless mode is configured correctly for Chrome."""
        # Mock Chrome driver
        mock_chrome_driver = MagicMock()
        mock_webdriver.Chrome.return_value = mock_chrome_driver
        
        # Create Chrome driver in headless mode
        driver = SeleniumWebDriver(browser_type=BrowserType.CHROME, headless=True)
        
        # Verify Chrome driver was created with headless option
        mock_webdriver.Chrome.assert_called_once()
        # Get the options argument from the call
        options = mock_webdriver.Chrome.call_args[1]['options']
        # Check if headless argument was added
        self.assertIn('--headless=new', options.arguments)
    
    @patch('src.infrastructure.webdrivers.selenium_driver.webdriver')
    def test_headless_mode_firefox(self, mock_webdriver):
        """Test that headless mode is configured correctly for Firefox."""
        # Mock Firefox driver
        mock_firefox_driver = MagicMock()
        mock_webdriver.Firefox.return_value = mock_firefox_driver
        
        # Create Firefox driver in headless mode
        driver = SeleniumWebDriver(browser_type=BrowserType.FIREFOX, headless=True)
        
        # Verify Firefox driver was created with headless option
        mock_webdriver.Firefox.assert_called_once()
        # Get the options argument from the call
        options = mock_webdriver.Firefox.call_args[1]['options']
        # Check if headless argument was added
        self.assertIn('-headless', options.arguments)
    
    @patch('src.infrastructure.webdrivers.selenium_driver.webdriver')
    def test_firefox_preferences(self, mock_webdriver):
        """Test that Firefox preferences are set correctly."""
        # Mock Firefox driver
        mock_firefox_driver = MagicMock()
        mock_webdriver.Firefox.return_value = mock_firefox_driver
        
        # Create Firefox driver
        driver = SeleniumWebDriver(browser_type=BrowserType.FIREFOX)
        
        # Verify Firefox driver was created with preferences
        mock_webdriver.Firefox.assert_called_once()
        # Get the options argument from the call
        options = mock_webdriver.Firefox.call_args[1]['options']
        # Check if preferences were set
        self.assertEqual(options.preferences['browser.download.folderList'], 2)
        self.assertEqual(options.preferences['browser.download.manager.showWhenStarting'], False)
    
    @patch('src.infrastructure.webdrivers.selenium_driver.os.path.exists')
    @patch('src.infrastructure.webdrivers.selenium_driver.webdriver')
    def test_firefox_with_geckodriver_path(self, mock_webdriver, mock_exists):
        """Test that Firefox driver uses the provided geckodriver path."""
        # Mock path exists
        mock_exists.return_value = True
        
        # Mock Firefox driver
        mock_firefox_driver = MagicMock()
        mock_webdriver.Firefox.return_value = mock_firefox_driver
        
        # Create Firefox driver with geckodriver path
        driver = SeleniumWebDriver(
            browser_type=BrowserType.FIREFOX,
            webdriver_path="/path/to/geckodriver"
        )
        
        # Verify Firefox driver was created with service using the path
        mock_webdriver.Firefox.assert_called_once()
        # Get the service argument from the call
        service = mock_webdriver.Firefox.call_args[1]['service']
        # Check if the path was set
        self.assertEqual(service.executable_path, "/path/to/geckodriver")
    
    @patch('src.infrastructure.webdrivers.selenium_driver.os.path.exists')
    def test_invalid_geckodriver_path(self, mock_exists):
        """Test that an invalid geckodriver path raises ConfigError."""
        # Mock path does not exist
        mock_exists.return_value = False
        
        # Attempt to create Firefox driver with invalid geckodriver path
        with self.assertRaises(ConfigError):
            SeleniumWebDriver(
                browser_type=BrowserType.FIREFOX,
                webdriver_path="/invalid/path/to/geckodriver"
            )
    
    @patch('src.infrastructure.webdrivers.selenium_driver.webdriver')
    def test_additional_methods(self, mock_webdriver):
        """Test that additional methods are implemented correctly."""
        # Mock Chrome driver
        mock_chrome_driver = MagicMock()
        mock_webdriver.Chrome.return_value = mock_chrome_driver
        
        # Create Chrome driver
        driver = SeleniumWebDriver(browser_type=BrowserType.CHROME)
        
        # Test additional methods
        driver.get_page_source()
        mock_chrome_driver.page_source.__str__.assert_called_once()
        
        driver.get_title()
        mock_chrome_driver.title.__str__.assert_called_once()
        
        driver.set_window_size(800, 600)
        mock_chrome_driver.set_window_size.assert_called_once_with(800, 600)
        
        driver.maximize_window()
        mock_chrome_driver.maximize_window.assert_called_once()
        
        driver.refresh()
        mock_chrome_driver.refresh.assert_called_once()
        
        driver.back()
        mock_chrome_driver.back.assert_called_once()
        
        driver.forward()
        mock_chrome_driver.forward.assert_called_once()

if __name__ == '__main__':
    unittest.main()
