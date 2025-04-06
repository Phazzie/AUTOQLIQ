"""Tests for the utility actions module."""
import unittest
from unittest.mock import Mock, patch

from src.core.interfaces import IWebDriver
from src.core.action_result import ActionResult
from src.core.exceptions import WebDriverError, ActionError
from src.core.actions.utility import WaitAction, ScreenshotAction

class TestWaitAction(unittest.TestCase):
    """Test cases for the WaitAction class."""

    def test_init(self):
        """Test that WaitAction can be initialized with the required parameters."""
        action = WaitAction(duration_seconds=5)
        self.assertEqual(action.duration_seconds, 5)
        self.assertEqual(action.name, "Wait")
        
        action = WaitAction(duration_seconds=10, name="Custom Name")
        self.assertEqual(action.duration_seconds, 10)
        self.assertEqual(action.name, "Custom Name")

    def test_validate(self):
        """Test that validate returns True if duration_seconds is a positive integer, False otherwise."""
        action = WaitAction(duration_seconds=5)
        self.assertTrue(action.validate())
        
        action = WaitAction(duration_seconds=0)
        self.assertFalse(action.validate())
        
        action = WaitAction(duration_seconds=-1)
        self.assertFalse(action.validate())

    @patch("time.sleep")
    def test_execute_success(self, mock_sleep):
        """Test that execute returns a success result when waiting succeeds."""
        driver = Mock(spec=IWebDriver)
        action = WaitAction(duration_seconds=5)
        
        result = action.execute(driver)
        
        mock_sleep.assert_called_once_with(5)
        self.assertTrue(result.is_success())
        self.assertEqual(result.message, "Waited for 5 seconds")

    @patch("time.sleep")
    def test_execute_type_error(self, mock_sleep):
        """Test that execute returns a failure result when TypeError is raised."""
        driver = Mock(spec=IWebDriver)
        mock_sleep.side_effect = TypeError("Invalid duration")
        action = WaitAction(duration_seconds=5)
        
        result = action.execute(driver)
        
        mock_sleep.assert_called_once_with(5)
        self.assertFalse(result.is_success())
        self.assertEqual(result.message, "Invalid duration type: Invalid duration")

    @patch("time.sleep")
    def test_execute_other_error(self, mock_sleep):
        """Test that execute returns a failure result when another exception is raised."""
        driver = Mock(spec=IWebDriver)
        mock_sleep.side_effect = Exception("Unexpected error")
        action = WaitAction(duration_seconds=5)
        
        result = action.execute(driver)
        
        mock_sleep.assert_called_once_with(5)
        self.assertFalse(result.is_success())
        self.assertTrue("Failed to wait for 5 seconds" in result.message)

    def test_to_dict(self):
        """Test that to_dict returns the correct dictionary representation."""
        action = WaitAction(duration_seconds=5, name="Custom Name")
        
        result = action.to_dict()
        
        self.assertEqual(result, {
            "type": "Wait",
            "name": "Custom Name",
            "duration_seconds": 5
        })

class TestScreenshotAction(unittest.TestCase):
    """Test cases for the ScreenshotAction class."""

    def test_init(self):
        """Test that ScreenshotAction can be initialized with the required parameters."""
        action = ScreenshotAction(file_path="screenshot.png")
        self.assertEqual(action.file_path, "screenshot.png")
        self.assertEqual(action.name, "Screenshot")
        
        action = ScreenshotAction(file_path="custom.png", name="Custom Name")
        self.assertEqual(action.file_path, "custom.png")
        self.assertEqual(action.name, "Custom Name")

    def test_validate(self):
        """Test that validate returns True if file_path is set, False otherwise."""
        action = ScreenshotAction(file_path="screenshot.png")
        self.assertTrue(action.validate())
        
        action = ScreenshotAction(file_path="")
        self.assertFalse(action.validate())

    def test_execute_success(self):
        """Test that execute returns a success result when taking a screenshot succeeds."""
        driver = Mock(spec=IWebDriver)
        action = ScreenshotAction(file_path="screenshot.png")
        
        result = action.execute(driver)
        
        driver.take_screenshot.assert_called_once_with("screenshot.png")
        self.assertTrue(result.is_success())
        self.assertEqual(result.message, "Took screenshot and saved to screenshot.png")

    def test_execute_webdriver_error(self):
        """Test that execute returns a failure result when WebDriverError is raised."""
        driver = Mock(spec=IWebDriver)
        driver.take_screenshot.side_effect = WebDriverError("Failed to take screenshot")
        action = ScreenshotAction(file_path="screenshot.png")
        
        result = action.execute(driver)
        
        driver.take_screenshot.assert_called_once_with("screenshot.png")
        self.assertFalse(result.is_success())
        self.assertEqual(result.message, "WebDriver error taking screenshot: Failed to take screenshot")

    def test_execute_io_error(self):
        """Test that execute returns a failure result when IOError is raised."""
        driver = Mock(spec=IWebDriver)
        driver.take_screenshot.side_effect = IOError("Failed to save file")
        action = ScreenshotAction(file_path="screenshot.png")
        
        result = action.execute(driver)
        
        driver.take_screenshot.assert_called_once_with("screenshot.png")
        self.assertFalse(result.is_success())
        self.assertEqual(result.message, "File error saving screenshot to screenshot.png: Failed to save file")

    def test_execute_other_error(self):
        """Test that execute returns a failure result when another exception is raised."""
        driver = Mock(spec=IWebDriver)
        driver.take_screenshot.side_effect = Exception("Unexpected error")
        action = ScreenshotAction(file_path="screenshot.png")
        
        result = action.execute(driver)
        
        driver.take_screenshot.assert_called_once_with("screenshot.png")
        self.assertFalse(result.is_success())
        self.assertTrue("Failed to take screenshot" in result.message)

    def test_to_dict(self):
        """Test that to_dict returns the correct dictionary representation."""
        action = ScreenshotAction(file_path="screenshot.png", name="Custom Name")
        
        result = action.to_dict()
        
        self.assertEqual(result, {
            "type": "Screenshot",
            "name": "Custom Name",
            "file_path": "screenshot.png"
        })

if __name__ == "__main__":
    unittest.main()
