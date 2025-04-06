"""Workflow editor view implementation for AutoQliq."""

import tkinter as tk
from tkinter import ttk, simpledialog
import logging
from typing import List, Dict, Any, Optional

# Core / Infrastructure
from src.core.interfaces import IAction
from src.core.exceptions import UIError

# UI elements
from src.ui.interfaces.presenter import IWorkflowEditorPresenter
from src.ui.interfaces.view import IWorkflowEditorView
from src.ui.views.base_view import BaseView
from src.ui.common.ui_factory import UIFactory

class WorkflowEditorView(BaseView, IWorkflowEditorView):
    """
    View component for the workflow editor. Displays workflows and actions,
    and forwards user interactions to the WorkflowEditorPresenter.
    """

    def __init__(self, root: tk.Widget, presenter: IWorkflowEditorPresenter):
        """
        Initialize the workflow editor view.

        Args:
            root: The parent widget (e.g., a frame in a notebook).
            presenter: The presenter handling the logic for this view.
        """
        super().__init__(root, presenter) # Initializes self.main_frame, self.presenter, self.logger
        self.presenter: IWorkflowEditorPresenter # Type hint for presenter

        # Widgets specific to this view
        self.workflow_list_widget: Optional[tk.Listbox] = None
        self.action_list_widget: Optional[tk.Listbox] = None
        # Add buttons if needed, or manage state via presenter calls triggered by main app menu/toolbar
        self.new_button: Optional[ttk.Button] = None
        self.save_button: Optional[ttk.Button] = None
        self.delete_button: Optional[ttk.Button] = None
        self.add_action_button: Optional[ttk.Button] = None
        self.edit_action_button: Optional[ttk.Button] = None
        self.delete_action_button: Optional[ttk.Button] = None

        try:
            self._create_widgets()
            self.logger.info("WorkflowEditorView initialized successfully.")
            # Initial population is handled by presenter.initialize_view() called externally or via set_view
        except Exception as e:
            error_msg = "Failed to create WorkflowEditorView widgets"
            self.logger.exception(error_msg) # Log traceback for creation errors
            # Display error directly as presenter might not be fully set up
            self.display_error("Initialization Error", f"{error_msg}: {e}")
            # Raise UIError to potentially stop application initialization if critical
            raise UIError(error_msg, component_name="WorkflowEditorView", cause=e) from e

    def _create_widgets(self) -> None:
        """Create the UI elements for the editor view."""
        self.logger.debug("Creating editor widgets.")

        # Configure grid weights for main_frame resizing
        self.main_frame.rowconfigure(0, weight=1) # Action list takes vertical space
        self.main_frame.rowconfigure(1, weight=0) # Action buttons fixed size
        self.main_frame.columnconfigure(0, weight=1, minsize=150) # Workflow list column
        self.main_frame.columnconfigure(1, weight=3, minsize=250) # Action list column

        # --- Workflow List Section ---
        wf_list_frame = UIFactory.create_label_frame(self.main_frame, text="Workflows")
        wf_list_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=(0, 5), pady=(0, 5))
        wf_list_frame.rowconfigure(0, weight=1)
        wf_list_frame.columnconfigure(0, weight=1)

        wf_scrolled_list = UIFactory.create_scrolled_listbox(wf_list_frame, height=15)
        self.workflow_list_widget = wf_scrolled_list["listbox"]
        wf_scrolled_list["frame"].grid(row=0, column=0, sticky=tk.NSEW)
        # Bind selection change to presenter method
        self.workflow_list_widget.bind("<<ListboxSelect>>", self._on_workflow_selected)

        # --- Workflow Buttons Section ---
        wf_button_frame = UIFactory.create_frame(self.main_frame, padding="5 0 0 0") # Padding top only
        wf_button_frame.grid(row=1, column=0, sticky=tk.EW, padx=(0, 5))

        self.new_button = UIFactory.create_button(wf_button_frame, text="New", command=self._on_new_workflow)
        self.new_button.pack(side=tk.LEFT, padx=2)

        self.save_button = UIFactory.create_button(wf_button_frame, text="Save", command=self._on_save_workflow, state=tk.DISABLED)
        self.save_button.pack(side=tk.LEFT, padx=2)

        self.delete_button = UIFactory.create_button(wf_button_frame, text="Delete", command=self._on_delete_workflow, state=tk.DISABLED)
        self.delete_button.pack(side=tk.LEFT, padx=2)

        # --- Action List Section ---
        action_list_frame = UIFactory.create_label_frame(self.main_frame, text="Actions")
        action_list_frame.grid(row=0, column=1, sticky=tk.NSEW, pady=(0, 5))
        action_list_frame.rowconfigure(0, weight=1)
        action_list_frame.columnconfigure(0, weight=1)

        action_scrolled_list = UIFactory.create_scrolled_listbox(action_list_frame, height=15)
        self.action_list_widget = action_scrolled_list["listbox"]
        action_scrolled_list["frame"].grid(row=0, column=0, sticky=tk.NSEW)
        # Bind selection change to enable/disable action buttons
        self.action_list_widget.bind("<<ListboxSelect>>", self._on_action_selected)
        # Add double-click binding to edit action
        self.action_list_widget.bind("<Double-1>", self._on_edit_action) # Double-Left-Click

        # --- Action Buttons Section ---
        action_button_frame = UIFactory.create_frame(self.main_frame, padding="5 0 0 0")
        action_button_frame.grid(row=1, column=1, sticky=tk.EW)

        self.add_action_button = UIFactory.create_button(action_button_frame, text="Add", command=self._on_add_action, state=tk.DISABLED)
        self.add_action_button.pack(side=tk.LEFT, padx=2)

        self.edit_action_button = UIFactory.create_button(action_button_frame, text="Edit", command=self._on_edit_action, state=tk.DISABLED)
        self.edit_action_button.pack(side=tk.LEFT, padx=2)

        self.delete_action_button = UIFactory.create_button(action_button_frame, text="Delete", command=self._on_delete_action, state=tk.DISABLED)
        self.delete_action_button.pack(side=tk.LEFT, padx=2)

        self.logger.debug("Editor widgets created.")

    # --- IWorkflowEditorView Implementation ---

    def set_workflow_list(self, workflow_names: List[str]) -> None:
        """Populate the workflow listbox."""
        if not self.workflow_list_widget: return
        self.logger.debug(f"Setting workflow list with {len(workflow_names)} items.")
        # Store current selection if possible
        selected_name = self.get_selected_workflow_name()
        # Clear and repopulate
        self.workflow_list_widget.delete(0, tk.END)
        for name in sorted(workflow_names): # Sort alphabetically
            self.workflow_list_widget.insert(tk.END, name)
        # Try to re-select the previously selected item
        if selected_name in workflow_names:
             try:
                  idx = workflow_names.index(selected_name)
                  self.workflow_list_widget.selection_set(idx)
                  self.workflow_list_widget.activate(idx)
                  self.workflow_list_widget.see(idx)
             except ValueError:
                   pass # Name not found after refresh
        # Update button states based on whether any workflow is selected
        self._update_workflow_button_states()


    def set_action_list(self, actions_display: List[str]) -> None:
        """Display the actions for the current workflow."""
        if not self.action_list_widget: return
        self.logger.debug(f"Setting action list with {len(actions_display)} items.")
        self.action_list_widget.delete(0, tk.END)
        for display_text in actions_display:
            self.action_list_widget.insert(tk.END, display_text)
        # Update action button states
        self._on_action_selected() # Update based on new list (likely nothing selected)

    def get_selected_workflow_name(self) -> Optional[str]:
        """Get the name of the currently selected workflow."""
        if not self.workflow_list_widget: return None
        selection_indices = self.workflow_list_widget.curselection()
        if not selection_indices:
            return None
        return self.workflow_list_widget.get(selection_indices[0])

    def get_selected_action_index(self) -> Optional[int]:
        """Get the index of the currently selected action."""
        if not self.action_list_widget: return None
        selection_indices = self.action_list_widget.curselection()
        if not selection_indices:
            return None
        return selection_indices[0]

    def show_action_editor(self, action_data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Show a dialog to add/edit an action."""
        # This is a simplified placeholder. A real implementation would use a dedicated dialog class.
        self.logger.debug(f"Showing action editor. Initial data: {action_data}")
        # Example using simpledialog; a custom Toplevel window is much better
        action_type = simpledialog.askstring("Action Type", "Enter type (Navigate, Click, Type, Wait, Screenshot):", parent=self.root)
        if not action_type: return None

        data = {"type": action_type, "name": action_type} # Default name to type
        if action_type == "Navigate":
            url = simpledialog.askstring("Navigate", "Enter URL:", initialvalue=action_data.get("url", "https://") if action_data else "https://", parent=self.root)
            if url is None: return None
            data["url"] = url
        elif action_type == "Click" or action_type == "Type":
            selector = simpledialog.askstring(action_type, "Enter CSS Selector:", initialvalue=action_data.get("selector", "") if action_data else "", parent=self.root)
            if selector is None: return None
            data["selector"] = selector
            if action_type == "Type":
                 text = simpledialog.askstring("Type", "Enter Text or 'credential:key.field':", initialvalue=action_data.get("text", "") if action_data else "", parent=self.root)
                 if text is None: return None
                 data["text"] = text
                 # Determine value_type based on text format - simplistic
                 data["value_type"] = "credential" if text.startswith("credential:") else "text"
        elif action_type == "Wait":
             duration = simpledialog.askfloat("Wait", "Enter duration (seconds):", initialvalue=action_data.get("duration_seconds", 1.0) if action_data else 1.0, minvalue=0.1, parent=self.root)
             if duration is None: return None
             data["duration_seconds"] = duration
        elif action_type == "Screenshot":
             filepath = simpledialog.askstring("Screenshot", "Enter file path:", initialvalue=action_data.get("file_path", "screenshot.png") if action_data else "screenshot.png", parent=self.root)
             if filepath is None: return None
             data["file_path"] = filepath
        else:
             self.display_error("Unknown Type", f"Action type '{action_type}' is not recognized.")
             return None

        custom_name = simpledialog.askstring("Action Name", "Enter a name for this action:", initialvalue=action_data.get("name", action_type) if action_data else action_type, parent=self.root)
        if custom_name: data["name"] = custom_name

        self.logger.debug(f"Action editor returning data: {data}")
        return data

    def prompt_for_workflow_name(self, title: str, prompt: str) -> Optional[str]:
        """Prompt user for a workflow name."""
        return simpledialog.askstring(title, prompt, parent=self.root)

    def clear(self) -> None:
        """Clear the workflow and action lists."""
        self.logger.debug("Clearing editor view.")
        if self.workflow_list_widget:
             self.workflow_list_widget.delete(0, tk.END)
        if self.action_list_widget:
             self.action_list_widget.delete(0, tk.END)
        self._update_workflow_button_states()
        self._update_action_button_states()

    # --- Internal Event Handlers ---

    def _on_workflow_selected(self, event: Optional[tk.Event] = None) -> None:
        """Callback when a workflow is selected."""
        selected_name = self.get_selected_workflow_name()
        self.logger.debug(f"Workflow selected: {selected_name}")
        self._update_workflow_button_states()
        if selected_name:
            # Delegate loading to presenter
            self.presenter.load_workflow(selected_name)
        else:
            # Clear action list if no workflow selected
            self.set_action_list([])


    def _on_action_selected(self, event: Optional[tk.Event] = None) -> None:
        """Callback when an action is selected."""
        self._update_action_button_states()

    def _on_new_workflow(self) -> None:
        """Handle 'New Workflow' button press."""
        self.logger.debug("New workflow button pressed.")
        name = self.prompt_for_workflow_name("New Workflow", "Enter name for new workflow:")
        if name:
            self.presenter.create_new_workflow(name)

    def _on_save_workflow(self) -> None:
        """Handle 'Save Workflow' button press."""
        self.logger.debug("Save workflow button pressed.")
        name = self.get_selected_workflow_name()
        if name:
             # Tell presenter to save the currently loaded state
             self.presenter.save_workflow(name) # Presenter holds the actions
        else:
             self.display_message("Save Error", "No workflow selected to save.")

    def _on_delete_workflow(self) -> None:
        """Handle 'Delete Workflow' button press."""
        self.logger.debug("Delete workflow button pressed.")
        name = self.get_selected_workflow_name()
        if name:
            if self.confirm_action("Confirm Delete", f"Are you sure you want to delete workflow '{name}'?"):
                self.presenter.delete_workflow(name)
        else:
            self.display_message("Delete Error", "No workflow selected to delete.")

    def _on_add_action(self) -> None:
        """Handle 'Add Action' button press."""
        self.logger.debug("Add action button pressed.")
        action_data = self.show_action_editor() # Show editor for new action
        if action_data:
            self.presenter.add_action(action_data)

    def _on_edit_action(self, event: Optional[tk.Event] = None) -> None: # Can be called by button or double-click
        """Handle 'Edit Action' button press or double-click."""
        self.logger.debug("Edit action triggered.")
        index = self.get_selected_action_index()
        if index is not None:
            current_action_data = self.presenter.get_action_data(index)
            if current_action_data:
                 new_action_data = self.show_action_editor(current_action_data) # Show editor with current data
                 if new_action_data:
                      self.presenter.update_action(index, new_action_data)
            else:
                 self.display_error("Edit Error", f"Could not retrieve data for action at index {index}.")
        else:
             self.display_message("Edit Action", "No action selected to edit.")

    def _on_delete_action(self) -> None:
        """Handle 'Delete Action' button press."""
        self.logger.debug("Delete action button pressed.")
        index = self.get_selected_action_index()
        if index is not None:
            if self.confirm_action("Confirm Delete", f"Are you sure you want to delete action {index+1}?"):
                self.presenter.delete_action(index)
        else:
             self.display_message("Delete Action", "No action selected to delete.")

    # --- Widget State Management ---

    def _update_workflow_button_states(self) -> None:
        """Enable/disable workflow buttons based on selection."""
        selected = self.get_selected_workflow_name() is not None
        if self.save_button: self.save_button.config(state=tk.NORMAL if selected else tk.DISABLED)
        if self.delete_button: self.delete_button.config(state=tk.NORMAL if selected else tk.DISABLED)
        # 'New' button is always enabled
        if self.new_button: self.new_button.config(state=tk.NORMAL)
        # Enable 'Add Action' only if a workflow is selected
        if self.add_action_button: self.add_action_button.config(state=tk.NORMAL if selected else tk.DISABLED)


    def _update_action_button_states(self) -> None:
        """Enable/disable action buttons based on selection."""
        selected = self.get_selected_action_index() is not None
        if self.edit_action_button: self.edit_action_button.config(state=tk.NORMAL if selected else tk.DISABLED)
        if self.delete_action_button: self.delete_action_button.config(state=tk.NORMAL if selected else tk.DISABLED)