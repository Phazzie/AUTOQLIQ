"""Tests for the ActionSelectionDialog."""

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
from src.ui.dialogs.action_selection_dialog import ActionSelectionDialog


class TestActionSelectionDialog(UITestBase):
    """Test cases for the ActionSelectionDialog."""
    
    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        
        # Create the dialog
        self.dialog = ActionSelectionDialog(self.root)
        
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
    
    def test_initialization(self):
        """Test that the dialog initializes correctly."""
        # Check that the dialog has the expected title
        self.assertEqual(self.dialog.title(), "Select Action Type")
        
        # Check that the dialog has the expected categories
        expected_categories = [
            "Navigation",
            "Interaction",
            "Waiting",
            "Data & Verification",
            "Control Flow"
        ]
        
        # Get the actual categories from the dialog
        category_frames = [child for child in self.dialog.category_frame.winfo_children() 
                          if isinstance(child, tk.LabelFrame)]
        actual_categories = [frame['text'] for frame in category_frames]
        
        # Check that all expected categories are present
        for category in expected_categories:
            self.assertIn(category, actual_categories)
    
    def test_action_buttons(self):
        """Test that action buttons are created for each action type."""
        # Get all buttons in the dialog
        buttons = []
        for child in self.dialog.category_frame.winfo_children():
            if isinstance(child, tk.LabelFrame):
                buttons.extend([btn for btn in child.winfo_children() 
                               if isinstance(btn, tk.Button)])
        
        # Check that we have buttons for all action types
        expected_actions = [
            "Navigate",
            "Click",
            "Type",
            "Wait",
            "Screenshot",
            "Conditional",
            "JavaScriptCondition"
        ]
        
        actual_actions = [btn['text'].split()[0] for btn in buttons]
        
        for action in expected_actions:
            self.assertIn(action, actual_actions)
    
    def test_search_functionality(self):
        """Test the search functionality."""
        # Set up a search term
        self.dialog.search_var.set("click")
        
        # Trigger the search
        self.dialog._on_search()
        
        # Check that only the matching action is visible
        for child in self.dialog.category_frame.winfo_children():
            if isinstance(child, tk.LabelFrame):
                for btn in child.winfo_children():
                    if isinstance(btn, tk.Button):
                        if "Click" in btn['text']:
                            self.assertTrue(btn.winfo_viewable())
                        else:
                            self.assertFalse(btn.winfo_viewable())
    
    def test_action_selection(self):
        """Test selecting an action."""
        # Find the Navigate button
        navigate_button = None
        for child in self.dialog.category_frame.winfo_children():
            if isinstance(child, tk.LabelFrame):
                for btn in child.winfo_children():
                    if isinstance(btn, tk.Button) and "Navigate" in btn['text']:
                        navigate_button = btn
                        break
        
        self.assertIsNotNone(navigate_button, "Navigate button not found")
        
        # Click the button
        navigate_button.invoke()
        
        # Check that the selected_action is set correctly
        self.assertEqual(self.dialog.selected_action, "Navigate")
    
    def test_show_method(self):
        """Test the show method."""
        # Set up the selected_action
        self.dialog.selected_action = "Click"
        
        # Call the show method
        result = self.dialog.show()
        
        # Check that the result is the selected action
        self.assertEqual(result, "Click")
    
    def test_cancel(self):
        """Test cancelling the dialog."""
        # Find the Cancel button
        cancel_button = None
        for child in self.dialog.winfo_children():
            if isinstance(child, tk.Frame):
                for btn in child.winfo_children():
                    if isinstance(btn, tk.Button) and btn['text'] == "Cancel":
                        cancel_button = btn
                        break
        
        self.assertIsNotNone(cancel_button, "Cancel button not found")
        
        # Click the Cancel button
        cancel_button.invoke()
        
        # Check that the selected_action is None
        self.assertIsNone(self.dialog.selected_action)


if __name__ == "__main__":
    unittest.main()
