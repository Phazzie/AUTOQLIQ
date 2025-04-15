"""Tests for workflow completion logger."""

import unittest
from unittest.mock import patch, MagicMock

from src.core.workflow.result_processing.workflow_completion_logger import WorkflowCompletionLogger


class TestWorkflowCompletionLogger(unittest.TestCase):
    """Test cases for workflow completion logger."""

    def setUp(self):
        """Set up test fixtures."""
        self.logger = WorkflowCompletionLogger()

    @patch('src.core.workflow.result_processing.workflow_completion_logger.logger')
    def test_log_workflow_completion_success(self, mock_logger):
        """Test logging a successful workflow completion."""
        # Log a successful workflow completion
        self.logger.log_workflow_completion(
            workflow_name="TestWorkflow",
            final_status="SUCCESS",
            error_message=None
        )
        
        # Verify that the logger was called with the correct message
        mock_logger.info.assert_called_once_with(
            "Workflow 'TestWorkflow' completed with status: SUCCESS"
        )
        
        # Verify that the error logger was not called
        mock_logger.error.assert_not_called()

    @patch('src.core.workflow.result_processing.workflow_completion_logger.logger')
    def test_log_workflow_completion_failure(self, mock_logger):
        """Test logging a failed workflow completion."""
        # Log a failed workflow completion
        self.logger.log_workflow_completion(
            workflow_name="TestWorkflow",
            final_status="FAILED",
            error_message="Test error message"
        )
        
        # Verify that the logger was called with the correct messages
        mock_logger.info.assert_called_once_with(
            "Workflow 'TestWorkflow' completed with status: FAILED"
        )
        mock_logger.error.assert_called_once_with(
            "Workflow error: Test error message"
        )

    @patch('src.core.workflow.result_processing.workflow_completion_logger.logger')
    def test_log_workflow_completion_with_empty_error_message(self, mock_logger):
        """Test logging a workflow completion with an empty error message."""
        # Log a workflow completion with an empty error message
        self.logger.log_workflow_completion(
            workflow_name="TestWorkflow",
            final_status="FAILED",
            error_message=""
        )
        
        # Verify that the logger was called with the correct messages
        mock_logger.info.assert_called_once_with(
            "Workflow 'TestWorkflow' completed with status: FAILED"
        )
        mock_logger.error.assert_called_once_with(
            "Workflow error: "
        )

    @patch('src.core.workflow.result_processing.workflow_completion_logger.logger')
    def test_log_workflow_completion_with_long_workflow_name(self, mock_logger):
        """Test logging a workflow completion with a long workflow name."""
        # Create a long workflow name
        long_name = "A" * 100
        
        # Log a workflow completion with a long workflow name
        self.logger.log_workflow_completion(
            workflow_name=long_name,
            final_status="SUCCESS",
            error_message=None
        )
        
        # Verify that the logger was called with the correct message
        mock_logger.info.assert_called_once_with(
            f"Workflow '{long_name}' completed with status: SUCCESS"
        )
        
        # Verify that the error logger was not called
        mock_logger.error.assert_not_called()


if __name__ == "__main__":
    unittest.main()
