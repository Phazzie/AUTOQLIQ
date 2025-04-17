"""Unit tests for control flow utility functions."""

import unittest
from unittest.mock import patch, MagicMock

from src.core.action_result import ActionResult
from src.core.workflow.control_flow.utils import evaluate_action_results, create_error_context


class TestControlFlowUtils(unittest.TestCase):
    """Test cases for control flow utility functions."""

    def test_evaluate_action_results_all_success(self):
        """Test evaluate_action_results with all successful results."""
        # Arrange
        results = [
            ActionResult.success("Action 1 succeeded"),
            ActionResult.success("Action 2 succeeded"),
            ActionResult.success("Action 3 succeeded")
        ]
        
        # Act
        result = evaluate_action_results(results, "test branch")
        
        # Assert
        self.assertTrue(result.is_success())
        self.assertEqual(result.message, "test branch executed successfully (3 actions)")

    def test_evaluate_action_results_with_failures(self):
        """Test evaluate_action_results with some failed results."""
        # Arrange
        results = [
            ActionResult.success("Action 1 succeeded"),
            ActionResult.failure("Action 2 failed"),
            ActionResult.success("Action 3 succeeded")
        ]
        
        # Act
        result = evaluate_action_results(results, "test branch")
        
        # Assert
        self.assertFalse(result.is_success())
        self.assertEqual(result.message, "test branch had failures (3 actions)")

    def test_evaluate_action_results_custom_templates(self):
        """Test evaluate_action_results with custom message templates."""
        # Arrange
        results = [
            ActionResult.success("Action 1 succeeded"),
            ActionResult.success("Action 2 succeeded")
        ]
        
        # Act
        result = evaluate_action_results(
            results, 
            "test branch",
            success_message_template="Custom success: {branch_name} with {action_count}",
            failure_message_template="Custom failure: {branch_name} with {action_count}"
        )
        
        # Assert
        self.assertTrue(result.is_success())
        self.assertEqual(result.message, "Custom success: test branch with 2")

    def test_create_error_context(self):
        """Test create_error_context with a standard exception."""
        # Arrange
        context = {"key1": "value1", "key2": "value2"}
        error = ValueError("Test error message")
        
        # Act
        error_context = create_error_context(context, error)
        
        # Assert
        self.assertEqual(error_context["key1"], "value1")  # Original context preserved
        self.assertEqual(error_context["key2"], "value2")  # Original context preserved
        self.assertEqual(error_context["error"], "Test error message")
        self.assertEqual(error_context["error_type"], "ValueError")
        self.assertEqual(error_context["error_message"], "Test error message")
        self.assertEqual(error_context["error_type_name"], "ValueError")

    def test_create_error_context_with_prefix(self):
        """Test create_error_context with a prefix."""
        # Arrange
        context = {"key1": "value1"}
        error = RuntimeError("Runtime error")
        
        # Act
        error_context = create_error_context(context, error, prefix="test_")
        
        # Assert
        self.assertEqual(error_context["key1"], "value1")  # Original context preserved
        self.assertEqual(error_context["test_error"], "Runtime error")
        self.assertEqual(error_context["test_error_type"], "RuntimeError")
        self.assertEqual(error_context["test_error_message"], "Runtime error")
        self.assertEqual(error_context["test_error_type_name"], "RuntimeError")


if __name__ == '__main__':
    unittest.main()
