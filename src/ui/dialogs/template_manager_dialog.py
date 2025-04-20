"""Template manager dialog implementation for AutoQliq.

This module provides the TemplateManagerDialog class for managing action templates.
"""

import logging
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, Optional, Callable, List

from src.core.template.repository import TemplateRepository
from src.core.exceptions import RepositoryError
from src.ui.common.ui_factory import UIFactory

logger = logging.getLogger(__name__)

class TemplateManagerDialog:
    """
    Dialog for managing action templates.
    
    Provides UI for creating, editing, and deleting templates.
    """
    
    def __init__(self, parent: tk.Widget, template_repository: Optional[TemplateRepository] = None):
        """
        Initialize the template manager dialog.
        
        Args:
            parent: The parent widget.
            template_repository: Optional template repository. If None, a new one will be created.
        """
        self.parent = parent
        self.template_repository = template_repository or TemplateRepository()
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Template Manager")
        self.dialog.geometry("700x500")
        self.dialog.minsize(600, 400)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog on the parent
        self._center_dialog()
        
        # Create UI elements
        self._create_ui()
        
        # Load templates
        self._load_templates()
        
        logger.debug("TemplateManagerDialog initialized")
    
    def _center_dialog(self) -> None:
        """Center the dialog on the parent window."""
        self.dialog.update_idletasks()
        
        # Get parent and dialog dimensions
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        
        dialog_width = self.dialog.winfo_width()
        dialog_height = self.dialog.winfo_height()
        
        # Calculate position
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        # Set position
        self.dialog.geometry(f"+{x}+{y}")
    
    def _create_ui(self) -> None:
        """Create the dialog UI elements."""
        # Main frame with padding
        self.main_frame = ttk.Frame(self.dialog, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Split into left (list) and right (details) panes
        self.paned_window = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Left pane - Template list
        self.left_frame = ttk.Frame(self.paned_window, padding="5")
        self.paned_window.add(self.left_frame, weight=1)
        
        # Template list with scrollbar
        self.list_frame = ttk.Frame(self.left_frame)
        self.list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.list_label = ttk.Label(self.list_frame, text="Templates:")
        self.list_label.pack(anchor=tk.W, padx=5, pady=5)
        
        self.template_listbox = tk.Listbox(self.list_frame, exportselection=0)
        self.template_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.template_listbox.bind('<<ListboxSelect>>', self._on_template_selected)
        
        self.list_scrollbar = ttk.Scrollbar(self.list_frame, orient=tk.VERTICAL, command=self.template_listbox.yview)
        self.list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.template_listbox.config(yscrollcommand=self.list_scrollbar.set)
        
        # Template list buttons
        self.list_button_frame = ttk.Frame(self.left_frame)
        self.list_button_frame.pack(fill=tk.X, pady=5)
        
        self.new_button = ttk.Button(self.list_button_frame, text="New", command=self._on_new)
        self.new_button.pack(side=tk.LEFT, padx=5)
        
        self.delete_button = ttk.Button(self.list_button_frame, text="Delete", command=self._on_delete)
        self.delete_button.pack(side=tk.LEFT, padx=5)
        
        # Right pane - Template details
        self.right_frame = ttk.Frame(self.paned_window, padding="5")
        self.paned_window.add(self.right_frame, weight=2)
        
        # Template details form
        self.details_frame = ttk.LabelFrame(self.right_frame, text="Template Details")
        self.details_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Name field
        self.name_frame = ttk.Frame(self.details_frame)
        self.name_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.name_label = ttk.Label(self.name_frame, text="Name:", width=15, anchor=tk.W)
        self.name_label.pack(side=tk.LEFT, padx=5)
        
        self.name_entry = ttk.Entry(self.name_frame, width=30)
        self.name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Description field
        self.description_frame = ttk.Frame(self.details_frame)
        self.description_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.description_label = ttk.Label(self.description_frame, text="Description:", width=15, anchor=tk.W)
        self.description_label.pack(side=tk.LEFT, padx=5)
        
        self.description_entry = ttk.Entry(self.description_frame, width=30)
        self.description_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Actions frame
        self.actions_frame = ttk.LabelFrame(self.details_frame, text="Actions")
        self.actions_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Actions list with scrollbar
        self.actions_list_frame = ttk.Frame(self.actions_frame)
        self.actions_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.actions_listbox = tk.Listbox(self.actions_list_frame, exportselection=0)
        self.actions_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.actions_scrollbar = ttk.Scrollbar(self.actions_list_frame, orient=tk.VERTICAL, command=self.actions_listbox.yview)
        self.actions_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.actions_listbox.config(yscrollcommand=self.actions_scrollbar.set)
        
        # Actions buttons
        self.actions_button_frame = ttk.Frame(self.actions_frame)
        self.actions_button_frame.pack(fill=tk.X, pady=5)
        
        self.add_action_button = ttk.Button(self.actions_button_frame, text="Add", command=self._on_add_action)
        self.add_action_button.pack(side=tk.LEFT, padx=5)
        
        self.edit_action_button = ttk.Button(self.actions_button_frame, text="Edit", command=self._on_edit_action)
        self.edit_action_button.pack(side=tk.LEFT, padx=5)
        
        self.remove_action_button = ttk.Button(self.actions_button_frame, text="Remove", command=self._on_remove_action)
        self.remove_action_button.pack(side=tk.LEFT, padx=5)
        
        self.move_up_button = ttk.Button(self.actions_button_frame, text="Up", command=self._on_move_action_up)
        self.move_up_button.pack(side=tk.LEFT, padx=5)
        
        self.move_down_button = ttk.Button(self.actions_button_frame, text="Down", command=self._on_move_action_down)
        self.move_down_button.pack(side=tk.LEFT, padx=5)
        
        # Save button
        self.save_button = ttk.Button(self.details_frame, text="Save", command=self._on_save)
        self.save_button.pack(anchor=tk.E, padx=10, pady=10)
        
        # Close button at the bottom
        self.close_button = ttk.Button(self.dialog, text="Close", command=self._on_close)
        self.close_button.pack(side=tk.RIGHT, padx=10, pady=10)
        
        # Disable details initially
        self._set_details_enabled(False)
        
        # Store current template data
        self.current_template = None
        self.current_actions = []
    
    def _load_templates(self) -> None:
        """Load templates from the repository."""
        try:
            # Clear the listbox
            self.template_listbox.delete(0, tk.END)
            
            # Get templates from repository
            templates = self.template_repository.list_templates()
            
            # Add to listbox
            for template in templates:
                self.template_listbox.insert(tk.END, template["name"])
            
            # Update status
            if templates:
                self.dialog.title(f"Template Manager ({len(templates)} templates)")
            else:
                self.dialog.title("Template Manager (No templates)")
        except RepositoryError as e:
            logger.error(f"Error loading templates: {e}")
            messagebox.showerror("Error", f"Failed to load templates: {e}", parent=self.dialog)
    
    def _on_template_selected(self, event) -> None:
        """
        Handle template selection.
        
        Args:
            event: The event that triggered this callback.
        """
        selection = self.template_listbox.curselection()
        if not selection:
            self._set_details_enabled(False)
            return
        
        # Get selected template name
        template_name = self.template_listbox.get(selection[0])
        
        try:
            # Get template from repository
            template = self.template_repository.get_template(template_name)
            if not template:
                self._set_details_enabled(False)
                return
            
            # Store current template
            self.current_template = template
            self.current_actions = template.get("actions", [])
            
            # Enable details form
            self._set_details_enabled(True)
            
            # Fill form with template data
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, template.get("name", ""))
            
            self.description_entry.delete(0, tk.END)
            self.description_entry.insert(0, template.get("description", ""))
            
            # Update actions list
            self._update_actions_list()
        except RepositoryError as e:
            logger.error(f"Error getting template: {e}")
            messagebox.showerror("Error", f"Failed to get template: {e}", parent=self.dialog)
    
    def _update_actions_list(self) -> None:
        """Update the actions list with current actions."""
        # Clear the listbox
        self.actions_listbox.delete(0, tk.END)
        
        # Add actions to listbox
        for action in self.current_actions:
            action_name = action.get("name", "Unnamed Action")
            action_type = action.get("type", "Unknown")
            self.actions_listbox.insert(tk.END, f"{action_name} ({action_type})")
    
    def _on_new(self) -> None:
        """Handle new template button click."""
        # Clear and enable the form
        self._set_details_enabled(True)
        self.name_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)
        self.actions_listbox.delete(0, tk.END)
        
        # Clear current template
        self.current_template = None
        self.current_actions = []
        
        # Clear selection
        self.template_listbox.selection_clear(0, tk.END)
        
        # Focus name field
        self.name_entry.focus_set()
    
    def _on_delete(self) -> None:
        """Handle delete template button click."""
        selection = self.template_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "No template selected.", parent=self.dialog)
            return
        
        # Get selected template name
        template_name = self.template_listbox.get(selection[0])
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", 
                                 f"Are you sure you want to delete template '{template_name}'?", 
                                 parent=self.dialog):
            return
        
        try:
            # Delete template
            self.template_repository.delete_template(template_name)
            
            # Reload templates
            self._load_templates()
            
            # Clear and disable form
            self._set_details_enabled(False)
            self.current_template = None
            self.current_actions = []
        except RepositoryError as e:
            logger.error(f"Error deleting template: {e}")
            messagebox.showerror("Error", f"Failed to delete template: {e}", parent=self.dialog)
    
    def _on_save(self) -> None:
        """Handle save template button click."""
        # Get form data
        name = self.name_entry.get().strip()
        description = self.description_entry.get().strip()
        
        # Validate
        if not name:
            messagebox.showwarning("Warning", "Name is required.", parent=self.dialog)
            self.name_entry.focus_set()
            return
        
        # Create template data
        template_data = {
            "name": name,
            "description": description,
            "actions": self.current_actions
        }
        
        try:
            # Save template
            self.template_repository.save_template(template_data)
            
            # Reload templates
            self._load_templates()
            
            # Select the saved template
            for i in range(self.template_listbox.size()):
                if self.template_listbox.get(i) == name:
                    self.template_listbox.selection_set(i)
                    self.template_listbox.see(i)
                    self._on_template_selected(None)
                    break
            
            messagebox.showinfo("Success", f"Template '{name}' saved.", parent=self.dialog)
        except RepositoryError as e:
            logger.error(f"Error saving template: {e}")
            messagebox.showerror("Error", f"Failed to save template: {e}", parent=self.dialog)
    
    def _on_close(self) -> None:
        """Handle close button click."""
        self.dialog.destroy()
    
    def _set_details_enabled(self, enabled: bool) -> None:
        """
        Enable or disable the details form.
        
        Args:
            enabled: Whether to enable the form.
        """
        state = tk.NORMAL if enabled else tk.DISABLED
        
        self.name_entry.config(state=state)
        self.description_entry.config(state=state)
        self.add_action_button.config(state=state)
        self.edit_action_button.config(state=state)
        self.remove_action_button.config(state=state)
        self.move_up_button.config(state=state)
        self.move_down_button.config(state=state)
        self.save_button.config(state=state)
    
    def _on_add_action(self) -> None:
        """Handle add action button click."""
        # Import here to avoid circular imports
        from src.ui.dialogs.action_editor_dialog import ActionEditorDialog
        
        # Create action editor dialog
        action_editor = ActionEditorDialog(self.dialog)
        
        # Show dialog and get result
        action_data = action_editor.show()
        
        # If action was created, add it to the list
        if action_data:
            self.current_actions.append(action_data)
            self._update_actions_list()
    
    def _on_edit_action(self) -> None:
        """Handle edit action button click."""
        selection = self.actions_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "No action selected.", parent=self.dialog)
            return
        
        # Get selected action index
        action_index = selection[0]
        
        # Get action data
        action_data = self.current_actions[action_index]
        
        # Import here to avoid circular imports
        from src.ui.dialogs.action_editor_dialog import ActionEditorDialog
        
        # Create action editor dialog
        action_editor = ActionEditorDialog(self.dialog, action_data)
        
        # Show dialog and get result
        updated_action_data = action_editor.show()
        
        # If action was updated, update the list
        if updated_action_data:
            self.current_actions[action_index] = updated_action_data
            self._update_actions_list()
            
            # Reselect the action
            self.actions_listbox.selection_set(action_index)
    
    def _on_remove_action(self) -> None:
        """Handle remove action button click."""
        selection = self.actions_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "No action selected.", parent=self.dialog)
            return
        
        # Get selected action index
        action_index = selection[0]
        
        # Get action name
        action_name = self.current_actions[action_index].get("name", "Unnamed Action")
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", 
                                 f"Are you sure you want to remove action '{action_name}'?", 
                                 parent=self.dialog):
            return
        
        # Remove action
        del self.current_actions[action_index]
        
        # Update list
        self._update_actions_list()
    
    def _on_move_action_up(self) -> None:
        """Handle move action up button click."""
        selection = self.actions_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "No action selected.", parent=self.dialog)
            return
        
        # Get selected action index
        action_index = selection[0]
        
        # Check if already at the top
        if action_index == 0:
            return
        
        # Swap with previous action
        self.current_actions[action_index], self.current_actions[action_index - 1] = \
            self.current_actions[action_index - 1], self.current_actions[action_index]
        
        # Update list
        self._update_actions_list()
        
        # Select the moved action
        self.actions_listbox.selection_set(action_index - 1)
    
    def _on_move_action_down(self) -> None:
        """Handle move action down button click."""
        selection = self.actions_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "No action selected.", parent=self.dialog)
            return
        
        # Get selected action index
        action_index = selection[0]
        
        # Check if already at the bottom
        if action_index == len(self.current_actions) - 1:
            return
        
        # Swap with next action
        self.current_actions[action_index], self.current_actions[action_index + 1] = \
            self.current_actions[action_index + 1], self.current_actions[action_index]
        
        # Update list
        self._update_actions_list()
        
        # Select the moved action
        self.actions_listbox.selection_set(action_index + 1)
    
    def show(self) -> None:
        """Show the dialog and wait for it to be closed."""
        self.dialog.wait_window()
