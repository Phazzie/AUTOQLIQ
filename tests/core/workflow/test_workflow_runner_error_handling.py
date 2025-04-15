"""Tests for WorkflowRunner error handling strategies."""

import unittest
from unittest.mock import MagicMock, patch
import threading
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.core.interfaces import IAction, IWebDriver, ICredentialRepository
from src.core.action_result import ActionResult, ActionStatus
from src.core.exceptions import ActionError, WorkflowError
from src.core.workflow.runner import WorkflowRunner, ErrorHandlingStrategy


class TestWorkflowRunnerErrorHandling(unittest.TestCase):
    """Test cases for WorkflowRunner error handling strategies."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_driver = MagicMock(spec=IWebDriver)
        self.mock_credential_repo = MagicMock(spec=ICredentialRepository)
        self.stop_event = threading.Event()

    def test_stop_on_error_strategy(self):
        """Test that STOP_ON_ERROR strategy stops workflow execution on first failure."""
        # Create a runner with STOP_ON_ERROR strategy
        runner = WorkflowRunner(
            self.mock_driver,
            self.mock_credential_repo,
            stop_event=self.stop_event,
            error_strategy=ErrorHandlingStrategy.STOP_ON_ERROR
        )

        # Create mock actions
        action1 = MagicMock(spec=IAction)
        action1.name = "Action1"
        action1.action_type = "TestAction"
        action1.execute.return_value = ActionResult.success("Action 1 succeeded")

        action2 = MagicMock(spec=IAction)
        action2.name = "Action2"
        action2.action_type = "TestAction"
        action2.execute.return_value = ActionResult.failure("Action 2 failed")

        action3 = MagicMock(spec=IAction)
        action3.name = "Action3"
        action3.action_type = "TestAction"
        action3.execute.return_value = ActionResult.success("Action 3 succeeded")

        # Run the workflow
        result = runner.run([action1, action2, action3], "Test Workflow")

        # Verify that action1 was executed
        action1.execute.assert_called_once()

        # Verify that action2 was executed
        action2.execute.assert_called_once()

        # Verify that action3 was NOT executed (because action2 failed and we're using STOP_ON_ERROR)
        action3.execute.assert_not_called()

        # Verify the final status is FAILED
        self.assertEqual(result["final_status"], "FAILED")
        self.assertIn("Action 2 failed", result["error_message"])

    def test_continue_on_error_strategy(self):
        """Test that CONTINUE_ON_ERROR strategy continues workflow execution after failures."""
        # Create a runner with CONTINUE_ON_ERROR strategy
        runner = WorkflowRunner(
            self.mock_driver,
            self.mock_credential_repo,
            stop_event=self.stop_event,
            error_strategy=ErrorHandlingStrategy.CONTINUE_ON_ERROR
        )

        # Create mock actions
        action1 = MagicMock(spec=IAction)
        action1.name = "Action1"
        action1.action_type = "TestAction"
        action1.execute.return_value = ActionResult.success("Action 1 succeeded")

        action2 = MagicMock(spec=IAction)
        action2.name = "Action2"
        action2.action_type = "TestAction"
        action2.execute.return_value = ActionResult.failure("Action 2 failed")

        action3 = MagicMock(spec=IAction)
        action3.name = "Action3"
        action3.action_type = "TestAction"
        action3.execute.return_value = ActionResult.success("Action 3 succeeded")

        # Run the workflow
        result = runner.run([action1, action2, action3], "Test Workflow")

        # Verify that all actions were executed
        action1.execute.assert_called_once()
        action2.execute.assert_called_once()
        action3.execute.assert_called_once()

        # Verify the final status reflects failures
        self.assertEqual(result["final_status"], "COMPLETED_WITH_ERRORS")
        self.assertIn("failures", result["summary"])

        # Verify action results are all included
        self.assertEqual(len(result["action_results"]), 3)
        self.assertEqual(result["action_results"][0]["status"], "success")
        self.assertEqual(result["action_results"][1]["status"], "failure")
        self.assertEqual(result["action_results"][2]["status"], "success")


if __name__ == "__main__":
    unittest.main()
