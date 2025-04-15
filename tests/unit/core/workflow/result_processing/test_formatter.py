"""Tests for result formatter."""

import unittest
from unittest.mock import MagicMock, patch
from typing import Dict, Any, List

from src.core.action_result import ActionResult, ActionStatus
from src.core.workflow.result_processing.formatter import ResultFormatter
from src.core.workflow.result_processing.sensitive_data_filter import SensitiveDataFilter


class TestResultFormatter(unittest.TestCase):
    """Test cases for result formatter."""

    def setUp(self):
        """Set up test fixtures."""
        self.formatter = ResultFormatter()
        
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
        
        # Create a test execution log
        self.execution_log = {
            "workflow_name": "TestWorkflow",
            "start_time_iso": "2023-01-01T12:00:00",
            "end_time_iso": "2023-01-01T12:01:00",
            "duration_seconds": 60.0,
            "final_status": "SUCCESS",
            "error_message": None,
            "summary": "All actions completed successfully",
            "error_strategy": "STOP_ON_ERROR",
            "action_results": [
                {"status": "success", "message": "Success 1"},
                {"status": "success", "message": "Success 2"},
                {"status": "success", "message": "Success 3"}
            ]
        }
        
        self.execution_log_with_error = {
            "workflow_name": "TestWorkflow",
            "start_time_iso": "2023-01-01T12:00:00",
            "end_time_iso": "2023-01-01T12:01:00",
            "duration_seconds": 60.0,
            "final_status": "FAILED",
            "error_message": "Test error",
            "summary": "Workflow failed",
            "error_strategy": "STOP_ON_ERROR",
            "action_results": [
                {"status": "success", "message": "Success 1"},
                {"status": "failure", "message": "Failure 1"},
                {"status": "success", "message": "Success 2"}
            ]
        }

    def test_format_summary(self):
        """Test formatting a summary of the workflow execution."""
        summary = self.formatter.format_summary(self.execution_log)
        
        self.assertIn("TestWorkflow", summary)
        self.assertIn("success", summary)
        self.assertIn("60.0", summary)
        self.assertIn("3/3", summary)
        
        # Test with error
        summary_with_error = self.formatter.format_summary(self.execution_log_with_error)
        
        self.assertIn("TestWorkflow", summary_with_error)
        self.assertIn("failed", summary_with_error)
        self.assertIn("60.0", summary_with_error)
        self.assertIn("2/3", summary_with_error)
        self.assertIn("Test error", summary_with_error)

    def test_format_detailed_report(self):
        """Test formatting a detailed report of the workflow execution."""
        report = self.formatter.format_detailed_report(self.execution_log)
        
        self.assertIn("Workflow Execution Report: 'TestWorkflow'", report)
        self.assertIn("Status: SUCCESS", report)
        self.assertIn("Start Time: 2023-01-01T12:00:00", report)
        self.assertIn("End Time: 2023-01-01T12:01:00", report)
        self.assertIn("Duration: 60.00 seconds", report)
        self.assertIn("Error: None", report)
        self.assertIn("Action Results:", report)
        self.assertIn("1. ✓ Success 1", report)
        self.assertIn("2. ✓ Success 2", report)
        self.assertIn("3. ✓ Success 3", report)
        
        # Test with error
        report_with_error = self.formatter.format_detailed_report(self.execution_log_with_error)
        
        self.assertIn("Workflow Execution Report: 'TestWorkflow'", report_with_error)
        self.assertIn("Status: FAILED", report_with_error)
        self.assertIn("Error: Test error", report_with_error)
        self.assertIn("1. ✓ Success 1", report_with_error)
        self.assertIn("2. ✗ Failure 1", report_with_error)
        self.assertIn("3. ✓ Success 2", report_with_error)

    def test_format_action_results(self):
        """Test formatting action results."""
        # Mock the sensitive data filter
        self.formatter.sensitive_data_filter = MagicMock()
        self.formatter.sensitive_data_filter.filter_data.return_value = {"filtered": "data"}
        
        # Test with results that have no data
        formatted_results = self.formatter.format_action_results(self.results_with_failure)
        
        self.assertEqual(len(formatted_results), 3)
        self.assertEqual(formatted_results[0]["status"], "success")
        self.assertEqual(formatted_results[1]["status"], "failure")
        self.assertEqual(formatted_results[2]["status"], "success")
        
        # Test with results that have data
        result_with_data = ActionResult(
            ActionStatus.SUCCESS, 
            "Success with data", 
            {"password": "secret", "other": "data"}
        )
        
        formatted_result = self.formatter.format_action_results([result_with_data])
        
        self.assertEqual(len(formatted_result), 1)
        self.assertEqual(formatted_result[0]["status"], "success")
        self.assertEqual(formatted_result[0]["message"], "Success with data")
        self.assertEqual(formatted_result[0]["data"], {"filtered": "data"})
        
        # Verify the filter was called
        self.formatter.sensitive_data_filter.filter_data.assert_called_once()

    def test_format_single_result(self):
        """Test formatting a single action result."""
        # Mock the sensitive data filter
        self.formatter.sensitive_data_filter = MagicMock()
        self.formatter.sensitive_data_filter.filter_data.return_value = {"filtered": "data"}
        
        # Test with a result that has no data
        formatted_result = self.formatter._format_single_result(self.success_result)
        
        self.assertEqual(formatted_result["status"], "success")
        self.assertEqual(formatted_result["message"], "Success")
        self.assertNotIn("data", formatted_result)
        
        # Test with a result that has data
        result_with_data = ActionResult(
            ActionStatus.SUCCESS, 
            "Success with data", 
            {"password": "secret", "other": "data"}
        )
        
        formatted_result = self.formatter._format_single_result(result_with_data)
        
        self.assertEqual(formatted_result["status"], "success")
        self.assertEqual(formatted_result["message"], "Success with data")
        self.assertEqual(formatted_result["data"], {"filtered": "data"})
        
        # Verify the filter was called
        self.formatter.sensitive_data_filter.filter_data.assert_called_once()


if __name__ == "__main__":
    unittest.main()
