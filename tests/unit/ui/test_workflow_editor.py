import unittest
from unittest.mock import MagicMock, patch, PropertyMock
import tkinter as tk

from src.ui.workflow_editor import WorkflowEditorView
from src.core.exceptions import UIError


class TestWorkflowEditorView(unittest.TestCase):
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

        # Return the mocks from the constructors
        mock_frame.return_value = MagicMock()
        mock_labelframe.return_value = MagicMock()
        mock_listbox.return_value = MagicMock()
        mock_button.return_value = MagicMock()

        # Create mock dependencies
        self.presenter = MagicMock()

        # Create a list of mock workflows for testing
        self.mock_workflows = ["workflow1", "workflow2", "workflow3"]
        self.presenter.get_workflow_list.return_value = self.mock_workflows

        # Create a mock action for testing
        self.mock_action = {"type": "Navigate", "url": "https://example.com"}

    def test_initialization(self):
        # Act
        view = WorkflowEditorView(self.root, self.presenter)

        # Assert
        self.assertEqual(view.root, self.root)
        self.assertEqual(view.presenter, self.presenter)
        self.assertIsNotNone(view.main_frame)

        # Verify that the presenter's get_workflow_list method was called
        self.presenter.get_workflow_list.assert_called_once()

    def test_create_widgets(self):
        # Arrange
        view = WorkflowEditorView(self.root, self.presenter)

        # Act - create_widgets is called in __init__

        # Assert - Check that all required widgets are created
        self.assertIsNotNone(view.workflow_listbox)
        self.assertIsNotNone(view.action_listbox)
        self.assertIsNotNone(view.new_workflow_button)
        self.assertIsNotNone(view.save_workflow_button)
        self.assertIsNotNone(view.delete_workflow_button)
        self.assertIsNotNone(view.add_action_button)
        self.assertIsNotNone(view.edit_action_button)
        self.assertIsNotNone(view.delete_action_button)

    def test_populate_workflow_list(self):
        # Arrange
        view = WorkflowEditorView(self.root, self.presenter)
        view.workflow_listbox = MagicMock()

        # Act
        view.populate_workflow_list()

        # Assert
        # Check that the listbox was cleared and populated with workflows
        view.workflow_listbox.delete.assert_called_with(0, tk.END)
        for workflow in self.mock_workflows:
            view.workflow_listbox.insert.assert_any_call(tk.END, workflow)

    def test_on_workflow_selected(self):
        # Arrange
        view = WorkflowEditorView(self.root, self.presenter)
        view.workflow_listbox = MagicMock()
        view.action_listbox = MagicMock()

        # Mock the get_selected_workflow method
        view.get_selected_workflow = MagicMock(return_value="workflow1")

        # Mock the presenter's load_workflow method
        mock_actions = [MagicMock(), MagicMock()]
        mock_actions[0].to_dict.return_value = {"type": "Navigate", "url": "https://example.com"}
        mock_actions[1].to_dict.return_value = {"type": "Click", "selector": "#button"}
        self.presenter.load_workflow.return_value = mock_actions

        # Act
        view.on_workflow_selected(None)  # Event parameter is not used

        # Assert
        # Check that the presenter's load_workflow method was called
        self.presenter.load_workflow.assert_called_once_with("workflow1")

        # Check that the action listbox was cleared and populated with actions
        view.action_listbox.delete.assert_called_with(0, tk.END)
        view.action_listbox.insert.assert_any_call(tk.END, "Navigate: https://example.com")
        view.action_listbox.insert.assert_any_call(tk.END, "Click: #button")

    def test_on_workflow_selected_no_selection(self):
        # Arrange
        view = WorkflowEditorView(self.root, self.presenter)
        view.workflow_listbox = MagicMock()
        view.action_listbox = MagicMock()

        # Mock the get_selected_workflow method to return None
        view.get_selected_workflow = MagicMock(return_value=None)

        # Act
        view.on_workflow_selected(None)  # Event parameter is not used

        # Assert
        # Check that the presenter's load_workflow method was not called
        self.presenter.load_workflow.assert_not_called()

        # Check that the action listbox was cleared
        view.action_listbox.delete.assert_called_with(0, tk.END)

    def test_get_selected_workflow(self):
        # Arrange
        view = WorkflowEditorView(self.root, self.presenter)
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
        view = WorkflowEditorView(self.root, self.presenter)
        view.workflow_listbox = MagicMock()

        # Mock the curselection method to return an empty tuple
        view.workflow_listbox.curselection.return_value = ()

        # Act
        result = view.get_selected_workflow()

        # Assert
        self.assertIsNone(result)

    def test_get_selected_action_index(self):
        # Arrange
        view = WorkflowEditorView(self.root, self.presenter)
        view.action_listbox = MagicMock()

        # Mock the curselection method to return a selection
        view.action_listbox.curselection.return_value = (1,)

        # Act
        result = view.get_selected_action_index()

        # Assert
        self.assertEqual(result, 1)

    def test_get_selected_action_index_no_selection(self):
        # Arrange
        view = WorkflowEditorView(self.root, self.presenter)
        view.action_listbox = MagicMock()

        # Mock the curselection method to return an empty tuple
        view.action_listbox.curselection.return_value = ()

        # Act
        result = view.get_selected_action_index()

        # Assert
        self.assertIsNone(result)

    def test_on_new_workflow(self):
        # Arrange
        view = WorkflowEditorView(self.root, self.presenter)

        # Mock the simpledialog.askstring function
        with patch("tkinter.simpledialog.askstring", return_value="new_workflow"):
            # Mock the presenter's create_workflow method
            self.presenter.create_workflow.return_value = True

            # Mock the populate_workflow_list method
            view.populate_workflow_list = MagicMock()

            # Act
            view.on_new_workflow()

            # Assert
            # Check that the presenter's create_workflow method was called
            self.presenter.create_workflow.assert_called_once_with("new_workflow")

            # Check that the workflow list was refreshed
            view.populate_workflow_list.assert_called_once()

    def test_on_new_workflow_cancelled(self):
        # Arrange
        view = WorkflowEditorView(self.root, self.presenter)

        # Mock the simpledialog.askstring function to return None (cancelled)
        with patch("tkinter.simpledialog.askstring", return_value=None):
            # Mock the populate_workflow_list method
            view.populate_workflow_list = MagicMock()

            # Act
            view.on_new_workflow()

            # Assert
            # Check that the presenter's create_workflow method was not called
            self.presenter.create_workflow.assert_not_called()

            # Check that the workflow list was not refreshed
            view.populate_workflow_list.assert_not_called()

    def test_on_save_workflow(self):
        # Arrange
        view = WorkflowEditorView(self.root, self.presenter)

        # Mock the get_selected_workflow method
        view.get_selected_workflow = MagicMock(return_value="workflow1")

        # Mock the presenter's save_workflow method
        self.presenter.save_workflow.return_value = True

        # Act
        view.on_save_workflow()

        # Assert
        # Check that the presenter's save_workflow method was called
        self.presenter.save_workflow.assert_called_once_with("workflow1")

    def test_on_save_workflow_no_selection(self):
        # Arrange
        view = WorkflowEditorView(self.root, self.presenter)

        # Mock the get_selected_workflow method to return None
        view.get_selected_workflow = MagicMock(return_value=None)

        # Mock the messagebox.showwarning function
        with patch("tkinter.messagebox.showwarning") as mock_showwarning:
            # Act
            view.on_save_workflow()

            # Assert
            # Check that the presenter's save_workflow method was not called
            self.presenter.save_workflow.assert_not_called()

            # Check that a warning message was shown
            mock_showwarning.assert_called_once()

    def test_on_delete_workflow(self):
        # Arrange
        view = WorkflowEditorView(self.root, self.presenter)

        # Mock the get_selected_workflow method
        view.get_selected_workflow = MagicMock(return_value="workflow1")

        # Mock the messagebox.askyesno function to return True (confirmed)
        with patch("tkinter.messagebox.askyesno", return_value=True):
            # Mock the presenter's delete_workflow method
            self.presenter.delete_workflow.return_value = True

            # Mock the populate_workflow_list method
            view.populate_workflow_list = MagicMock()

            # Act
            view.on_delete_workflow()

            # Assert
            # Check that the presenter's delete_workflow method was called
            self.presenter.delete_workflow.assert_called_once_with("workflow1")

            # Check that the workflow list was refreshed
            view.populate_workflow_list.assert_called_once()

    def test_on_delete_workflow_cancelled(self):
        # Arrange
        view = WorkflowEditorView(self.root, self.presenter)

        # Mock the get_selected_workflow method
        view.get_selected_workflow = MagicMock(return_value="workflow1")

        # Mock the messagebox.askyesno function to return False (cancelled)
        with patch("tkinter.messagebox.askyesno", return_value=False):
            # Act
            view.on_delete_workflow()

            # Assert
            # Check that the presenter's delete_workflow method was not called
            self.presenter.delete_workflow.assert_not_called()

    def test_on_delete_workflow_no_selection(self):
        # Arrange
        view = WorkflowEditorView(self.root, self.presenter)

        # Mock the get_selected_workflow method to return None
        view.get_selected_workflow = MagicMock(return_value=None)

        # Mock the messagebox.showwarning function
        with patch("tkinter.messagebox.showwarning") as mock_showwarning:
            # Act
            view.on_delete_workflow()

            # Assert
            # Check that the presenter's delete_workflow method was not called
            self.presenter.delete_workflow.assert_not_called()

            # Check that a warning message was shown
            mock_showwarning.assert_called_once()

    def test_on_add_action(self):
        # Arrange
        view = WorkflowEditorView(self.root, self.presenter)
        view.action_listbox = MagicMock()

        # Mock the get_selected_workflow method
        view.get_selected_workflow = MagicMock(return_value="workflow1")

        # Mock the show_action_dialog method
        view.show_action_dialog = MagicMock(return_value=self.mock_action)

        # Mock the presenter's add_action method
        self.presenter.add_action.return_value = True

        # Act
        view.on_add_action()

        # Assert
        # Check that the show_action_dialog method was called
        view.show_action_dialog.assert_called_once_with(None)

        # Check that the presenter's add_action method was called
        self.presenter.add_action.assert_called_once_with("workflow1", self.mock_action)

        # Check that the action was added to the listbox
        view.action_listbox.insert.assert_called_with(tk.END, "Navigate: https://example.com")

    def test_on_add_action_no_workflow_selected(self):
        # Arrange
        view = WorkflowEditorView(self.root, self.presenter)

        # Mock the get_selected_workflow method to return None
        view.get_selected_workflow = MagicMock(return_value=None)

        # Mock the messagebox.showwarning function
        with patch("tkinter.messagebox.showwarning") as mock_showwarning:
            # Act
            view.on_add_action()

            # Assert
            # Check that the show_action_dialog method was not called
            self.assertFalse(hasattr(view, "show_action_dialog_called"))

            # Check that a warning message was shown
            mock_showwarning.assert_called_once()

    def test_on_add_action_cancelled(self):
        # Arrange
        view = WorkflowEditorView(self.root, self.presenter)

        # Mock the get_selected_workflow method
        view.get_selected_workflow = MagicMock(return_value="workflow1")

        # Mock the show_action_dialog method to return None (cancelled)
        view.show_action_dialog = MagicMock(return_value=None)

        # Act
        view.on_add_action()

        # Assert
        # Check that the presenter's add_action method was not called
        self.presenter.add_action.assert_not_called()

    def test_on_edit_action(self):
        # Arrange
        view = WorkflowEditorView(self.root, self.presenter)
        view.action_listbox = MagicMock()

        # Mock the get_selected_workflow method
        view.get_selected_workflow = MagicMock(return_value="workflow1")

        # Mock the get_selected_action_index method
        view.get_selected_action_index = MagicMock(return_value=0)

        # Mock the presenter's get_action method
        self.presenter.get_action.return_value = self.mock_action

        # Mock the show_action_dialog method
        updated_action = {"type": "Navigate", "url": "https://updated.com"}
        view.show_action_dialog = MagicMock(return_value=updated_action)

        # Mock the presenter's update_action method
        self.presenter.update_action.return_value = True

        # Act
        view.on_edit_action()

        # Assert
        # Check that the presenter's get_action method was called
        self.presenter.get_action.assert_called_once_with("workflow1", 0)

        # Check that the show_action_dialog method was called with the current action
        view.show_action_dialog.assert_called_once_with(self.mock_action)

        # Check that the presenter's update_action method was called
        self.presenter.update_action.assert_called_once_with("workflow1", 0, updated_action)

        # Check that the action was updated in the listbox
        view.action_listbox.delete.assert_called_with(0)
        view.action_listbox.insert.assert_called_with(0, "Navigate: https://updated.com")

    def test_on_edit_action_no_workflow_selected(self):
        # Arrange
        view = WorkflowEditorView(self.root, self.presenter)

        # Mock the get_selected_workflow method to return None
        view.get_selected_workflow = MagicMock(return_value=None)

        # Mock the messagebox.showwarning function
        with patch("tkinter.messagebox.showwarning") as mock_showwarning:
            # Act
            view.on_edit_action()

            # Assert
            # Check that a warning message was shown
            mock_showwarning.assert_called_once()

    def test_on_edit_action_no_action_selected(self):
        # Arrange
        view = WorkflowEditorView(self.root, self.presenter)

        # Mock the get_selected_workflow method
        view.get_selected_workflow = MagicMock(return_value="workflow1")

        # Mock the get_selected_action_index method to return None
        view.get_selected_action_index = MagicMock(return_value=None)

        # Mock the messagebox.showwarning function
        with patch("tkinter.messagebox.showwarning") as mock_showwarning:
            # Act
            view.on_edit_action()

            # Assert
            # Check that a warning message was shown
            mock_showwarning.assert_called_once()

    def test_on_edit_action_cancelled(self):
        # Arrange
        view = WorkflowEditorView(self.root, self.presenter)

        # Mock the get_selected_workflow method
        view.get_selected_workflow = MagicMock(return_value="workflow1")

        # Mock the get_selected_action_index method
        view.get_selected_action_index = MagicMock(return_value=0)

        # Mock the presenter's get_action method
        self.presenter.get_action.return_value = self.mock_action

        # Mock the show_action_dialog method to return None (cancelled)
        view.show_action_dialog = MagicMock(return_value=None)

        # Act
        view.on_edit_action()

        # Assert
        # Check that the presenter's update_action method was not called
        self.presenter.update_action.assert_not_called()

    def test_on_delete_action(self):
        # Arrange
        view = WorkflowEditorView(self.root, self.presenter)
        view.action_listbox = MagicMock()

        # Mock the get_selected_workflow method
        view.get_selected_workflow = MagicMock(return_value="workflow1")

        # Mock the get_selected_action_index method
        view.get_selected_action_index = MagicMock(return_value=0)

        # Mock the messagebox.askyesno function to return True (confirmed)
        with patch("tkinter.messagebox.askyesno", return_value=True):
            # Mock the presenter's delete_action method
            self.presenter.delete_action.return_value = True

            # Act
            view.on_delete_action()

            # Assert
            # Check that the presenter's delete_action method was called
            self.presenter.delete_action.assert_called_once_with("workflow1", 0)

            # Check that the action was removed from the listbox
            view.action_listbox.delete.assert_called_with(0)

    def test_on_delete_action_no_workflow_selected(self):
        # Arrange
        view = WorkflowEditorView(self.root, self.presenter)

        # Mock the get_selected_workflow method to return None
        view.get_selected_workflow = MagicMock(return_value=None)

        # Mock the messagebox.showwarning function
        with patch("tkinter.messagebox.showwarning") as mock_showwarning:
            # Act
            view.on_delete_action()

            # Assert
            # Check that a warning message was shown
            mock_showwarning.assert_called_once()

    def test_on_delete_action_no_action_selected(self):
        # Arrange
        view = WorkflowEditorView(self.root, self.presenter)

        # Mock the get_selected_workflow method
        view.get_selected_workflow = MagicMock(return_value="workflow1")

        # Mock the get_selected_action_index method to return None
        view.get_selected_action_index = MagicMock(return_value=None)

        # Mock the messagebox.showwarning function
        with patch("tkinter.messagebox.showwarning") as mock_showwarning:
            # Act
            view.on_delete_action()

            # Assert
            # Check that a warning message was shown
            mock_showwarning.assert_called_once()

    def test_on_delete_action_cancelled(self):
        # Arrange
        view = WorkflowEditorView(self.root, self.presenter)

        # Mock the get_selected_workflow method
        view.get_selected_workflow = MagicMock(return_value="workflow1")

        # Mock the get_selected_action_index method
        view.get_selected_action_index = MagicMock(return_value=0)

        # Mock the messagebox.askyesno function to return False (cancelled)
        with patch("tkinter.messagebox.askyesno", return_value=False):
            # Act
            view.on_delete_action()

            # Assert
            # Check that the presenter's delete_action method was not called
            self.presenter.delete_action.assert_not_called()

    @patch('tkinter.ttk.OptionMenu')
    @patch('tkinter.ttk.Entry')
    @patch('tkinter.StringVar')
    @patch('tkinter.Toplevel')
    def test_show_action_dialog(self, MockToplevel, MockStringVar, MockEntry, MockOptionMenu):
        # This test is more complex as it involves creating a Toplevel window
        # We'll mock the Toplevel and test the basic functionality

        # Arrange
        view = WorkflowEditorView(self.root, self.presenter)

        # Mock the dialog window
        mock_dialog = MagicMock()
        MockToplevel.return_value = mock_dialog
        mock_dialog.children = {}

        # Set up the mock StringVar
        mock_type_var = MagicMock()
        MockStringVar.return_value = mock_type_var
        mock_type_var.get.return_value = "Navigate"

        # Set up the mock Entry
        mock_entry = MagicMock()
        MockEntry.return_value = mock_entry
        mock_entry.get.return_value = "https://example.com"

        # Set up the mock OptionMenu
        mock_option_menu = MagicMock()
        MockOptionMenu.return_value = mock_option_menu

        # Mock the ttk.Frame
        mock_frame = MagicMock()
        with patch('tkinter.ttk.Frame', return_value=mock_frame):
            # Mock the ttk.Button
            mock_button = MagicMock()
            with patch('tkinter.ttk.Button', return_value=mock_button):
                # Mock the ttk.Label
                mock_label = MagicMock()
                with patch('tkinter.ttk.Label', return_value=mock_label):
                    # Set up the on_ok function to set the result
                    def side_effect(*args, **kwargs):
                        # Simulate the on_ok function being called
                        view.show_action_dialog_result = {
                            "type": "Navigate",
                            "url": "https://example.com"
                        }
                        return None

                    # Make the button's command call our side effect
                    mock_button.configure = MagicMock(side_effect=side_effect)

                    # Act - Call with an existing action
                    result = view.show_action_dialog(self.mock_action)

                    # Assert
                    # Check that the dialog was created
                    MockToplevel.assert_called_once()

                    # Check that the StringVar was set to the action type
                    mock_type_var.set.assert_called_with("Navigate")

                    # Check that the result contains the expected action
                    self.assertEqual(result["type"], "Navigate")
                    self.assertEqual(result["url"], "https://example.com")


if __name__ == "__main__":
    unittest.main()
