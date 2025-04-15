"""Tests for the ClickAction class."""

import unittest
from unittest.mock import MagicMock, patch
import logging

from src.core.actions.click_action import ClickAction
from src.core.actions.constants import SUPPORTED_LOCATORS
from src.core.interfaces import IWebDriver, ICredentialRepository
from src.core.action_result import ActionResult, ActionStatus
from src.core.exceptions import ValidationError, WebDriverError


class TestClickAction(unittest.TestCase):
    """Test cases for the ClickAction class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Capture logs for testing
        self.log_patcher = patch('src.core.actions.click_action.logger')
        self.mock_logger = self.log_patcher.start()
        
        # Mock objects
        self.mock_driver = MagicMock(spec=IWebDriver)
        self.mock_cred_repo = MagicMock(spec=ICredentialRepository)
        self.mock_element = MagicMock()  # Mock web element
        
        # Valid parameters for testing
        self.valid_params = {
            "locator_type": "id",
            "locator_value": "submit-button"
        }
        
        # Configure the mock driver to find an element
        self.mock_driver.find_element.return_value = self.mock_element
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.log_patcher.stop()
    
    def test_init_with_valid_parameters(self):
        """Test initialization with valid parameters."""
        action = ClickAction(
            name="ClickSubmit",
            locator_type=self.valid_params["locator_type"],
            locator_value=self.valid_params["locator_value"]
        )
        self.assertEqual(action.name, "ClickSubmit")
        self.assertEqual(action.parameters, self.valid_params)
        self.assertEqual(action.action_type, "Click")  # Assuming action_type is "Click"
    
    def test_validate_parameters_success(self):
        """Test successful parameter validation."""
        action = ClickAction(
            name="TestClick",
            locator_type=self.valid_params["locator_type"],
            locator_value=self.valid_params["locator_value"]
        )
        self.assertTrue(action.validate_parameters())
        self.mock_logger.debug.assert_called_once()
    
    def test_validate_parameters_missing_locator_type(self):
        """Test validation fails with missing locator_type."""
        action = ClickAction(
            name="TestClick",
            locator_value=self.valid_params["locator_value"]
        )
        
        with self.assertRaises(ValidationError) as context:
            action.validate_parameters()
        
        self.assertIn("locator_type", str(context.exception))
    
    def test_validate_parameters_missing_locator_value(self):
        """Test validation fails with missing locator_value."""
        action = ClickAction(
            name="TestClick",
            locator_type=self.valid_params["locator_type"]
        )
        
        with self.assertRaises(ValidationError) as context:
            action.validate_parameters()
        
        self.assertIn("locator_value", str(context.exception))
    
    def test_validate_parameters_invalid_locator_type(self):
        """Test validation fails with invalid locator_type."""
        action = ClickAction(
            name="TestClick",
            locator_type="invalid_type",  # Not in SUPPORTED_LOCATORS
            locator_value=self.valid_params["locator_value"]
        )
        
        with self.assertRaises(ValidationError) as context:
            action.validate_parameters()
        
        self.assertIn("Unsupported locator_type", str(context.exception))
        self.assertIn("SUPPORTED_LOCATORS", str(context.exception))
    
    def test_validate_parameters_non_string_locator_type(self):
        """Test validation fails with non-string locator_type."""
        action = ClickAction(
            name="TestClick",
            locator_type=123,  # Not a string
            locator_value=self.valid_params["locator_value"]
        )
        
        with self.assertRaises(ValidationError) as context:
            action.validate_parameters()
        
        self.assertIn("locator_type", str(context.exception))
        self.assertIn("string expected", str(context.exception))
    
    def test_validate_parameters_non_string_locator_value(self):
        """Test validation fails with non-string locator_value."""
        action = ClickAction(
            name="TestClick",
            locator_type=self.valid_params["locator_type"],
            locator_value=456  # Not a string
        )
        
        with self.assertRaises(ValidationError) as context:
            action.validate_parameters()
        
        self.assertIn("locator_value", str(context.exception))
        self.assertIn("string expected", str(context.exception))
    
    def test_execute_success(self):
        """Test successful execution of the click action."""
        action = ClickAction(
            name="ClickSubmit",
            locator_type=self.valid_params["locator_type"],
            locator_value=self.valid_params["locator_value"]
        )
        
        result = action.execute(self.mock_driver)
        
        self.assertTrue(result.is_success())
        self.assertEqual(result.status, ActionStatus.SUCCESS)
        self.assertIn("clicked", result.message.lower())
        
        # Verify driver interactions
        self.mock_driver.find_element.assert_called_once_with(
            by=self.valid_params["locator_type"],
            value=self.valid_params["locator_value"]
        )
        self.mock_driver.click.assert_called_once_with(self.mock_element)
        self.mock_logger.info.assert_called()
    
    def test_execute_element_not_found(self):
        """Test execution when element is not found."""
        action = ClickAction(
            name="ClickMissing",
            locator_type=self.valid_params["locator_type"],
            locator_value="nonexistent-element"
        )
        
        # Configure driver to raise exception on find_element
        self.mock_driver.find_element.side_effect = WebDriverError("Element not found")
        
        result = action.execute(self.mock_driver)
        
        self.assertFalse(result.is_success())
        self.assertEqual(result.status, ActionStatus.FAILURE)
        self.assertIn("failed", result.message.lower())
        self.assertIn("not found", result.message.lower())
        
        self.mock_driver.find_element.assert_called_once()
        self.mock_driver.click.assert_not_called()
        self.mock_logger.error.assert_called()
    
    def test_execute_element_not_clickable(self):
        """Test execution when element is found but not clickable."""
        action = ClickAction(
            name="ClickDisabled",
            locator_type=self.valid_params["locator_type"],
            locator_value=self.valid_params["locator_value"]
        )
        
        # Configure driver to find element but raise on click
        self.mock_driver.find_element.return_value = self.mock_element
        self.mock_driver.click.side_effect = WebDriverError("Element not clickable")
        
        result = action.execute(self.mock_driver)
        
        self.assertFalse(result.is_success())
        self.assertEqual(result.status, ActionStatus.FAILURE)
        self.assertIn("failed", result.message.lower())
        self.assertIn("not clickable", result.message.lower())
        
        self.mock_driver.find_element.assert_called_once()
        self.mock_driver.click.assert_called_once()
        self.mock_logger.error.assert_called()
    
    def test_execute_unexpected_error(self):
        """Test execution when an unexpected error occurs."""
        action = ClickAction(
            name="ClickError",
            locator_type=self.valid_params["locator_type"],
            locator_value=self.valid_params["locator_value"]
        )
        
        # Configure driver to raise unexpected error
        self.mock_driver.find_element.side_effect = RuntimeError("Unexpected error")
        
        result = action.execute(self.mock_driver)
        
        self.assertFalse(result.is_success())
        self.assertEqual(result.status, ActionStatus.FAILURE)
        self.assertIn("unexpected", result.message.lower())
        
        self.mock_driver.find_element.assert_called_once()
        self.mock_driver.click.assert_not_called()
        self.mock_logger.error.assert_called()
    
    def test_to_dict_serialization(self):
        """Test serialization to dictionary includes parameters."""
        action = ClickAction(
            name="SerializeTest",
            locator_type=self.valid_params["locator_type"],
            locator_value=self.valid_params["locator_value"]
        )
        
        result = action.to_dict()
        
        self.assertEqual(result["type"], "Click")  # Assuming action_type is "Click"
        self.assertEqual(result["name"], "SerializeTest")
        self.assertEqual(result["locator_type"], self.valid_params["locator_type"])
        self.assertEqual(result["locator_value"], self.valid_params["locator_value"])


if __name__ == "__main__":
    unittest.main()
