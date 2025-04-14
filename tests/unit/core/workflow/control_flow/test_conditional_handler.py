"""Tests for conditional handler."""

import unittest
from unittest.mock import MagicMock, patch

from src.core.interfaces import IWebDriver, IAction
from src.core.action_result import ActionResult
from src.core.exceptions import ActionError, WorkflowError
from src.core.actions.conditional_action import ConditionalAction
from src.core.workflow.control_flow.conditional_handler import ConditionalHandler


class TestConditionalHandler(unittest.TestCase):
    """Test cases for conditional handler."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_driver = MagicMock(spec=IWebDriver)
        self.mock_action = MagicMock(spec=ConditionalAction)
        self.mock_action.name = "TestConditional"
        self.mock_action.action_type = "conditional"
        self.mock_action.condition_type = "element_exists"
        self.mock_action._evaluate_condition = MagicMock(return_value=True)
        
        self.mock_true_action = MagicMock(spec=IAction)
        self.mock_true_action.name = "TrueAction"
        self.mock_true_action.action_type = "test"
        
        self.mock_false_action = MagicMock(spec=IAction)
        self.mock_false_action.name = "FalseAction"
        self.mock_false_action.action_type = "test"
        
        self.mock_action.true_branch = [self.mock_true_action]
        self.mock_action.false_branch = [self.mock_false_action]
        
        self.context = {"test_var": "test_value"}
        self.workflow_name = "TestWorkflow"
        self.log_prefix = "Test: "
        
        self.handler = ConditionalHandler(self.mock_driver)
        
        # Mock execute_actions_func
        self.mock_execute_actions = MagicMock(return_value=[ActionResult.success("Test success")])
        self.handler.set_execute_actions_func(self.mock_execute_actions)

    def test_handle_with_true_condition(self):
        """Test handling a conditional action with a true condition."""
        self.mock_action._evaluate_condition.return_value = True
        
        result = self.handler.handle(
            self.mock_action, self.context, self.workflow_name, self.log_prefix
        )
        
        self.assertTrue(result.is_success())
        self.assertIn("true", result.message)
        self.mock_execute_actions.assert_called_once_with(
            self.mock_action.true_branch,
            self.context,
            self.workflow_name,
            f"{self.log_prefix}'true' branch: "
        )

    def test_handle_with_false_condition(self):
        """Test handling a conditional action with a false condition."""
        self.mock_action._evaluate_condition.return_value = False
        
        result = self.handler.handle(
            self.mock_action, self.context, self.workflow_name, self.log_prefix
        )
        
        self.assertTrue(result.is_success())
        self.assertIn("false", result.message)
        self.mock_execute_actions.assert_called_once_with(
            self.mock_action.false_branch,
            self.context,
            self.workflow_name,
            f"{self.log_prefix}'false' branch: "
        )

    def test_handle_with_empty_branch(self):
        """Test handling a conditional action with an empty branch."""
        self.mock_action._evaluate_condition.return_value = True
        self.mock_action.true_branch = []
        
        result = self.handler.handle(
            self.mock_action, self.context, self.workflow_name, self.log_prefix
        )
        
        self.assertTrue(result.is_success())
        self.assertIn("empty", result.message)
        self.mock_execute_actions.assert_not_called()

    def test_handle_with_branch_failure(self):
        """Test handling a conditional action with a branch that fails."""
        self.mock_action._evaluate_condition.return_value = True
        self.mock_execute_actions.return_value = [ActionResult.failure("Test failure")]
        
        result = self.handler.handle(
            self.mock_action, self.context, self.workflow_name, self.log_prefix
        )
        
        self.assertFalse(result.is_success())
        self.assertIn("failures", result.message)

    def test_handle_with_condition_error(self):
        """Test handling a conditional action with an error in condition evaluation."""
        self.mock_action._evaluate_condition.side_effect = Exception("Test error")
        
        with self.assertRaises(ActionError):
            self.handler.handle(
                self.mock_action, self.context, self.workflow_name, self.log_prefix
            )

    def test_handle_with_non_conditional_action(self):
        """Test handling a non-conditional action."""
        mock_non_conditional = MagicMock(spec=IAction)
        mock_non_conditional.name = "NonConditional"
        mock_non_conditional.action_type = "test"
        
        with self.assertRaises(WorkflowError):
            self.handler.handle(
                mock_non_conditional, self.context, self.workflow_name, self.log_prefix
            )


if __name__ == "__main__":
    unittest.main()
