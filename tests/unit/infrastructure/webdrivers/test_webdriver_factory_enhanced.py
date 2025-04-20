"""Unit tests for the enhanced WebDriverFactory implementation."""

import unittest
from unittest.mock import MagicMock, patch

from src.infrastructure.webdrivers.factory import WebDriverFactory
from src.infrastructure.webdrivers.base import BrowserType
from src.core.exceptions import WebDriverError, ConfigError

class TestWebDriverFactoryEnhanced(unittest.TestCase):
    """Test cases for the enhanced WebDriverFactory implementation."""

    @patch('src.infrastructure.webdrivers.factory.SeleniumWebDriver')
    def test_create_driver_with_headless(self, mock_selenium_driver):
        """Test that create_driver passes headless parameter to SeleniumWebDriver."""
        # Mock SeleniumWebDriver
        mock_driver_instance = MagicMock()
        mock_selenium_driver.return_value = mock_driver_instance
        
        # Create driver with headless=True
        driver = WebDriverFactory.create_driver(
            browser_type=BrowserType.CHROME,
            headless=True
        )
        
        # Verify SeleniumWebDriver was called with headless=True
        mock_selenium_driver.assert_called_once()
        self.assertEqual(mock_selenium_driver.call_args[1]['headless'], True)
    
    @patch('src.infrastructure.webdrivers.factory.SeleniumWebDriver')
    def test_create_driver_with_headless_false(self, mock_selenium_driver):
        """Test that create_driver passes headless=False to SeleniumWebDriver."""
        # Mock SeleniumWebDriver
        mock_driver_instance = MagicMock()
        mock_selenium_driver.return_value = mock_driver_instance
        
        # Create driver with headless=False
        driver = WebDriverFactory.create_driver(
            browser_type=BrowserType.CHROME,
            headless=False
        )
        
        # Verify SeleniumWebDriver was called with headless=False
        mock_selenium_driver.assert_called_once()
        self.assertEqual(mock_selenium_driver.call_args[1]['headless'], False)
    
    @patch('src.infrastructure.webdrivers.factory.PlaywrightDriver')
    def test_create_playwright_driver_with_headless(self, mock_playwright_driver):
        """Test that create_driver sets headless in playwright_options."""
        # Mock PlaywrightDriver
        mock_driver_instance = MagicMock()
        mock_playwright_driver.return_value = mock_driver_instance
        
        # Create driver with headless=True
        driver = WebDriverFactory.create_driver(
            browser_type=BrowserType.CHROME,
            driver_type="playwright",
            headless=True
        )
        
        # Verify PlaywrightDriver was called with headless=True in launch_options
        mock_playwright_driver.assert_called_once()
        self.assertEqual(mock_playwright_driver.call_args[1]['launch_options']['headless'], True)
    
    @patch('src.infrastructure.webdrivers.factory.PlaywrightDriver')
    def test_create_playwright_driver_with_custom_options_and_headless(self, mock_playwright_driver):
        """Test that create_driver preserves custom options when setting headless."""
        # Mock PlaywrightDriver
        mock_driver_instance = MagicMock()
        mock_playwright_driver.return_value = mock_driver_instance
        
        # Create driver with custom options and headless=True
        custom_options = {'slowMo': 100, 'devtools': True}
        driver = WebDriverFactory.create_driver(
            browser_type=BrowserType.CHROME,
            driver_type="playwright",
            playwright_options=custom_options,
            headless=True
        )
        
        # Verify PlaywrightDriver was called with all options preserved
        mock_playwright_driver.assert_called_once()
        launch_options = mock_playwright_driver.call_args[1]['launch_options']
        self.assertEqual(launch_options['headless'], True)
        self.assertEqual(launch_options['slowMo'], 100)
        self.assertEqual(launch_options['devtools'], True)
    
    @patch('src.infrastructure.webdrivers.factory.PlaywrightDriver')
    def test_create_playwright_driver_with_explicit_headless_option(self, mock_playwright_driver):
        """Test that explicit headless option in playwright_options is preserved."""
        # Mock PlaywrightDriver
        mock_driver_instance = MagicMock()
        mock_playwright_driver.return_value = mock_driver_instance
        
        # Create driver with explicit headless=False in options but headless=True parameter
        custom_options = {'headless': False}
        driver = WebDriverFactory.create_driver(
            browser_type=BrowserType.CHROME,
            driver_type="playwright",
            playwright_options=custom_options,
            headless=True
        )
        
        # Verify PlaywrightDriver was called with original headless value preserved
        mock_playwright_driver.assert_called_once()
        self.assertEqual(mock_playwright_driver.call_args[1]['launch_options']['headless'], False)
    
    def test_unsupported_driver_type(self):
        """Test that an unsupported driver type raises ConfigError."""
        with self.assertRaises(ConfigError):
            WebDriverFactory.create_driver(driver_type="unsupported")

if __name__ == '__main__':
    unittest.main()
