"""Tests for the nested action handler module."""
import unittest
from unittest.mock import patch, MagicMock

from src.core.actions.nested_handler import NestedActionHandler
from src.core.exceptions import SerializationError


class TestNestedActionHandler(unittest.TestCase):
    """Test cases for the NestedActionHandler class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock action creator function
        self.mock_action_creator = MagicMock()
        self.mock_action_creator.return_value = MagicMock()

        # Create a nested action handler with the mock action creator
        self.handler = NestedActionHandler(self.mock_action_creator)

    def test_process_nested_actions_non_control_flow(self):
        """Test that process_nested_actions returns unchanged params for non-control flow actions."""
        # Create action params for a non-control flow action
        action_params = {
            "url": "https://example.com",
            "name": "Custom Name"
        }

        # Process the params
        processed_params = self.handler.process_nested_actions("Navigate", action_params)

        # Check that the params were not changed
        self.assertEqual(processed_params, action_params)

        # Check that the action creator was not called
        self.mock_action_creator.assert_not_called()

    def test_process_nested_actions_conditional(self):
        """Test that process_nested_actions processes nested actions for conditional actions."""
        # Create action params for a conditional action
        action_params = {
            "condition": "true",
            "true_branch": [
                {"type": "Navigate", "url": "https://example.com"},
                {"type": "Click", "selector": "#button"}
            ],
            "false_branch": [
                {"type": "Navigate", "url": "https://example.org"}
            ]
        }

        # Process the params
        processed_params = self.handler.process_nested_actions("Conditional", action_params)

        # Check that the action creator was called for each nested action
        self.assertEqual(self.mock_action_creator.call_count, 3)

        # Check that the nested actions were replaced with the created actions
        self.assertEqual(processed_params["true_branch"], [self.mock_action_creator.return_value, self.mock_action_creator.return_value])
        self.assertEqual(processed_params["false_branch"], [self.mock_action_creator.return_value])

    def test_process_nested_actions_loop(self):
        """Test that process_nested_actions processes nested actions for loop actions."""
        # Create action params for a loop action
        action_params = {
            "loop_condition": "i < 10",
            "loop_actions": [
                {"type": "Navigate", "url": "https://example.com"},
                {"type": "Click", "selector": "#button"}
            ]
        }

        # Process the params
        processed_params = self.handler.process_nested_actions("Loop", action_params)

        # Check that the action creator was called for each nested action
        self.assertEqual(self.mock_action_creator.call_count, 2)

        # Check that the nested actions were replaced with the created actions
        self.assertEqual(processed_params["loop_actions"], [self.mock_action_creator.return_value, self.mock_action_creator.return_value])

    def test_process_nested_actions_error_handling(self):
        """Test that process_nested_actions processes nested actions for error handling actions."""
        # Create action params for an error handling action
        action_params = {
            "try_actions": [
                {"type": "Navigate", "url": "https://example.com"}
            ],
            "catch_actions": [
                {"type": "Navigate", "url": "https://example.org"}
            ]
        }

        # Process the params
        processed_params = self.handler.process_nested_actions("ErrorHandling", action_params)

        # Check that the action creator was called for each nested action
        self.assertEqual(self.mock_action_creator.call_count, 2)

        # Check that the nested actions were replaced with the created actions
        self.assertEqual(processed_params["try_actions"], [self.mock_action_creator.return_value])
        self.assertEqual(processed_params["catch_actions"], [self.mock_action_creator.return_value])

    def test_process_nested_actions_invalid_nested_data(self):
        """Test that process_nested_actions raises SerializationError for invalid nested data."""
        # Create action params with invalid nested data
        action_params = {
            "true_branch": "not a list",
            "false_branch": []
        }

        # Try to process the params
        with self.assertRaises(SerializationError):
            self.handler.process_nested_actions("Conditional", action_params)

    def test_process_nested_actions_creator_error(self):
        """Test that process_nested_actions raises SerializationError when action creation fails."""
        # Make the action creator raise an exception
        self.mock_action_creator.side_effect = ValueError("Invalid action data")

        # Create action params
        action_params = {
            "true_branch": [
                {"type": "Navigate", "url": "https://example.com"}
            ],
            "false_branch": []
        }

        # Try to process the params
        with self.assertRaises(SerializationError):
            self.handler.process_nested_actions("Conditional", action_params)

        # Reset the side effect for other tests
        self.mock_action_creator.side_effect = None


if __name__ == "__main__":
    unittest.main()
