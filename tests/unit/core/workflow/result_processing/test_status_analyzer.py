"""Tests for status analyzer."""

import unittest
from unittest.mock import MagicMock, patch

from src.core.action_result import ActionResult
from src.core.exceptions import ActionError, WorkflowError
from src.core.workflow.result_processing.status_analyzer import StatusAnalyzer


class TestStatusAnalyzer(unittest.TestCase):
    """Test cases for status analyzer."""

    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = StatusAnalyzer()
        
        # Create some test results
        self.success_result = ActionResult.success("Success")
        self.failure_result = ActionResult.failure("Failure")
        self.results_all_success = [
            ActionResult.success("Success 1"),
            ActionResult.success("Success 2"),
            ActionResult.success("Success 3")
        ]
        self.results_with_failure = [
            ActionResult.success("Success 1"),
            ActionResult.failure("Failure 1"),
            ActionResult.success("Success 2")
        ]
        
        # Create some test errors
        self.action_error = ActionError("Test action error", action_name="TestAction")
        self.workflow_error = WorkflowError("Test workflow error")
        self.stop_error = WorkflowError("Workflow execution stopped by request")
        self.generic_error = Exception("Test generic error")

    def test_determine_status_success(self):
        """Test determining status for a successful workflow."""
        status, error_message, summary = self.analyzer.determine_status(
            action_results=self.results_all_success
        )
        
        self.assertEqual(status, "SUCCESS")
        self.assertIsNone(error_message)
        self.assertIn("All 3 actions completed successfully", summary)

    def test_determine_status_with_failures(self):
        """Test determining status for a workflow with failures."""
        status, error_message, summary = self.analyzer.determine_status(
            action_results=self.results_with_failure
        )
        
        self.assertEqual(status, "COMPLETED_WITH_ERRORS")
        self.assertIsNotNone(error_message)
        self.assertIn("1 action(s) failed", error_message)
        self.assertIn("Completed with 2 successful actions and 1 failures", summary)

    def test_determine_status_with_action_error(self):
        """Test determining status for a workflow with an action error."""
        status, error_message, summary = self.analyzer.determine_status(
            action_results=self.results_all_success,
            error=self.action_error
        )
        
        self.assertEqual(status, "FAILED")
        self.assertIn("Test action error", error_message)
        self.assertIn("Failed during action 'TestAction'", summary)

    def test_determine_status_with_workflow_error(self):
        """Test determining status for a workflow with a workflow error."""
        status, error_message, summary = self.analyzer.determine_status(
            action_results=self.results_all_success,
            error=self.workflow_error
        )
        
        self.assertEqual(status, "FAILED")
        self.assertIn("Test workflow error", error_message)
        self.assertIn("Workflow error", summary)

    def test_determine_status_with_stop_error(self):
        """Test determining status for a workflow that was stopped."""
        status, error_message, summary = self.analyzer.determine_status(
            action_results=self.results_all_success,
            error=self.stop_error
        )
        
        self.assertEqual(status, "STOPPED")
        self.assertIn("stopped by request", error_message.lower())
        self.assertIn("stopped by request", summary.lower())

    def test_determine_status_with_generic_error(self):
        """Test determining status for a workflow with a generic error."""
        status, error_message, summary = self.analyzer.determine_status(
            action_results=self.results_all_success,
            error=self.generic_error
        )
        
        self.assertEqual(status, "FAILED")
        self.assertIn("Test generic error", error_message)
        self.assertIn("Unexpected error", summary)

    def test_analyze_error(self):
        """Test analyzing different types of errors."""
        # Test with action error
        status, error_message, summary = self.analyzer._analyze_error(self.action_error)
        self.assertEqual(status, "FAILED")
        self.assertIn("Test action error", error_message)
        self.assertIn("Failed during action 'TestAction'", summary)
        
        # Test with workflow error
        status, error_message, summary = self.analyzer._analyze_error(self.workflow_error)
        self.assertEqual(status, "FAILED")
        self.assertIn("Test workflow error", error_message)
        self.assertIn("Workflow error", summary)
        
        # Test with stop error
        status, error_message, summary = self.analyzer._analyze_error(self.stop_error)
        self.assertEqual(status, "STOPPED")
        self.assertIn("stopped by request", error_message.lower())
        self.assertIn("stopped by request", summary.lower())
        
        # Test with generic error
        status, error_message, summary = self.analyzer._analyze_error(self.generic_error)
        self.assertEqual(status, "FAILED")
        self.assertIn("Test generic error", error_message)
        self.assertIn("Unexpected error", summary)

    def test_analyze_results(self):
        """Test analyzing action results."""
        # Test with all successful results
        status, error_message, summary = self.analyzer._analyze_results(self.results_all_success)
        self.assertEqual(status, "SUCCESS")
        self.assertIsNone(error_message)
        self.assertIn("All 3 actions completed successfully", summary)
        
        # Test with some failures
        status, error_message, summary = self.analyzer._analyze_results(self.results_with_failure)
        self.assertEqual(status, "COMPLETED_WITH_ERRORS")
        self.assertIn("1 action(s) failed", error_message)
        self.assertIn("Completed with 2 successful actions and 1 failures", summary)
        
        # Test with empty results
        status, error_message, summary = self.analyzer._analyze_results([])
        self.assertEqual(status, "SUCCESS")
        self.assertIsNone(error_message)
        self.assertIn("All 0 actions completed successfully", summary)


if __name__ == "__main__":
    unittest.main()
