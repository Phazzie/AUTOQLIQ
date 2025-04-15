"""Tests for status analyzer."""

import unittest
from unittest.mock import MagicMock, patch

from src.core.action_result import ActionResult
from src.core.exceptions import ActionError, WorkflowError
from src.core.workflow.result_processing.status_analyzer import StatusAnalyzer
from src.core.workflow.result_processing.interfaces import (
    IErrorStatusAnalyzer, IResultStatusAnalyzer
)


class TestStatusAnalyzer(unittest.TestCase):
    """Test cases for status analyzer."""

    def setUp(self):
        """Set up test fixtures."""
        # Create mock dependencies
        self.mock_error_analyzer = MagicMock(spec=IErrorStatusAnalyzer)
        self.mock_result_analyzer = MagicMock(spec=IResultStatusAnalyzer)

        # Create the analyzer with mock dependencies
        self.analyzer = StatusAnalyzer(
            error_analyzer=self.mock_error_analyzer,
            result_analyzer=self.mock_result_analyzer
        )

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
        # Set up mock return value
        self.mock_result_analyzer.analyze_results.return_value = (
            "SUCCESS", None, "All 3 actions completed successfully"
        )

        # Call the method
        status, error_message, summary = self.analyzer.determine_status(
            action_results=self.results_all_success
        )

        # Verify the result
        self.assertEqual(status, "SUCCESS")
        self.assertIsNone(error_message)
        self.assertEqual(summary, "All 3 actions completed successfully")

        # Verify the mock was called
        self.mock_result_analyzer.analyze_results.assert_called_once_with(self.results_all_success)
        self.mock_error_analyzer.analyze_error.assert_not_called()

    def test_determine_status_with_failures(self):
        """Test determining status for a workflow with failures."""
        # Set up mock return value
        self.mock_result_analyzer.analyze_results.return_value = (
            "COMPLETED_WITH_ERRORS", "1 action(s) failed", "Completed with 2 successful actions and 1 failures"
        )

        # Call the method
        status, error_message, summary = self.analyzer.determine_status(
            action_results=self.results_with_failure
        )

        # Verify the result
        self.assertEqual(status, "COMPLETED_WITH_ERRORS")
        self.assertEqual(error_message, "1 action(s) failed")
        self.assertEqual(summary, "Completed with 2 successful actions and 1 failures")

        # Verify the mock was called
        self.mock_result_analyzer.analyze_results.assert_called_once_with(self.results_with_failure)
        self.mock_error_analyzer.analyze_error.assert_not_called()

    def test_determine_status_with_action_error(self):
        """Test determining status for a workflow with an action error."""
        # Set up mock return value
        self.mock_error_analyzer.analyze_error.return_value = (
            "FAILED", "Test action error", "Failed during action 'TestAction': Test action error"
        )

        # Call the method
        status, error_message, summary = self.analyzer.determine_status(
            action_results=self.results_all_success,
            error=self.action_error
        )

        # Verify the result
        self.assertEqual(status, "FAILED")
        self.assertEqual(error_message, "Test action error")
        self.assertEqual(summary, "Failed during action 'TestAction': Test action error")

        # Verify the mock was called
        self.mock_error_analyzer.analyze_error.assert_called_once_with(self.action_error)
        self.mock_result_analyzer.analyze_results.assert_not_called()

    def test_determine_status_with_workflow_error(self):
        """Test determining status for a workflow with a workflow error."""
        # Set up mock return value
        self.mock_error_analyzer.analyze_error.return_value = (
            "FAILED", "Test workflow error", "Workflow error: Test workflow error"
        )

        # Call the method
        status, error_message, summary = self.analyzer.determine_status(
            action_results=self.results_all_success,
            error=self.workflow_error
        )

        # Verify the result
        self.assertEqual(status, "FAILED")
        self.assertEqual(error_message, "Test workflow error")
        self.assertEqual(summary, "Workflow error: Test workflow error")

        # Verify the mock was called
        self.mock_error_analyzer.analyze_error.assert_called_once_with(self.workflow_error)
        self.mock_result_analyzer.analyze_results.assert_not_called()

    def test_determine_status_with_stop_error(self):
        """Test determining status for a workflow that was stopped."""
        # Set up mock return value
        self.mock_error_analyzer.analyze_error.return_value = (
            "STOPPED", "Execution stopped by user request.", "Execution stopped by user request"
        )

        # Call the method
        status, error_message, summary = self.analyzer.determine_status(
            action_results=self.results_all_success,
            error=self.stop_error
        )

        # Verify the result
        self.assertEqual(status, "STOPPED")
        self.assertEqual(error_message, "Execution stopped by user request.")
        self.assertEqual(summary, "Execution stopped by user request")

        # Verify the mock was called
        self.mock_error_analyzer.analyze_error.assert_called_once_with(self.stop_error)
        self.mock_result_analyzer.analyze_results.assert_not_called()

    def test_determine_status_with_generic_error(self):
        """Test determining status for a workflow with a generic error."""
        # Set up mock return value
        self.mock_error_analyzer.analyze_error.return_value = (
            "FAILED", "Unexpected error: Test generic error", "Unexpected error: Test generic error"
        )

        # Call the method
        status, error_message, summary = self.analyzer.determine_status(
            action_results=self.results_all_success,
            error=self.generic_error
        )

        # Verify the result
        self.assertEqual(status, "FAILED")
        self.assertEqual(error_message, "Unexpected error: Test generic error")
        self.assertEqual(summary, "Unexpected error: Test generic error")

        # Verify the mock was called
        self.mock_error_analyzer.analyze_error.assert_called_once_with(self.generic_error)
        self.mock_result_analyzer.analyze_results.assert_not_called()






if __name__ == "__main__":
    unittest.main()
