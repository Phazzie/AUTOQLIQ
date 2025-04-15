"""Tests for result processor."""

import unittest
from unittest.mock import MagicMock, patch
import time
from datetime import datetime

from src.core.action_result import ActionResult
from src.core.exceptions import ActionError, WorkflowError
from src.core.workflow.result_processing.processor import ResultProcessor
from src.core.workflow.result_processing.formatter import ResultFormatter
from src.core.workflow.result_processing.status_analyzer import StatusAnalyzer


class TestResultProcessor(unittest.TestCase):
    """Test cases for result processor."""

    def setUp(self):
        """Set up test fixtures."""
        # Create mock dependencies
        self.mock_formatter = MagicMock(spec=ResultFormatter)
        self.mock_status_analyzer = MagicMock(spec=StatusAnalyzer)

        # Create the processor with mock dependencies
        self.processor = ResultProcessor(
            formatter=self.mock_formatter,
            status_analyzer=self.mock_status_analyzer
        )

        self.workflow_name = "TestWorkflow"
        self.start_time = time.time()

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

        # Set up mock return values
        self.mock_formatter.format_action_results.return_value = [
            {"status": "success", "message": "Success 1"},
            {"status": "success", "message": "Success 2"},
            {"status": "success", "message": "Success 3"}
        ]

    def test_create_execution_log_success(self):
        """Test creating an execution log for a successful workflow."""
        # Set up mock return values
        self.mock_status_analyzer.determine_status.return_value = ("SUCCESS", None, "All actions completed successfully")

        log = self.processor.create_execution_log(
            workflow_name=self.workflow_name,
            action_results=self.results_all_success,
            start_time=self.start_time
        )

        # Verify the mock was called correctly
        self.mock_status_analyzer.determine_status.assert_called_once_with(self.results_all_success, None)
        self.mock_formatter.format_action_results.assert_called_once_with(self.results_all_success)

        # Verify the log structure
        self.assertEqual(log["workflow_name"], self.workflow_name)
        self.assertEqual(log["final_status"], "SUCCESS")
        self.assertIsNone(log["error_message"])
        self.assertEqual(len(log["action_results"]), 3)
        self.assertGreater(log["duration_seconds"], 0)

    def test_create_execution_log_with_failures(self):
        """Test creating an execution log for a workflow with failures."""
        # Set up mock return values
        self.mock_status_analyzer.determine_status.return_value = ("COMPLETED_WITH_ERRORS", "Some actions failed", "Completed with some actions failing")
        self.mock_formatter.format_action_results.return_value = [
            {"status": "success", "message": "Success 1"},
            {"status": "failure", "message": "Failure 1"},
            {"status": "success", "message": "Success 2"}
        ]

        log = self.processor.create_execution_log(
            workflow_name=self.workflow_name,
            action_results=self.results_with_failure,
            start_time=self.start_time
        )

        # Verify the mock was called correctly
        self.mock_status_analyzer.determine_status.assert_called_once_with(self.results_with_failure, None)
        self.mock_formatter.format_action_results.assert_called_once_with(self.results_with_failure)

        # Verify the log structure
        self.assertEqual(log["workflow_name"], self.workflow_name)
        self.assertEqual(log["final_status"], "COMPLETED_WITH_ERRORS")
        self.assertEqual(log["error_message"], "Some actions failed")
        self.assertEqual(len(log["action_results"]), 3)

    def test_create_execution_log_with_action_error(self):
        """Test creating an execution log for a workflow with an action error."""
        # Set up mock return values
        error_message = f"Failed during action 'TestAction': {self.action_error}"
        self.mock_status_analyzer.determine_status.return_value = ("FAILED", str(self.action_error), error_message)

        log = self.processor.create_execution_log(
            workflow_name=self.workflow_name,
            action_results=self.results_all_success,
            start_time=self.start_time,
            error=self.action_error
        )

        # Verify the mock was called correctly
        self.mock_status_analyzer.determine_status.assert_called_once_with(self.results_all_success, self.action_error)
        self.mock_formatter.format_action_results.assert_called_once_with(self.results_all_success)

        # Verify the log structure
        self.assertEqual(log["workflow_name"], self.workflow_name)
        self.assertEqual(log["final_status"], "FAILED")
        self.assertEqual(log["error_message"], str(self.action_error))
        self.assertEqual(len(log["action_results"]), 3)

    def test_create_execution_log_with_workflow_error(self):
        """Test creating an execution log for a workflow with a workflow error."""
        # Set up mock return values
        error_message = f"Workflow error: {self.workflow_error}"
        self.mock_status_analyzer.determine_status.return_value = ("FAILED", str(self.workflow_error), error_message)

        log = self.processor.create_execution_log(
            workflow_name=self.workflow_name,
            action_results=self.results_all_success,
            start_time=self.start_time,
            error=self.workflow_error
        )

        # Verify the mock was called correctly
        self.mock_status_analyzer.determine_status.assert_called_once_with(self.results_all_success, self.workflow_error)
        self.mock_formatter.format_action_results.assert_called_once_with(self.results_all_success)

        # Verify the log structure
        self.assertEqual(log["workflow_name"], self.workflow_name)
        self.assertEqual(log["final_status"], "FAILED")
        self.assertEqual(log["error_message"], str(self.workflow_error))
        self.assertEqual(len(log["action_results"]), 3)

    def test_create_execution_log_with_stop_error(self):
        """Test creating an execution log for a workflow that was stopped."""
        # Set up mock return values
        stop_message = "Execution stopped by user request."
        self.mock_status_analyzer.determine_status.return_value = ("STOPPED", stop_message, stop_message)

        log = self.processor.create_execution_log(
            workflow_name=self.workflow_name,
            action_results=self.results_all_success,
            start_time=self.start_time,
            error=self.stop_error
        )

        # Verify the mock was called correctly
        self.mock_status_analyzer.determine_status.assert_called_once_with(self.results_all_success, self.stop_error)
        self.mock_formatter.format_action_results.assert_called_once_with(self.results_all_success)

        # Verify the log structure
        self.assertEqual(log["workflow_name"], self.workflow_name)
        self.assertEqual(log["final_status"], "STOPPED")
        self.assertEqual(log["error_message"], stop_message)
        self.assertEqual(len(log["action_results"]), 3)

    def test_create_execution_log_with_generic_error(self):
        """Test creating an execution log for a workflow with a generic error."""
        # Set up mock return values
        error_message = f"Unexpected error: {self.generic_error}"
        self.mock_status_analyzer.determine_status.return_value = ("FAILED", error_message, error_message)

        log = self.processor.create_execution_log(
            workflow_name=self.workflow_name,
            action_results=self.results_all_success,
            start_time=self.start_time,
            error=self.generic_error
        )

        # Verify the mock was called correctly
        self.mock_status_analyzer.determine_status.assert_called_once_with(self.results_all_success, self.generic_error)
        self.mock_formatter.format_action_results.assert_called_once_with(self.results_all_success)

        # Verify the log structure
        self.assertEqual(log["workflow_name"], self.workflow_name)
        self.assertEqual(log["final_status"], "FAILED")
        self.assertEqual(log["error_message"], error_message)
        self.assertEqual(len(log["action_results"]), 3)

    def test_calculate_time_metrics(self):
        """Test calculating time metrics."""
        # Use a fixed start time for predictable testing
        fixed_start_time = time.time() - 60  # 60 seconds ago

        # Calculate time metrics
        time_metrics = self.processor._calculate_time_metrics(fixed_start_time)

        # Verify the structure and values
        self.assertEqual(time_metrics["start_time"], fixed_start_time)
        self.assertIsNotNone(time_metrics["end_time"])
        self.assertIsNotNone(time_metrics["duration"])
        self.assertIsNotNone(time_metrics["start_time_iso"])
        self.assertIsNotNone(time_metrics["end_time_iso"])

        # Verify the duration is approximately 60 seconds (with some tolerance)
        self.assertGreaterEqual(time_metrics["duration"], 59.0)
        self.assertLessEqual(time_metrics["duration"], 61.0)

    def test_create_log_structure(self):
        """Test creating the log structure."""
        # Create test data
        workflow_name = "TestWorkflow"
        time_metrics = {
            "start_time": time.time() - 60,
            "end_time": time.time(),
            "duration": 60.0,
            "start_time_iso": "2023-01-01T12:00:00",
            "end_time_iso": "2023-01-01T12:01:00"
        }
        final_status = "SUCCESS"
        error_message = None
        summary = "All actions completed successfully"
        error_strategy_name = "STOP_ON_ERROR"
        formatted_results = [
            {"status": "success", "message": "Success 1"},
            {"status": "success", "message": "Success 2"},
            {"status": "success", "message": "Success 3"}
        ]

        # Create the log structure
        log = self.processor._create_log_structure(
            workflow_name,
            time_metrics,
            final_status,
            error_message,
            summary,
            error_strategy_name,
            formatted_results
        )

        # Verify the structure
        self.assertEqual(log["workflow_name"], workflow_name)
        self.assertEqual(log["start_time_iso"], time_metrics["start_time_iso"])
        self.assertEqual(log["end_time_iso"], time_metrics["end_time_iso"])
        self.assertEqual(log["duration_seconds"], time_metrics["duration"])
        self.assertEqual(log["final_status"], final_status)
        self.assertEqual(log["error_message"], error_message)
        self.assertEqual(log["summary"], summary)
        self.assertEqual(log["error_strategy"], error_strategy_name)
        self.assertEqual(log["action_results"], formatted_results)


if __name__ == "__main__":
    unittest.main()
