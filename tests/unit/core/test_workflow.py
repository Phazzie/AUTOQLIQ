import unittest
from unittest.mock import Mock, patch
from src.core.workflow import WorkflowRunner
from src.core.interfaces import IWebDriver, ICredentialRepository, IWorkflowRepository, IAction
from src.core.exceptions import WorkflowError
from src.core.action_result import ActionResult, ActionStatus

class TestWorkflowRunner(unittest.TestCase):
    def setUp(self):
        self.driver = Mock(spec=IWebDriver)
        self.credential_repo = Mock(spec=ICredentialRepository)
        self.workflow_repo = Mock(spec=IWorkflowRepository)
        self.runner = WorkflowRunner(self.driver, self.credential_repo, self.workflow_repo)

    def test_run_workflow_success(self):
        action1 = Mock(spec=IAction)
        action2 = Mock(spec=IAction)
        action1.name = "Action1"
        action2.name = "Action2"
        action1.execute.return_value = ActionResult.success()
        action2.execute.return_value = ActionResult.success()
        self.workflow_repo.load.return_value = [action1, action2]

        results = self.runner.run_workflow("example_workflow")

        action1.execute.assert_called_once_with(self.driver)
        action2.execute.assert_called_once_with(self.driver)
        self.assertEqual(len(results), 2)
        self.assertTrue(results[0].is_success())
        self.assertTrue(results[1].is_success())

    def test_run_workflow_login_failed(self):
        action = Mock(spec=IAction)
        action.name = "LoginAction"
        action.execute.return_value = ActionResult.failure("Login failed")
        self.workflow_repo.load.return_value = [action]

        with self.assertRaises(WorkflowError) as context:
            self.runner.run_workflow("example_workflow")

        # Check that the exception message contains the expected text
        exception_message = str(context.exception)
        self.assertIn("Action 'LoginAction' failed: Login failed", exception_message)
        self.assertIn("workflow: example_workflow", exception_message)

    def test_run_workflow_unexpected_error(self):
        action = Mock(spec=IAction)
        action.name = "ErrorAction"
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
