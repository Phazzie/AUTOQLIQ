#!/usr/bin/env python3
"""
Enhanced unit tests for ActionBase class in src/core/actions/base.py.
"""

import unittest
from unittest.mock import MagicMock, patch
from typing import Dict, Any, Optional, List

# Import the module under test
from src.core.actions.base import ActionBase
from src.core.exceptions import ValidationError


# Create a concrete implementation for testing
class TestAction(ActionBase):
    """Concrete implementation of ActionBase for testing."""
    action_type = "TestAction"
    
    def __init__(self, name: Optional[str] = None, test_param: str = "", **kwargs):
        """Initialize with test parameters."""
        super().__init__(name, **kwargs)
        self.test_param = test_param
    
    def execute(self, driver, credential_repo=None, context=None):
        """Implement abstract method."""
        return MagicMock()
    
    def to_dict(self) -> Dict[str, Any]:
        """Implement abstract method."""
        result = super().to_dict()
        result["test_param"] = self.test_param
        return result


class TestActionBase(unittest.TestCase):
    """
    Test cases for the ActionBase class to ensure it follows SOLID, KISS, and DRY principles.
    
    These tests cover the 6 main responsibilities of ActionBase:
    1. Initialization and parameter validation
    2. Enforcing the basic action interface
    3. Name and type management
    4. Providing a common validation mechanism
    5. Serialization to dictionary (to_dict)
    6. Providing string representations
    """
    
    def test_init_with_name(self):
        """Test initialization with a name."""
        action = TestAction(name="MyTestAction")
        self.assertEqual(action.name, "MyTestAction")
        self.assertEqual(action.action_type, "TestAction")
    
    def test_init_without_name(self):
        """Test initialization without a name."""
        action = TestAction()
        self.assertEqual(action.name, "TestAction")  # Should default to action_type
    
    def test_init_with_empty_name(self):
        """Test initialization with an empty name."""
        action = TestAction(name="   ")  # Empty after stripping
        self.assertEqual(action.name, "TestAction")  # Should default to action_type
    
    def test_init_with_whitespace_in_name(self):
        """Test initialization with whitespace in the name."""
        action = TestAction(name="  My Test Action  ")
        self.assertEqual(action.name, "My Test Action")  # Should be stripped
    
    def test_init_base_class_directly(self):
        """Test that ActionBase cannot be instantiated directly."""
        with self.assertRaises(TypeError):
            ActionBase()  # Abstract class
    
    def test_init_without_action_type(self):
        """Test initialization of a subclass that doesn't define action_type."""
        class InvalidAction(ActionBase):
            # Missing action_type
            def execute(self, driver, credential_repo=None, context=None):
                return MagicMock()
            
            def to_dict(self):
                return super().to_dict()
        
        with self.assertRaises(NotImplementedError):
            InvalidAction()
    
    def test_init_with_base_action_type(self):
        """Test initialization of a subclass that doesn't override action_type."""
        class InvalidAction(ActionBase):
            action_type = "Base"  # This should be overridden
            
            def execute(self, driver, credential_repo=None, context=None):
                return MagicMock()
            
            def to_dict(self):
                return super().to_dict()
        
        with self.assertRaises(NotImplementedError):
            InvalidAction()
    
    def test_init_with_extra_kwargs(self):
        """Test initialization with extra kwargs."""
        with patch('logging.getLogger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            action = TestAction(name="MyAction", test_param="value", extra_param="extra")
            
            # Should store unused kwargs
            self.assertIn("extra_param", action._unused_kwargs)
            self.assertEqual(action._unused_kwargs["extra_param"], "extra")
            
            # Should log a warning
            mock_logger.warning.assert_called_once()
    
    def test_validate_with_valid_name(self):
        """Test validation with a valid name."""
        action = TestAction(name="MyAction")
        self.assertTrue(action.validate())
    
    def test_validate_with_empty_name(self):
        """Test validation with an empty name."""
        action = TestAction()
        # Set name to empty after initialization
        action.name = ""
        
        with self.assertRaises(ValidationError) as context:
            action.validate()
        
        self.assertIn("name", str(context.exception))
    
    def test_validate_with_non_string_name(self):
        """Test validation with a non-string name."""
        action = TestAction()
        # Set name to a non-string after initialization
        action.name = 123
        
        with self.assertRaises(ValidationError) as context:
            action.validate()
        
        self.assertIn("name", str(context.exception))
    
    def test_to_dict_basic_fields(self):
        """Test that to_dict includes the basic fields."""
        action = TestAction(name="MyAction", test_param="value")
        result = action.to_dict()
        
        self.assertEqual(result["type"], "TestAction")
        self.assertEqual(result["name"], "MyAction")
        self.assertEqual(result["test_param"], "value")
    
    def test_get_nested_actions(self):
        """Test that get_nested_actions returns an empty list by default."""
        action = TestAction(name="MyAction")
        self.assertEqual(action.get_nested_actions(), [])
    
    def test_repr(self):
        """Test the __repr__ method."""
        action = TestAction(name="MyAction", test_param="value")
        repr_str = repr(action)
        
        self.assertIn("TestAction", repr_str)
        self.assertIn("name='MyAction'", repr_str)
        self.assertIn("test_param=", repr_str)
    
    def test_str(self):
        """Test the __str__ method."""
        action = TestAction(name="MyAction")
        self.assertEqual(str(action), "TestAction: MyAction")


if __name__ == '__main__':
    unittest.main()