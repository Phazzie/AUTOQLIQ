"""Tests for the ClickAction class."""

import unittest
from unittest.mock import MagicMock, patch
import logging
import pytest

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

from src.core.actions.interaction import ClickAction
from src.core.exceptions import ValidationError, WebDriverError
from src.core.action_result import ActionResult

class DummyDriver:
    def __init__(self):
        self.clicked = None
    def click(self, selector: str):
        self.clicked = selector

class ErrorDriver:
    def click(self, selector: str):
        raise WebDriverError("click failed")


def test_init_empty_selector_raises_validation_error():
    with pytest.raises(ValidationError):
        ClickAction("", name="BadClick")


def test_execute_success_calls_driver_and_returns_success():
    driver = DummyDriver()
    action = ClickAction("button#submit", name="TestClick")
    result = action.execute(driver)
    assert isinstance(result, ActionResult)
    assert result.is_success()
    assert driver.clicked == "button#submit"


def test_execute_driver_error_returns_failure():
    driver = ErrorDriver()
    action = ClickAction("button#submit", name="TestClick")
    result = action.execute(driver)
    assert not result.is_success()
    assert "click failed" in result.message


def test_to_dict_serializes_selector_and_metadata():
    action = ClickAction("button", name="ClickTest")
    data = action.to_dict()
    assert data["selector"] == "button"
    assert data["type"] == action.action_type
    assert data["name"] == action.name

import pytest
from unittest.mock import Mock, call
from src.core.actions.click_action import ClickAction
from src.core.action_result import ActionResult, ActionStatus
from src.core.exceptions import ValidationError, ActionError
from src.core.interfaces import IWebDriver

@pytest.fixture
def driver_stub():
    return Mock(spec=IWebDriver)

def test_click_action_success(driver_stub):
    selector = "#myButton"
    action = ClickAction(name="Click Button", parameters={
        "locator_type": "css selector",
        "locator_value": selector
    })
    
    # Mock the find_element to return a mock element with a click method
    mock_element = Mock()
    driver_stub.find_element.return_value = mock_element

    result = action.execute(driver_stub)

    driver_stub.find_element.assert_called_once_with(selector)
    mock_element.click.assert_called_once()
    assert result.status == ActionStatus.SUCCESS
    assert result.message == f"Clicked element located by css selector: {selector}"

def test_click_action_validation_fails_on_missing_locator_type():
    with pytest.raises(ValidationError) as excinfo:
        ClickAction(name="Click Button", parameters={
            "locator_value": "#myButton"
        })
    assert "Missing or invalid 'locator_type' parameter" in str(excinfo.value)

def test_click_action_validation_fails_on_unsupported_locator_type():
    with pytest.raises(ValidationError) as excinfo:
        ClickAction(name="Click Button", parameters={
            "locator_type": "invalid_type",
            "locator_value": "#myButton"
        })
    assert "Unsupported locator_type: 'invalid_type'" in str(excinfo.value)

def test_click_action_validation_fails_on_missing_locator_value():
    with pytest.raises(ValidationError) as excinfo:
        ClickAction(name="Click Button", parameters={
            "locator_type": "css selector"
        })
    assert "Missing or invalid 'locator_value' parameter" in str(excinfo.value)

def test_click_action_execution_fails_if_element_not_found(driver_stub):
    selector = "#nonExistentButton"
    action = ClickAction(name="Click Button", parameters={
        "locator_type": "css selector",
        "locator_value": selector
    })
    
    # Configure find_element to return None or raise an error if your driver does
    driver_stub.find_element.return_value = None # Assuming find_element returns None if not found

    result = action.execute(driver_stub)

    driver_stub.find_element.assert_called_once_with(selector)
    # Ensure click was NOT called on the mock element
    # Note: This check depends on how your mock driver handles find_element returning None
    # If find_element raises an exception, the test_click_action_execution_fails_on_webdriver_error would cover it.
    # If it returns None, you might need a more sophisticated mock or check for the absence of calls.
    # For this example, we'll assume returning None is the behavior and check the result.

    assert result.status == ActionStatus.FAILURE
    assert f"Element not found using css selector: {selector}" in result.message

def test_click_action_execution_fails_on_webdriver_error(driver_stub):
    selector = "#myButton"
    action = ClickAction(name="Click Button", parameters={
        "locator_type": "css selector",
        "locator_value": selector
    })
    
    driver_stub.find_element.side_effect = Exception("Simulated WebDriver error")

    result = action.execute(driver_stub)

    driver_stub.find_element.assert_called_once_with(selector)
    assert result.status == ActionStatus.FAILURE
    assert "Simulated WebDriver error" in result.message

def test_click_action_to_dict():
    action = ClickAction(name="Submit", parameters={
        "locator_type": "xpath",
        "locator_value": "//button[@type='submit']"
    })
    expected_dict = {
        "type": "Click",
        "name": "Submit",
        "locator_type": "xpath",
        "locator_value": "//button[@type='submit']"
    }
    assert action.to_dict() == expected_dict

def test_click_action_default_name():
    action = ClickAction(parameters={
        "locator_type": "css selector",
        "locator_value": ".some-class"
    })
    assert action.name == "Click"
