"""Unit tests for the WorkflowService."""

import unittest
from unittest.mock import MagicMock, patch, call, ANY

# Assuming correct paths for imports
from src.application.services.workflow_service import WorkflowService
from src.core.interfaces import IWorkflowRepository, ICredentialRepository, IWebDriver, IAction
from src.core.interfaces.service import IWorkflowService # Import from new location
from src.infrastructure.webdrivers.factory import WebDriverFactory
from src.infrastructure.webdrivers.base import BrowserType
from src.core.workflow.runner import WorkflowRunner
from src.core.exceptions import WorkflowError, RepositoryError, ValidationError, WebDriverError, ActionError
from src.core.action_result import ActionResult

# Mock Action
class MockServiceAction(IAction):
    action_type = "MockService"
    def __init__(self, name: str = "MockAction", success: bool = True, message: str = ""):
        self.name = name
        self.success = success
        self.message = message
    def execute(self, driver, credential_repo=None) -> ActionResult:
        if self.success: return ActionResult.success(f"{self.name} OK")
        else: raise ActionError(self.message or f"{self.name} FAILED", action_name=self.name)
    def to_dict(self): return {"type": self.action_type, "name": self.name}
    def validate(self): return True


class TestWorkflowService(unittest.TestCase):
    """Test suite for WorkflowService."""

    def setUp(self):
        """Set up mocks for each test."""
        self.mock_wf_repo = MagicMock(spec=IWorkflowRepository)
        self.mock_cred_repo = MagicMock(spec=ICredentialRepository)
        self.mock_webdriver_factory = MagicMock(spec=WebDriverFactory)
        self.mock_driver = MagicMock(spec=IWebDriver)

        # Configure factory to return mock driver
        self.mock_webdriver_factory.create_driver.return_value = self.mock_driver

        # Patch the WorkflowRunner used by the service
        self.runner_patcher = patch('src.application.services.workflow_service.WorkflowRunner', autospec=True)
        self.mock_workflow_runner_class = self.runner_patcher.start()
        self.mock_workflow_runner_instance = self.mock_workflow_runner_class.return_value
        # Default run behavior: success, return empty list of ActionResults
        self.mock_workflow_runner_instance.run.return_value = []


        # Create service instance
        self.service = WorkflowService(
            self.mock_wf_repo,
            self.mock_cred_repo,
            self.mock_webdriver_factory
        )

    def tearDown(self):
        """Clean up after tests."""
        self.runner_patcher.stop()


    def test_create_workflow_success(self):
        """Test creating a workflow successfully."""
        name = "new_wf"
        self.mock_wf_repo.create_workflow.return_value = None # Simulate success

        result = self.service.create_workflow(name)

        self.assertTrue(result)
        self.mock_wf_repo.create_workflow.assert_called_once_with(name)

    def test_create_workflow_repo_error(self):
        """Test create workflow handles repository errors."""
        name = "error_wf"
        self.mock_wf_repo.create_workflow.side_effect = RepositoryError("DB connection failed")

        with self.assertRaisesRegex(WorkflowError, "DB connection failed"):
            self.service.create_workflow(name)

    def test_delete_workflow_success(self):
        """Test deleting a workflow successfully."""
        name = "del_wf"
        self.mock_wf_repo.delete.return_value = True

        result = self.service.delete_workflow(name)

        self.assertTrue(result)
        self.mock_wf_repo.delete.assert_called_once_with(name)

    def test_delete_workflow_not_found(self):
        """Test deleting a non-existent workflow."""
        name = "not_found"
        self.mock_wf_repo.delete.return_value = False

        result = self.service.delete_workflow(name)

        self.assertFalse(result)
        self.mock_wf_repo.delete.assert_called_once_with(name)

    def test_list_workflows(self):
        """Test listing workflows."""
        expected_list = ["wf1", "wf2"]
        self.mock_wf_repo.list_workflows.return_value = expected_list
        result = self.service.list_workflows()
        self.assertEqual(result, expected_list)
        self.mock_wf_repo.list_workflows.assert_called_once()

    def test_get_workflow(self):
        """Test getting workflow actions."""
        name = "my_wf"
        expected_actions = [MockServiceAction("A1")]
        self.mock_wf_repo.load.return_value = expected_actions
        result = self.service.get_workflow(name)
        self.assertEqual(result, expected_actions)
        self.mock_wf_repo.load.assert_called_once_with(name)

    def test_save_workflow(self):
        """Test saving workflow actions."""
        name = "save_wf"
        actions_to_save = [MockServiceAction("A1")]
        self.mock_wf_repo.save.return_value = None

        result = self.service.save_workflow(name, actions_to_save)

        self.assertTrue(result)
        self.mock_wf_repo.save.assert_called_once_with(name, actions_to_save)

    # --- Run Workflow Tests ---

    def test_run_workflow_success_flow(self):
        """Test the successful flow of run_workflow."""
        name = "run_success"
        cred_name = "cred1"
        browser = BrowserType.CHROME
        mock_actions = [MockServiceAction("A1"), MockServiceAction("A2")]
        # Simulate successful results from runner
        mock_results = [ActionResult.success("A1 OK"), ActionResult.success("A2 OK")]

        self.mock_wf_repo.load.return_value = mock_actions
        self.mock_workflow_runner_instance.run.return_value = mock_results

        results_dicts = self.service.run_workflow(name, cred_name, browser)

        # Verify sequence
        self.mock_wf_repo.load.assert_called_once_with(name)
        self.mock_webdriver_factory.create_driver.assert_called_once_with(browser)
        self.mock_workflow_runner_class.assert_called_once_with(self.mock_driver, self.mock_cred_repo)
        self.mock_workflow_runner_instance.run.assert_called_once_with(mock_actions, workflow_name=name)
        self.mock_driver.quit.assert_called_once() # Ensure cleanup

        # Verify returned results format
        self.assertEqual(len(results_dicts), 2)
        self.assertEqual(results_dicts[0], {"status": "success", "message": "A1 OK"})
        self.assertEqual(results_dicts[1], {"status": "success", "message": "A2 OK"})


    def test_run_workflow_runner_raises_action_error(self):
        """Test run_workflow handles ActionError from runner."""
        name = "run_fail"
        cred_name = "cred1"
        mock_actions = [MockServiceAction("A1"), MockServiceAction("A2")]
        # Simulate runner raising ActionError during run
        action_error = ActionError("Element timed out", action_name="A2")
        workflow_error = WorkflowError("Execution failed", cause=action_error) # Runner wraps it
        self.mock_workflow_runner_instance.run.side_effect = workflow_error

        self.mock_wf_repo.load.return_value = mock_actions

        with self.assertRaises(WorkflowError) as cm:
            self.service.run_workflow(name, cred_name)

        # Check original cause is preserved if needed
        self.assertIsInstance(cm.exception.__cause__, ActionError)
        self.assertIn("Element timed out", str(cm.exception))

        # Ensure cleanup still happens
        self.mock_driver.quit.assert_called_once()


    def test_run_workflow_driver_create_fails(self):
        """Test run_workflow handles WebDriverError during driver creation."""
        name = "driver_fail"
        self.mock_wf_repo.load.return_value = [MockServiceAction("A1")] # Load succeeds
        # Simulate driver creation failure
        driver_error = WebDriverError("Browser failed to start")
        self.mock_webdriver_factory.create_driver.side_effect = driver_error

        with self.assertRaises(WebDriverError) as cm:
            self.service.run_workflow(name)

        self.assertEqual(cm.exception, driver_error) # Service should re-raise the specific error
        self.mock_workflow_runner_instance.run.assert_not_called() # Run not reached
        self.mock_driver.quit.assert_not_called() # Driver instance wasn't assigned

    def test_run_workflow_cleanup_on_error(self):
        """Test WebDriver is quit even if runner fails."""
        name = "cleanup_test"
        self.mock_wf_repo.load.return_value = [MockServiceAction("A1")]
        # Simulate runner failure
        self.mock_workflow_runner_instance.run.side_effect = WorkflowError("Runner error")

        with self.assertRaises(WorkflowError):
            self.service.run_workflow(name)

        # Crucial check: ensure quit was called despite the error
        self.mock_driver.quit.assert_called_once()


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)