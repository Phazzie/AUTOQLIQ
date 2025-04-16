"""Tests for the action validator module."""
import unittest
from unittest.mock import patch, MagicMock

from src.core.actions.validator import ActionValidator
from src.core.exceptions import ActionError


class TestActionValidator(unittest.TestCase):
    """Test cases for the ActionValidator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.validator = ActionValidator()
    
    def test_validate_action_data_valid(self):
        """Test that validate_action_data accepts valid action data."""
        # Create valid action data
        action_data = {
            "type": "Navigate",
            "url": "https://example.com",
            "name": "Custom Name"
        }
        
        # This should not raise an exception
        self.validator.validate_action_data(action_data)
    
    def test_validate_action_data_not_dict(self):
        """Test that validate_action_data raises TypeError for non-dict data."""
        # Try to validate a non-dict
        with self.assertRaises(TypeError):
            self.validator.validate_action_data("not a dict")
    
    def test_validate_action_data_missing_type(self):
        """Test that validate_action_data raises ActionError for data without a type."""
        # Create action data without a type
        action_data = {
            "url": "https://example.com",
            "name": "Custom Name"
        }
        
        # Try to validate the data
        with self.assertRaises(ActionError):
            self.validator.validate_action_data(action_data)
    
    def test_validate_action_data_invalid_type(self):
        """Test that validate_action_data raises ActionError for data with an invalid type."""
        # Create action data with a non-string type
        action_data = {
            "type": 123,
            "url": "https://example.com",
            "name": "Custom Name"
        }
        
        # Try to validate the data
        with self.assertRaises(ActionError):
            self.validator.validate_action_data(action_data)


if __name__ == "__main__":
    unittest.main()
