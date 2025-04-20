"""Tests for the TemplateManagerDialog.

This module tests the TemplateManagerDialog class.
"""

import unittest
from unittest.mock import MagicMock, patch
import tkinter as tk

from src.ui.dialogs.template_manager_dialog import TemplateManagerDialog
from src.core.template.repository import TemplateRepository
from src.core.exceptions import RepositoryError

class TestTemplateManagerDialog(unittest.TestCase):
    """Test case for TemplateManagerDialog."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window
        
        # Create a mock template repository
        self.mock_repository = MagicMock(spec=TemplateRepository)
        
        # Set up mock repository to return test templates
        self.test_templates = [
            {
                "name": "Template 1",
                "description": "Test Template 1",
                "actions": [
                    {"type": "Navigate", "name": "Navigate Action", "url": "https://example.com"}
                ]
            },
            {
                "name": "Template 2",
                "description": "Test Template 2",
                "actions": [
                    {"type": "Click", "name": "Click Action", "selector": "#test-button"}
                ]
            }
        ]
        self.mock_repository.list_templates.return_value = self.test_templates
        
        # Mock get_template to return the correct template
        def mock_get_template(name):
            for template in self.test_templates:
                if template["name"] == name:
                    return template
            return None
        
        self.mock_repository.get_template.side_effect = mock_get_template
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.root.destroy()
    
    def test_init(self):
        """Test initialization."""
        # Create dialog with mock repository
        with patch('tkinter.Toplevel.wait_window'):  # Prevent wait_window from blocking
            dialog = TemplateManagerDialog(self.root, self.mock_repository)
            
            # Check that the repository was used
            self.mock_repository.list_templates.assert_called_once()
            
            # Check that the templates were loaded
            self.assertEqual(dialog.template_listbox.size(), 2)
            self.assertEqual(dialog.template_listbox.get(0), "Template 1")
            self.assertEqual(dialog.template_listbox.get(1), "Template 2")
    
    def test_on_template_selected(self):
        """Test template selection."""
        # Create dialog with mock repository
        with patch('tkinter.Toplevel.wait_window'):  # Prevent wait_window from blocking
            dialog = TemplateManagerDialog(self.root, self.mock_repository)
            
            # Select the first template
            dialog.template_listbox.selection_set(0)
            dialog._on_template_selected(None)
            
            # Check that the template was loaded
            self.mock_repository.get_template.assert_called_with("Template 1")
            
            # Check that the form was filled
            self.assertEqual(dialog.name_entry.get(), "Template 1")
            self.assertEqual(dialog.description_entry.get(), "Test Template 1")
            
            # Check that the actions were loaded
            self.assertEqual(dialog.actions_listbox.size(), 1)
            self.assertEqual(dialog.actions_listbox.get(0), "Navigate Action (Navigate)")
    
    def test_on_new(self):
        """Test new template button."""
        # Create dialog with mock repository
        with patch('tkinter.Toplevel.wait_window'):  # Prevent wait_window from blocking
            dialog = TemplateManagerDialog(self.root, self.mock_repository)
            
            # Select a template first
            dialog.template_listbox.selection_set(0)
            dialog._on_template_selected(None)
            
            # Check that the form is filled
            self.assertEqual(dialog.name_entry.get(), "Template 1")
            
            # Click new button
            dialog._on_new()
            
            # Check that the form was cleared
            self.assertEqual(dialog.name_entry.get(), "")
            self.assertEqual(dialog.description_entry.get(), "")
            self.assertEqual(dialog.actions_listbox.size(), 0)
            
            # Check that the current template was cleared
            self.assertIsNone(dialog.current_template)
            self.assertEqual(dialog.current_actions, [])
    
    def test_on_delete(self):
        """Test delete template button."""
        # Create dialog with mock repository
        with patch('tkinter.Toplevel.wait_window'):  # Prevent wait_window from blocking
            dialog = TemplateManagerDialog(self.root, self.mock_repository)
            
            # Select a template
            dialog.template_listbox.selection_set(0)
            
            # Mock messagebox.askyesno to return True
            with patch('tkinter.messagebox.askyesno', return_value=True):
                # Click delete button
                dialog._on_delete()
                
                # Check that the template was deleted
                self.mock_repository.delete_template.assert_called_with("Template 1")
                
                # Check that the templates were reloaded
                self.assertEqual(self.mock_repository.list_templates.call_count, 2)
    
    def test_on_save(self):
        """Test save template button."""
        # Create dialog with mock repository
        with patch('tkinter.Toplevel.wait_window'):  # Prevent wait_window from blocking
            dialog = TemplateManagerDialog(self.root, self.mock_repository)
            
            # Fill the form
            dialog.name_entry.insert(0, "New Template")
            dialog.description_entry.insert(0, "New Description")
            dialog.current_actions = [
                {"type": "Navigate", "name": "Navigate Action", "url": "https://example.com"}
            ]
            
            # Click save button
            dialog._on_save()
            
            # Check that the template was saved
            self.mock_repository.save_template.assert_called_once()
            
            # Check the saved template data
            saved_template = self.mock_repository.save_template.call_args[0][0]
            self.assertEqual(saved_template["name"], "New Template")
            self.assertEqual(saved_template["description"], "New Description")
            self.assertEqual(len(saved_template["actions"]), 1)
            self.assertEqual(saved_template["actions"][0]["type"], "Navigate")
    
    def test_on_save_validation(self):
        """Test save template validation."""
        # Create dialog with mock repository
        with patch('tkinter.Toplevel.wait_window'):  # Prevent wait_window from blocking
            dialog = TemplateManagerDialog(self.root, self.mock_repository)
            
            # Leave name empty
            dialog.name_entry.delete(0, tk.END)
            
            # Mock messagebox.showwarning
            with patch('tkinter.messagebox.showwarning') as mock_showwarning:
                # Click save button
                dialog._on_save()
                
                # Check that warning was shown
                mock_showwarning.assert_called_once()
                
                # Check that template was not saved
                self.mock_repository.save_template.assert_not_called()
    
    def test_on_add_action(self):
        """Test add action button."""
        # Create dialog with mock repository
        with patch('tkinter.Toplevel.wait_window'):  # Prevent wait_window from blocking
            dialog = TemplateManagerDialog(self.root, self.mock_repository)
            
            # Mock ActionEditorDialog
            mock_action_data = {"type": "Navigate", "name": "New Action", "url": "https://example.com"}
            
            with patch('src.ui.dialogs.action_editor_dialog.ActionEditorDialog') as MockActionEditor:
                # Set up mock to return action data
                mock_editor = MagicMock()
                mock_editor.show.return_value = mock_action_data
                MockActionEditor.return_value = mock_editor
                
                # Click add action button
                dialog._on_add_action()
                
                # Check that ActionEditorDialog was created
                MockActionEditor.assert_called_once_with(dialog.dialog)
                
                # Check that action was added
                self.assertEqual(len(dialog.current_actions), 1)
                self.assertEqual(dialog.current_actions[0], mock_action_data)
                
                # Check that actions list was updated
                self.assertEqual(dialog.actions_listbox.size(), 1)
                self.assertEqual(dialog.actions_listbox.get(0), "New Action (Navigate)")
    
    def test_on_edit_action(self):
        """Test edit action button."""
        # Create dialog with mock repository
        with patch('tkinter.Toplevel.wait_window'):  # Prevent wait_window from blocking
            dialog = TemplateManagerDialog(self.root, self.mock_repository)
            
            # Add an action to edit
            dialog.current_actions = [
                {"type": "Navigate", "name": "Original Action", "url": "https://example.com"}
            ]
            dialog._update_actions_list()
            
            # Select the action
            dialog.actions_listbox.selection_set(0)
            
            # Mock ActionEditorDialog
            mock_updated_action = {"type": "Navigate", "name": "Updated Action", "url": "https://example.com"}
            
            with patch('src.ui.dialogs.action_editor_dialog.ActionEditorDialog') as MockActionEditor:
                # Set up mock to return updated action data
                mock_editor = MagicMock()
                mock_editor.show.return_value = mock_updated_action
                MockActionEditor.return_value = mock_editor
                
                # Click edit action button
                dialog._on_edit_action()
                
                # Check that ActionEditorDialog was created with original action
                MockActionEditor.assert_called_once_with(dialog.dialog, dialog.current_actions[0])
                
                # Check that action was updated
                self.assertEqual(len(dialog.current_actions), 1)
                self.assertEqual(dialog.current_actions[0], mock_updated_action)
                
                # Check that actions list was updated
                self.assertEqual(dialog.actions_listbox.size(), 1)
                self.assertEqual(dialog.actions_listbox.get(0), "Updated Action (Navigate)")
    
    def test_on_remove_action(self):
        """Test remove action button."""
        # Create dialog with mock repository
        with patch('tkinter.Toplevel.wait_window'):  # Prevent wait_window from blocking
            dialog = TemplateManagerDialog(self.root, self.mock_repository)
            
            # Add actions to remove
            dialog.current_actions = [
                {"type": "Navigate", "name": "Action 1", "url": "https://example.com"},
                {"type": "Click", "name": "Action 2", "selector": "#test-button"}
            ]
            dialog._update_actions_list()
            
            # Select the first action
            dialog.actions_listbox.selection_set(0)
            
            # Mock messagebox.askyesno to return True
            with patch('tkinter.messagebox.askyesno', return_value=True):
                # Click remove action button
                dialog._on_remove_action()
                
                # Check that action was removed
                self.assertEqual(len(dialog.current_actions), 1)
                self.assertEqual(dialog.current_actions[0]["name"], "Action 2")
                
                # Check that actions list was updated
                self.assertEqual(dialog.actions_listbox.size(), 1)
                self.assertEqual(dialog.actions_listbox.get(0), "Action 2 (Click)")
    
    def test_on_move_action_up(self):
        """Test move action up button."""
        # Create dialog with mock repository
        with patch('tkinter.Toplevel.wait_window'):  # Prevent wait_window from blocking
            dialog = TemplateManagerDialog(self.root, self.mock_repository)
            
            # Add actions to move
            dialog.current_actions = [
                {"type": "Navigate", "name": "Action 1", "url": "https://example.com"},
                {"type": "Click", "name": "Action 2", "selector": "#test-button"}
            ]
            dialog._update_actions_list()
            
            # Select the second action
            dialog.actions_listbox.selection_set(1)
            
            # Click move up button
            dialog._on_move_action_up()
            
            # Check that actions were swapped
            self.assertEqual(dialog.current_actions[0]["name"], "Action 2")
            self.assertEqual(dialog.current_actions[1]["name"], "Action 1")
            
            # Check that actions list was updated
            self.assertEqual(dialog.actions_listbox.size(), 2)
            self.assertEqual(dialog.actions_listbox.get(0), "Action 2 (Click)")
            self.assertEqual(dialog.actions_listbox.get(1), "Action 1 (Navigate)")
    
    def test_on_move_action_down(self):
        """Test move action down button."""
        # Create dialog with mock repository
        with patch('tkinter.Toplevel.wait_window'):  # Prevent wait_window from blocking
            dialog = TemplateManagerDialog(self.root, self.mock_repository)
            
            # Add actions to move
            dialog.current_actions = [
                {"type": "Navigate", "name": "Action 1", "url": "https://example.com"},
                {"type": "Click", "name": "Action 2", "selector": "#test-button"}
            ]
            dialog._update_actions_list()
            
            # Select the first action
            dialog.actions_listbox.selection_set(0)
            
            # Click move down button
            dialog._on_move_action_down()
            
            # Check that actions were swapped
            self.assertEqual(dialog.current_actions[0]["name"], "Action 2")
            self.assertEqual(dialog.current_actions[1]["name"], "Action 1")
            
            # Check that actions list was updated
            self.assertEqual(dialog.actions_listbox.size(), 2)
            self.assertEqual(dialog.actions_listbox.get(0), "Action 2 (Click)")
            self.assertEqual(dialog.actions_listbox.get(1), "Action 1 (Navigate)")
    
    def test_repository_error_handling(self):
        """Test error handling for repository errors."""
        # Set up mock repository to raise RepositoryError
        self.mock_repository.list_templates.side_effect = RepositoryError("Test error")
        
        # Create dialog with mock repository
        with patch('tkinter.Toplevel.wait_window'):  # Prevent wait_window from blocking
            with patch('tkinter.messagebox.showerror') as mock_showerror:
                dialog = TemplateManagerDialog(self.root, self.mock_repository)
                
                # Check that error was shown
                mock_showerror.assert_called_once()

if __name__ == "__main__":
    unittest.main()
