import unittest
from unittest.mock import Mock
from typing import Dict, Any
from abc import ABC, abstractmethod

from src.core.interfaces import IWebDriver, IAction
from src.core.action_base import ActionBase
from src.core.action_result import ActionResult, ActionStatus


class TestActionBase(unittest.TestCase):
    """
    Tests for the ActionBase abstract class to ensure it provides
    common functionality for all action implementations.
    """

    def test_action_base_is_abstract(self):
        """Test that ActionBase is an abstract class that can't be instantiated directly."""
        with self.assertRaises(TypeError):
            ActionBase("test_action")

    def test_action_base_implements_iaction(self):
        """Test that ActionBase implements the IAction interface."""
        # Create a concrete subclass of ActionBase for testing
        class ConcreteAction(ActionBase):
            def execute(self, driver: IWebDriver) -> ActionResult:
                return ActionResult(ActionStatus.SUCCESS)

            def to_dict(self) -> Dict[str, Any]:
                return {"type": "ConcreteAction", "name": self.name}

        # Create an instance of the concrete subclass
        action = ConcreteAction("test_action")

        # Verify it's an instance of IAction
        self.assertIsInstance(action, IAction)

    def test_action_base_initialization(self):
        """Test that ActionBase subclasses can be initialized with a name."""
        # Create a concrete subclass of ActionBase for testing
        class ConcreteAction(ActionBase):
            def execute(self, driver: IWebDriver) -> ActionResult:
                return ActionResult(ActionStatus.SUCCESS)

            def to_dict(self) -> Dict[str, Any]:
                return {"type": "ConcreteAction", "name": self.name}

        # Create an instance of the concrete subclass
        action = ConcreteAction("test_action")

        # Verify the name was set correctly
        self.assertEqual(action.name, "test_action")

    def test_action_base_validate_method(self):
        """Test that ActionBase provides a validate method that can be overridden."""
        # Create a concrete subclass of ActionBase for testing
        class ConcreteAction(ActionBase):
            def execute(self, driver: IWebDriver) -> ActionResult:
                return ActionResult(ActionStatus.SUCCESS)

            def to_dict(self) -> Dict[str, Any]:
                return {"type": "ConcreteAction", "name": self.name}

            def validate(self) -> bool:
                return len(self.name) > 0

        # Create an instance of the concrete subclass
        action = ConcreteAction("test_action")

        # Verify the validate method works
        self.assertTrue(action.validate())

        # Create an instance with an invalid name
        action_invalid = ConcreteAction("")

        # Verify the validate method returns False
        self.assertFalse(action_invalid.validate())


class TestActionResult(unittest.TestCase):
    """
    Tests for the ActionResult class to ensure it properly represents
    the result of an action execution.
    """

    def test_action_result_initialization(self):
        """Test that ActionResult can be initialized with a status and optional message."""
        # Create an ActionResult with just a status
        result = ActionResult(ActionStatus.SUCCESS)

        # Verify the status was set correctly and message is None
        self.assertEqual(result.status, ActionStatus.SUCCESS)
        self.assertIsNone(result.message)

        # Create an ActionResult with a status and message
        result_with_message = ActionResult(ActionStatus.FAILURE, "Failed to execute action")

        # Verify both status and message were set correctly
        self.assertEqual(result_with_message.status, ActionStatus.FAILURE)
        self.assertEqual(result_with_message.message, "Failed to execute action")

    def test_action_result_success_factory_method(self):
        """Test the success factory method for creating success results."""
        # Create a success result without a message
        result = ActionResult.success()

        # Verify it's a success result with no message
        self.assertEqual(result.status, ActionStatus.SUCCESS)
        self.assertIsNone(result.message)

        # Create a success result with a message
        result_with_message = ActionResult.success("Action completed successfully")

        # Verify it's a success result with the correct message
        self.assertEqual(result_with_message.status, ActionStatus.SUCCESS)
        self.assertEqual(result_with_message.message, "Action completed successfully")

    def test_action_result_failure_factory_method(self):
        """Test the failure factory method for creating failure results."""
        # Create a failure result without a message
        result = ActionResult.failure()

        # Verify it's a failure result with a default message
        self.assertEqual(result.status, ActionStatus.FAILURE)
        self.assertEqual(result.message, "Action failed")

        # Create a failure result with a message
        result_with_message = ActionResult.failure("Failed due to network error")

        # Verify it's a failure result with the correct message
        self.assertEqual(result_with_message.status, ActionStatus.FAILURE)
        self.assertEqual(result_with_message.message, "Failed due to network error")

    def test_action_result_is_success_method(self):
        """Test the is_success method for checking if a result is successful."""
        # Create a success result
        success_result = ActionResult(ActionStatus.SUCCESS)

        # Verify is_success returns True
        self.assertTrue(success_result.is_success())

        # Create a failure result
        failure_result = ActionResult(ActionStatus.FAILURE)

        # Verify is_success returns False
        self.assertFalse(failure_result.is_success())

    def test_action_result_string_representation(self):
        """Test that ActionResult has a meaningful string representation."""
        # Create a success result with a message
        success_result = ActionResult(ActionStatus.SUCCESS, "Action completed successfully")

        # Verify the string representation
        self.assertEqual(str(success_result), "Success: Action completed successfully")

        # Create a failure result with a message
        failure_result = ActionResult(ActionStatus.FAILURE, "Failed due to network error")

        # Verify the string representation
        self.assertEqual(str(failure_result), "Failure: Failed due to network error")


if __name__ == "__main__":
    unittest.main()
