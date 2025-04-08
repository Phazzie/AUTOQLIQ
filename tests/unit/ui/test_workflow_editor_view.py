import unittest
from unittest.mock import MagicMock, patch
import tkinter as tk

from src.ui.views.workflow_editor_view import WorkflowEditorView
from src.ui.interfaces.presenter import IWorkflowEditorPresenter
from src.core.exceptions import UIError, ValidationError, WorkflowError


class TestWorkflowEditorView(unittest.TestCase):
    """Unit tests for WorkflowEditorView implementation."""

    def setUp(self):
        """Set up test environment before each test."""
        # Mock the root window
        self.root = MagicMock(spec=tk.Tk)
        
        # Mock the presenter
        self.presenter = MagicMock(spec=IWorkflowEditorPresenter)
        
        # Create the view
        self.view = WorkflowEditorView(self.root)
        self.view.set_presenter(self.presenter)

    def test_initialization(self):
        """Test that the view initializes correctly."""
        # Verify that the view is initialized with the correct attributes
        self.assertIsNotNone(self.view)
        self.assertEqual(self.view.presenter, self.presenter)
        self.assertEqual(self.view.parent, self.root)

    @patch('tkinter.messagebox.askokcancel')
    def test_confirm_action(self, mock_askokcancel):
        """Test the confirm_action method."""
        # Setup mock
        mock_askokcancel.return_value = True
        
        # Execute test
        result = self.view.confirm_action("Test Title", "Test Message")
        
        # Verify
        self.assertTrue(result)
        mock_askokcancel.assert_called_once_with("Test Title", "Test Message")

    @patch('tkinter.messagebox.showerror')
    def test_display_error(self, mock_showerror):
        """Test the display_error method."""
        # Execute test
        self.view.display_error("Test Error", "Test Message")
        
        # Verify
        mock_showerror.assert_called_once_with("Test Error", "Test Message")

    @patch('tkinter.simpledialog.askstring')
    def test_prompt_for_name(self, mock_askstring):
        """Test the prompt_for_name method."""
        # Setup mock
        mock_askstring.return_value = "Test Name"
        
        # Execute test
        result = self.view.prompt_for_name("Test Prompt")
        
        # Verify
        self.assertEqual(result, "Test Name")
        mock_askstring.assert_called_once()

    def test_update_workflows_list(self):
        """Test updating the workflows list."""
        # Setup mock for the listbox
        self.view.workflows_listbox = MagicMock()
        
        # Test data
        workflow_names = ["Workflow1", "Workflow2", "Workflow3"]
        
        # Execute test
        self.view.update_workflows_list(workflow_names)
        
        # Verify
        self.view.workflows_listbox.delete.assert_called_once_with(0, tk.END)
        # Verify each workflow name was inserted
        for i, name in enumerate(workflow_names):
            self.view.workflows_listbox.insert.assert_any_call(i, name)

    def test_update_actions_list(self):
        """Test updating the actions list."""
        # Setup mock for the listbox
        self.view.actions_listbox = MagicMock()
        
        # Test data
        actions_display = [
            "Navigate to https://example.com",
            "Click on button#submit",
            "Type 'test' into input#username"
        ]
        
        # Execute test
        self.view.update_actions_list(actions_display)
        
        # Verify
        self.view.actions_listbox.delete.assert_called_once_with(0, tk.END)
        # Verify each action was inserted
        for i, action in enumerate(actions_display):
            self.view.actions_listbox.insert.assert_any_call(i, action)

    def test_get_selected_workflow(self):
        """Test getting the selected workflow name."""
        # Setup mock for the listbox
        self.view.workflows_listbox = MagicMock()
        self.view.workflows_listbox.curselection.return_value = (0,)
        self.view.workflows_listbox.get.return_value = "TestWorkflow"
        
        # Execute test
        result = self.view.get_selected_workflow()
        
        # Verify
        self.assertEqual(result, "TestWorkflow")

    def test_get_selected_workflow_none_selected(self):
        """Test getting the selected workflow when none is selected."""
        # Setup mock for the listbox
        self.view.workflows_listbox = MagicMock()
        self.view.workflows_listbox.curselection.return_value = ()
        
        # Execute test
        result = self.view.get_selected_workflow()
        
        # Verify
        self.assertIsNone(result)

    def test_get_selected_action_index(self):
        """Test getting the selected action index."""
        # Setup mock for the listbox
        self.view.actions_listbox = MagicMock()
        self.view.actions_listbox.curselection.return_value = (2,)
        
        # Execute test
        result = self.view.get_selected_action_index()
        
        # Verify
        self.assertEqual(result, 2)

    def test_get_selected_action_index_none_selected(self):
        """Test getting the selected action index when none is selected."""
        # Setup mock for the listbox
        self.view.actions_listbox = MagicMock()
        self.view.actions_listbox.curselection.return_value = ()
        
        # Execute test
        result = self.view.get_selected_action_index()
        
        # Verify
        self.assertEqual(result, -1)

    @patch.object(WorkflowEditorView, 'prompt_for_name')
    def test_on_create_workflow(self, mock_prompt):
        """Test creating a new workflow."""
        # Setup mocks
        mock_prompt.return_value = "NewWorkflow"
        
        # Execute test
        self.view.on_create_workflow()
        
        # Verify
        mock_prompt.assert_called_once_with("Enter new workflow name:")
        self.presenter.create_workflow.assert_called_once_with("NewWorkflow")

    @patch.object(WorkflowEditorView, 'prompt_for_name')
    def test_on_create_workflow_cancelled(self, mock_prompt):
        """Test cancelling workflow creation."""
        # Setup mocks
        mock_prompt.return_value = None
        
        # Execute test
        self.view.on_create_workflow()
        
        # Verify
        mock_prompt.assert_called_once_with("Enter new workflow name:")
        self.presenter.create_workflow.assert_not_called()

    @patch.object(WorkflowEditorView, 'get_selected_workflow')
    @patch.object(WorkflowEditorView, 'confirm_action')
    def test_on_delete_workflow(self, mock_confirm, mock_get_selected):
        """Test deleting a workflow."""
        # Setup mocks
        mock_get_selected.return_value = "TestWorkflow"
        mock_confirm.return_value = True
        
        # Execute test
        self.view.on_delete_workflow()
        
        # Verify
        mock_get_selected.assert_called_once()
        mock_confirm.assert_called_once_with(
            "Delete Workflow",
            "Are you sure you want to delete workflow 'TestWorkflow'?"
        )
        self.presenter.delete_workflow.assert_called_once_with("TestWorkflow")

    @patch.object(WorkflowEditorView, 'get_selected_workflow')
    @patch.object(WorkflowEditorView, 'confirm_action')
    def test_on_delete_workflow_cancelled(self, mock_confirm, mock_get_selected):
        """Test cancelling workflow deletion."""
        # Setup mocks
        mock_get_selected.return_value = "TestWorkflow"
        mock_confirm.return_value = False
        
        # Execute test
        self.view.on_delete_workflow()
        
        # Verify
        mock_get_selected.assert_called_once()
        mock_confirm.assert_called_once()
        self.presenter.delete_workflow.assert_not_called()

    @patch.object(WorkflowEditorView, 'get_selected_workflow')
    def test_on_delete_workflow_none_selected(self, mock_get_selected):
        """Test deleting a workflow when none is selected."""
        # Setup mocks
        mock_get_selected.return_value = None
        
        # Execute test
        self.view.on_delete_workflow()
        
        # Verify
        mock_get_selected.assert_called_once()
        self.presenter.delete_workflow.assert_not_called()

    @patch.object(WorkflowEditorView, 'get_selected_workflow')
    def test_on_load_workflow(self, mock_get_selected):
        """Test loading a workflow."""
        # Setup mocks
        mock_get_selected.return_value = "TestWorkflow"
        
        # Execute test
        self.view.on_load_workflow()
        
        # Verify
        mock_get_selected.assert_called_once()
        self.presenter.load_workflow.assert_called_once_with("TestWorkflow")

    @patch.object(WorkflowEditorView, 'get_selected_workflow')
    def test_on_load_workflow_none_selected(self, mock_get_selected):
        """Test loading a workflow when none is selected."""
        # Setup mocks
        mock_get_selected.return_value = None
        
        # Execute test
        self.view.on_load_workflow()
        
        # Verify
        mock_get_selected.assert_called_once()
        self.presenter.load_workflow.assert_not_called()

    @patch.object(WorkflowEditorView, 'get_selected_action_index')
    def test_on_edit_action(self, mock_get_selected):
        """Test editing an action."""
        # Setup mocks
        mock_get_selected.return_value = 2
        
        # Execute test
        self.view.on_edit_action()
        
        # Verify
        mock_get_selected.assert_called_once()
        self.presenter.edit_action.assert_called_once_with(2)

    @patch.object(WorkflowEditorView, 'get_selected_action_index')
    def test_on_edit_action_none_selected(self, mock_get_selected):
        """Test editing an action when none is selected."""
        # Setup mocks
        mock_get_selected.return_value = -1
        
        # Execute test
        self.view.on_edit_action()
        
        # Verify
        mock_get_selected.assert_called_once()
        self.presenter.edit_action.assert_not_called()

    @patch.object(WorkflowEditorView, 'get_selected_action_index')
    @patch.object(WorkflowEditorView, 'confirm_action')
    def test_on_delete_action(self, mock_confirm, mock_get_selected):
        """Test deleting an action."""
        # Setup mocks
        mock_get_selected.return_value = 2
        mock_confirm.return_value = True
        
        # Execute test
        self.view.on_delete_action()
        
        # Verify
        mock_get_selected.assert_called_once()
        mock_confirm.assert_called_once_with(
            "Delete Action",
            "Are you sure you want to delete this action?"
        )
        self.presenter.delete_action.assert_called_once_with(2)

    @patch.object(WorkflowEditorView, 'get_selected_action_index')
    @patch.object(WorkflowEditorView, 'confirm_action')
    def test_on_delete_action_cancelled(self, mock_confirm, mock_get_selected):
        """Test cancelling action deletion."""
        # Setup mocks
        mock_get_selected.return_value = 2
        mock_confirm.return_value = False
        
        # Execute test
        self.view.on_delete_action()
        
        # Verify
        mock_get_selected.assert_called_once()
        mock_confirm.assert_called_once()
        self.presenter.delete_action.assert_not_called()

    @patch.object(WorkflowEditorView, 'get_selected_action_index')
    def test_on_delete_action_none_selected(self, mock_get_selected):
        """Test deleting an action when none is selected."""
        # Setup mocks
        mock_get_selected.return_value = -1
        
        # Execute test
        self.view.on_delete_action()
        
        # Verify
        mock_get_selected.assert_called_once()
        self.presenter.delete_action.assert_not_called()

    def test_on_add_action(self):
        """Test adding a new action."""
        # Execute test
        self.view.on_add_action()
        
        # Verify
        self.presenter.add_action.assert_called_once()

    def test_on_save_workflow(self):
        """Test saving a workflow."""
        # Execute test
        self.view.on_save_workflow()
        
        # Verify
        self.presenter.save_workflow.assert_called_once()

    @patch.object(WorkflowEditorView, 'get_selected_action_index')
    def test_on_move_action_up(self, mock_get_selected):
        """Test moving an action up."""
        # Setup mocks
        mock_get_selected.return_value = 2
        
        # Execute test
        self.view.on_move_action_up()
        
        # Verify
        mock_get_selected.assert_called_once()
        self.presenter.move_action_up.assert_called_once_with(2)

    @patch.object(WorkflowEditorView, 'get_selected_action_index')
    def test_on_move_action_up_none_selected(self, mock_get_selected):
        """Test moving an action up when none is selected."""
        # Setup mocks
        mock_get_selected.return_value = -1
        
        # Execute test
        self.view.on_move_action_up()
        
        # Verify
        mock_get_selected.assert_called_once()
        self.presenter.move_action_up.assert_not_called()

    @patch.object(WorkflowEditorView, 'get_selected_action_index')
    def test_on_move_action_down(self, mock_get_selected):
        """Test moving an action down."""
        # Setup mocks
        mock_get_selected.return_value = 2
        
        # Execute test
        self.view.on_move_action_down()
        
        # Verify
        mock_get_selected.assert_called_once()
        self.presenter.move_action_down.assert_called_once_with(2)

    @patch.object(WorkflowEditorView, 'get_selected_action_index')
    def test_on_move_action_down_none_selected(self, mock_get_selected):
        """Test moving an action down when none is selected."""
        # Setup mocks
        mock_get_selected.return_value = -1
        
        # Execute test
        self.view.on_move_action_down()
        
        # Verify
        mock_get_selected.assert_called_once()
        self.presenter.move_action_down.assert_not_called()


if __name__ == '__main__':
    unittest.main()
