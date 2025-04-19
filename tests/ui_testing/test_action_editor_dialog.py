"""Tests for the ActionEditorDialog."""

import unittest
import tkinter as tk
from unittest.mock import MagicMock, patch
import sys
import os
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import the base test class
from tests.ui_testing.ui_test_base import UITestBase

# Import the dialog to test
from src.ui.dialogs.action_editor_dialog import ActionEditorDialog


class TestActionEditorDialog(UITestBase):
    """Test cases for the ActionEditorDialog."""
    
    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        
        # Mock the ActionFactory
        self.setup_action_factory_mock()
        
        # Create the dialog with no initial data (add mode)
        self.dialog = ActionEditorDialog(self.root)
        
        # Patch the wait_window method to prevent blocking
        self.original_wait_window = self.dialog.wait_window
        self.dialog.wait_window = MagicMock()
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Restore the original wait_window method
        self.dialog.wait_window = self.original_wait_window
        
        # Destroy the dialog
        self.dialog.destroy()
        
        super().tearDown()
    
    def setup_action_factory_mock(self):
        """Set up a mock for the ActionFactory."""
        patcher = patch('src.ui.dialogs.action_editor_dialog.ActionFactory')
        self.mock_action_factory = patcher.start()
        self._patchers.append(patcher)
        
        # Configure the mock
        self.mock_action_factory.get_registered_action_types.return_value = [
            "Navigate", "Click", "Type", "Wait", "Screenshot", "Conditional"
        ]
        
        # Mock the create_action method
        mock_action = MagicMock()
        mock_action.validate.return_value = None  # No validation errors
        self.mock_action_factory.create_action.return_value = mock_action
        
        return self.mock_action_factory
    
    def test_initialization_add_mode(self):
        """Test that the dialog initializes correctly in add mode."""
        # Check that the dialog has the expected title
        self.assertEqual(self.dialog.title(), "Add Action")
        
        # Check that is_edit_mode is False
        self.assertFalse(self.dialog.is_edit_mode)
        
        # Check that the action type is set to the first type
        self.assertEqual(self.dialog._action_type_var.get(), "Navigate")
    
    def test_initialization_edit_mode(self):
        """Test that the dialog initializes correctly in edit mode."""
        # Create a dialog with initial data (edit mode)
        initial_data = {
            "type": "Click",
            "name": "Test Click",
            "selector": "#test-button"
        }
        
        edit_dialog = ActionEditorDialog(self.root, initial_data)
        
        try:
            # Check that the dialog has the expected title
            self.assertEqual(edit_dialog.title(), "Edit Action")
            
            # Check that is_edit_mode is True
            self.assertTrue(edit_dialog.is_edit_mode)
            
            # Check that the action type is set to the initial type
            self.assertEqual(edit_dialog._action_type_var.get(), "Click")
            
            # Check that the name field is populated
            name_var = edit_dialog._param_widgets.get("name", {}).get("var")
            self.assertIsNotNone(name_var)
            self.assertEqual(name_var.get(), "Test Click")
        finally:
            # Clean up
            edit_dialog.destroy()
    
    def test_parameter_fields_for_navigate(self):
        """Test that the correct parameter fields are shown for Navigate action."""
        # Set the action type to Navigate
        self.dialog._action_type_var.set("Navigate")
        
        # Check that the url parameter field is present
        self.assertIn("url", self.dialog._param_widgets)
        
        # Check that the label is correct
        url_label = self.dialog._param_widgets["url"]["label"]
        self.assertEqual(url_label["text"], "URL:")
    
    def test_parameter_fields_for_click(self):
        """Test that the correct parameter fields are shown for Click action."""
        # Set the action type to Click
        self.dialog._action_type_var.set("Click")
        
        # Check that the selector parameter field is present
        self.assertIn("selector", self.dialog._param_widgets)
        
        # Check that the label is correct
        selector_label = self.dialog._param_widgets["selector"]["label"]
        self.assertEqual(selector_label["text"], "CSS Selector:")
    
    def test_parameter_fields_for_type(self):
        """Test that the correct parameter fields are shown for Type action."""
        # Set the action type to Type
        self.dialog._action_type_var.set("Type")
        
        # Check that the required parameter fields are present
        required_params = ["selector", "value_type", "value_key"]
        for param in required_params:
            self.assertIn(param, self.dialog._param_widgets)
    
    def test_parameter_fields_for_conditional(self):
        """Test that the correct parameter fields are shown for Conditional action."""
        # Set the action type to Conditional
        self.dialog._action_type_var.set("Conditional")
        
        # Check that the required parameter fields are present
        required_params = ["condition_type", "selector", "variable_name", "expected_value"]
        for param in required_params:
            self.assertIn(param, self.dialog._param_widgets)
    
    def test_on_ok_valid_data(self):
        """Test the OK button with valid data."""
        # Set the action type to Navigate
        self.dialog._action_type_var.set("Navigate")
        
        # Set the name
        name_var = self.dialog._param_widgets["name"]["var"]
        name_var.set("Test Navigate")
        
        # Set the URL
        url_var = self.dialog._param_widgets["url"]["var"]
        url_var.set("https://example.com")
        
        # Click the OK button
        self.dialog._on_ok()
        
        # Check that the result is set correctly
        self.assertEqual(self.dialog.result["type"], "Navigate")
        self.assertEqual(self.dialog.result["name"], "Test Navigate")
        self.assertEqual(self.dialog.result["url"], "https://example.com")
    
    def test_on_ok_invalid_data(self):
        """Test the OK button with invalid data."""
        # Set the action type to Navigate
        self.dialog._action_type_var.set("Navigate")
        
        # Set the name but leave the URL empty
        name_var = self.dialog._param_widgets["name"]["var"]
        name_var.set("Test Navigate")
        
        # Mock the validation to fail
        mock_action = MagicMock()
        mock_action.validate.side_effect = Exception("URL is required")
        self.mock_action_factory.create_action.return_value = mock_action
        
        # Mock the messagebox.showerror
        with patch('tkinter.messagebox.showerror') as mock_showerror:
            # Click the OK button
            self.dialog._on_ok()
            
            # Check that showerror was called
            mock_showerror.assert_called_once()
            
            # Check that the result is not set
            self.assertIsNone(self.dialog.result)
    
    def test_on_cancel(self):
        """Test the Cancel button."""
        # Click the Cancel button
        self.dialog._on_cancel()
        
        # Check that the result is None
        self.assertIsNone(self.dialog.result)
    
    def test_show_action_selection_dialog(self):
        """Test showing the action selection dialog."""
        # Mock the ActionSelectionDialog
        with patch('src.ui.dialogs.action_editor_dialog.ActionSelectionDialog') as MockDialog:
            # Configure the mock
            mock_dialog_instance = MagicMock()
            MockDialog.return_value = mock_dialog_instance
            mock_dialog_instance.show.return_value = "Type"
            
            # Call the method
            self.dialog._show_action_selection_dialog()
            
            # Check that the dialog was created and shown
            MockDialog.assert_called_once_with(self.dialog)
            mock_dialog_instance.show.assert_called_once()
            
            # Check that the action type was updated
            self.assertEqual(self.dialog._action_type_var.get(), "Type")
    
    def test_browse_for_path(self):
        """Test browsing for a path."""
        # Create a parameter with a browse button
        self.dialog._create_parameter_widget(
            self.dialog._param_frame,
            "file_path",
            "File Path:",
            "entry_with_browse",
            row=0,
            options={'browse_type': 'save_as'}
        )
        
        # Mock the filedialog
        with patch('tkinter.filedialog.asksaveasfilename') as mock_asksaveasfilename:
            # Configure the mock
            mock_asksaveasfilename.return_value = "/path/to/file.png"
            
            # Call the method
            self.dialog._browse_for_path("file_path", "save_as")
            
            # Check that the dialog was shown
            mock_asksaveasfilename.assert_called_once()
            
            # Check that the path was set
            file_path_var = self.dialog._param_widgets["file_path"]["var"]
            self.assertEqual(file_path_var.get(), "/path/to/file.png")


if __name__ == "__main__":
    unittest.main()
