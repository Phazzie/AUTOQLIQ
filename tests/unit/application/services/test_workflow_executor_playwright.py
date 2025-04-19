"""Unit tests for the WorkflowExecutor with Playwright."""

import unittest
import threading
from unittest.mock import MagicMock, patch, call, ANY

# Assuming correct paths for imports
from src.application.services.workflow_executor import WorkflowExecutor
from src.core.interfaces import (IWorkflowRepository, ICredentialRepository, IWebDriver, IAction)
from src.core.interfaces.service import IWebDriverService, IReportingService
from src.core.workflow.runner_refactored import WorkflowRunner
from src.core.exceptions import WorkflowError, WebDriverError, RepositoryError
from src.infrastructure.webdrivers.base import BrowserType

# Mock Action for testing
class MockExecAction(IAction):
    action_type = "MockExec"
    def __init__(self, name="MockExecAction"): self.name = name
    def execute(self, d, cr=None, ctx=None): return MagicMock()
    def to_dict(self): return {"type": "MockExec", "name": self.name}
    def validate(self): return True

class TestWorkflowExecutorPlaywright(unittest.TestCase):
    """Test suite for WorkflowExecutor with Playwright."""

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

    def test_execute_with_playwright(self):
        """Test execution with Playwright driver."""
        wf_name = "playwright_wf"
        browser = BrowserType.FIREFOX
        driver_type = "playwright"
        mock_actions = [MockExecAction("A1")]
        expected_log = {"final_status": "SUCCESS", "workflow_name": wf_name}

        self.mock_wf_repo.load.return_value = mock_actions
        self.mock_runner_instance.run.return_value = expected_log

        # Execute with Playwright driver
        result_log = self.executor.execute(wf_name, browser_type=browser, driver_type=driver_type, stop_event=self.mock_stop_event)

        # Verify sequence
        self.mock_wf_repo.load.assert_called_once_with(wf_name)
        self.mock_wd_service.create_web_driver.assert_called_once_with(
            browser_type_str=browser.value,
            driver_type=driver_type
        )
        self.mock_runner_class.assert_called_once_with(
            driver=self.mock_driver,
            credential_repo=self.mock_cred_repo,
            workflow_repo=self.mock_wf_repo,
            stop_event=self.mock_stop_event
        )
        self.mock_runner_instance.run.assert_called_once_with(mock_actions, workflow_name=wf_name)
        self.mock_wd_service.dispose_web_driver.assert_called_once_with(self.mock_driver)
        self.mock_reporting_service.save_execution_log.assert_called_once_with(expected_log)
        self.assertEqual(result_log, expected_log)

    def test_execute_with_playwright_driver_error(self):
        """Test execution with Playwright driver when driver creation fails."""
        wf_name = "playwright_error_wf"
        browser = BrowserType.FIREFOX
        driver_type = "playwright"
        mock_actions = [MockExecAction("A1")]
        driver_error = WebDriverError("Cannot start Playwright browser")

        self.mock_wf_repo.load.return_value = mock_actions
        self.mock_wd_service.create_web_driver.side_effect = driver_error

        with self.assertRaises(WebDriverError) as cm:
            self.executor.execute(wf_name, browser_type=browser, driver_type=driver_type)

        # Check the specific error is raised
        self.assertIs(cm.exception, driver_error)

        # Verify sequence
        self.mock_wf_repo.load.assert_called_once_with(wf_name)
        self.mock_wd_service.create_web_driver.assert_called_once_with(
            browser_type_str=browser.value,
            driver_type=driver_type
        )
        self.mock_runner_instance.run.assert_not_called()
        self.mock_wd_service.dispose_web_driver.assert_not_called()
        self.mock_reporting_service.save_execution_log.assert_called_once()  # Error log should still be saved

if __name__ == "__main__":
    unittest.main()
