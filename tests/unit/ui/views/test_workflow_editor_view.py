"""Tests for the workflow editor view."""
import unittest
from unittest.mock import Mock, patch
import tkinter as tk

from src.ui.views.workflow_editor_view import WorkflowEditorView
from src.core.exceptions import UIError

class TestWorkflowEditorView(unittest.TestCase):
    """Test cases for the WorkflowEditorView class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock root window
        self.root = Mock(spec=tk.Tk)
        
        # Create a mock presenter
        self.presenter = Mock()
        self.presenter.get_workflow_list.return_value = ["workflow1", "workflow2"]
        
        # Patch the ttk.Frame constructor to avoid UI creation
        self.frame_patcher = patch("src.ui.views.workflow_editor_view.ttk.Frame")
        self.mock_frame = self.frame_patcher.start()
        
        # Patch the tk.Listbox constructor
        self.listbox_patcher = patch("src.ui.views.workflow_editor_view.tk.Listbox")
        self.mock_listbox = self.listbox_patcher.start()
        
        # Patch the ttk.Button constructor
        self.button_patcher = patch("src.ui.views.workflow_editor_view.ttk.Button")
        self.mock_button = self.button_patcher.start()
        
        # Patch the messagebox module
        self.messagebox_patcher = patch("src.ui.views.workflow_editor_view.messagebox")
        self.mock_messagebox = self.messagebox_patcher.start()
        
        # Patch the simpledialog module
        self.simpledialog_patcher = patch("src.ui.views.workflow_editor_view.simpledialog")
        self.mock_simpledialog = self.simpledialog_patcher.start()

    def tearDown(self):
        """Tear down test fixtures."""
        self.frame_patcher.stop()
        self.listbox_patcher.stop()
        self.button_patcher.stop()
        self.messagebox_patcher.stop()
        self.simpledialog_patcher.stop()

    def test_initialization(self):
        """Test that a WorkflowEditorView can be initialized with the required parameters."""
        view = WorkflowEditorView(self.root, self.presenter)
        
        # Check that the view was initialized correctly
        self.assertEqual(view.root, self.root)
        self.assertEqual(view.presenter, self.presenter)
        
        # Check that the presenter's get_workflow_list method was called
        self.presenter.get_workflow_list.assert_called_once()

    def test_on_new_workflow_success(self):
        """Test that on_new_workflow creates a new workflow when the user enters a valid name."""
        # Set up the mock simpledialog to return a workflow name
        self.mock_simpledialog.askstring.return_value = "new_workflow"
        
        # Set up the mock presenter to return success
        self.presenter.create_workflow.return_value = True
        
        # Create the view
        view = WorkflowEditorView(self.root, self.presenter)
        
        # Call the method
        view.on_new_workflow()
        
        # Check that the presenter's create_workflow method was called
        self.presenter.create_workflow.assert_called_once_with("new_workflow")
        
        # Check that the presenter's get_workflow_list method was called again
        self.assertEqual(self.presenter.get_workflow_list.call_count, 2)

    def test_on_new_workflow_cancelled(self):
        """Test that on_new_workflow does nothing when the user cancels the dialog."""
        # Set up the mock simpledialog to return None (user cancelled)
        self.mock_simpledialog.askstring.return_value = None
        
        # Create the view
        view = WorkflowEditorView(self.root, self.presenter)
        
        # Call the method
        view.on_new_workflow()
        
        # Check that the presenter's create_workflow method was not called
        self.presenter.create_workflow.assert_not_called()

    def test_on_new_workflow_failure(self):
        """Test that on_new_workflow shows an error when the presenter returns failure."""
        # Set up the mock simpledialog to return a workflow name
        self.mock_simpledialog.askstring.return_value = "new_workflow"
        
        # Set up the mock presenter to return failure
        self.presenter.create_workflow.return_value = False
        
        # Create the view
        view = WorkflowEditorView(self.root, self.presenter)
        
        # Call the method
        view.on_new_workflow()
        
        # Check that the presenter's create_workflow method was called
        self.presenter.create_workflow.assert_called_once_with("new_workflow")
        
        # Check that an error message was shown
        self.mock_messagebox.showerror.assert_called_once()

    def test_on_new_workflow_exception(self):
        """Test that on_new_workflow handles exceptions."""
        # Set up the mock simpledialog to return a workflow name
        self.mock_simpledialog.askstring.return_value = "new_workflow"
        
        # Set up the mock presenter to raise an exception
        self.presenter.create_workflow.side_effect = Exception("Test error")
        
        # Create the view
        view = WorkflowEditorView(self.root, self.presenter)
        
        # Call the method
        view.on_new_workflow()
        
        # Check that the presenter's create_workflow method was called
        self.presenter.create_workflow.assert_called_once_with("new_workflow")
        
        # Check that an error message was shown
        self.mock_messagebox.showerror.assert_called_once()

if __name__ == "__main__":
    unittest.main()
