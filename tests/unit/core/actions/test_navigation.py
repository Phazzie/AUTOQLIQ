"""Tests for the navigation actions module."""
import unittest
from unittest.mock import Mock

from src.core.interfaces import IWebDriver
from src.core.action_result import ActionResult
from src.core.exceptions import WebDriverError, ActionError
from src.core.actions.navigation import NavigateAction

class TestNavigateAction(unittest.TestCase):
    """Test cases for the NavigateAction class."""

    def test_init(self):
        """Test that NavigateAction can be initialized with the required parameters."""
        action = NavigateAction(url="https://example.com")
        self.assertEqual(action.url, "https://example.com")
        self.assertEqual(action.name, "Navigate")
        
        action = NavigateAction(url="https://example.com", name="Custom Name")
        self.assertEqual(action.url, "https://example.com")
        self.assertEqual(action.name, "Custom Name")

    def test_validate(self):
        """Test that validate returns True if the URL is set, False otherwise."""
        action = NavigateAction(url="https://example.com")
        self.assertTrue(action.validate())
        
        action = NavigateAction(url="")
        self.assertFalse(action.validate())

    def test_execute_success(self):
        """Test that execute returns a success result when navigation succeeds."""
        driver = Mock(spec=IWebDriver)
        action = NavigateAction(url="https://example.com")
        
        result = action.execute(driver)
        
        driver.get.assert_called_once_with("https://example.com")
        self.assertTrue(result.is_success())
        self.assertEqual(result.message, "Navigated to https://example.com")

    def test_execute_webdriver_error(self):
        """Test that execute returns a failure result when WebDriverError is raised."""
        driver = Mock(spec=IWebDriver)
        driver.get.side_effect = WebDriverError("Failed to navigate")
        action = NavigateAction(url="https://example.com")
        
        result = action.execute(driver)
        
        driver.get.assert_called_once_with("https://example.com")
        self.assertFalse(result.is_success())
        self.assertEqual(result.message, "WebDriver error navigating to https://example.com: Failed to navigate")

    def test_execute_other_error(self):
        """Test that execute returns a failure result when another exception is raised."""
        driver = Mock(spec=IWebDriver)
        driver.get.side_effect = Exception("Unexpected error")
        action = NavigateAction(url="https://example.com")
        
        result = action.execute(driver)
        
        driver.get.assert_called_once_with("https://example.com")
        self.assertFalse(result.is_success())
        self.assertTrue("Failed to navigate to https://example.com" in result.message)

    def test_to_dict(self):
        """Test that to_dict returns the correct dictionary representation."""
        action = NavigateAction(url="https://example.com", name="Custom Name")
        
        result = action.to_dict()
        
        self.assertEqual(result, {
            "type": "Navigate",
            "name": "Custom Name",
            "url": "https://example.com"
        })

if __name__ == "__main__":
    unittest.main()
