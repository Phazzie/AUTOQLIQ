"""Tests for count loop handler."""

import unittest
from unittest.mock import MagicMock, patch, call

from src.core.interfaces import IWebDriver, IAction
from src.core.action_result import ActionResult
from src.core.exceptions import ActionError, WorkflowError
from src.core.actions.loop_action import LoopAction
from src.core.workflow.control_flow.loop_handlers.count_loop import CountLoopHandler


class TestCountLoopHandler(unittest.TestCase):
    """Test cases for count loop handler."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_driver = MagicMock(spec=IWebDriver)
        self.mock_action = MagicMock(spec=LoopAction)
        self.mock_action.name = "TestLoop"
        self.mock_action.action_type = "loop"
        self.mock_action.loop_type = "count"
        self.mock_action.count = 3
        
        self.mock_loop_action = MagicMock(spec=IAction)
        self.mock_loop_action.name = "LoopAction"
        self.mock_loop_action.action_type = "test"
        
        self.mock_action.loop_actions = [self.mock_loop_action]
        
        self.context = {"test_var": "test_value"}
        self.workflow_name = "TestWorkflow"
        self.log_prefix = "Test: "
        
        self.handler = CountLoopHandler(self.mock_driver)
        
        # Mock execute_actions_func
        self.mock_execute_actions = MagicMock(return_value=[ActionResult.success("Test success")])
        self.handler.set_execute_actions_func(self.mock_execute_actions)

    def test_handle_loop_with_positive_count(self):
        """Test handling a count loop with a positive count."""
        result = self.handler.handle_loop(
            self.mock_action, self.context, self.workflow_name, self.log_prefix
        )
        
        self.assertEqual(result, 3)  # Should return the count
        self.assertEqual(self.mock_execute_actions.call_count, 3)
        
        # Check that context was updated correctly for each iteration
        expected_calls = [
            call(
                [self.mock_loop_action],
                {
                    "test_var": "test_value",
                    "loop_index": i,
                    "loop_iteration": i + 1,
                    "loop_total": 3
                },
                self.workflow_name,
                f"{self.log_prefix}Iteration {i + 1}/3: "
            )
            for i in range(3)
        ]
        self.mock_execute_actions.assert_has_calls(expected_calls)

    def test_handle_loop_with_zero_count(self):
        """Test handling a count loop with a zero count."""
        self.mock_action.count = 0
        
        result = self.handler.handle_loop(
            self.mock_action, self.context, self.workflow_name, self.log_prefix
        )
        
        self.assertEqual(result, 0)  # Should return the count
        self.mock_execute_actions.assert_not_called()

    def test_handle_loop_with_negative_count(self):
        """Test handling a count loop with a negative count."""
        self.mock_action.count = -1
        
        result = self.handler.handle_loop(
            self.mock_action, self.context, self.workflow_name, self.log_prefix
        )
        
        self.assertEqual(result, 0)  # Should return 0
        self.mock_execute_actions.assert_not_called()

    def test_handle_loop_preserves_original_context(self):
        """Test that the original context is not modified."""
        original_context = self.context.copy()
        
        self.handler.handle_loop(
            self.mock_action, self.context, self.workflow_name, self.log_prefix
        )
        
        self.assertEqual(self.context, original_context)


if __name__ == "__main__":
    unittest.main()
