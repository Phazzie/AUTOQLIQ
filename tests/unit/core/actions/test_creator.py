"""Tests for the action creator module."""
import unittest
from unittest.mock import patch, MagicMock

from src.core.actions.creator import ActionCreator
from src.core.exceptions import ActionError, ValidationError, SerializationError


class TestActionCreator(unittest.TestCase):
    """Test cases for the ActionCreator class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create mock components
        self.mock_registry = MagicMock()
        self.mock_validator = MagicMock()
        self.mock_nested_handler = MagicMock()
        
        # Create an action creator with the mock components
        self.creator = ActionCreator(
            self.mock_registry,
            self.mock_validator,
            self.mock_nested_handler
        )
        
        # Set up the mock registry to return a mock action class
        self.mock_action_class = MagicMock()
        self.mock_action_instance = MagicMock()
        self.mock_action_class.return_value = self.mock_action_instance
        self.mock_registry.get_action_class.return_value = self.mock_action_class
        
        # Set up the mock nested handler to return the input params
        self.mock_nested_handler.process_nested_actions.side_effect = lambda action_type, params: params
    
    def test_create_action_success(self):
        """Test that create_action creates an action successfully."""
        # Create action data
        action_data = {
            "type": "Navigate",
            "url": "https://example.com",
            "name": "Custom Name"
        }
        
        # Create the action
        action = self.creator.create_action(action_data)
        
        # Check that the validator was called
        self.mock_validator.validate_action_data.assert_called_once_with(action_data)
        
        # Check that the registry was used to get the action class
        self.mock_registry.get_action_class.assert_called_once_with("Navigate")
        
        # Check that the nested handler was called
        self.mock_nested_handler.process_nested_actions.assert_called_once_with(
            "Navigate",
            {"url": "https://example.com", "name": "Custom Name"}
        )
        
        # Check that the action class was instantiated with the processed params
        self.mock_action_class.assert_called_once_with(
            url="https://example.com",
            name="Custom Name"
        )
        
        # Check that the created action was returned
        self.assertEqual(action, self.mock_action_instance)
    
    def test_create_action_validation_error(self):
        """Test that create_action raises ActionError when validation fails."""
        # Make the validator raise a ValidationError
        self.mock_validator.validate_action_data.side_effect = ValidationError("Invalid action data")
        
        # Create action data
        action_data = {
            "type": "Navigate",
            "url": "https://example.com"
        }
        
        # Try to create the action
        with self.assertRaises(ActionError):
            self.creator.create_action(action_data)
    
    def test_create_action_unknown_type(self):
        """Test that create_action raises ActionError for unknown action types."""
        # Make the registry return None for the action class
        self.mock_registry.get_action_class.return_value = None
        
        # Create action data
        action_data = {
            "type": "Unknown",
            "name": "Custom Name"
        }
        
        # Try to create the action
        with self.assertRaises(ActionError):
            self.creator.create_action(action_data)
    
    def test_create_action_nested_handler_error(self):
        """Test that create_action raises ActionError when nested handler fails."""
        # Make the nested handler raise a SerializationError
        self.mock_nested_handler.process_nested_actions.side_effect = SerializationError("Invalid nested action")
        
        # Create action data
        action_data = {
            "type": "Conditional",
            "true_branch": [{"type": "Navigate", "url": "https://example.com"}],
            "false_branch": []
        }
        
        # Try to create the action
        with self.assertRaises(ActionError):
            self.creator.create_action(action_data)
    
    def test_create_action_instantiation_error(self):
        """Test that create_action raises ActionError when action instantiation fails."""
        # Make the action class raise a ValueError
        self.mock_action_class.side_effect = ValueError("Invalid parameters")
        
        # Create action data
        action_data = {
            "type": "Navigate",
            "url": "https://example.com"
        }
        
        # Try to create the action
        with self.assertRaises(ActionError):
            self.creator.create_action(action_data)


if __name__ == "__main__":
    unittest.main()
