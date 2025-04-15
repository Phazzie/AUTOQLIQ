"""Tests for error handlers."""

import unittest
from unittest.mock import MagicMock

from src.core.exceptions import ActionError, WorkflowError
from src.core.workflow.result_processing.error_handlers import (
    StopRequestHandler, ActionErrorHandler, WorkflowErrorHandler, GenericErrorHandler
)


class TestErrorHandlers(unittest.TestCase):
    """Test cases for error handlers."""

    def setUp(self):
        """Set up test fixtures."""
        # Create handlers
        self._stop_request_handler = StopRequestHandler()
        self._action_error_handler = ActionErrorHandler()
        self._workflow_error_handler = WorkflowErrorHandler()
        self._generic_error_handler = GenericErrorHandler()
        
        # Create test errors
        self._action_error = ActionError("Test action error", action_name="TestAction")
        self._workflow_error = WorkflowError("Test workflow error")
        self._stop_error = WorkflowError("Workflow execution stopped by request")
        self._generic_error = Exception("Test generic error")

    def test_stop_request_handler(self):
        """Test the stop request handler."""
        # Test can_handle
        self.assertTrue(self._stop_request_handler.can_handle(self._stop_error))
        self.assertFalse(self._stop_request_handler.can_handle(self._action_error))
        self.assertFalse(self._stop_request_handler.can_handle(self._workflow_error))
        self.assertFalse(self._stop_request_handler.can_handle(self._generic_error))
        
        # Test handle
        status, error_message, summary = self._stop_request_handler.handle(self._stop_error)
        self.assertEqual(status, "STOPPED")
        self.assertEqual(error_message, "Execution stopped by user request.")
        self.assertEqual(summary, "Execution stopped by user request")

    def test_action_error_handler(self):
        """Test the action error handler."""
        # Test can_handle
        self.assertTrue(self._action_error_handler.can_handle(self._action_error))
        self.assertFalse(self._action_error_handler.can_handle(self._workflow_error))
        self.assertFalse(self._action_error_handler.can_handle(self._stop_error))
        self.assertFalse(self._action_error_handler.can_handle(self._generic_error))
        
        # Test handle
        status, error_message, summary = self._action_error_handler.handle(self._action_error)
        self.assertEqual(status, "FAILED")
        self.assertEqual(error_message, str(self._action_error))
        self.assertEqual(summary, f"Failed during action 'TestAction': {self._action_error}")

    def test_workflow_error_handler(self):
        """Test the workflow error handler."""
        # Test can_handle
        self.assertTrue(self._workflow_error_handler.can_handle(self._workflow_error))
        self.assertTrue(self._workflow_error_handler.can_handle(self._stop_error))
        self.assertFalse(self._workflow_error_handler.can_handle(self._action_error))
        self.assertFalse(self._workflow_error_handler.can_handle(self._generic_error))
        
        # Test handle
        status, error_message, summary = self._workflow_error_handler.handle(self._workflow_error)
        self.assertEqual(status, "FAILED")
        self.assertEqual(error_message, str(self._workflow_error))
        self.assertEqual(summary, f"Workflow error: {self._workflow_error}")

    def test_generic_error_handler(self):
        """Test the generic error handler."""
        # Test can_handle
        self.assertTrue(self._generic_error_handler.can_handle(self._generic_error))
        self.assertTrue(self._generic_error_handler.can_handle(self._action_error))
        self.assertTrue(self._generic_error_handler.can_handle(self._workflow_error))
        self.assertTrue(self._generic_error_handler.can_handle(self._stop_error))
        
        # Test handle
        status, error_message, summary = self._generic_error_handler.handle(self._generic_error)
        self.assertEqual(status, "FAILED")
        self.assertEqual(error_message, f"Unexpected error: {self._generic_error}")
        self.assertEqual(summary, f"Unexpected error: {self._generic_error}")


if __name__ == "__main__":
    unittest.main()
