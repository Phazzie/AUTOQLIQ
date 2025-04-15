"""Tests for the ReadAttributeAction class."""

import unittest
from unittest.mock import MagicMock, patch
import logging

from src.core.actions.read_attribute_action import ReadAttributeAction
from src.core.actions.constants import SUPPORTED_LOCATORS
from src.core.interfaces import IWebDriver, ICredentialRepository
from src.core.action_result import ActionResult, ActionStatus
from src.core.exceptions import ValidationError, WebDriverError


class TestReadAttributeAction(unittest.TestCase):
    """Test cases for the ReadAttributeAction class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Capture logs for testing
        self.log_patcher = patch('src.core.actions.read_attribute_action.logger')
        self.mock_logger = self.log_patcher.start()
        
        # Mock objects
        self.mock_driver = MagicMock(spec=IWebDriver)
        self.mock_cred_repo = MagicMock(spec=ICredentialRepository)
        self.mock_element = MagicMock()  # Mock web element
        
        # Valid parameters for testing
        self.valid_params = {
            "locator_type": "id",
            "locator_value": "submit-button",
            "attribute_name": "disabled"
        }
        
        # Configure the mock driver to find an element
        self.mock_driver.find_element.return_value = self.mock_element
        # Configure get_attribute to return a value
        self.mock_driver.get_attribute.return_value = "true"
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.log_patcher.stop()
    
    def test_init_with_valid_parameters(self):
        """Test initialization with valid parameters."""
        action = ReadAttributeAction(
            name="CheckDisabled",
            locator_type=self.valid_params["locator_type"],
            locator_value=self.valid_params["locator_value"],
            attribute_name=self.valid_params["attribute_name"]
        )
        self.assertEqual(action.name, "CheckDisabled")
        self.assertEqual(action.parameters["locator_type"], self.valid_params["locator_type"])
        self.assertEqual(action.parameters["locator_value"], self.valid_params["locator_value"])
        self.assertEqual(action.parameters["attribute_name"], self.valid_params["attribute_name"])
        self.assertEqual(action.action_type, "ReadAttribute")  # Assuming action_type is "ReadAttribute"
    
    def test_validate_parameters_success(self):
        """Test successful parameter validation."""
        action = ReadAttributeAction(
            name="ReadTest",
            locator_type=self.valid_params["locator_type"],
            locator_value=self.valid_params["locator_value"],
            attribute_name=self.valid_params["attribute_name"]
        )
        # Should not raise an exception
        action.validate_parameters()
        self.mock_logger.debug.assert_called_once()
    
    def test_validate_parameters_missing_locator_type(self):
        """Test validation fails with missing locator_type."""
        action = ReadAttributeAction(
            name="ReadTest",
            locator_value=self.valid_params["locator_value"],
            attribute_name=self.valid_params["attribute_name"]
        )
        
        with self.assertRaises(ValidationError) as context:
            action.validate_parameters()
        
        self.assertIn("locator_type", str(context.exception))
    
    def test_validate_parameters_missing_locator_value(self):
        """Test validation fails with missing locator_value."""
        action = ReadAttributeAction(
            name="ReadTest",
            locator_type=self.valid_params["locator_type"],
            attribute_name=self.valid_params["attribute_name"]
        )
        
        with self.assertRaises(ValidationError) as context:
            action.validate_parameters()
        
        self.assertIn("locator_value", str(context.exception))
    
    def test_validate_parameters_missing_attribute_name(self):
        """Test validation fails with missing attribute_name."""
        action = ReadAttributeAction(
            name="ReadTest",
            locator_type=self.valid_params["locator_type"],
            locator_value=self.valid_params["locator_value"]
        )
        
        with self.assertRaises(ValidationError) as context:
            action.validate_parameters()
        
        self.assertIn("attribute_name", str(context.exception))
    
    def test_validate_parameters_invalid_locator_type(self):
        """Test validation fails with invalid locator_type."""
        action = ReadAttributeAction(
            name="ReadTest",
            locator_type="invalid_type",  # Not in SUPPORTED_LOCATORS
            locator_value=self.valid_params["locator_value"],
            attribute_name=self.valid_params["attribute_name"]
        )
        
        with self.assertRaises(ValidationError) as context:
            action.validate_parameters()
        
        self.assertIn("Unsupported locator_type", str(context.exception))
        self.assertIn("SUPPORTED_LOCATORS", str(context.exception))
    
    def test_validate_parameters_non_string_locator_type(self):
        """Test validation fails with non-string locator_type."""
        action = ReadAttributeAction(
            name="ReadTest",
            locator_type=123,  # Not a string
            locator_value=self.valid_params["locator_value"],
            attribute_name=self.valid_params["attribute_name"]
        )
        
        with self.assertRaises(ValidationError) as context:
            action.validate_parameters()
        
        self.assertIn("locator_type", str(context.exception))
        self.assertIn("string expected", str(context.exception))
    
    def test_validate_parameters_empty_attribute_name(self):
        """Test validation fails with empty attribute_name."""
        action = ReadAttributeAction(
            name="ReadTest",
            locator_type=self.valid_params["locator_type"],
            locator_value=self.valid_params["locator_value"],
            attribute_name=""  # Empty string
        )
        
        with self.assertRaises(ValidationError) as context:
            action.validate_parameters()
        
        self.assertIn("attribute_name", str(context.exception))
    
    def test_execute_success(self):
        """Test successful execution of the read attribute action."""
        action = ReadAttributeAction(
            name="ReadDisabled",
            locator_type=self.valid_params["locator_type"],
            locator_value=self.valid_params["locator_value"],
            attribute_name=self.valid_params["attribute_name"]
        )
        
        result = action.execute(self.mock_driver)
        
        self.assertTrue(result.is_success())
        self.assertEqual(result.status, ActionStatus.SUCCESS)
        self.assertIn("read attribute", result.message.lower())
        self.assertEqual(result.data["attribute_value"], "true")
        
        # Verify driver interactions
        self.mock_driver.find_element.assert_called_once_with(
            by=self.valid_params["locator_type"],
            value=self.valid_params["locator_value"]
        )
        self.mock_driver.get_attribute.assert_called_once_with(
            self.mock_element, 
            self.valid_params["attribute_name"]
        )
        self.mock_logger.info.assert_called()
    
    def test_execute_element_not_found(self):
        """Test execution when element is not found."""
        action = ReadAttributeAction(
            name="ReadMissing",
            locator_type=self.valid_params["locator_type"],
            locator_value="nonexistent-element",
            attribute_name=self.valid_params["attribute_name"]
        )
        
        # Configure driver to raise exception on find_element
        self.mock_driver.find_element.side_effect = WebDriverError("Element not found")
        
        result = action.execute(self.mock_driver)
        
        self.assertFalse(result.is_success())
        self.assertEqual(result.status, ActionStatus.FAILURE)
        self.assertIn("failed", result.message.lower())
        self.assertIn("not found", result.message.lower())
        
        self.mock_driver.find_element.assert_called_once()
        self.mock_driver.get_attribute.assert_not_called()
        self.mock_logger.error.assert_called()
    
    def test_execute_attribute_error(self):
        """Test execution when attribute access causes an error."""
        action = ReadAttributeAction(
            name="ReadInvalidAttr",
            locator_type=self.valid_params["locator_type"],
            locator_value=self.valid_params["locator_value"],
            attribute_name="nonexistent_attr"
        )
        
        # Configure driver to find element but raise on get_attribute
        self.mock_driver.find_element.return_value = self.mock_element
        self.mock_driver.get_attribute.side_effect = WebDriverError("Attribute not found")
        
        result = action.execute(self.mock_driver)
        
        self.assertFalse(result.is_success())
        self.assertEqual(result.status, ActionStatus.FAILURE)
        self.assertIn("failed", result.message.lower())
        self.assertIn("attribute", result.message.lower())
        
        self.mock_driver.find_element.assert_called_once()
        self.mock_driver.get_attribute.assert_called_once()
        self.mock_logger.error.assert_called()
    
    def test_execute_unexpected_error(self):
        """Test execution when an unexpected error occurs."""
        action = ReadAttributeAction(
            name="ReadError",
            locator_type=self.valid_params["locator_type"],
            locator_value=self.valid_params["locator_value"],
            attribute_name=self.valid_params["attribute_name"]
        )
        
        # Configure driver to raise unexpected error
        self.mock_driver.find_element.side_effect = RuntimeError("Unexpected error")
        
        result = action.execute(self.mock_driver)
        
        self.assertFalse(result.is_success())
        self.assertEqual(result.status, ActionStatus.FAILURE)
        self.assertIn("unexpected", result.message.lower())
        
        self.mock_driver.find_element.assert_called_once()
        self.mock_driver.get_attribute.assert_not_called()
        self.mock_logger.error.assert_called()
    
    def test_execute_null_attribute_value(self):
        """Test execution when attribute value is None."""
        action = ReadAttributeAction(
            name="ReadNullAttr",
            locator_type=self.valid_params["locator_type"],
            locator_value=self.valid_params["locator_value"],
            attribute_name=self.valid_params["attribute_name"]
        )
        
        # Configure get_attribute to return None
        self.mock_driver.get_attribute.return_value = None
        
        result = action.execute(self.mock_driver)
        
        self.assertTrue(result.is_success())
        self.assertEqual(result.status, ActionStatus.SUCCESS)
        self.assertIn("read attribute", result.message.lower())
        self.assertIsNone(result.data["attribute_value"])
        
        self.mock_driver.find_element.assert_called_once()
        self.mock_driver.get_attribute.assert_called_once()
        self.mock_logger.info.assert_called()
    
    def test_to_dict_serialization(self):
        """Test serialization to dictionary includes all parameters."""
        action = ReadAttributeAction(
            name="SerializeTest",
            locator_type=self.valid_params["locator_type"],
            locator_value=self.valid_params["locator_value"],
            attribute_name=self.valid_params["attribute_name"]
        )
        
        result = action.to_dict()
        
        self.assertEqual(result["type"], "ReadAttribute")  # Assuming action_type is "ReadAttribute"
        self.assertEqual(result["name"], "SerializeTest")
        self.assertEqual(result["locator_type"], self.valid_params["locator_type"])
        self.assertEqual(result["locator_value"], self.valid_params["locator_value"])
        self.assertEqual(result["attribute_name"], self.valid_params["attribute_name"])


if __name__ == "__main__":
    unittest.main()
