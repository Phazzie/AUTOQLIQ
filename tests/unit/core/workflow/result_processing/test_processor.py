"""Tests for result processor."""

import unittest
from unittest.mock import MagicMock, patch
import time
from datetime import datetime

from src.core.action_result import ActionResult
from src.core.exceptions import ActionError, WorkflowError
from src.core.workflow.result_processing.processor import ResultProcessor


class TestResultProcessor(unittest.TestCase):
    """Test cases for result processor."""

    def setUp(self):
        """Set up test fixtures."""
        self.processor = ResultProcessor()
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

    def test_create_execution_log_success(self):
        """Test creating an execution log for a successful workflow."""
        log = self.processor.create_execution_log(
            workflow_name=self.workflow_name,
            action_results=self.results_all_success,
            start_time=self.start_time
        )
        
        self.assertEqual(log["workflow_name"], self.workflow_name)
        self.assertEqual(log["final_status"], "SUCCESS")
        self.assertIsNone(log["error_message"])
        self.assertEqual(len(log["action_results"]), 3)
        self.assertGreater(log["duration_seconds"], 0)

    def test_create_execution_log_with_failures(self):
        """Test creating an execution log for a workflow with failures."""
        log = self.processor.create_execution_log(
            workflow_name=self.workflow_name,
            action_results=self.results_with_failure,
            start_time=self.start_time
        )
        
        self.assertEqual(log["workflow_name"], self.workflow_name)
        self.assertEqual(log["final_status"], "COMPLETED_WITH_ERRORS")
        self.assertIsNotNone(log["error_message"])
        self.assertEqual(len(log["action_results"]), 3)

    def test_create_execution_log_with_action_error(self):
        """Test creating an execution log for a workflow with an action error."""
        log = self.processor.create_execution_log(
            workflow_name=self.workflow_name,
            action_results=self.results_all_success,
            start_time=self.start_time,
            error=self.action_error
        )
        
        self.assertEqual(log["workflow_name"], self.workflow_name)
        self.assertEqual(log["final_status"], "FAILED")
        self.assertIn("Test action error", log["error_message"])
        self.assertEqual(len(log["action_results"]), 3)

    def test_create_execution_log_with_workflow_error(self):
        """Test creating an execution log for a workflow with a workflow error."""
        log = self.processor.create_execution_log(
            workflow_name=self.workflow_name,
            action_results=self.results_all_success,
            start_time=self.start_time,
            error=self.workflow_error
        )
        
        self.assertEqual(log["workflow_name"], self.workflow_name)
        self.assertEqual(log["final_status"], "FAILED")
        self.assertIn("Test workflow error", log["error_message"])
        self.assertEqual(len(log["action_results"]), 3)

    def test_create_execution_log_with_stop_error(self):
        """Test creating an execution log for a workflow that was stopped."""
        log = self.processor.create_execution_log(
            workflow_name=self.workflow_name,
            action_results=self.results_all_success,
            start_time=self.start_time,
            error=self.stop_error
        )
        
        self.assertEqual(log["workflow_name"], self.workflow_name)
        self.assertEqual(log["final_status"], "STOPPED")
        self.assertIn("stopped by request", log["error_message"])
        self.assertEqual(len(log["action_results"]), 3)

    def test_create_execution_log_with_generic_error(self):
        """Test creating an execution log for a workflow with a generic error."""
        log = self.processor.create_execution_log(
            workflow_name=self.workflow_name,
            action_results=self.results_all_success,
            start_time=self.start_time,
            error=self.generic_error
        )
        
        self.assertEqual(log["workflow_name"], self.workflow_name)
        self.assertEqual(log["final_status"], "FAILED")
        self.assertIn("Test generic error", log["error_message"])
        self.assertEqual(len(log["action_results"]), 3)

    def test_format_action_results(self):
        """Test formatting action results."""
        formatted_results = self.processor._format_action_results(self.results_with_failure)
        
        self.assertEqual(len(formatted_results), 3)
        self.assertEqual(formatted_results[0]["status"], "success")
        self.assertEqual(formatted_results[1]["status"], "failure")
        self.assertEqual(formatted_results[2]["status"], "success")

    def test_filter_sensitive_data(self):
        """Test filtering sensitive data."""
        data = {
            "username": "test_user",
            "password": "secret_password",
            "token": "secret_token",
            "api_key": "secret_key",
            "credential": "secret_credential",
            "other_data": "not_sensitive"
        }
        
        filtered_data = self.processor._filter_sensitive_data(data)
        
        self.assertEqual(filtered_data["username"], "test_user")
        self.assertEqual(filtered_data["password"], "********")
        self.assertEqual(filtered_data["token"], "********")
        self.assertEqual(filtered_data["api_key"], "********")
        self.assertEqual(filtered_data["credential"], "********")
        self.assertEqual(filtered_data["other_data"], "not_sensitive")


if __name__ == "__main__":
    unittest.main()
