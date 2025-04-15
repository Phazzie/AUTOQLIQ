"""Tests for the ActionExecutor class."""

import unittest
from unittest.mock import MagicMock, patch

from src.core.interfaces import IWebDriver, IAction, ICredentialRepository
from src.core.action_result import ActionResult, ActionStatus
from src.core.exceptions import ActionError, ValidationError
from src.core.workflow.action_executor import ActionExecutor


class MockAction(MagicMock):
    """Mock action for testing."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(spec=IAction, *args, **kwargs)
        self.name = kwargs.get('name', 'MockAction')
        self.action_type = kwargs.get('action_type', 'Mock')
        self.should_fail = kwargs.get('should_fail', False)
        self.should_raise = kwargs.get('should_raise', False)
        self.exception_type = kwargs.get('exception_type', ActionError)
        self.validate_fails = kwargs.get('validate_fails', False)
        self.validate_called = False
        self.execute_called = False
        self.context_received = None
    
    def validate(self):
        """Mock validation."""
        self.validate_called = True
        if self.validate_fails:
            raise ValidationError(f"Validation failed for {self.name}")
        return True
    
    def execute(self, driver, credential_repo=None, context=None):
        """Mock execution."""
        self.execute_called = True
        self.context_received = context
        
        if self.should_raise:
            raise self.exception_type(f"{self.name} raised test exception")
            
        if self.should_fail:
            return ActionResult.failure(f"{self.name} failed intentionally")
        
        return ActionResult.success(f"{self.name} succeeded")


class TestActionExecutor(unittest.TestCase):
    """Test cases for the ActionExecutor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_driver = MagicMock(spec=IWebDriver)
        self.mock_credential_repo = MagicMock(spec=ICredentialRepository)
        self.executor = ActionExecutor(self.mock_driver, self.mock_credential_repo)
    
    def test_init(self):
        """Test initialization."""
        self.assertEqual(self.executor.driver, self.mock_driver)
        self.assertEqual(self.executor.credential_repo, self.mock_credential_repo)
    
    def test_execute_action_success(self):
        """Test executing an action that succeeds."""
        action = MockAction(name="SuccessAction")
        context = {"test_key": "test_value"}
        
        result = self.executor.execute_action(action, context)
        
        self.assertTrue(action.validate_called)
        self.assertTrue(action.execute_called)
        self.assertEqual(action.context_received, context)
        self.assertTrue(result.is_success())
        self.assertEqual(result.message, "SuccessAction succeeded")
    
    def test_execute_action_failure(self):
        """Test executing an action that fails."""
        action = MockAction(name="FailureAction", should_fail=True)
        context = {"test_key": "test_value"}
        
        result = self.executor.execute_action(action, context)
        
        self.assertTrue(action.validate_called)
        self.assertTrue(action.execute_called)
        self.assertEqual(action.context_received, context)
        self.assertFalse(result.is_success())
        self.assertEqual(result.message, "FailureAction failed intentionally")
    
    def test_execute_action_validation_error(self):
        """Test executing an action that fails validation."""
        action = MockAction(name="ValidationFailAction", validate_fails=True)
        context = {"test_key": "test_value"}
        
        result = self.executor.execute_action(action, context)
        
        self.assertTrue(action.validate_called)
        self.assertFalse(action.execute_called)
        self.assertFalse(result.is_success())
        self.assertIn("Validation failed", result.message)
    
    def test_execute_action_execution_error(self):
        """Test executing an action that raises an error."""
        action = MockAction(name="ErrorAction", should_raise=True, exception_type=ActionError)
        context = {"test_key": "test_value"}
        
        result = self.executor.execute_action(action, context)
        
        self.assertTrue(action.validate_called)
        self.assertTrue(action.execute_called)
        self.assertEqual(action.context_received, context)
        self.assertFalse(result.is_success())
        self.assertIn("Action execution error", result.message)
    
    def test_execute_action_unexpected_error(self):
        """Test executing an action that raises an unexpected error."""
        action = MockAction(name="UnexpectedErrorAction", should_raise=True, exception_type=ValueError)
        context = {"test_key": "test_value"}
        
        result = self.executor.execute_action(action, context)
        
        self.assertTrue(action.validate_called)
        self.assertTrue(action.execute_called)
        self.assertEqual(action.context_received, context)
        self.assertFalse(result.is_success())
        self.assertIn("Unexpected exception", result.message)
    
    def test_execute_action_invalid_result(self):
        """Test executing an action that returns an invalid result."""
        action = MockAction(name="InvalidResultAction")
        context = {"test_key": "test_value"}
        
        # Mock the execute method to return something other than an ActionResult
        action.execute.return_value = "Not an ActionResult"
        
        result = self.executor.execute_action(action, context)
        
        self.assertTrue(action.validate_called)
        self.assertTrue(action.execute_called)
        self.assertEqual(action.context_received, context)
        self.assertFalse(result.is_success())
        self.assertIn("implementation error: Invalid return type", result.message)


if __name__ == "__main__":
    unittest.main()
