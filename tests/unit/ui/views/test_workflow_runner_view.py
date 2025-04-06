"""Tests for the workflow runner view."""
import unittest
from unittest.mock import Mock, patch
import tkinter as tk

from src.ui.views.workflow_runner_view import WorkflowRunnerView
from src.core.exceptions import UIError

class TestWorkflowRunnerView(unittest.TestCase):
    """Test cases for the WorkflowRunnerView class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock root window
        self.root = Mock(spec=tk.Tk)
        
        # Create a mock presenter
        self.presenter = Mock()
        self.presenter.get_workflow_list.return_value = ["workflow1", "workflow2"]
        self.presenter.get_credential_list.return_value = [
            {"name": "credential1", "username": "user1", "password": "pass1"},
            {"name": "credential2", "username": "user2", "password": "pass2"}
        ]
        
        # Patch the ttk.Frame constructor to avoid UI creation
        self.frame_patcher = patch("src.ui.views.workflow_runner_view.ttk.Frame")
        self.mock_frame = self.frame_patcher.start()
        
        # Patch the tk.Listbox constructor
        self.listbox_patcher = patch("src.ui.views.workflow_runner_view.tk.Listbox")
        self.mock_listbox = self.listbox_patcher.start()
        
        # Patch the ttk.Combobox constructor
        self.combobox_patcher = patch("src.ui.views.workflow_runner_view.ttk.Combobox")
        self.mock_combobox = self.combobox_patcher.start()
        
        # Patch the ttk.Button constructor
        self.button_patcher = patch("src.ui.views.workflow_runner_view.ttk.Button")
        self.mock_button = self.button_patcher.start()
        
        # Patch the tk.Text constructor
        self.text_patcher = patch("src.ui.views.workflow_runner_view.tk.Text")
        self.mock_text = self.text_patcher.start()
        
        # Patch the messagebox module
        self.messagebox_patcher = patch("src.ui.views.workflow_runner_view.messagebox")
        self.mock_messagebox = self.messagebox_patcher.start()

    def tearDown(self):
        """Tear down test fixtures."""
        self.frame_patcher.stop()
        self.listbox_patcher.stop()
        self.combobox_patcher.stop()
        self.button_patcher.stop()
        self.text_patcher.stop()
        self.messagebox_patcher.stop()

    def test_initialization(self):
        """Test that a WorkflowRunnerView can be initialized with the required parameters."""
        view = WorkflowRunnerView(self.root, self.presenter)
        
        # Check that the view was initialized correctly
        self.assertEqual(view.root, self.root)
        self.assertEqual(view.presenter, self.presenter)
        
        # Check that the presenter's methods were called
        self.presenter.get_workflow_list.assert_called_once()
        self.presenter.get_credential_list.assert_called_once()

    def test_on_run_workflow_success(self):
        """Test that on_run_workflow runs a workflow when a workflow and credential are selected."""
        # Set up the mock listbox to return a selected index
        self.mock_listbox.return_value.curselection.return_value = (0,)
        self.mock_listbox.return_value.get.return_value = "workflow1"
        
        # Set up the mock combobox to return a selected credential
        self.mock_combobox.return_value.get.return_value = "credential1"
        
        # Set up the mock presenter to return success
        self.presenter.run_workflow.return_value = True
        
        # Create the view
        view = WorkflowRunnerView(self.root, self.presenter)
        
        # Set up the view's widgets
        view.workflow_listbox = self.mock_listbox.return_value
        view.credential_combobox = self.mock_combobox.return_value
        
        # Call the method
        view.on_run_workflow()
        
        # Check that the presenter's run_workflow method was called
        self.presenter.run_workflow.assert_called_once_with("workflow1", "credential1")

    def test_on_run_workflow_no_workflow_selected(self):
        """Test that on_run_workflow shows a warning when no workflow is selected."""
        # Set up the mock listbox to return no selection
        self.mock_listbox.return_value.curselection.return_value = ()
        
        # Create the view
        view = WorkflowRunnerView(self.root, self.presenter)
        
        # Set up the view's widgets
        view.workflow_listbox = self.mock_listbox.return_value
        
        # Call the method
        view.on_run_workflow()
        
        # Check that a warning message was shown
        self.mock_messagebox.showwarning.assert_called_once()
        
        # Check that the presenter's run_workflow method was not called
        self.presenter.run_workflow.assert_not_called()

    def test_on_run_workflow_no_credential_selected(self):
        """Test that on_run_workflow shows a warning when no credential is selected."""
        # Set up the mock listbox to return a selected index
        self.mock_listbox.return_value.curselection.return_value = (0,)
        self.mock_listbox.return_value.get.return_value = "workflow1"
        
        # Set up the mock combobox to return no selection
        self.mock_combobox.return_value.get.return_value = ""
        
        # Create the view
        view = WorkflowRunnerView(self.root, self.presenter)
        
        # Set up the view's widgets
        view.workflow_listbox = self.mock_listbox.return_value
        view.credential_combobox = self.mock_combobox.return_value
        
        # Call the method
        view.on_run_workflow()
        
        # Check that a warning message was shown
        self.mock_messagebox.showwarning.assert_called_once()
        
        # Check that the presenter's run_workflow method was not called
        self.presenter.run_workflow.assert_not_called()

    def test_on_run_workflow_failure(self):
        """Test that on_run_workflow logs an error when the presenter returns failure."""
        # Set up the mock listbox to return a selected index
        self.mock_listbox.return_value.curselection.return_value = (0,)
        self.mock_listbox.return_value.get.return_value = "workflow1"
        
        # Set up the mock combobox to return a selected credential
        self.mock_combobox.return_value.get.return_value = "credential1"
        
        # Set up the mock presenter to return failure
        self.presenter.run_workflow.return_value = False
        
        # Create the view
        view = WorkflowRunnerView(self.root, self.presenter)
        
        # Set up the view's widgets
        view.workflow_listbox = self.mock_listbox.return_value
        view.credential_combobox = self.mock_combobox.return_value
        view.log_text = self.mock_text.return_value
        
        # Call the method
        view.on_run_workflow()
        
        # Check that the presenter's run_workflow method was called
        self.presenter.run_workflow.assert_called_once_with("workflow1", "credential1")
        
        # Check that an error was logged
        self.mock_text.return_value.insert.assert_called()

    def test_on_stop_workflow(self):
        """Test that on_stop_workflow stops a running workflow."""
        # Set up the mock presenter
        self.presenter.stop_workflow.return_value = True
        
        # Create the view
        view = WorkflowRunnerView(self.root, self.presenter)
        
        # Set up the view's widgets
        view.log_text = self.mock_text.return_value
        
        # Call the method
        view.on_stop_workflow()
        
        # Check that the presenter's stop_workflow method was called
        self.presenter.stop_workflow.assert_called_once()
        
        # Check that a message was logged
        self.mock_text.return_value.insert.assert_called()

if __name__ == "__main__":
    unittest.main()
