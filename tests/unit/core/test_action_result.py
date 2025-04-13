"""Tests for the ActionResult entity module."""

import unittest
import json
from src.core.action_result import ActionResult, ActionStatus


class TestActionResultEntity(unittest.TestCase):
    """
    Tests for the ActionResult class to ensure it properly represents
    the result of an action execution.
    """

    def test_initialization(self):
        """Test that ActionResult can be initialized with a status and optional message."""
        # Create an ActionResult with just a status
        result = ActionResult(ActionStatus.SUCCESS)

        # Verify the status was set correctly and message is None
        self.assertEqual(result.status, ActionStatus.SUCCESS)
        self.assertIsNone(result.message)
        self.assertEqual(result.data, {})

        # Create an ActionResult with a status and message
        result_with_message = ActionResult(ActionStatus.FAILURE, "Failed to execute action")

        # Verify both status and message were set correctly
        self.assertEqual(result_with_message.status, ActionStatus.FAILURE)
        self.assertEqual(result_with_message.message, "Failed to execute action")
        self.assertEqual(result_with_message.data, {})

        # Create an ActionResult with a status, message, and data
        data = {"error_code": 404, "details": "Page not found"}
        result_with_data = ActionResult(ActionStatus.FAILURE, "Failed to execute action", data)

        # Verify all fields were set correctly
        self.assertEqual(result_with_data.status, ActionStatus.FAILURE)
        self.assertEqual(result_with_data.message, "Failed to execute action")
        self.assertEqual(result_with_data.data, data)

    def test_initialization_with_invalid_status(self):
        """Test that ActionResult raises TypeError when initialized with an invalid status."""
        with self.assertRaises(TypeError):
            ActionResult("success")  # Not an ActionStatus enum

    def test_success_factory_method(self):
        """Test the success factory method for creating success results."""
        # Create a success result without a message
        result = ActionResult.success()

        # Verify it's a success result with no message
        self.assertEqual(result.status, ActionStatus.SUCCESS)
        self.assertIsNone(result.message)
        self.assertEqual(result.data, {})

        # Create a success result with a message
        result_with_message = ActionResult.success("Action completed successfully")

        # Verify it's a success result with the correct message
        self.assertEqual(result_with_message.status, ActionStatus.SUCCESS)
        self.assertEqual(result_with_message.message, "Action completed successfully")
        self.assertEqual(result_with_message.data, {})

        # Create a success result with a message and data
        data = {"value": "test", "count": 42}
        result_with_data = ActionResult.success("Action completed successfully", data)

        # Verify it's a success result with the correct message and data
        self.assertEqual(result_with_data.status, ActionStatus.SUCCESS)
        self.assertEqual(result_with_data.message, "Action completed successfully")
        self.assertEqual(result_with_data.data, data)

    def test_failure_factory_method(self):
        """Test the failure factory method for creating failure results."""
        # Create a failure result without a message
        result = ActionResult.failure()

        # Verify it's a failure result with a default message
        self.assertEqual(result.status, ActionStatus.FAILURE)
        self.assertEqual(result.message, "Action failed")
        self.assertEqual(result.data, {})

        # Create a failure result with a message
        result_with_message = ActionResult.failure("Failed due to network error")

        # Verify it's a failure result with the correct message
        self.assertEqual(result_with_message.status, ActionStatus.FAILURE)
        self.assertEqual(result_with_message.message, "Failed due to network error")
        self.assertEqual(result_with_message.data, {})

        # Create a failure result with a message and data
        data = {"error_code": 500, "details": "Internal server error"}
        result_with_data = ActionResult.failure("Failed due to server error", data)

        # Verify it's a failure result with the correct message and data
        self.assertEqual(result_with_data.status, ActionStatus.FAILURE)
        self.assertEqual(result_with_data.message, "Failed due to server error")
        self.assertEqual(result_with_data.data, data)

    def test_is_success_method(self):
        """Test the is_success method for checking if a result is successful."""
        # Create a success result
        success_result = ActionResult(ActionStatus.SUCCESS)

        # Verify is_success returns True
        self.assertTrue(success_result.is_success())

        # Create a failure result
        failure_result = ActionResult(ActionStatus.FAILURE)

        # Verify is_success returns False
        self.assertFalse(failure_result.is_success())

    def test_to_dict_method(self):
        """Test the to_dict method for serializing an ActionResult."""
        # Create an ActionResult with all fields
        data = {"error_code": 404, "details": "Page not found"}
        result = ActionResult(ActionStatus.FAILURE, "Failed to execute action", data)

        # Get the dictionary representation
        result_dict = result.to_dict()

        # Verify the dictionary contains all fields
        self.assertEqual(result_dict["status"], "failure")
        self.assertEqual(result_dict["message"], "Failed to execute action")
        self.assertEqual(result_dict["data"], data)

    def test_from_dict_method(self):
        """Test the from_dict method for deserializing an ActionResult."""
        # Create a dictionary representation
        result_dict = {
            "status": "success",
            "message": "Action completed successfully",
            "data": {"value": "test", "count": 42}
        }

        # Create an ActionResult from the dictionary
        result = ActionResult.from_dict(result_dict)

        # Verify all fields were set correctly
        self.assertEqual(result.status, ActionStatus.SUCCESS)
        self.assertEqual(result.message, "Action completed successfully")
        self.assertEqual(result.data, {"value": "test", "count": 42})

        # Test with missing status (should default to FAILURE)
        result_dict = {
            "message": "Action failed",
            "data": {"error": "test"}
        }

        result = ActionResult.from_dict(result_dict)
        self.assertEqual(result.status, ActionStatus.FAILURE)
        self.assertEqual(result.message, "Action failed")
        self.assertEqual(result.data, {"error": "test"})

    def test_string_representation(self):
        """Test that ActionResult has a meaningful string representation."""
        # Create a success result with a message
        success_result = ActionResult(ActionStatus.SUCCESS, "Action completed successfully")

        # Verify the string representation
        self.assertEqual(str(success_result), "Success: Action completed successfully")

        # Create a failure result with a message
        failure_result = ActionResult(ActionStatus.FAILURE, "Failed due to network error")

        # Verify the string representation
        self.assertEqual(str(failure_result), "Failure: Failed due to network error")

        # Create a result without a message
        result_without_message = ActionResult(ActionStatus.SUCCESS)

        # Verify the string representation
        self.assertEqual(str(result_without_message), "Success")

    def test_repr_representation(self):
        """Test that ActionResult has a meaningful repr representation."""
        # Create an ActionResult with all fields
        data = {"error_code": 404, "details": "Page not found"}
        result = ActionResult(ActionStatus.FAILURE, "Failed to execute action", data)

        # Verify the repr representation
        expected_repr = "ActionResult(status=ActionStatus.FAILURE, message='Failed to execute action', data={'error_code': 404, 'details': 'Page not found'})"
        self.assertEqual(repr(result), expected_repr)


if __name__ == "__main__":
    unittest.main()
