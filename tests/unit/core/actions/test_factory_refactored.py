"""Tests for the refactored action factory module."""
import unittest
from unittest.mock import patch, MagicMock

from src.core.interfaces import IAction
from src.core.actions.factory import ActionFactory
from src.core.actions.base import ActionBase
from src.core.actions.registry import ActionRegistry
from src.core.actions.validator import ActionValidator
from src.core.actions.nested_handler import NestedActionHandler
from src.core.actions.creator import ActionCreator


class TestActionFactoryRefactored(unittest.TestCase):
    """Test cases for the refactored ActionFactory class."""

    def setUp(self):
        """Set up test fixtures."""
        # Reset the ActionFactory components
        ActionFactory._registry = ActionRegistry()
        ActionFactory._validator = ActionValidator()
        ActionFactory._nested_handler = None
        ActionFactory._creator = None

    def test_register_action(self):
        """Test that register_action delegates to the registry."""
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

        # Create a spy on the registry's register_action method
        with patch.object(ActionFactory._registry, 'register_action', wraps=ActionFactory._registry.register_action) as mock_register:
            # Register the mock action
            ActionFactory.register_action(MockAction)

            # Check that the registry's register_action method was called
            mock_register.assert_called_once_with(MockAction)

            # Check that the action was registered
            self.assertEqual(ActionFactory._registry.get_action_class("Mock"), MockAction)

    def test_get_registered_action_types(self):
        """Test that get_registered_action_types delegates to the registry."""
        # Create a spy on the registry's get_registered_types method
        with patch.object(ActionFactory._registry, 'get_registered_types', wraps=ActionFactory._registry.get_registered_types) as mock_get_types:
            # Call get_registered_action_types
            types = ActionFactory.get_registered_action_types()

            # Check that the registry's get_registered_types method was called
            mock_get_types.assert_called_once()

            # Check that the result was returned
            self.assertEqual(types, ActionFactory._registry.get_registered_types())

    def test_create_action(self):
        """Test that create_action initializes components and delegates to the creator."""
        # Create action data
        action_data = {
            "type": "Navigate",
            "url": "https://example.com",
            "name": "Custom Name"
        }

        # Create a mock action
        mock_action = MagicMock(spec=IAction)

        # Create a spy on the _initialize_components method
        with patch.object(ActionFactory, '_initialize_components', wraps=ActionFactory._initialize_components) as mock_init:
            # Create a mock creator that returns the mock action
            mock_creator = MagicMock()
            mock_creator.create_action.return_value = mock_action
            ActionFactory._creator = mock_creator

            # Call create_action
            action = ActionFactory.create_action(action_data)

            # Check that _initialize_components was called
            mock_init.assert_called_once()

            # Check that the creator's create_action method was called
            mock_creator.create_action.assert_called_once_with(action_data)

            # Check that the mock action was returned
            self.assertEqual(action, mock_action)

    def test_initialize_components(self):
        """Test that _initialize_components initializes the components correctly."""
        # Call _initialize_components
        ActionFactory._initialize_components()

        # Check that the nested handler was created
        self.assertIsInstance(ActionFactory._nested_handler, NestedActionHandler)

        # Check that the creator was created
        self.assertIsInstance(ActionFactory._creator, ActionCreator)

        # Check that the nested handler uses the create_action method
        self.assertEqual(ActionFactory._nested_handler._action_creator_func, ActionFactory.create_action)

        # Check that the creator uses the registry, validator, and nested handler
        self.assertEqual(ActionFactory._creator._registry, ActionFactory._registry)
        self.assertEqual(ActionFactory._creator._validator, ActionFactory._validator)
        self.assertEqual(ActionFactory._creator._nested_handler, ActionFactory._nested_handler)


if __name__ == "__main__":
    unittest.main()
