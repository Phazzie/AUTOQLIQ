"""Tests for action executor."""

import unittest
from unittest.mock import MagicMock, patch

from src.core.interfaces import IWebDriver, IAction, ICredentialRepository
from src.core.action_result import ActionResult
from src.core.exceptions import ActionError, ValidationError
from src.core.workflow.action_executor import ActionExecutor


class TestActionExecutor(unittest.TestCase):
    """Test cases for action executor."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_driver = MagicMock(spec=IWebDriver)
        self.mock_credential_repo = MagicMock(spec=ICredentialRepository)
        self.executor = ActionExecutor(self.mock_driver, self.mock_credential_repo)
        
        self.mock_action = MagicMock(spec=IAction)
        self.mock_action.name = "TestAction"
        self.mock_action.action_type = "test"
        self.mock_action.validate = MagicMock()
        self.mock_action.execute = MagicMock(return_value=ActionResult.success("Test success"))
        
        self.context = {"test_var": "test_value"}

    def test_execute_action_success(self):
        """Test executing an action successfully."""
        result = self.executor.execute_action(self.mock_action, self.context)
        
        self.mock_action.validate.assert_called_once()
        self.mock_action.execute.assert_called_once_with(
            self.mock_driver, self.mock_credential_repo, self.context
        )
        self.assertTrue(result.is_success())
        self.assertEqual(result.message, "Test success")

    def test_execute_action_validation_error(self):
        """Test executing an action with a validation error."""
        self.mock_action.validate.side_effect = ValidationError("Test validation error")
        
        result = self.executor.execute_action(self.mock_action, self.context)
        
        self.mock_action.validate.assert_called_once()
        self.mock_action.execute.assert_not_called()
        self.assertFalse(result.is_success())
        self.assertIn("validation failed", result.message)

    def test_execute_action_execution_error(self):
        """Test executing an action with an execution error."""
        self.mock_action.execute.side_effect = ActionError("Test execution error")
        
        result = self.executor.execute_action(self.mock_action, self.context)
        
        self.mock_action.validate.assert_called_once()
        self.mock_action.execute.assert_called_once_with(
            self.mock_driver, self.mock_credential_repo, self.context
        )
        self.assertFalse(result.is_success())
        self.assertIn("execution error", result.message)

    def test_execute_action_unexpected_error(self):
        """Test executing an action with an unexpected error."""
        self.mock_action.execute.side_effect = Exception("Test unexpected error")
        
        result = self.executor.execute_action(self.mock_action, self.context)
        
        self.mock_action.validate.assert_called_once()
        self.mock_action.execute.assert_called_once_with(
            self.mock_driver, self.mock_credential_repo, self.context
        )
        self.assertFalse(result.is_success())
        self.assertIn("Unexpected exception", result.message)

    def test_execute_action_invalid_result(self):
        """Test executing an action that returns an invalid result."""
        self.mock_action.execute.return_value = "Not an ActionResult"
        
        result = self.executor.execute_action(self.mock_action, self.context)
        
        self.mock_action.validate.assert_called_once()
        self.mock_action.execute.assert_called_once_with(
            self.mock_driver, self.mock_credential_repo, self.context
        )
        self.assertFalse(result.is_success())
        self.assertIn("Invalid return type", result.message)


if __name__ == "__main__":
    unittest.main()
