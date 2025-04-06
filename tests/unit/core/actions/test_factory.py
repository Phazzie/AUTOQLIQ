"""Tests for the action factory module."""
import unittest
from unittest.mock import patch

from src.core.interfaces import IAction
from src.core.actions.factory import ActionFactory
from src.core.actions.navigation import NavigateAction
from src.core.actions.interaction import ClickAction, TypeAction
from src.core.actions.utility import WaitAction, ScreenshotAction

class TestActionFactory(unittest.TestCase):
    """Test cases for the ActionFactory class."""

    def test_create_action_navigate(self):
        """Test that create_action creates a NavigateAction."""
        action_data = {
            "type": "Navigate",
            "url": "https://example.com",
            "name": "Custom Name"
        }
        
        action = ActionFactory.create_action(action_data)
        
        self.assertIsInstance(action, NavigateAction)
        self.assertEqual(action.url, "https://example.com")
        self.assertEqual(action.name, "Custom Name")

    def test_create_action_click(self):
        """Test that create_action creates a ClickAction."""
        action_data = {
            "type": "Click",
            "selector": "#button",
            "name": "Custom Name",
            "check_success_selector": "#success",
            "check_failure_selector": "#failure"
        }
        
        action = ActionFactory.create_action(action_data)
        
        self.assertIsInstance(action, ClickAction)
        self.assertEqual(action.selector, "#button")
        self.assertEqual(action.name, "Custom Name")
        self.assertEqual(action.check_success_selector, "#success")
        self.assertEqual(action.check_failure_selector, "#failure")

    def test_create_action_type(self):
        """Test that create_action creates a TypeAction."""
        action_data = {
            "type": "Type",
            "selector": "#input",
            "value_type": "text",
            "value_key": "test",
            "name": "Custom Name"
        }
        
        action = ActionFactory.create_action(action_data)
        
        self.assertIsInstance(action, TypeAction)
        self.assertEqual(action.selector, "#input")
        self.assertEqual(action.value_type, "text")
        self.assertEqual(action.value_key, "test")
        self.assertEqual(action.name, "Custom Name")

    def test_create_action_wait(self):
        """Test that create_action creates a WaitAction."""
        action_data = {
            "type": "Wait",
            "duration_seconds": 5,
            "name": "Custom Name"
        }
        
        action = ActionFactory.create_action(action_data)
        
        self.assertIsInstance(action, WaitAction)
        self.assertEqual(action.duration_seconds, 5)
        self.assertEqual(action.name, "Custom Name")

    def test_create_action_screenshot(self):
        """Test that create_action creates a ScreenshotAction."""
        action_data = {
            "type": "Screenshot",
            "file_path": "screenshot.png",
            "name": "Custom Name"
        }
        
        action = ActionFactory.create_action(action_data)
        
        self.assertIsInstance(action, ScreenshotAction)
        self.assertEqual(action.file_path, "screenshot.png")
        self.assertEqual(action.name, "Custom Name")

    def test_create_action_unsupported(self):
        """Test that create_action raises ValueError for unsupported action types."""
        action_data = {
            "type": "Unsupported",
            "name": "Custom Name"
        }
        
        with self.assertRaises(ValueError):
            ActionFactory.create_action(action_data)

    def test_register_action(self):
        """Test that register_action adds a new action type to the registry."""
        # Create a mock action class
        class MockAction(IAction):
            def __init__(self, name="Mock", param=None):
                self.name = name
                self.param = param
            
            def execute(self, driver):
                pass
            
            def to_dict(self):
                return {"type": "Mock", "name": self.name, "param": self.param}
        
        # Register the mock action
        ActionFactory.register_action("Mock", MockAction)
        
        # Create an action using the factory
        action_data = {
            "type": "Mock",
            "name": "Custom Name",
            "param": "test"
        }
        
        action = ActionFactory.create_action(action_data)
        
        self.assertIsInstance(action, MockAction)
        self.assertEqual(action.name, "Custom Name")
        self.assertEqual(action.param, "test")
        
        # Clean up by removing the mock action from the registry
        del ActionFactory._registry["Mock"]

if __name__ == "__main__":
    unittest.main()
