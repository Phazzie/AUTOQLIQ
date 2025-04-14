"""Tests for error handling strategies."""

import unittest
from unittest.mock import MagicMock, patch

from src.core.interfaces import IAction
from src.core.action_result import ActionResult
from src.core.exceptions import ActionError, WorkflowError
from src.core.workflow.error_handling import (
    StopOnErrorStrategy,
    ContinueOnErrorStrategy,
    RetryOnErrorStrategy,
    create_error_handling_strategy
)


class TestErrorHandlingStrategies(unittest.TestCase):
    """Test cases for error handling strategies."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_action = MagicMock(spec=IAction)
        self.mock_action.name = "TestAction"
        self.mock_action.action_type = "TestType"
        self.action_display = "TestAction (TestType)"
        self.test_error = Exception("Test error")
        self.test_workflow_error = WorkflowError("Test workflow error")
        self.test_action_error = ActionError("Test action error")
        self.test_result = ActionResult.failure("Test failure")

    def test_stop_on_error_strategy_handle_action_error(self):
        """Test that StopOnErrorStrategy raises ActionError on handle_action_error."""
        strategy = StopOnErrorStrategy()
        
        # Test with regular exception
        with self.assertRaises(ActionError):
            strategy.handle_action_error(self.test_error, self.mock_action, self.action_display)
        
        # Test with WorkflowError
        with self.assertRaises(WorkflowError):
            strategy.handle_action_error(self.test_workflow_error, self.mock_action, self.action_display)
        
        # Test with ActionError
        with self.assertRaises(ActionError):
            strategy.handle_action_error(self.test_action_error, self.mock_action, self.action_display)

    def test_stop_on_error_strategy_handle_action_failure(self):
        """Test that StopOnErrorStrategy raises ActionError on handle_action_failure."""
        strategy = StopOnErrorStrategy()
        
        with self.assertRaises(ActionError):
            strategy.handle_action_failure(self.test_result, self.mock_action, self.action_display)

    def test_continue_on_error_strategy_handle_action_error(self):
        """Test that ContinueOnErrorStrategy returns failure result on handle_action_error."""
        strategy = ContinueOnErrorStrategy()
        
        # Test with regular exception
        result = strategy.handle_action_error(self.test_error, self.mock_action, self.action_display)
        self.assertFalse(result.is_success())
        self.assertIn("Test error", result.message)
        
        # Test with WorkflowError
        with self.assertRaises(WorkflowError):
            strategy.handle_action_error(self.test_workflow_error, self.mock_action, self.action_display)
        
        # Test with ActionError
        result = strategy.handle_action_error(self.test_action_error, self.mock_action, self.action_display)
        self.assertFalse(result.is_success())
        self.assertIn("Test action error", result.message)

    def test_continue_on_error_strategy_handle_action_failure(self):
        """Test that ContinueOnErrorStrategy does not raise on handle_action_failure."""
        strategy = ContinueOnErrorStrategy()
        
        # Should not raise
        strategy.handle_action_failure(self.test_result, self.mock_action, self.action_display)

    def test_retry_on_error_strategy_handle_action_error(self):
        """Test that RetryOnErrorStrategy returns retry result on handle_action_error."""
        strategy = RetryOnErrorStrategy(max_retries=2)
        
        # First attempt should return retry result
        result1 = strategy.handle_action_error(self.test_error, self.mock_action, self.action_display)
        self.assertFalse(result1.is_success())
        self.assertTrue(result1.data.get("retry"))
        self.assertEqual(result1.data.get("retry_count"), 1)
        
        # Second attempt should return retry result
        result2 = strategy.handle_action_error(self.test_error, self.mock_action, self.action_display)
        self.assertFalse(result2.is_success())
        self.assertTrue(result2.data.get("retry"))
        self.assertEqual(result2.data.get("retry_count"), 2)
        
        # Third attempt should use fallback strategy (StopOnErrorStrategy by default)
        with self.assertRaises(ActionError):
            strategy.handle_action_error(self.test_error, self.mock_action, self.action_display)
        
        # Test with WorkflowError
        with self.assertRaises(WorkflowError):
            strategy.handle_action_error(self.test_workflow_error, self.mock_action, self.action_display)

    def test_retry_on_error_strategy_with_continue_fallback(self):
        """Test RetryOnErrorStrategy with ContinueOnErrorStrategy as fallback."""
        strategy = RetryOnErrorStrategy(
            max_retries=1,
            fallback_strategy=ContinueOnErrorStrategy()
        )
        
        # First attempt should return retry result
        result1 = strategy.handle_action_error(self.test_error, self.mock_action, self.action_display)
        self.assertFalse(result1.is_success())
        self.assertTrue(result1.data.get("retry"))
        
        # Second attempt should use fallback strategy (ContinueOnErrorStrategy)
        result2 = strategy.handle_action_error(self.test_error, self.mock_action, self.action_display)
        self.assertFalse(result2.is_success())
        self.assertFalse(result2.data.get("retry", False))

    def test_create_error_handling_strategy(self):
        """Test that create_error_handling_strategy creates the correct strategy."""
        # Test stop strategy
        stop_strategy = create_error_handling_strategy("stop")
        self.assertIsInstance(stop_strategy, StopOnErrorStrategy)
        
        # Test continue strategy
        continue_strategy = create_error_handling_strategy("continue")
        self.assertIsInstance(continue_strategy, ContinueOnErrorStrategy)
        
        # Test retry strategy
        retry_strategy = create_error_handling_strategy("retry")
        self.assertIsInstance(retry_strategy, RetryOnErrorStrategy)
        
        # Test retry strategy with custom parameters
        custom_retry_strategy = create_error_handling_strategy(
            "retry",
            max_retries=5,
            retry_delay_seconds=2.0,
            fallback_strategy="continue"
        )
        self.assertIsInstance(custom_retry_strategy, RetryOnErrorStrategy)
        self.assertEqual(custom_retry_strategy.max_retries, 5)
        self.assertEqual(custom_retry_strategy.retry_delay_seconds, 2.0)
        self.assertIsInstance(custom_retry_strategy.fallback_strategy, ContinueOnErrorStrategy)
        
        # Test invalid strategy type
        with self.assertRaises(ValueError):
            create_error_handling_strategy("invalid")


if __name__ == "__main__":
    unittest.main()
