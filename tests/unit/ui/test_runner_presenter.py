import unittest
from unittest.mock import Mock
from src.ui.runner_presenter import RunnerPresenter
from src.core.interfaces import IWorkflowRepository, IWebDriver

class TestRunnerPresenter(unittest.TestCase):
    def setUp(self):
        self.view = Mock()
        self.workflow_repo = Mock(spec=IWorkflowRepository)
        self.driver = Mock(spec=IWebDriver)
        self.presenter = RunnerPresenter(self.view, self.workflow_repo, self.driver)

    def test_run_workflow_success(self):
        self.presenter.workflow_runner.run_workflow = Mock()
        self.presenter.run_workflow("test_workflow")
        self.presenter.workflow_runner.run_workflow.assert_called_once_with("test_workflow")
        self.view.show_message.assert_called_once_with("Workflow 'test_workflow' completed successfully.")

    def test_run_workflow_failure(self):
        self.presenter.workflow_runner.run_workflow = Mock(side_effect=Exception("Test error"))
        self.presenter.run_workflow("test_workflow")
        self.presenter.workflow_runner.run_workflow.assert_called_once_with("test_workflow")
        self.view.show_error.assert_called_once_with("Error running workflow 'test_workflow': Test error")

    def test_list_workflows(self):
        self.workflow_repo.list_workflows.return_value = ["workflow1", "workflow2"]
        workflows = self.presenter.list_workflows()
        self.assertEqual(workflows, ["workflow1", "workflow2"])

if __name__ == "__main__":
    unittest.main()
