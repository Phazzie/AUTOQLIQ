"""Tests for log structure builder."""

import unittest
from typing import Dict, Any

from src.core.workflow.result_processing.log_structure_builder import LogStructureBuilder


class TestLogStructureBuilder(unittest.TestCase):
    """Test cases for log structure builder."""

    def setUp(self):
        """Set up test fixtures."""
        self.builder = LogStructureBuilder()
        
        # Sample time metrics for testing
        self.time_metrics = {
            "start_time": 1672567200.0,  # 2023-01-01T12:00:00
            "end_time": 1672567260.0,    # 2023-01-01T12:01:00
            "duration": 60.0,
            "start_time_iso": "2023-01-01T12:00:00",
            "end_time_iso": "2023-01-01T12:01:00"
        }
        
        # Sample formatted results for testing
        self.formatted_results = [
            {"status": "success", "message": "Success 1"},
            {"status": "success", "message": "Success 2"},
            {"status": "success", "message": "Success 3"}
        ]

    def test_create_log_structure_success(self):
        """Test creating a log structure for a successful workflow."""
        # Create the log structure
        log = self.builder.create_log_structure(
            workflow_name="TestWorkflow",
            time_metrics=self.time_metrics,
            final_status="SUCCESS",
            error_message=None,
            summary="All actions completed successfully",
            error_strategy_name="STOP_ON_ERROR",
            formatted_results=self.formatted_results
        )
        
        # Verify the structure
        self._verify_log_structure(
            log,
            workflow_name="TestWorkflow",
            final_status="SUCCESS",
            error_message=None,
            summary="All actions completed successfully",
            error_strategy="STOP_ON_ERROR"
        )

    def test_create_log_structure_failure(self):
        """Test creating a log structure for a failed workflow."""
        # Create the log structure
        log = self.builder.create_log_structure(
            workflow_name="TestWorkflow",
            time_metrics=self.time_metrics,
            final_status="FAILED",
            error_message="Test error message",
            summary="Workflow failed",
            error_strategy_name="STOP_ON_ERROR",
            formatted_results=self.formatted_results
        )
        
        # Verify the structure
        self._verify_log_structure(
            log,
            workflow_name="TestWorkflow",
            final_status="FAILED",
            error_message="Test error message",
            summary="Workflow failed",
            error_strategy="STOP_ON_ERROR"
        )

    def test_create_log_structure_with_empty_results(self):
        """Test creating a log structure with empty results."""
        # Create the log structure
        log = self.builder.create_log_structure(
            workflow_name="TestWorkflow",
            time_metrics=self.time_metrics,
            final_status="SUCCESS",
            error_message=None,
            summary="No actions executed",
            error_strategy_name="STOP_ON_ERROR",
            formatted_results=[]
        )
        
        # Verify the structure
        self._verify_log_structure(
            log,
            workflow_name="TestWorkflow",
            final_status="SUCCESS",
            error_message=None,
            summary="No actions executed",
            error_strategy="STOP_ON_ERROR"
        )
        
        # Verify that the action_results is an empty list
        self.assertEqual(log["action_results"], [])

    def test_create_log_structure_with_long_workflow_name(self):
        """Test creating a log structure with a long workflow name."""
        # Create a long workflow name
        long_name = "A" * 100
        
        # Create the log structure
        log = self.builder.create_log_structure(
            workflow_name=long_name,
            time_metrics=self.time_metrics,
            final_status="SUCCESS",
            error_message=None,
            summary="All actions completed successfully",
            error_strategy_name="STOP_ON_ERROR",
            formatted_results=self.formatted_results
        )
        
        # Verify the structure
        self._verify_log_structure(
            log,
            workflow_name=long_name,
            final_status="SUCCESS",
            error_message=None,
            summary="All actions completed successfully",
            error_strategy="STOP_ON_ERROR"
        )

    def _verify_log_structure(self, log: Dict[str, Any], **expected_values):
        """Verify that the log structure has the expected values."""
        # Verify the structure
        self.assertEqual(log["workflow_name"], expected_values["workflow_name"])
        self.assertEqual(log["start_time_iso"], self.time_metrics["start_time_iso"])
        self.assertEqual(log["end_time_iso"], self.time_metrics["end_time_iso"])
        self.assertEqual(log["duration_seconds"], self.time_metrics["duration"])
        self.assertEqual(log["final_status"], expected_values["final_status"])
        self.assertEqual(log["error_message"], expected_values["error_message"])
        self.assertEqual(log["summary"], expected_values["summary"])
        self.assertEqual(log["error_strategy"], expected_values["error_strategy"])
        
        # Verify that action_results is present
        self.assertIn("action_results", log)


if __name__ == "__main__":
    unittest.main()
