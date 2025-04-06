"""Unit tests for the WorkflowEditorPresenter."""

import unittest
from unittest.mock import MagicMock, patch, call, ANY

# Assuming correct paths for imports
from src.ui.presenters.workflow_editor_presenter_refactored import WorkflowEditorPresenter
from src.ui.interfaces.view import IWorkflowEditorView
from src.core.interfaces import IWorkflowRepository, IAction
from src.core.actions.factory import ActionFactory # Assuming this path
from src.core.exceptions import WorkflowError, RepositoryError, ValidationError, ActionError, AutoQliqError
from src.core.actions.base import ActionBase # Import base for type checking/mocking

# Mock concrete action for testing
class MockTestAction(ActionBase):
    action_type = "MockTest"
    def __init__(self, param: str, name: str = "Mock"): self.name = name; self.param = param
    def execute(self, d, cr=None): pass
    def to_dict(self): return {"type": "MockTest", "name": self.name, "param": self.param}
    def validate(self): return bool(self.param)


class TestWorkflowEditorPresenter(unittest.TestCase):
    """Test suite for WorkflowEditorPresenter."""

    def setUp(self):
        """Set up test environment."""
        self.mock_view = MagicMock(spec=IWorkflowEditorView)
        self.mock_repo = MagicMock(spec=IWorkflowRepository)

        # Patch ActionFactory if its create_action is complex or has side effects
        # For now, assume ActionFactory works correctly or mock its direct usage
        self.factory_patcher = patch('src.ui.presenters.workflow_editor_presenter_refactored.ActionFactory', spec=ActionFactory)
        self.mock_action_factory = self.factory_patcher.start()
        self.mock_action_factory.create_action.side_effect = lambda data: MockTestAction(**{k:v for k,v in data.items() if k!='type'})


        # Create presenter instance, initially without the view
        self.presenter = WorkflowEditorPresenter(self.mock_repo)
        # Set the view using the dedicated method
        self.presenter.set_view(self.mock_view)

    def tearDown(self):
        """Clean up after tests."""
        self.factory_patcher.stop()


    def test_initialize_view_populates_lists(self):
        """Test that initialize_view fetches and sets workflow list."""
        mock_workflows = ["wf1", "wf2"]
        self.mock_repo.list_workflows.return_value = mock_workflows

        self.presenter.initialize_view()

        self.mock_repo.list_workflows.assert_called_once()
        self.mock_view.set_workflow_list.assert_called_once_with(mock_workflows)
        # Should also clear/set action list (empty initially)
        self.mock_view.set_action_list.assert_called_once_with([])


    def test_get_workflow_list(self):
        """Test getting the workflow list."""
        mock_workflows = ["wf_a", "wf_b"]
        self.mock_repo.list_workflows.return_value = mock_workflows

        result = self.presenter.get_workflow_list()

        self.assertEqual(result, mock_workflows)
        self.mock_repo.list_workflows.assert_called_once()


    def test_load_workflow_success(self):
        """Test loading a workflow successfully."""
        workflow_name = "test_workflow"
        mock_actions = [MockTestAction(param="p1"), MockTestAction(param="p2")]
        self.mock_repo.load.return_value = mock_actions

        self.presenter.load_workflow(workflow_name)

        self.mock_repo.load.assert_called_once_with(workflow_name)
        self.assertEqual(self.presenter._current_workflow_name, workflow_name)
        self.assertEqual(self.presenter._current_actions, mock_actions)
        # Check that the view's action list was updated with formatted strings
        self.mock_view.set_action_list.assert_called_once()
        args, _ = self.mock_view.set_action_list.call_args
        action_display_list = args[0]
        self.assertEqual(len(action_display_list), 2)
        self.assertIn("1: MockTest: Mock", action_display_list[0])
        self.assertIn("2: MockTest: Mock", action_display_list[1])
        self.mock_view.set_status.assert_called_once_with(f"Workflow '{workflow_name}' loaded.")


    def test_load_workflow_not_found_error(self):
        """Test loading a workflow that doesn't exist."""
        workflow_name = "not_found"
        self.mock_repo.load.side_effect = WorkflowError(f"Workflow not found: '{workflow_name}'")

        self.presenter.load_workflow(workflow_name)

        self.mock_repo.load.assert_called_once_with(workflow_name)
        # Ensure current state is cleared
        self.assertIsNone(self.presenter._current_workflow_name)
        self.assertEqual(self.presenter._current_actions, [])
        # Ensure view's action list was cleared
        self.mock_view.set_action_list.assert_called_once_with([])
        # Ensure error was displayed in view
        self.mock_view.display_error.assert_called_once()
        args, _ = self.mock_view.display_error.call_args
        self.assertIn("Workflow Error", args[0])
        self.assertIn("Workflow not found", args[1])


    def test_save_workflow_success(self):
        """Test saving the current workflow."""
        workflow_name = "current_wf"
        mock_actions = [MockTestAction(param="p1")]
        self.presenter._current_workflow_name = workflow_name
        self.presenter._current_actions = mock_actions
        # Mock list_workflows for refresh after save
        self.mock_repo.list_workflows.return_value = [workflow_name]

        self.presenter.save_workflow(workflow_name) # Save current actions

        self.mock_repo.save.assert_called_once_with(workflow_name, mock_actions)
        self.mock_view.set_status.assert_called_once_with(f"Workflow '{workflow_name}' saved successfully.")
        # Check if workflow list was refreshed
        self.mock_repo.list_workflows.assert_called_once()
        self.mock_view.set_workflow_list.assert_called_once_with([workflow_name])


    def test_save_workflow_validation_error(self):
        """Test saving with an invalid name."""
        self.presenter.save_workflow("") # Empty name

        self.mock_repo.save.assert_not_called()
        self.mock_view.display_error.assert_called_once()
        args, _ = self.mock_view.display_error.call_args
        self.assertIn("Validation Error", args[0])
        self.assertIn("Workflow name cannot be empty", args[1])

    def test_create_new_workflow_success(self):
        """Test creating a new workflow."""
        new_name = "new_wf"
        self.mock_repo.create_workflow.return_value = None # Simulate success
        # Simulate list refresh and load after creation
        self.mock_repo.list_workflows.return_value = [new_name]
        self.mock_repo.load.return_value = [] # Load returns empty list for new wf

        self.presenter.create_new_workflow(new_name)

        self.mock_repo.create_workflow.assert_called_once_with(new_name)
        self.mock_view.set_status.assert_called_once_with(f"Created new workflow: '{new_name}'.")
        # Check refresh and load occurred
        self.mock_repo.list_workflows.assert_called_once()
        self.mock_view.set_workflow_list.assert_called_once_with([new_name])
        self.mock_repo.load.assert_called_once_with(new_name)
        self.assertEqual(self.presenter._current_workflow_name, new_name)
        self.assertEqual(self.presenter._current_actions, [])
        self.mock_view.set_action_list.assert_called_with([]) # Called during load


    def test_delete_workflow_success(self):
        """Test deleting a workflow."""
        name_to_delete = "delete_me"
        self.presenter._current_workflow_name = name_to_delete # Simulate it was loaded
        self.mock_repo.delete.return_value = True # Simulate successful deletion
        self.mock_repo.list_workflows.return_value = ["other_wf"] # Simulate refresh result

        self.presenter.delete_workflow(name_to_delete)

        self.mock_repo.delete.assert_called_once_with(name_to_delete)
        self.mock_view.set_status.assert_called_once_with(f"Workflow '{name_to_delete}' deleted.")
        # Check state cleared and lists refreshed
        self.assertIsNone(self.presenter._current_workflow_name)
        self.assertEqual(self.presenter._current_actions, [])
        self.mock_view.set_action_list.assert_called_with([])
        self.mock_repo.list_workflows.assert_called_once()
        self.mock_view.set_workflow_list.assert_called_once_with(["other_wf"])

    # --- Action Management Tests ---

    def test_add_action_success(self):
        """Test adding an action when a workflow is loaded."""
        self.presenter._current_workflow_name = "my_wf"
        self.presenter._current_actions = []
        action_data = {"type": "MockTest", "param": "val1", "name": "Action1"}
        mock_action = MockTestAction(**{k:v for k,v in action_data.items() if k!='type'})
        self.mock_action_factory.create_action.return_value = mock_action

        self.presenter.add_action(action_data)

        self.mock_action_factory.create_action.assert_called_once_with(action_data)
        self.assertEqual(len(self.presenter._current_actions), 1)
        self.assertEqual(self.presenter._current_actions[0], mock_action)
        self.mock_view.set_action_list.assert_called_once() # Check view updated
        self.mock_view.set_status.assert_called_once_with("Action 'Action1' added.")
         # Ensure save was *not* called yet
        self.mock_repo.save.assert_not_called()


    def test_add_action_no_workflow_loaded(self):
        """Test adding action when no workflow is loaded."""
        self.presenter._current_workflow_name = None
        action_data = {"type": "MockTest", "param": "val1"}

        self.presenter.add_action(action_data)

        self.mock_action_factory.create_action.assert_not_called()
        self.mock_view.display_error.assert_called_once()
        args, _ = self.mock_view.display_error.call_args
        self.assertIn("Workflow Error", args[0])
        self.assertIn("No workflow loaded", args[1])


    def test_update_action_success(self):
        """Test updating an existing action."""
        action1 = MockTestAction(param="old", name="OldAction")
        self.presenter._current_workflow_name = "my_wf"
        self.presenter._current_actions = [action1]
        updated_data = {"type": "MockTest", "param": "new", "name": "NewAction"}
        mock_updated_action = MockTestAction(**{k:v for k,v in updated_data.items() if k!='type'})
        self.mock_action_factory.create_action.return_value = mock_updated_action

        self.presenter.update_action(0, updated_data)

        self.mock_action_factory.create_action.assert_called_once_with(updated_data)
        self.assertEqual(len(self.presenter._current_actions), 1)
        self.assertEqual(self.presenter._current_actions[0], mock_updated_action)
        self.assertNotEqual(self.presenter._current_actions[0], action1)
        self.mock_view.set_action_list.assert_called_once() # View updated
        self.mock_view.set_status.assert_called_once_with("Action 1 ('NewAction') updated.")
        self.mock_repo.save.assert_not_called()


    def test_delete_action_success(self):
        """Test deleting an action."""
        action1 = MockTestAction(param="p1", name="ActionToDelete")
        action2 = MockTestAction(param="p2", name="ActionToKeep")
        self.presenter._current_workflow_name = "my_wf"
        self.presenter._current_actions = [action1, action2]

        self.presenter.delete_action(0) # Delete first action

        self.assertEqual(len(self.presenter._current_actions), 1)
        self.assertEqual(self.presenter._current_actions[0], action2)
        self.mock_view.set_action_list.assert_called_once() # View updated
        self.mock_view.set_status.assert_called_once_with("Action 1 ('ActionToDelete') deleted.")
        self.mock_repo.save.assert_not_called()


    def test_delete_action_invalid_index(self):
        """Test deleting action with invalid index."""
        self.presenter._current_workflow_name = "my_wf"
        self.presenter._current_actions = [MockTestAction(param="p1")]

        self.presenter.delete_action(5) # Index out of bounds

        self.assertEqual(len(self.presenter._current_actions), 1) # List unchanged
        self.mock_view.display_error.assert_called_once()
        args, _ = self.mock_view.display_error.call_args
        self.assertIn("IndexError", args[0]) # BasePresenter wraps it
        self.assertIn("Invalid action index: 5", args[1])


    def test_get_action_data_success(self):
        """Test getting action data."""
        action1 = MockTestAction(param="p1", name="Action1")
        self.presenter._current_workflow_name = "my_wf"
        self.presenter._current_actions = [action1]

        data = self.presenter.get_action_data(0)

        self.assertEqual(data, {"type": "MockTest", "name": "Action1", "param": "p1"})


    def test_get_action_data_invalid_index(self):
        """Test getting action data with invalid index."""
        self.presenter._current_workflow_name = "my_wf"
        self.presenter._current_actions = [MockTestAction(param="p1")]

        data = self.presenter.get_action_data(1)

        self.assertIsNone(data) # Decorator returns None on error
        self.mock_view.display_error.assert_called_once()
        args, _ = self.mock_view.display_error.call_args
        self.assertIn("IndexError", args[0])
        self.assertIn("Invalid action index: 1", args[1])


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)