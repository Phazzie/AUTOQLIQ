"""Unit tests for the DialogCoordinator."""

import unittest
import tkinter as tk
from unittest.mock import patch, MagicMock

# Assuming correct paths for imports
from src.ui.coordinators.dialog_coordinator import DialogCoordinator
from src.core.exceptions import UIError

# We need to mock the actual dialog classes themselves
# Need to know their expected paths after refactoring
ACTION_EDITOR_PATH = 'src.ui.dialogs.action_editor_dialog.ActionEditorDialog'
ACTION_SELECTOR_PATH = 'src.ui.dialogs.action_selection_dialog.ActionSelectionDialog'
SIMPLEDIALOG_PATH = 'src.ui.coordinators.dialog_coordinator.simpledialog'
MESSAGEBOX_PATH = 'src.ui.coordinators.dialog_coordinator.messagebox'
FILEDIALOG_PATH = 'src.ui.coordinators.dialog_coordinator.filedialog'

class TestDialogCoordinator(unittest.TestCase):
    """Test suite for DialogCoordinator."""

    def setUp(self):
        """Set up mocks and coordinator instance."""
        self.coordinator = DialogCoordinator()
        self.mock_parent = MagicMock(spec=tk.Widget)

    @patch(ACTION_EDITOR_PATH)
    def test_show_action_editor_add(self, MockActionEditorDialog):
        """Test showing the action editor for adding."""
        mock_dialog_instance = MockActionEditorDialog.return_value
        mock_dialog_instance.show.return_value = {"type": "Click", "selector": "#id"} # Simulate OK

        result = self.coordinator.show_action_editor(self.mock_parent, initial_data=None)

        MockActionEditorDialog.assert_called_once_with(self.mock_parent, initial_data=None)
        mock_dialog_instance.show.assert_called_once()
        self.assertEqual(result, {"type": "Click", "selector": "#id"})

    @patch(ACTION_EDITOR_PATH)
    def test_show_action_editor_edit(self, MockActionEditorDialog):
        """Test showing the action editor for editing."""
        mock_dialog_instance = MockActionEditorDialog.return_value
        initial_data = {"type": "Navigate", "url": "http://a.com"}
        mock_dialog_instance.show.return_value = {"type": "Navigate", "url": "http://b.com"} # Simulate OK with change

        result = self.coordinator.show_action_editor(self.mock_parent, initial_data=initial_data)

        MockActionEditorDialog.assert_called_once_with(self.mock_parent, initial_data=initial_data)
        mock_dialog_instance.show.assert_called_once()
        self.assertEqual(result, {"type": "Navigate", "url": "http://b.com"})

    @patch(ACTION_EDITOR_PATH)
    def test_show_action_editor_cancel(self, MockActionEditorDialog):
        """Test cancelling the action editor."""
        mock_dialog_instance = MockActionEditorDialog.return_value
        mock_dialog_instance.show.return_value = None # Simulate Cancel

        result = self.coordinator.show_action_editor(self.mock_parent, initial_data=None)

        MockActionEditorDialog.assert_called_once_with(self.mock_parent, initial_data=None)
        mock_dialog_instance.show.assert_called_once()
        self.assertIsNone(result)

    @patch(ACTION_EDITOR_PATH)
    def test_show_action_editor_exception(self, MockActionEditorDialog):
        """Test exception handling when showing action editor."""
        MockActionEditorDialog.side_effect = Exception("Dialog creation failed")

        with self.assertRaisesRegex(UIError, "Failed to display action editor"):
            self.coordinator.show_action_editor(self.mock_parent)

    @patch(ACTION_SELECTOR_PATH)
    def test_show_action_selector_select(self, MockActionSelectorDialog):
        """Test selecting an action type."""
        mock_dialog_instance = MockActionSelectorDialog.return_value
        mock_dialog_instance.show.return_value = "Type" # Simulate selection

        result = self.coordinator.show_action_selector(self.mock_parent)

        MockActionSelectorDialog.assert_called_once_with(self.mock_parent)
        mock_dialog_instance.show.assert_called_once()
        self.assertEqual(result, "Type")

    @patch(ACTION_SELECTOR_PATH)
    def test_show_action_selector_cancel(self, MockActionSelectorDialog):
        """Test cancelling the action selector."""
        mock_dialog_instance = MockActionSelectorDialog.return_value
        mock_dialog_instance.show.return_value = None # Simulate Cancel

        result = self.coordinator.show_action_selector(self.mock_parent)

        MockActionSelectorDialog.assert_called_once_with(self.mock_parent)
        mock_dialog_instance.show.assert_called_once()
        self.assertIsNone(result)

    @patch(SIMPLEDIALOG_PATH)
    def test_prompt_for_text_ok(self, mock_simpledialog):
        """Test prompting for text input successfully."""
        mock_simpledialog.askstring.return_value = "User input"

        result = self.coordinator.prompt_for_text(self.mock_parent, "Title", "Prompt", "Initial")

        mock_simpledialog.askstring.assert_called_once_with("Title", "Prompt", initialvalue="Initial", parent=self.mock_parent)
        self.assertEqual(result, "User input")

    @patch(SIMPLEDIALOG_PATH)
    def test_prompt_for_text_cancel(self, mock_simpledialog):
        """Test cancelling the text input prompt."""
        mock_simpledialog.askstring.return_value = None

        result = self.coordinator.prompt_for_text(self.mock_parent, "Title", "Prompt")

        mock_simpledialog.askstring.assert_called_once_with("Title", "Prompt", initialvalue="", parent=self.mock_parent)
        self.assertIsNone(result)

    @patch(MESSAGEBOX_PATH)
    def test_confirm_action_yes(self, mock_messagebox):
        """Test confirming an action with 'Yes'."""
        mock_messagebox.askyesno.return_value = True

        result = self.coordinator.confirm_action(self.mock_parent, "Confirm?", "Proceed?")

        mock_messagebox.askyesno.assert_called_once_with("Confirm?", "Proceed?", parent=self.mock_parent)
        self.assertTrue(result)

    @patch(MESSAGEBOX_PATH)
    def test_confirm_action_no(self, mock_messagebox):
        """Test confirming an action with 'No'."""
        mock_messagebox.askyesno.return_value = False

        result = self.coordinator.confirm_action(self.mock_parent, "Confirm?", "Proceed?")

        mock_messagebox.askyesno.assert_called_once_with("Confirm?", "Proceed?", parent=self.mock_parent)
        self.assertFalse(result)

    @patch(MESSAGEBOX_PATH)
    def test_show_error(self, mock_messagebox):
        """Test showing an error dialog."""
        self.coordinator.show_error(self.mock_parent, "Error", "An error occurred")
        mock_messagebox.showerror.assert_called_once_with("Error", "An error occurred", parent=self.mock_parent)

    @patch(MESSAGEBOX_PATH)
    def test_show_info(self, mock_messagebox):
        """Test showing an info dialog."""
        self.coordinator.show_info(self.mock_parent, "Info", "Information message")
        mock_messagebox.showinfo.assert_called_once_with("Info", "Information message", parent=self.mock_parent)

    @patch(MESSAGEBOX_PATH)
    def test_show_warning(self, mock_messagebox):
        """Test showing a warning dialog."""
        self.coordinator.show_warning(self.mock_parent, "Warning", "Warning message")
        mock_messagebox.showwarning.assert_called_once_with("Warning", "Warning message", parent=self.mock_parent)

    @patch(FILEDIALOG_PATH)
    def test_browse_for_file_selected(self, mock_filedialog):
        """Test browsing for a file with selection."""
        mock_filedialog.askopenfilename.return_value = "/path/to/file.txt"

        result = self.coordinator.browse_for_file(
            self.mock_parent,
            title="Select Test File",
            initial_dir="/initial/dir",
            file_types=[("Text Files", "*.txt")]
        )

        mock_filedialog.askopenfilename.assert_called_once_with(
            title="Select Test File",
            initialdir="/initial/dir",
            filetypes=[("Text Files", "*.txt")],
            parent=self.mock_parent
        )
        self.assertEqual(result, "/path/to/file.txt")

    @patch(FILEDIALOG_PATH)
    def test_browse_for_file_cancelled(self, mock_filedialog):
        """Test browsing for a file with cancellation."""
        mock_filedialog.askopenfilename.return_value = ""  # Empty string on cancel

        result = self.coordinator.browse_for_file(self.mock_parent)

        mock_filedialog.askopenfilename.assert_called_once_with(
            title="Select File",
            initialdir=".",
            filetypes=[("All Files", "*.*")],
            parent=self.mock_parent
        )
        self.assertIsNone(result)

    @patch(FILEDIALOG_PATH)
    def test_browse_for_directory_selected(self, mock_filedialog):
        """Test browsing for a directory with selection."""
        mock_filedialog.askdirectory.return_value = "/path/to/directory"

        result = self.coordinator.browse_for_directory(
            self.mock_parent,
            title="Select Test Directory",
            initial_dir="/initial/dir"
        )

        mock_filedialog.askdirectory.assert_called_once_with(
            title="Select Test Directory",
            initialdir="/initial/dir",
            parent=self.mock_parent
        )
        self.assertEqual(result, "/path/to/directory")

    @patch(FILEDIALOG_PATH)
    def test_browse_for_directory_cancelled(self, mock_filedialog):
        """Test browsing for a directory with cancellation."""
        mock_filedialog.askdirectory.return_value = ""  # Empty string on cancel

        result = self.coordinator.browse_for_directory(self.mock_parent)

        mock_filedialog.askdirectory.assert_called_once_with(
            title="Select Directory",
            initialdir=".",
            parent=self.mock_parent
        )
        self.assertIsNone(result)

    @patch(FILEDIALOG_PATH)
    def test_browse_for_save_file_selected(self, mock_filedialog):
        """Test browsing for a save file location with selection."""
        mock_filedialog.asksaveasfilename.return_value = "/path/to/save/file.txt"

        result = self.coordinator.browse_for_save_file(
            self.mock_parent,
            title="Save Test File",
            initial_dir="/initial/dir",
            initial_file="default.txt",
            file_types=[("Text Files", "*.txt")]
        )

        mock_filedialog.asksaveasfilename.assert_called_once_with(
            title="Save Test File",
            initialdir="/initial/dir",
            initialfile="default.txt",
            filetypes=[("Text Files", "*.txt")],
            parent=self.mock_parent
        )
        self.assertEqual(result, "/path/to/save/file.txt")

    @patch(FILEDIALOG_PATH)
    def test_browse_for_save_file_cancelled(self, mock_filedialog):
        """Test browsing for a save file location with cancellation."""
        mock_filedialog.asksaveasfilename.return_value = ""  # Empty string on cancel

        result = self.coordinator.browse_for_save_file(self.mock_parent)

        mock_filedialog.asksaveasfilename.assert_called_once_with(
            title="Save As",
            initialdir=".",
            initialfile="",
            filetypes=[("All Files", "*.*")],
            parent=self.mock_parent
        )
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
