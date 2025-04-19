"""Unit tests for the WorkflowExecutor."""

import unittest
import threading
from unittest.mock import MagicMock, patch, call, ANY

# Assuming correct paths for imports
from src.application.services.workflow_executor import WorkflowExecutor
from src.core.interfaces import IWorkflowRepository, ICredentialRepository, IWebDriver, IAction
from src.core.interfaces.service import IWebDriverService, IReportingService
from src.core.workflow.runner_refactored import WorkflowRunner # Use refactored runner
from src.core.exceptions import WorkflowError, WebDriverError, RepositoryError
from src.infrastructure.webdrivers.base import BrowserType

# Mock Action for testing
class MockExecAction(IAction):
    action_type = "MockExec"
    def __init__(self, name="MockExecAction"): self.name = name
    def execute(self, d, cr=None, ctx=None): return MagicMock()
    def to_dict(self): return {"type": "MockExec", "name": self.name}
    def validate(self): return True

class TestWorkflowExecutor(unittest.TestCase):
    """Test suite for WorkflowExecutor."""

    def setUp(self):
        """Set up mocks for each test."""
        self.mock_wf_repo = MagicMock(spec=IWorkflowRepository)
        self.mock_cred_repo = MagicMock(spec=ICredentialRepository)
        self.mock_wd_service = MagicMock(spec=IWebDriverService)
        self.mock_reporting_service = MagicMock(spec=IReportingService)
        self.mock_driver = MagicMock(spec=IWebDriver)
        self.mock_stop_event = MagicMock(spec=threading.Event)

        # Mock services return values
        self.mock_wd_service.create_web_driver.return_value = self.mock_driver

        # Patch the WorkflowRunner class used by the executor
        self.runner_patcher = patch('src.application.services.workflow_executor.WorkflowRunner', autospec=True)
        self.mock_runner_class = self.runner_patcher.start()
        self.mock_runner_instance = self.mock_runner_class.return_value

        # Instantiate the executor
        self.executor = WorkflowExecutor(
            self.mock_wf_repo, self.mock_cred_repo, self.mock_wd_service, self.mock_reporting_service
        )

    def tearDown(self):
        self.runner_patcher.stop()

    def test_execute_success_flow(self):
        """Test the successful execution flow."""
        wf_name = "success_wf"; cred_name = "c1"; browser = BrowserType.FIREFOX
        mock_actions = [MockExecAction("A1")]
        expected_log = {"final_status": "SUCCESS", "workflow_name": wf_name}

        self.mock_wf_repo.load.return_value = mock_actions
        self.mock_runner_instance.run.return_value = expected_log # Runner generates the log

        # Execute
        result_log = self.executor.execute(wf_name, cred_name, browser, driver_type="selenium", stop_event=self.mock_stop_event)

        # Verify sequence
        self.mock_wf_repo.load.assert_called_once_with(wf_name)
        self.mock_wd_service.create_web_driver.assert_called_once_with(browser_type_str=browser.value, driver_type="selenium")
        self.mock_runner_class.assert_called_once_with(
            driver=self.mock_driver,
            credential_repo=self.mock_cred_repo,
            workflow_repo=self.mock_wf_repo,
            stop_event=self.mock_stop_event
        )
        self.mock_runner_instance.run.assert_called_once_with(mock_actions, workflow_name=wf_name)
        self.mock_wd_service.dispose_web_driver.assert_called_once_with(self.mock_driver)
        self.mock_reporting_service.save_execution_log.assert_called_once_with(expected_log)
        self.assertEqual(result_log, expected_log) # Executor returns runner's log


    def test_execute_load_actions_fails(self):
        """Test execution flow when loading actions fails."""
        wf_name = "load_fail_wf"; load_error = RepositoryError("Cannot load")
        self.mock_wf_repo.load.side_effect = load_error

        with self.assertRaises(WorkflowError) as cm:
            self.executor.execute(wf_name)

        # Check the raised exception wraps the original
        self.assertIs(cm.exception.__cause__, load_error)
        self.assertIn(f"Failed to load actions for workflow '{wf_name}'", str(cm.exception))

        # Verify sequence stops early
        self.mock_wf_repo.load.assert_called_once_with(wf_name)
        self.mock_wd_service.create_web_driver.assert_not_called()
        self.mock_runner_instance.run.assert_not_called()
        self.mock_wd_service.dispose_web_driver.assert_not_called() # No driver to dispose
        # Error log is still saved
        self.mock_reporting_service.save_execution_log.assert_called_once()


    def test_execute_create_driver_fails(self):
        """Test execution flow when creating the driver fails."""
        wf_name = "driver_fail_wf"; mock_actions = [MockExecAction("A1")]
        driver_error = WebDriverError("Cannot start browser")
        self.mock_wf_repo.load.return_value = mock_actions
        self.mock_wd_service.create_web_driver.side_effect = driver_error

        with self.assertRaises(WebDriverError) as cm:
            self.executor.execute(wf_name)

        # Check the specific error is raised
        self.assertIs(cm.exception, driver_error)

        # Verify sequence
        self.mock_wf_repo.load.assert_called_once_with(wf_name)
        self.mock_wd_service.create_web_driver.assert_called_once()
        self.mock_runner_instance.run.assert_not_called()
        self.mock_wd_service.dispose_web_driver.assert_not_called() # No driver to dispose
        # Error log is still saved
        self.mock_reporting_service.save_execution_log.assert_called_once()


    def test_execute_runner_fails(self):
        """Test execution flow when the workflow runner fails."""
        wf_name = "runner_fail_wf"; mock_actions = [MockExecAction("A1")]
        run_error = WorkflowError("Execution failed mid-run")
        partial_log = {"final_status": "FAILED", "error_message": "Runner error", "workflow_name": wf_name, "action_results": []}
        self.mock_wf_repo.load.return_value = mock_actions
        self.mock_runner_instance.run.side_effect = run_error
        # Simulate runner still returning a partial log on error
        # This depends on the runner's implementation, but executor should handle it
        self.mock_runner_instance.run.return_value = partial_log # THIS IS THE KEY PART

        # Executor should re-raise the error from runner
        with self.assertRaises(WorkflowError) as cm:
             self.executor.execute(wf_name)

        # Check the error
        self.assertIs(cm.exception, run_error)

        # Verify sequence including cleanup and logging
        self.mock_wf_repo.load.assert_called_once_with(wf_name)
        self.mock_wd_service.create_web_driver.assert_called_once()
        self.mock_runner_instance.run.assert_called_once_with(mock_actions, workflow_name=wf_name)
        self.mock_wd_service.dispose_web_driver.assert_called_once_with(self.mock_driver)
        # Log should still be saved (even if partial/error)
        # The executor creates its own error log, not using the partial log from the runner
        self.mock_reporting_service.save_execution_log.assert_called_once()


    def test_execute_dispose_driver_fails(self):
        """Test execution flow when disposing the driver fails (should not raise)."""
        wf_name = "dispose_fail_wf"; mock_actions = [MockExecAction("A1")]
        expected_log = {"final_status": "SUCCESS", "workflow_name": wf_name}

        self.mock_wf_repo.load.return_value = mock_actions
        self.mock_runner_instance.run.return_value = expected_log
        self.mock_wd_service.dispose_web_driver.side_effect = Exception("Dispose error")

        # Execute - should NOT raise error from dispose
        result_log = self.executor.execute(wf_name)

        # Verify result and sequence (dispose was called)
        self.assertEqual(result_log, expected_log)
        self.mock_wd_service.dispose_web_driver.assert_called_once_with(self.mock_driver)
        self.mock_reporting_service.save_execution_log.assert_called_once_with(expected_log)


    def test_execute_save_log_fails(self):
        """Test execution flow when saving the log fails (should not raise)."""
        wf_name = "log_save_fail_wf"; mock_actions = [MockExecAction("A1")]
        expected_log = {"final_status": "SUCCESS", "workflow_name": wf_name}

        self.mock_wf_repo.load.return_value = mock_actions
        self.mock_runner_instance.run.return_value = expected_log
        self.mock_reporting_service.save_execution_log.side_effect = RepositoryError("Log DB error")

        # Execute - should NOT raise error from log saving
        result_log = self.executor.execute(wf_name)

        # Verify result and sequence (save was called)
        self.assertEqual(result_log, expected_log)
        self.mock_wd_service.dispose_web_driver.assert_called_once_with(self.mock_driver)
        self.mock_reporting_service.save_execution_log.assert_called_once_with(expected_log)

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
