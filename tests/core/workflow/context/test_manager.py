import unittest
from unittest.mock import MagicMock, patch

from src.core.workflow.context.manager import WorkflowContextManager


class TestWorkflowContextManager(unittest.TestCase):
    """Test suite for WorkflowContextManager class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self._manager = WorkflowContextManager()

        # Mock internal components to isolate the tests
        self._manager.serializer = MagicMock()
        self._manager.validator = MagicMock()
        self._manager.variable_substitutor = MagicMock()

    def test_execute_action_with_valid_action_returns_success_result(self):
        """Test that executing a valid action returns a success result with all expected fields."""
        # Arrange
        test_action = {"type": "test_action", "param": "value"}
        test_context = {"driver": MagicMock(), "credential_repo": MagicMock()}

        # Act
        result = self._manager._execute_action(test_action, test_context)

        # Assert
        self.assertEqual("success", result["status"], "Result status should be 'success'")
        self.assertEqual("test_action", result["action_type"], "Action type should match the input")

        # Check for expected keys in the result dictionary
        expected_keys = ["status", "action_type"]
        for key in expected_keys:
            self.assertIn(key, result, f"Result should contain '{key}' field")

        # Verify no unexpected error field is present
        self.assertNotIn("error", result, "Success result should not contain error field")

    def test_execute_action_with_missing_type_returns_failure_result(self):
        """Test that executing an action without a type returns a failure result with appropriate error message."""
        # Arrange
        test_action = {"param": "value"}
        test_context = {"driver": MagicMock(), "credential_repo": MagicMock()}

        # Act
        result = self._manager._execute_action(test_action, test_context)

        # Assert
        self.assertEqual("failure", result["status"], "Result status should be 'failure'")
        self.assertEqual(None, result["action_type"], "Action type should be None for missing type")

        # Check for expected keys in the result dictionary
        expected_keys = ["status", "action_type", "error"]
        for key in expected_keys:
            self.assertIn(key, result, f"Result should contain '{key}' field")

        # Verify error message content
        self.assertIn("missing action type", result["error"].lower(), "Error message should mention missing action type")

    def test_execute_actions_returns_correct_results(self):
        """Test that execute_actions returns complete results for all actions in the correct order."""
        # Arrange
        test_actions = [
            {"type": "action1", "param": "value1"},
            {"type": "action2", "param": "value2"},
            {"type": "action3", "param": "value3"}
        ]
        test_context = {"driver": MagicMock(), "credential_repo": MagicMock()}

        # Act
        results = self._manager.execute_actions(test_actions, test_context)

        # Assert
        self.assertEqual(len(test_actions), len(results), "Should return one result per action")

        # Verify each result matches the corresponding action
        for i, result in enumerate(results):
            self.assertEqual("success", result["status"], f"Result {i} status should be 'success'")
            self.assertEqual(test_actions[i]["type"], result["action_type"],
                             f"Result {i} action_type should match input action type")

            # Check for expected keys in each result dictionary
            expected_keys = ["status", "action_type"]
            for key in expected_keys:
                self.assertIn(key, result, f"Result {i} should contain '{key}' field")

    def test_execute_actions_calls_execute_for_each_action(self):
        """Test that execute_actions calls _execute_action for each action."""
        # Arrange
        test_actions = [
            {"type": "action1", "param": "value1"},
            {"type": "action2", "param": "value2"}
        ]
        test_context = {"driver": MagicMock(), "credential_repo": MagicMock()}

        # Create a spy on _execute_action
        original_execute = self._manager._execute_action
        self._manager._execute_action = MagicMock(side_effect=original_execute)

        # Act
        self._manager.execute_actions(test_actions, test_context)

        # Assert
        self.assertEqual(len(test_actions), self._manager._execute_action.call_count)
        for i, action in enumerate(test_actions):
            self._manager._execute_action.assert_any_call(action, test_context)
