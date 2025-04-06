"""Tests for the WebDriverService class."""
import unittest
from unittest.mock import patch, MagicMock, call

from src.core.exceptions import WebDriverError
from src.core.interfaces import IWebDriver
from src.infrastructure.webdrivers.browser_type import BrowserType
from src.application.interfaces import IWebDriverService
from src.application.services.webdriver_service import WebDriverService


class TestWebDriverService(unittest.TestCase):
    """Test cases for the WebDriverService class."""

    def setUp(self):
        """Set up test fixtures."""
        self.web_driver_factory = MagicMock()
        self.web_driver = MagicMock(spec=IWebDriver)
        self.web_driver_factory.create_driver.return_value = self.web_driver
        
        self.service = WebDriverService(web_driver_factory=self.web_driver_factory)

    def test_create_web_driver(self):
        """Test that create_web_driver creates a new web driver instance."""
        # Call create_web_driver
        result = self.service.create_web_driver("chrome")
        
        # Check result
        self.assertEqual(result, self.web_driver)
        
        # Verify web_driver_factory.create_driver was called with correct arguments
        self.web_driver_factory.create_driver.assert_called_once_with(
            BrowserType.CHROME, 
            options=None
        )

    def test_create_web_driver_with_options(self):
        """Test that create_web_driver creates a new web driver instance with options."""
        # Call create_web_driver with options
        options = {"headless": True, "window_size": (1024, 768)}
        result = self.service.create_web_driver("chrome", options)
        
        # Check result
        self.assertEqual(result, self.web_driver)
        
        # Verify web_driver_factory.create_driver was called with correct arguments
        self.web_driver_factory.create_driver.assert_called_once_with(
            BrowserType.CHROME, 
            options=options
        )

    def test_create_web_driver_firefox(self):
        """Test that create_web_driver creates a Firefox web driver instance."""
        # Call create_web_driver
        result = self.service.create_web_driver("firefox")
        
        # Check result
        self.assertEqual(result, self.web_driver)
        
        # Verify web_driver_factory.create_driver was called with correct arguments
        self.web_driver_factory.create_driver.assert_called_once_with(
            BrowserType.FIREFOX, 
            options=None
        )

    def test_create_web_driver_edge(self):
        """Test that create_web_driver creates an Edge web driver instance."""
        # Call create_web_driver
        result = self.service.create_web_driver("edge")
        
        # Check result
        self.assertEqual(result, self.web_driver)
        
        # Verify web_driver_factory.create_driver was called with correct arguments
        self.web_driver_factory.create_driver.assert_called_once_with(
            BrowserType.EDGE, 
            options=None
        )

    def test_create_web_driver_unsupported_browser(self):
        """Test that create_web_driver raises WebDriverError for unsupported browser types."""
        # Try to call create_web_driver with an unsupported browser type
        with self.assertRaises(WebDriverError):
            self.service.create_web_driver("unsupported")

    def test_create_web_driver_error(self):
        """Test that create_web_driver raises WebDriverError when creating a web driver fails."""
        # Set up mock to raise an exception
        self.web_driver_factory.create_driver.side_effect = ValueError("Create web driver failed")
        
        # Try to call create_web_driver
        with self.assertRaises(WebDriverError):
            self.service.create_web_driver("chrome")

    def test_dispose_web_driver(self):
        """Test that dispose_web_driver disposes of a web driver instance."""
        # Call dispose_web_driver
        result = self.service.dispose_web_driver(self.web_driver)
        
        # Check result
        self.assertTrue(result)
        
        # Verify web_driver.quit was called
        self.web_driver.quit.assert_called_once()

    def test_dispose_web_driver_error(self):
        """Test that dispose_web_driver raises WebDriverError when disposing of a web driver fails."""
        # Set up mock to raise an exception
        self.web_driver.quit.side_effect = Exception("Dispose web driver failed")
        
        # Try to call dispose_web_driver
        with self.assertRaises(WebDriverError):
            self.service.dispose_web_driver(self.web_driver)


if __name__ == "__main__":
    unittest.main()
