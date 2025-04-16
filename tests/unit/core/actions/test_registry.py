"""Tests for the action registry module."""
import unittest
from unittest.mock import patch, MagicMock

from src.core.actions.base import ActionBase
from src.core.actions.registry import ActionRegistry


class TestActionRegistry(unittest.TestCase):
    """Test cases for the ActionRegistry class."""

    def setUp(self):
        """Set up test fixtures."""
        self.registry = ActionRegistry()

    def test_register_action(self):
        """Test that register_action adds a new action type to the registry."""
        # Create a mock action class
        class MockAction(ActionBase):
            action_type = "Mock"

            def __init__(self, name="Mock", param=None):
                super().__init__(name=name)
                self.param = param

            def execute(self, driver, credential_repo=None, context=None):
                return None

            def to_dict(self):
                return {"type": "Mock", "name": self.name, "param": self.param}

        # Register the mock action
        self.registry.register_action(MockAction)

        # Check that the action was registered
        self.assertEqual(self.registry.get_action_class("Mock"), MockAction)

    def test_register_action_invalid_class(self):
        """Test that register_action raises ValueError for invalid action classes."""
        # Create a class that doesn't inherit from ActionBase
        class InvalidAction:
            action_type = "Invalid"

        # Try to register the invalid action
        with self.assertRaises(ValueError):
            self.registry.register_action(InvalidAction)

    def test_register_action_missing_action_type(self):
        """Test that register_action raises ValueError for action classes without action_type."""
        # Create a class that inherits from ActionBase but doesn't define action_type
        class NoTypeAction(ActionBase):
            # Explicitly set action_type to None to ensure the test works
            action_type = None

            def execute(self, driver, credential_repo=None, context=None):
                return None

            def to_dict(self):
                return {"type": "NoType", "name": self.name}

        # Try to register the action without action_type
        with self.assertRaises(ValueError):
            self.registry.register_action(NoTypeAction)

    def test_get_action_class(self):
        """Test that get_action_class returns the correct action class."""
        # Create a mock action class
        class MockAction(ActionBase):
            action_type = "Mock"

            def execute(self, driver, credential_repo=None, context=None):
                return None

            def to_dict(self):
                return {"type": "Mock", "name": self.name}

        # Register the mock action
        self.registry.register_action(MockAction)

        # Check that get_action_class returns the correct class
        self.assertEqual(self.registry.get_action_class("Mock"), MockAction)

        # Check that get_action_class returns None for unknown action types
        self.assertIsNone(self.registry.get_action_class("Unknown"))

    def test_get_registered_types(self):
        """Test that get_registered_types returns a sorted list of action types."""
        # Create mock action classes
        class MockAction1(ActionBase):
            action_type = "MockA"

            def execute(self, driver, credential_repo=None, context=None):
                return None

            def to_dict(self):
                return {"type": "MockA", "name": self.name}

        class MockAction2(ActionBase):
            action_type = "MockB"

            def execute(self, driver, credential_repo=None, context=None):
                return None

            def to_dict(self):
                return {"type": "MockB", "name": self.name}

        class MockAction3(ActionBase):
            action_type = "MockC"

            def execute(self, driver, credential_repo=None, context=None):
                return None

            def to_dict(self):
                return {"type": "MockC", "name": self.name}

        # Register the mock actions
        self.registry.register_action(MockAction2)
        self.registry.register_action(MockAction1)
        self.registry.register_action(MockAction3)

        # Check that get_registered_types returns a sorted list
        self.assertEqual(self.registry.get_registered_types(), ["MockA", "MockB", "MockC"])


if __name__ == "__main__":
    unittest.main()
