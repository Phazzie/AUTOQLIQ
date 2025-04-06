"""Tests for the interaction actions module."""
import unittest
from unittest.mock import Mock

from src.core.interfaces import IWebDriver, ICredentialRepository
from src.core.action_result import ActionResult
from src.core.exceptions import WebDriverError, ActionError, CredentialError
from src.core.actions.interaction import ClickAction, TypeAction

class TestClickAction(unittest.TestCase):
    """Test cases for the ClickAction class."""

    def test_init(self):
        """Test that ClickAction can be initialized with the required parameters."""
        action = ClickAction(selector="#button")
        self.assertEqual(action.selector, "#button")
        self.assertEqual(action.name, "Click")
        self.assertIsNone(action.check_success_selector)
        self.assertIsNone(action.check_failure_selector)
        
        action = ClickAction(
            selector="#button",
            name="Custom Name",
            check_success_selector="#success",
            check_failure_selector="#failure"
        )
        self.assertEqual(action.selector, "#button")
        self.assertEqual(action.name, "Custom Name")
        self.assertEqual(action.check_success_selector, "#success")
        self.assertEqual(action.check_failure_selector, "#failure")

    def test_validate(self):
        """Test that validate returns True if the selector is set, False otherwise."""
        action = ClickAction(selector="#button")
        self.assertTrue(action.validate())
        
        action = ClickAction(selector="")
        self.assertFalse(action.validate())

    def test_execute_success(self):
        """Test that execute returns a success result when click succeeds."""
        driver = Mock(spec=IWebDriver)
        action = ClickAction(selector="#button")
        
        result = action.execute(driver)
        
        driver.click_element.assert_called_once_with("#button")
        self.assertTrue(result.is_success())
        self.assertEqual(result.message, "Clicked element #button")

    def test_execute_with_success_check_success(self):
        """Test that execute returns a success result when click succeeds and success element is present."""
        driver = Mock(spec=IWebDriver)
        driver.is_element_present.return_value = True
        action = ClickAction(selector="#button", check_success_selector="#success")
        
        result = action.execute(driver)
        
        driver.click_element.assert_called_once_with("#button")
        driver.is_element_present.assert_called_once_with("#success")
        self.assertTrue(result.is_success())
        self.assertEqual(result.message, "Clicked element #button")

    def test_execute_with_success_check_failure(self):
        """Test that execute returns a failure result when click succeeds but success element is not present."""
        driver = Mock(spec=IWebDriver)
        driver.is_element_present.return_value = False
        action = ClickAction(selector="#button", check_success_selector="#success")
        
        result = action.execute(driver)
        
        driver.click_element.assert_called_once_with("#button")
        driver.is_element_present.assert_called_once_with("#success")
        self.assertFalse(result.is_success())
        self.assertEqual(result.message, "Login failed due to absence of success element.")

    def test_execute_with_failure_check(self):
        """Test that execute returns a failure result when click succeeds but failure element is present."""
        driver = Mock(spec=IWebDriver)
        driver.is_element_present.side_effect = [False, True]  # First call for success, second for failure
        action = ClickAction(
            selector="#button",
            check_success_selector="#success",
            check_failure_selector="#failure"
        )
        
        result = action.execute(driver)
        
        driver.click_element.assert_called_once_with("#button")
        driver.is_element_present.assert_any_call("#success")
        driver.is_element_present.assert_any_call("#failure")
        self.assertFalse(result.is_success())
        self.assertEqual(result.message, "Login failed due to presence of failure element.")

    def test_execute_webdriver_error(self):
        """Test that execute returns a failure result when WebDriverError is raised."""
        driver = Mock(spec=IWebDriver)
        driver.click_element.side_effect = WebDriverError("Failed to click")
        action = ClickAction(selector="#button")
        
        result = action.execute(driver)
        
        driver.click_element.assert_called_once_with("#button")
        self.assertFalse(result.is_success())
        self.assertEqual(result.message, "WebDriver error clicking element #button: Failed to click")

    def test_execute_other_error(self):
        """Test that execute returns a failure result when another exception is raised."""
        driver = Mock(spec=IWebDriver)
        driver.click_element.side_effect = Exception("Unexpected error")
        action = ClickAction(selector="#button")
        
        result = action.execute(driver)
        
        driver.click_element.assert_called_once_with("#button")
        self.assertFalse(result.is_success())
        self.assertTrue("Failed to click element #button" in result.message)

    def test_to_dict(self):
        """Test that to_dict returns the correct dictionary representation."""
        action = ClickAction(
            selector="#button",
            name="Custom Name",
            check_success_selector="#success",
            check_failure_selector="#failure"
        )
        
        result = action.to_dict()
        
        self.assertEqual(result, {
            "type": "Click",
            "name": "Custom Name",
            "selector": "#button",
            "check_success_selector": "#success",
            "check_failure_selector": "#failure"
        })

class TestTypeAction(unittest.TestCase):
    """Test cases for the TypeAction class."""

    def test_init(self):
        """Test that TypeAction can be initialized with the required parameters."""
        action = TypeAction(selector="#input", value_type="text", value_key="test")
        self.assertEqual(action.selector, "#input")
        self.assertEqual(action.value_type, "text")
        self.assertEqual(action.value_key, "test")
        self.assertEqual(action.name, "Type")
        self.assertIsNone(action.credential_repository)
        
        repo = Mock(spec=ICredentialRepository)
        action = TypeAction(
            selector="#input",
            value_type="credential",
            value_key="test.password",
            name="Custom Name",
            credential_repository=repo
        )
        self.assertEqual(action.selector, "#input")
        self.assertEqual(action.value_type, "credential")
        self.assertEqual(action.value_key, "test.password")
        self.assertEqual(action.name, "Custom Name")
        self.assertEqual(action.credential_repository, repo)

    def test_validate(self):
        """Test that validate returns True if all required fields are set, False otherwise."""
        action = TypeAction(selector="#input", value_type="text", value_key="test")
        self.assertTrue(action.validate())
        
        action = TypeAction(selector="", value_type="text", value_key="test")
        self.assertFalse(action.validate())
        
        action = TypeAction(selector="#input", value_type="", value_key="test")
        self.assertFalse(action.validate())
        
        action = TypeAction(selector="#input", value_type="text", value_key="")
        self.assertFalse(action.validate())

    def test_get_value_text(self):
        """Test that _get_value returns the value_key when value_type is 'text'."""
        action = TypeAction(selector="#input", value_type="text", value_key="test")
        
        value = action._get_value(None)
        
        self.assertEqual(value, "test")

    def test_get_value_credential(self):
        """Test that _get_value returns the credential value when value_type is 'credential'."""
        repo = Mock(spec=ICredentialRepository)
        repo.get_by_name.return_value = {"username": "user", "password": "pass"}
        action = TypeAction(selector="#input", value_type="credential", value_key="test.password")
        
        value = action._get_value(repo)
        
        repo.get_by_name.assert_called_once_with("test")
        self.assertEqual(value, "pass")

    def test_get_value_credential_not_found(self):
        """Test that _get_value raises CredentialError when credential is not found."""
        repo = Mock(spec=ICredentialRepository)
        repo.get_by_name.return_value = None
        action = TypeAction(selector="#input", value_type="credential", value_key="test.password")
        
        with self.assertRaises(CredentialError):
            action._get_value(repo)
        
        repo.get_by_name.assert_called_once_with("test")

    def test_get_value_credential_field_not_found(self):
        """Test that _get_value raises CredentialError when credential field is not found."""
        repo = Mock(spec=ICredentialRepository)
        repo.get_by_name.return_value = {"username": "user"}
        action = TypeAction(selector="#input", value_type="credential", value_key="test.password")
        
        with self.assertRaises(CredentialError):
            action._get_value(repo)
        
        repo.get_by_name.assert_called_once_with("test")

    def test_get_value_invalid_type(self):
        """Test that _get_value raises ValueError when value_type is invalid."""
        action = TypeAction(selector="#input", value_type="invalid", value_key="test")
        
        with self.assertRaises(ValueError):
            action._get_value(None)

    def test_get_value_no_repository(self):
        """Test that _get_value raises CredentialError when value_type is 'credential' but no repository is provided."""
        action = TypeAction(selector="#input", value_type="credential", value_key="test.password")
        
        with self.assertRaises(CredentialError):
            action._get_value(None)

    def test_execute_success_text(self):
        """Test that execute returns a success result when typing text succeeds."""
        driver = Mock(spec=IWebDriver)
        action = TypeAction(selector="#input", value_type="text", value_key="test")
        
        result = action.execute(driver)
        
        driver.type_text.assert_called_once_with("#input", "test")
        self.assertTrue(result.is_success())
        self.assertEqual(result.message, "Typed text into element #input")

    def test_execute_success_credential(self):
        """Test that execute returns a success result when typing credential succeeds."""
        driver = Mock(spec=IWebDriver)
        repo = Mock(spec=ICredentialRepository)
        repo.get_by_name.return_value = {"username": "user", "password": "pass"}
        action = TypeAction(selector="#input", value_type="credential", value_key="test.password")
        
        result = action.execute(driver, repo)
        
        repo.get_by_name.assert_called_once_with("test")
        driver.type_text.assert_called_once_with("#input", "pass")
        self.assertTrue(result.is_success())
        self.assertEqual(result.message, "Typed text into element #input")

    def test_execute_value_error(self):
        """Test that execute returns a failure result when ValueError is raised."""
        driver = Mock(spec=IWebDriver)
        action = TypeAction(selector="#input", value_type="invalid", value_key="test")
        
        result = action.execute(driver)
        
        self.assertFalse(result.is_success())
        self.assertTrue("Invalid value configuration" in result.message)

    def test_execute_credential_error(self):
        """Test that execute returns a failure result when CredentialError is raised."""
        driver = Mock(spec=IWebDriver)
        repo = Mock(spec=ICredentialRepository)
        repo.get_by_name.return_value = None
        action = TypeAction(selector="#input", value_type="credential", value_key="test.password")
        
        result = action.execute(driver, repo)
        
        repo.get_by_name.assert_called_once_with("test")
        self.assertFalse(result.is_success())
        self.assertTrue("Credential not found" in result.message)

    def test_execute_webdriver_error(self):
        """Test that execute returns a failure result when WebDriverError is raised."""
        driver = Mock(spec=IWebDriver)
        driver.type_text.side_effect = WebDriverError("Failed to type")
        action = TypeAction(selector="#input", value_type="text", value_key="test")
        
        result = action.execute(driver)
        
        driver.type_text.assert_called_once_with("#input", "test")
        self.assertFalse(result.is_success())
        self.assertEqual(result.message, "WebDriver error typing text into element #input: Failed to type")

    def test_execute_other_error(self):
        """Test that execute returns a failure result when another exception is raised."""
        driver = Mock(spec=IWebDriver)
        driver.type_text.side_effect = Exception("Unexpected error")
        action = TypeAction(selector="#input", value_type="text", value_key="test")
        
        result = action.execute(driver)
        
        driver.type_text.assert_called_once_with("#input", "test")
        self.assertFalse(result.is_success())
        self.assertTrue("Failed to type text into element #input" in result.message)

    def test_to_dict(self):
        """Test that to_dict returns the correct dictionary representation."""
        action = TypeAction(
            selector="#input",
            value_type="credential",
            value_key="test.password",
            name="Custom Name"
        )
        
        result = action.to_dict()
        
        self.assertEqual(result, {
            "type": "Type",
            "name": "Custom Name",
            "selector": "#input",
            "value_type": "credential",
            "value_key": "test.password"
        })

if __name__ == "__main__":
    unittest.main()
