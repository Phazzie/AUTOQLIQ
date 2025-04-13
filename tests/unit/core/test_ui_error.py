#!/usr/bin/env python3
"""
Unit tests for UIError class in src/core/exceptions.py.
"""

import unittest
from unittest.mock import MagicMock

# Import the module under test
from src.core.exceptions import UIError, AutoQliqError


class TestUIError(unittest.TestCase):
    """
    Test cases for the UIError exception class.
    
    This test suite verifies that UIError properly inherits from AutoQliqError
    and provides the expected behavior for UI-related exceptions.
    """
    
    def test_init_with_basic_message(self):
        """Test initialization with a basic error message."""
        # Create a UIError with a basic message
        error = UIError("Failed to create widget")
        
        # Verify attributes
        self.assertEqual(str(error), "Failed to create widget")
        self.assertEqual(error.message, "Failed to create widget")
        self.assertIsNone(error.component_name)
        self.assertIsNone(error.cause)
        self.assertIsNone(error.ui_context)
        
        # Verify it inherits from AutoQliqError
        self.assertIsInstance(error, AutoQliqError)
    
    def test_init_with_component_name(self):
        """Test initialization with a component name."""
        # Create a UIError with a component name
        error = UIError("Failed to create button", component_name="Button")
        
        # Verify attributes
        self.assertEqual(str(error), "Failed to create button (Component: Button)")
        self.assertEqual(error.message, "Failed to create button")
        self.assertEqual(error.component_name, "Button")
        self.assertIsNone(error.cause)
        self.assertIsNone(error.ui_context)
    
    def test_init_with_cause(self):
        """Test initialization with a cause exception."""
        # Create a cause exception
        cause = ValueError("Invalid parameter")
        
        # Create a UIError with a cause
        error = UIError("Failed to create widget", cause=cause)
        
        # Verify attributes
        self.assertEqual(str(error), "Failed to create widget (Cause: Invalid parameter)")
        self.assertEqual(error.message, "Failed to create widget")
        self.assertIsNone(error.component_name)
        self.assertEqual(error.cause, cause)
        self.assertIsNone(error.ui_context)
    
    def test_init_with_ui_context(self):
        """Test initialization with UI context."""
        # Create UI context
        ui_context = {"window": "main", "action": "button_click"}
        
        # Create a UIError with UI context
        error = UIError("Failed to process action", ui_context=ui_context)
        
        # Verify attributes
        self.assertEqual(str(error), "Failed to process action (UI Context: {'window': 'main', 'action': 'button_click'})")
        self.assertEqual(error.message, "Failed to process action")
        self.assertIsNone(error.component_name)
        self.assertIsNone(error.cause)
        self.assertEqual(error.ui_context, ui_context)
    
    def test_init_with_all_parameters(self):
        """Test initialization with all parameters."""
        # Create a cause exception
        cause = ValueError("Invalid parameter")
        
        # Create UI context
        ui_context = {"window": "main", "action": "button_click"}
        
        # Create a UIError with all parameters
        error = UIError(
            "Failed to create button",
            component_name="Button",
            cause=cause,
            ui_context=ui_context
        )
        
        # Verify attributes
        expected_message = "Failed to create button (Component: Button) (Cause: Invalid parameter) (UI Context: {'window': 'main', 'action': 'button_click'})"
        self.assertEqual(str(error), expected_message)
        self.assertEqual(error.message, "Failed to create button")
        self.assertEqual(error.component_name, "Button")
        self.assertEqual(error.cause, cause)
        self.assertEqual(error.ui_context, ui_context)
    
    def test_with_context(self):
        """Test the with_context method."""
        # Create a UIError
        error = UIError("Failed to create widget")
        
        # Create UI context
        ui_context = {"window": "main", "action": "button_click"}
        
        # Add context
        new_error = error.with_context(ui_context)
        
        # Verify the new error
        self.assertEqual(new_error.message, "Failed to create widget")
        self.assertIsNone(new_error.component_name)
        self.assertIsNone(new_error.cause)
        self.assertEqual(new_error.ui_context, ui_context)
        
        # Original error should not be modified
        self.assertIsNone(error.ui_context)
    
    def test_with_component(self):
        """Test the with_component method."""
        # Create a UIError
        error = UIError("Failed to create widget")
        
        # Add component name
        new_error = error.with_component("Button")
        
        # Verify the new error
        self.assertEqual(new_error.message, "Failed to create widget")
        self.assertEqual(new_error.component_name, "Button")
        self.assertIsNone(new_error.cause)
        self.assertIsNone(new_error.ui_context)
        
        # Original error should not be modified
        self.assertIsNone(error.component_name)
    
    def test_from_exception(self):
        """Test the from_exception class method."""
        # Create an exception
        exception = ValueError("Invalid parameter")
        
        # Create a UIError from the exception
        error = UIError.from_exception(
            exception,
            "Failed to process widget",
            component_name="Button"
        )
        
        # Verify attributes
        self.assertEqual(str(error), "Failed to process widget (Component: Button) (Cause: Invalid parameter)")
        self.assertEqual(error.message, "Failed to process widget")
        self.assertEqual(error.component_name, "Button")
        self.assertEqual(error.cause, exception)
        self.assertIsNone(error.ui_context)


if __name__ == '__main__':
    unittest.main()