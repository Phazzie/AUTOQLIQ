import unittest
from unittest.mock import MagicMock, patch
import tkinter as tk

from src.ui.workflow_runner import WorkflowRunnerView
from src.core.exceptions import UIError


class TestWorkflowRunnerView(unittest.TestCase):
    @patch('tkinter.ttk.Frame')
    @patch('tkinter.ttk.LabelFrame')
    @patch('tkinter.Listbox')
    @patch('tkinter.ttk.Button')
    def setUp(self, mock_button, mock_listbox, mock_labelframe, mock_frame):
        # Create a mock root window with the necessary attributes
        self.root = MagicMock(spec=tk.Tk)
        # Add the tk attribute to the mock
        self.root.tk = MagicMock()
        # Add the children attribute to the mock
        self.root.children = {}
        # Add the _w attribute to the mock
        self.root._w = "."
        # Add the winfo_toplevel method to the mock
        self.root.winfo_toplevel = MagicMock(return_value=self.root)

        # Set up the mocks for tkinter widgets
        self.mock_frame = mock_frame
        self.mock_labelframe = mock_labelframe
        self.mock_listbox = mock_listbox
        self.mock_button = mock_button

        # Create mock dependencies
        self.presenter = MagicMock()
        
        # Create a list of mock workflows for testing
        self.mock_workflows = ["workflow1", "workflow2", "workflow3"]
        self.presenter.get_workflow_list.return_value = self.mock_workflows
        
        # Create a list of mock credentials for testing
        self.mock_credentials = [
            {"name": "credential1", "username": "user1", "password": "pass1"},
            {"name": "credential2", "username": "user2", "password": "pass2"}
        ]
        self.presenter.get_credential_list.return_value = self.mock_credentials

    def test_initialization(self):
        # Act
        view = WorkflowRunnerView(self.root, self.presenter)
        
        # Assert
        self.assertEqual(view.root, self.root)
        self.assertEqual(view.presenter, self.presenter)
        self.assertIsNotNone(view.main_frame)
        
        # Verify that the presenter's get_workflow_list method was called
        self.presenter.get_workflow_list.assert_called_once()
    
    def test_create_widgets(self):
        # Arrange
        view = WorkflowRunnerView(self.root, self.presenter)
        
        # Act - create_widgets is called in __init__
        
        # Assert - Check that all required widgets are created
        self.assertIsNotNone(view.workflow_listbox)
        self.assertIsNotNone(view.credential_combobox)
        self.assertIsNotNone(view.run_button)
        self.assertIsNotNone(view.stop_button)
        self.assertIsNotNone(view.log_text)
    
    def test_populate_workflow_list(self):
        # Arrange
        view = WorkflowRunnerView(self.root, self.presenter)
        view.workflow_listbox = MagicMock()
        
        # Act
        view.populate_workflow_list()
        
        # Assert
        # Check that the listbox was cleared and populated with workflows
        view.workflow_listbox.delete.assert_called_with(0, tk.END)
        for workflow in self.mock_workflows:
            view.workflow_listbox.insert.assert_any_call(tk.END, workflow)
    
    def test_populate_credential_list(self):
        # Arrange
        view = WorkflowRunnerView(self.root, self.presenter)
        view.credential_combobox = MagicMock()
        
        # Act
        view.populate_credential_list()
        
        # Assert
        # Check that the combobox was configured with credential names
        credential_names = [cred["name"] for cred in self.mock_credentials]
        view.credential_combobox.configure.assert_called_with(values=credential_names)
    
    def test_get_selected_workflow(self):
        # Arrange
        view = WorkflowRunnerView(self.root, self.presenter)
        view.workflow_listbox = MagicMock()
        
        # Mock the curselection method to return a selection
        view.workflow_listbox.curselection.return_value = (0,)
        view.workflow_listbox.get.return_value = "workflow1"
        
        # Act
        result = view.get_selected_workflow()
        
        # Assert
        self.assertEqual(result, "workflow1")
    
    def test_get_selected_workflow_no_selection(self):
        # Arrange
        view = WorkflowRunnerView(self.root, self.presenter)
        view.workflow_listbox = MagicMock()
        
        # Mock the curselection method to return an empty tuple
        view.workflow_listbox.curselection.return_value = ()
        
        # Act
        result = view.get_selected_workflow()
        
        # Assert
        self.assertIsNone(result)
    
    def test_get_selected_credential(self):
        # Arrange
        view = WorkflowRunnerView(self.root, self.presenter)
        view.credential_combobox = MagicMock()
        
        # Mock the get method to return a selection
        view.credential_combobox.get.return_value = "credential1"
        
        # Act
        result = view.get_selected_credential()
        
        # Assert
        self.assertEqual(result, "credential1")
    
    def test_on_run_workflow(self):
        # Arrange
        view = WorkflowRunnerView(self.root, self.presenter)
        
        # Mock the get_selected_workflow method
        view.get_selected_workflow = MagicMock(return_value="workflow1")
        
        # Mock the get_selected_credential method
        view.get_selected_credential = MagicMock(return_value="credential1")
        
        # Mock the log_message method
        view.log_message = MagicMock()
        
        # Mock the presenter's run_workflow method
        self.presenter.run_workflow.return_value = True
        
        # Act
        view.on_run_workflow()
        
        # Assert
        # Check that the presenter's run_workflow method was called
        self.presenter.run_workflow.assert_called_once_with("workflow1", "credential1")
        
        # Check that log messages were added
        view.log_message.assert_any_call("Starting workflow: workflow1")
        view.log_message.assert_any_call("Workflow completed successfully")
    
    def test_on_run_workflow_no_workflow_selected(self):
        # Arrange
        view = WorkflowRunnerView(self.root, self.presenter)
        
        # Mock the get_selected_workflow method to return None
        view.get_selected_workflow = MagicMock(return_value=None)
        
        # Mock the messagebox.showwarning function
        with patch("tkinter.messagebox.showwarning") as mock_showwarning:
            # Act
            view.on_run_workflow()
            
            # Assert
            # Check that the presenter's run_workflow method was not called
            self.presenter.run_workflow.assert_not_called()
            
            # Check that a warning message was shown
            mock_showwarning.assert_called_once()
    
    def test_on_run_workflow_no_credential_selected(self):
        # Arrange
        view = WorkflowRunnerView(self.root, self.presenter)
        
        # Mock the get_selected_workflow method
        view.get_selected_workflow = MagicMock(return_value="workflow1")
        
        # Mock the get_selected_credential method to return None
        view.get_selected_credential = MagicMock(return_value=None)
        
        # Mock the messagebox.showwarning function
        with patch("tkinter.messagebox.showwarning") as mock_showwarning:
            # Act
            view.on_run_workflow()
            
            # Assert
            # Check that the presenter's run_workflow method was not called
            self.presenter.run_workflow.assert_not_called()
            
            # Check that a warning message was shown
            mock_showwarning.assert_called_once()
    
    def test_on_run_workflow_error(self):
        # Arrange
        view = WorkflowRunnerView(self.root, self.presenter)
        
        # Mock the get_selected_workflow method
        view.get_selected_workflow = MagicMock(return_value="workflow1")
        
        # Mock the get_selected_credential method
        view.get_selected_credential = MagicMock(return_value="credential1")
        
        # Mock the log_message method
        view.log_message = MagicMock()
        
        # Mock the presenter's run_workflow method to raise an exception
        self.presenter.run_workflow.side_effect = Exception("Test error")
        
        # Mock the messagebox.showerror function
        with patch("tkinter.messagebox.showerror") as mock_showerror:
            # Act
            view.on_run_workflow()
            
            # Assert
            # Check that the presenter's run_workflow method was called
            self.presenter.run_workflow.assert_called_once_with("workflow1", "credential1")
            
            # Check that log messages were added
            view.log_message.assert_any_call("Starting workflow: workflow1")
            view.log_message.assert_any_call("Error running workflow: Test error")
            
            # Check that an error message was shown
            mock_showerror.assert_called_once()
    
    def test_on_stop_workflow(self):
        # Arrange
        view = WorkflowRunnerView(self.root, self.presenter)
        
        # Mock the log_message method
        view.log_message = MagicMock()
        
        # Mock the presenter's stop_workflow method
        self.presenter.stop_workflow.return_value = True
        
        # Act
        view.on_stop_workflow()
        
        # Assert
        # Check that the presenter's stop_workflow method was called
        self.presenter.stop_workflow.assert_called_once()
        
        # Check that a log message was added
        view.log_message.assert_called_once_with("Stopping workflow...")
    
    def test_log_message(self):
        # Arrange
        view = WorkflowRunnerView(self.root, self.presenter)
        view.log_text = MagicMock()
        
        # Act
        view.log_message("Test message")
        
        # Assert
        # Check that the message was added to the log
        view.log_text.configure.assert_called()
        view.log_text.see.assert_called_with(tk.END)


if __name__ == "__main__":
    unittest.main()
