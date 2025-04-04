import unittest
from unittest.mock import Mock
from src.ui.editor_presenter import EditorPresenter
from src.core.interfaces import IWorkflowRepository, IAction

class TestEditorPresenter(unittest.TestCase):
    def setUp(self):
        self.view = Mock()
        self.workflow_repo = Mock(spec=IWorkflowRepository)
        self.presenter = EditorPresenter(self.view, self.workflow_repo)

    def test_add_action(self):
        action_data = {"type": "Navigate", "url": "https://example.com"}
        self.presenter.add_action(action_data)
        self.assertEqual(len(self.presenter.actions), 1)
        self.view.update_action_list.assert_called_once()

    def test_remove_action(self):
        action_data = {"type": "Navigate", "url": "https://example.com"}
        self.presenter.add_action(action_data)
        self.presenter.remove_action(0)
        self.assertEqual(len(self.presenter.actions), 0)
        self.view.update_action_list.assert_called()

    def test_save_workflow(self):
        action_data = {"type": "Navigate", "url": "https://example.com"}
        self.presenter.add_action(action_data)
        self.presenter.save_workflow("test_workflow")
        self.workflow_repo.save.assert_called_once_with("test_workflow", self.presenter.actions)

    def test_load_workflow(self):
        action_data = {"type": "Navigate", "url": "https://example.com"}
        self.workflow_repo.load.return_value = [Mock(spec=IAction)]
        self.presenter.load_workflow("test_workflow")
        self.assertEqual(len(self.presenter.actions), 1)
        self.view.update_action_list.assert_called_once()

    def test_list_workflows(self):
        self.workflow_repo.list_workflows.return_value = ["workflow1", "workflow2"]
        workflows = self.presenter.list_workflows()
        self.assertEqual(workflows, ["workflow1", "workflow2"])

if __name__ == "__main__":
    unittest.main()
