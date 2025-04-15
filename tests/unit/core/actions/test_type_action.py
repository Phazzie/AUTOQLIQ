"""Tests for the TypeAction class."""

import unittest
from unittest.mock import MagicMock, patch
import logging

from src.core.actions.type_action import TypeAction
from src.core.actions.constants import SUPPORTED_LOCATORS
from src.core.interfaces import IWebDriver, ICredentialRepository
from src.core.action_result import ActionResult, ActionStatus
from src.core.exceptions import ValidationError, WebDriverError


class TestTypeAction(unittest.TestCase):
    """Test cases for the TypeAction class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Capture logs for testing
        self.log_patcher = patch('src.core.actions.type_action.logger')
        self.mock_logger = self.log_patcher.start()
        
        # Mock objects
        self.mock_driver = MagicMock(spec=IWebDriver)
        self.mock_cred_repo = MagicMock(spec=ICredentialRepository)
        self.mock_element = MagicMock()  # Mock web element
        
        # Valid parameters for testing
        self.valid_params = {
            "locator_type": "id",
            "locator_value": "username-input",
            "text": "test_user@example.com",
            "clear_first": True
        }
        
        # Configure the mock driver to find an element
        self.mock_driver.find_element.return_value = self.mock_element
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.log_patcher.stop()
    
    def test_init_with_valid_parameters(self):
        """Test initialization with valid parameters."""
        action = TypeAction(
            name="TypeUsername",
            locator_type=self.valid_params["locator_type"],
            locator_value=self.valid_params["locator_value"],
            text=self.valid_params["text"],
            clear_first=self.valid_params["clear_first"]
        )
        self.assertEqual(action.name, "TypeUsername")
        self.assertEqual(action.parameters["locator_type"], self.valid_params["locator_type"])
        self.assertEqual(action.parameters["locator_value"], self.valid_params["locator_value"])
        self.assertEqual(action.parameters["text"], self.valid_params["text"])
        self.assertEqual(action.parameters["clear_first"], self.valid_params["clear_first"])
        self.assertEqual(action.action_type, "Type")  # Assuming action_type is "Type"
    
    def test_init_with_default_clear_first(self):
        """Test initialization with default clear_first parameter."""
        action = TypeAction(
            name="TypeUsername",
            locator_type=self.valid_params["locator_type"],
            locator_value=self.valid_params["locator_value"],
            text=self.valid_params["text"]
        )
        self.assertEqual(action.parameters["clear_first"], True)  # Default should be True
    
    def test_validate_parameters_success(self):
        """Test successful parameter validation."""
        action = TypeAction(
            name="TypeTest",
            locator_type=self.valid_params["locator_type"],
            locator_value=self.valid_params["locator_value"],
            text=self.valid_params["text"],
            clear_first=self.valid_params["clear_first"]
        )
        # Should not raise an exception
        action.validate_parameters()
        self.mock_logger.debug.assert_called_once()
    
    def test_validate_parameters_empty_text_allowed(self):
        """Test validation allows empty text string."""
        action = TypeAction(
            name="TypeEmpty",
            locator_type=self.valid_params["locator_type"],
            locator_value=self.valid_params["locator_value"],
            text="",  # Empty string is allowed
            clear_first=self.valid_params["clear_first"]
        )
        # Should not raise an exception
        action.validate_parameters()
        self.mock_logger.debug.assert_called_once()
    
    def test_validate_parameters_missing_locator_type(self):
        """Test validation fails with missing locator_type."""
        action = TypeAction(
            name="TypeTest",
            locator_value=self.valid_params["locator_value"],
            text=self.valid_params["text"]
        )
        
        with self.assertRaises(ValidationError) as context:
            action.validate_parameters()
        
        self.assertIn("locator_type", str(context.exception))
    
    def test_validate_parameters_missing_locator_value(self):
        """Test validation fails with missing locator_value."""
        action = TypeAction(
            name="TypeTest",
            locator_type=self.valid_params["locator_type"],
            text=self.valid_params["text"]
        )
        
        with self.assertRaises(ValidationError) as context:
            action.validate_parameters()
        
        self.assertIn("locator_value", str(context.exception))
    
    def test_validate_parameters_missing_text(self):
        """Test validation fails with missing text."""
        action = TypeAction(
            name="TypeTest",
            locator_type=self.valid_params["locator_type"],
            locator_value=self.valid_params["locator_value"]
        )
        
        with self.assertRaises(ValidationError) as context:
            action.validate_parameters()
        
        self.assertIn("text", str(context.exception))
    
    def test_validate_parameters_invalid_locator_type(self):
        """Test validation fails with invalid locator_type."""
        action = TypeAction(
            name="TypeTest",
            locator_type="invalid_type",  # Not in SUPPORTED_LOCATORS
            locator_value=self.valid_params["locator_value"],
            text=self.valid_params["text"]
        )
        
        with self.assertRaises(ValidationError) as context:
            action.validate_parameters()
        
        self.assertIn("Unsupported locator_type", str(context.exception))
        self.assertIn("SUPPORTED_LOCATORS", str(context.exception))
    
    def test_validate_parameters_invalid_clear_first_type(self):
        """Test validation fails with non-boolean clear_first."""
        action = TypeAction(
            name="TypeTest",
            locator_type=self.valid_params["locator_type"],
            locator_value=self.valid_params["locator_value"],
            text=self.valid_params["text"],
            clear_first="yes"  # Not a boolean
        )
        
        with self.assertRaises(ValidationError) as context:
            action.validate_parameters()
        
        self.assertIn("clear_first", str(context.exception))
        self.assertIn("boolean", str(context.exception))
    
    def test_execute_success_with_clear(self):
        """Test successful execution of the type action with clearing."""
        action = TypeAction(
            name="TypeEmail",
            locator_type=self.valid_params["locator_type"],
            locator_value=self.valid_params["locator_value"],
            text=self.valid_params["text"],
            clear_first=True
        )
        
        result = action.execute(self.mock_driver)
        
        self.assertTrue(result.is_success())
        self.assertEqual(result.status, ActionStatus.SUCCESS)
        self.assertIn("typed", result.message.lower())
        
        # Verify driver interactions
        self.mock_driver.find_element.assert_called_once_with(
            by=self.valid_params["locator_type"],
            value=self.valid_params["locator_value"]
        )
        self.mock_driver.clear.assert_called_once_with(self.mock_element)
        self.mock_driver.type_text.assert_called_once_with(
            self.mock_element, 
            self.valid_params["text"]
        )
        self.mock_logger.info.assert_called()
    
    def test_execute_success_without_clear(self):
        """Test successful execution of the type action without clearing."""
        action = TypeAction(
            name="TypeAppend",
            locator_type=self.valid_params["locator_type"],
            locator_value=self.valid_params["locator_value"],
            text=self.valid_params["text"],
            clear_first=False
        )
        
        result = action.execute(self.mock_driver)
        
        self.assertTrue(result.is_success())
        self.assertEqual(result.status, ActionStatus.SUCCESS)
        self.assertIn("typed", result.message.lower())
        
        # Verify driver interactions
        self.mock_driver.find_element.assert_called_once_with(
            by=self.valid_params["locator_type"],
            value=self.valid_params["locator_value"]
        )
        self.mock_driver.clear.assert_not_called()  # Should not clear
        self.mock_driver.type_text.assert_called_once_with(
            self.mock_element, 
            self.valid_params["text"]
        )
        self.mock_logger.info.assert_called()
    
    def test_execute_element_not_found(self):
        """Test execution when element is not found."""
        action = TypeAction(
            name="TypeMissing",
            locator_type=self.valid_params["locator_type"],
            locator_value="nonexistent-element",
            text=self.valid_params["text"]
        )
        
        # Configure driver to raise exception on find_element
        self.mock_driver.find_element.side_effect = WebDriverError("Element not found")
        
        result = action.execute(self.mock_driver)
        
        self.assertFalse(result.is_success())
        self.assertEqual(result.status, ActionStatus.FAILURE)
        self.assertIn("failed", result.message.lower())
        self.assertIn("not found", result.message.lower())
        
        self.mock_driver.find_element.assert_called_once()
        self.mock_driver.type_text.assert_not_called()
        self.mock_logger.error.assert_called()
    
    def test_execute_element_not_interactable(self):
        """Test execution when element is found but not interactable."""
        action = TypeAction(
            name="TypeDisabled",
            locator_type=self.valid_params["locator_type"],
            locator_value=self.valid_params["locator_value"],
            text=self.valid_params["text"]
        )
        
        # Configure driver to find element but raise on type_text
        self.mock_driver.find_element.return_value = self.mock_element
        self.mock_driver.type_text.side_effect = WebDriverError("Element not interactable")
        
        result = action.execute(self.mock_driver)
        
        self.assertFalse(result.is_success())
        self.assertEqual(result.status, ActionStatus.FAILURE)
        self.assertIn("failed", result.message.lower())
        self.assertIn("not interactable", result.message.lower())
        
        self.mock_driver.find_element.assert_called_once()
        self.mock_driver.type_text.assert_called_once()
        self.mock_logger.error.assert_called()
    
    def test_execute_unexpected_error(self):
        """Test execution when an unexpected error occurs."""
        action = TypeAction(
            name="TypeError",
            locator_type=self.valid_params["locator_type"],
            locator_value=self.valid_params["locator_value"],
            text=self.valid_params["text"]
        )
        
        # Configure driver to raise unexpected error
        self.mock_driver.find_element.side_effect = RuntimeError("Unexpected error")
        
        result = action.execute(self.mock_driver)
        
        self.assertFalse(result.is_success())
        self.assertEqual(result.status, ActionStatus.FAILURE)
        self.assertIn("unexpected", result.message.lower())
        
        self.mock_driver.find_element.assert_called_once()
        self.mock_driver.type_text.assert_not_called()
        self.mock_logger.error.assert_called()
    
    def test_to_dict_serialization(self):
        """Test serialization to dictionary includes all parameters."""
        action = TypeAction(
            name="SerializeTest",
            locator_type=self.valid_params["locator_type"],
            locator_value=self.valid_params["locator_value"],
            text=self.valid_params["text"],
            clear_first=False  # Non-default value
        )
        
        result = action.to_dict()
        
        self.assertEqual(result["type"], "Type")  # Assuming action_type is "Type"
        self.assertEqual(result["name"], "SerializeTest")
        self.assertEqual(result["locator_type"], self.valid_params["locator_type"])
        self.assertEqual(result["locator_value"], self.valid_params["locator_value"])
        self.assertEqual(result["text"], self.valid_params["text"])
        self.assertEqual(result["clear_first"], False)


if __name__ == "__main__":
    unittest.main()
