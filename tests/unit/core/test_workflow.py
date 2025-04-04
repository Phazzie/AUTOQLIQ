import unittest
from unittest.mock import Mock, patch
from src.core.workflow import WorkflowRunner
from src.core.interfaces import IWebDriver, ICredentialRepository, IWorkflowRepository
from src.core.exceptions import LoginFailedError, WorkflowError
from src.core.actions import IAction

class TestWorkflowRunner(unittest.TestCase):
    def setUp(self):
        self.driver = Mock(spec=IWebDriver)
        self.credential_repo = Mock(spec=ICredentialRepository)
        self.workflow_repo = Mock(spec=IWorkflowRepository)
        self.runner = WorkflowRunner(self.driver, self.credential_repo, self.workflow_repo)

    def test_run_workflow_success(self):
        action1 = Mock(spec=IAction)
        action2 = Mock(spec=IAction)
        self.workflow_repo.load.return_value = [action1, action2]

        self.runner.run_workflow("example_workflow")

        action1.execute.assert_called_once_with(self.driver)
        action2.execute.assert_called_once_with(self.driver)

    def test_run_workflow_login_failed(self):
        action = Mock(spec=IAction)
        action.execute.side_effect = LoginFailedError("Login failed")
        self.workflow_repo.load.return_value = [action]

        with self.assertRaises(WorkflowError) as context:
            self.runner.run_workflow("example_workflow")

        self.assertEqual(str(context.exception), "Workflow 'example_workflow' failed: Login failed")

    def test_run_workflow_unexpected_error(self):
        action = Mock(spec=IAction)
        action.execute.side_effect = Exception("Unexpected error")
        self.workflow_repo.load.return_value = [action]

        with self.assertRaises(WorkflowError) as context:
            self.runner.run_workflow("example_workflow")

        self.assertEqual(str(context.exception), "An unexpected error occurred during workflow 'example_workflow': Unexpected error")

    def test_save_workflow(self):
        action1 = Mock(spec=IAction)
        action2 = Mock(spec=IAction)

        self.runner.save_workflow("example_workflow", [action1, action2])

        self.workflow_repo.save.assert_called_once_with("example_workflow", [action1, action2])

    def test_list_workflows(self):
        self.workflow_repo.list_workflows.return_value = ["workflow1", "workflow2"]

        result = self.runner.list_workflows()

        self.assertEqual(result, ["workflow1", "workflow2"])

    def test_load_workflow(self):
        action1 = Mock(spec=IAction)
        action2 = Mock(spec=IAction)
        self.workflow_repo.load.return_value = [action1, action2]

        result = self.runner.load_workflow("example_workflow")

        self.assertEqual(result, [action1, action2])

if __name__ == "__main__":
    unittest.main()
