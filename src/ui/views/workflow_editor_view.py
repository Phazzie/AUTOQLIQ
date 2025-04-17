"""Workflow editor view implementation for AutoQliq."""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import List, Dict, Any, Optional

# Core / Infrastructure
from src.core.exceptions import UIError

# UI elements
from src.ui.interfaces.presenter import IWorkflowEditorPresenter
from src.ui.interfaces.view import IWorkflowEditorView
from src.ui.views.base_view import BaseView
from src.ui.common.ui_factory import UIFactory
# Import the new dialog
from src.ui.dialogs.action_editor_dialog import ActionEditorDialog


class WorkflowEditorView(BaseView, IWorkflowEditorView):
    """
    View component for the workflow editor. Displays workflows and actions,
    and forwards user interactions to the WorkflowEditorPresenter.
    Uses ActionEditorDialog for adding/editing actions.
    """

    def __init__(self, root: tk.Widget, presenter: IWorkflowEditorPresenter):
        """
        Initialize the workflow editor view.

        Args:
            root: The parent widget (e.g., a frame in a notebook).
            presenter: The presenter handling the logic for this view.
        """
        super().__init__(root, presenter)
        self.presenter: IWorkflowEditorPresenter # Type hint

        # Widgets specific to this view
        self.workflow_list_widget: Optional[tk.Listbox] = None
        self.action_list_widget: Optional[tk.Listbox] = None
        self.new_button: Optional[ttk.Button] = None
        self.save_button: Optional[ttk.Button] = None
        self.delete_button: Optional[ttk.Button] = None
        self.add_action_button: Optional[ttk.Button] = None
        self.edit_action_button: Optional[ttk.Button] = None
        self.delete_action_button: Optional[ttk.Button] = None

        try:
            self._create_widgets()
            self.logger.info("WorkflowEditorView initialized successfully.")
        except Exception as e:
            error_msg = "Failed to create WorkflowEditorView widgets"
            self.logger.exception(error_msg)
            self.display_error("Initialization Error", f"{error_msg}: {e}")
            raise UIError(error_msg, component_name="WorkflowEditorView", cause=e) from e

    def _create_widgets(self) -> None:
        """Create the UI elements for the editor view within self.main_frame."""
        self.logger.debug("Creating editor widgets.")

        # Configure grid weights for self.main_frame resizing
        self.main_frame.rowconfigure(0, weight=1) # Lists take vertical space
        self.main_frame.rowconfigure(1, weight=0) # Buttons fixed size
        self.main_frame.columnconfigure(0, weight=1, minsize=200) # Workflow list column
        self.main_frame.columnconfigure(1, weight=3, minsize=350) # Action list column

        # --- Workflow List Section ---
        self._create_workflow_list_section()

        # --- Workflow Buttons Section ---
        self._create_workflow_buttons_section()

        # --- Action List Section ---
        self._create_action_list_section()

        # --- Action Buttons Section ---
        self._create_action_buttons_section()

        self.logger.debug("Editor widgets created.")

    def _create_workflow_list_section(self) -> None:
        """Create the workflow list section."""
        wf_list_frame = UIFactory.create_label_frame(self.main_frame, text="Workflows")
        wf_list_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=(0, 5), pady=(0, 5))
        wf_list_frame.rowconfigure(0, weight=1)
        wf_list_frame.columnconfigure(0, weight=1)

        wf_scrolled_list = UIFactory.create_scrolled_listbox(wf_list_frame, height=15, selectmode=tk.BROWSE)
        self.workflow_list_widget = wf_scrolled_list["listbox"]
        wf_scrolled_list["frame"].grid(row=0, column=0, sticky=tk.NSEW)
        self.workflow_list_widget.bind("<<ListboxSelect>>", self._on_workflow_selected)

    def _create_workflow_buttons_section(self) -> None:
        """Create the workflow buttons section."""
        wf_button_frame = UIFactory.create_frame(self.main_frame, padding="5 0 0 0")
        wf_button_frame.grid(row=1, column=0, sticky=tk.EW, padx=(0, 5))

        self.new_button = UIFactory.create_button(wf_button_frame, text="New", command=self._on_new_workflow)
        self.new_button.pack(side=tk.LEFT, padx=2)

        self.save_button = UIFactory.create_button(wf_button_frame, text="Save", command=self._on_save_workflow, state=tk.DISABLED)
        self.save_button.pack(side=tk.LEFT, padx=2)

        self.delete_button = UIFactory.create_button(wf_button_frame, text="Delete", command=self._on_delete_workflow, state=tk.DISABLED)
        self.delete_button.pack(side=tk.LEFT, padx=2)

    def _create_action_list_section(self) -> None:
        """Create the action list section."""
        action_list_frame = UIFactory.create_label_frame(self.main_frame, text="Actions")
        action_list_frame.grid(row=0, column=1, sticky=tk.NSEW, pady=(0, 5))
        action_list_frame.rowconfigure(0, weight=1)
        action_list_frame.columnconfigure(0, weight=1)

        action_scrolled_list = UIFactory.create_scrolled_listbox(action_list_frame, height=15, selectmode=tk.BROWSE)
        self.action_list_widget = action_scrolled_list["listbox"]
        action_scrolled_list["frame"].grid(row=0, column=0, sticky=tk.NSEW)
        self.action_list_widget.bind("<<ListboxSelect>>", self._on_action_selected)
        self.action_list_widget.bind("<Double-1>", self._on_edit_action)

    def _create_action_buttons_section(self) -> None:
        """Create the action buttons section."""
        action_button_frame = UIFactory.create_frame(self.main_frame, padding="5 0 0 0")
        action_button_frame.grid(row=1, column=1, sticky=tk.EW)

        self.add_action_button = UIFactory.create_button(action_button_frame, text="Add Action", command=self._on_add_action, state=tk.DISABLED)
        self.add_action_button.pack(side=tk.LEFT, padx=2)

        self.edit_action_button = UIFactory.create_button(action_button_frame, text="Edit Action", command=self._on_edit_action, state=tk.DISABLED)
        self.edit_action_button.pack(side=tk.LEFT, padx=2)

        self.delete_action_button = UIFactory.create_button(action_button_frame, text="Delete Action", command=self._on_delete_action, state=tk.DISABLED)
        self.delete_action_button.pack(side=tk.LEFT, padx=2)

    # --- IWorkflowEditorView Implementation ---

    def set_workflow_list(self, workflow_names: List[str]) -> None:
        """Populate the workflow listbox."""
        if not self.workflow_list_widget: return
        self.logger.debug(f"Setting workflow list with {len(workflow_names)} items.")
        selected_name = self.get_selected_workflow_name()
        self.workflow_list_widget.delete(0, tk.END)
        sorted_names = sorted(workflow_names)
        for name in sorted_names:
            self.workflow_list_widget.insert(tk.END, name)
        if selected_name in sorted_names:
             try:
                  list_items = self.workflow_list_widget.get(0, tk.END)
                  idx = list_items.index(selected_name)
                  self.workflow_list_widget.selection_set(idx)
                  self.workflow_list_widget.activate(idx)
                  self.workflow_list_widget.see(idx)
             except (ValueError, tk.TclError): pass
        self._update_workflow_button_states() # Update states after list changes


    def set_action_list(self, actions_display: List[str]) -> None:
        """Display the actions for the current workflow."""
        if not self.action_list_widget: return
        self.logger.debug(f"Setting action list with {len(actions_display)} items.")
        selected_index = self.get_selected_action_index()
        self.action_list_widget.delete(0, tk.END)
        for display_text in actions_display:
            self.action_list_widget.insert(tk.END, display_text)
        if selected_index is not None and selected_index < len(actions_display):
             try:
                  self.action_list_widget.selection_set(selected_index)
                  self.action_list_widget.activate(selected_index)
                  self.action_list_widget.see(selected_index)
             except tk.TclError: pass
        self._update_action_button_states() # Update states after list changes

    def get_selected_workflow_name(self) -> Optional[str]:
        """Get the name of the currently selected workflow."""
        if not self.workflow_list_widget: return None
        selection_indices = self.workflow_list_widget.curselection()
        return self.workflow_list_widget.get(selection_indices[0]) if selection_indices else None

    def get_selected_action_index(self) -> Optional[int]:
         """Get the index of the action currently selected in the list."""
         if not self.action_list_widget: return None
         selection_indices = self.action_list_widget.curselection()
         return selection_indices[0] if selection_indices else None

    def show_action_editor(self, action_data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
         """Show the dedicated ActionEditorDialog to add/edit an action."""
         self.logger.debug(f"Showing ActionEditorDialog. Initial data: {action_data}")
         try:
              # Use the new custom dialog, passing main_frame as parent
              dialog = ActionEditorDialog(self.main_frame, initial_data=action_data)
              result_data = dialog.show() # show() blocks and returns data or None
              self.logger.debug(f"ActionEditorDialog returned: {result_data}")
              return result_data
         except Exception as e:
              self.logger.error(f"Error showing ActionEditorDialog: {e}", exc_info=True)
              self.display_error("Dialog Error", f"Could not open action editor: {e}")
              return None

    def prompt_for_workflow_name(self, title: str, prompt: str) -> Optional[str]:
         """Prompt user for a workflow name."""
         return super().prompt_for_input(title, prompt)

    def clear(self) -> None:
        """Clear the workflow and action lists."""
        self.logger.debug("Clearing editor view.")
        if self.workflow_list_widget: self.workflow_list_widget.delete(0, tk.END)
        if self.action_list_widget: self.action_list_widget.delete(0, tk.END)
        self._update_workflow_button_states()
        self._update_action_button_states()
        super().clear() # Call base clear for status bar etc.

    # --- Internal Event Handlers ---

    def _on_workflow_selected(self, event: Optional[tk.Event] = None) -> None:
        """Callback when a workflow is selected."""
        selected_name = self.get_selected_workflow_name()
        self.logger.debug(f"Workflow selected: {selected_name}")
        self._update_workflow_button_states()
        self._update_action_button_states() # Update action buttons based on workflow selection
        if selected_name:
            self.presenter.load_workflow(selected_name)
        else:
            self.set_action_list([]) # Clear action list if nothing selected


    def _on_action_selected(self, event: Optional[tk.Event] = None) -> None:
        """Callback when an action is selected."""
        self._update_action_button_states()

    def _on_new_workflow(self) -> None:
        """Handle 'New Workflow' button press."""
        self.logger.debug("New workflow button pressed.")
        name = self.prompt_for_workflow_name("New Workflow", "Enter name for new workflow:")
        if name:
            self.presenter.create_new_workflow(name)
        else:
             self.logger.debug("New workflow cancelled by user.")

    def _on_save_workflow(self) -> None:
        """Handle 'Save Workflow' button press."""
        self.logger.debug("Save workflow button pressed.")
        name = self.get_selected_workflow_name()
        if name:
             # Tell presenter to save the currently loaded state
             self.presenter.save_workflow(name) # Presenter holds the actions
        else:
             self.logger.warning("Save button pressed but no workflow selected.")
             self.set_status("Please select a workflow to save.")


    def _on_delete_workflow(self) -> None:
        """Handle 'Delete Workflow' button press."""
        self.logger.debug("Delete workflow button pressed.")
        name = self.get_selected_workflow_name()
        if name:
            if self.confirm_action("Confirm Delete", f"Are you sure you want to delete workflow '{name}'? This cannot be undone."):
                self.presenter.delete_workflow(name) # Delegate to presenter
        else:
             self.logger.warning("Delete button pressed but no workflow selected.")
             self.set_status("Please select a workflow to delete.")

    def _on_add_action(self) -> None:
        """Handle 'Add Action' button press."""
        self.logger.debug("Add action button pressed.")
        if self.get_selected_workflow_name() is None:
             self.display_message("Add Action", "Please select or create a workflow first.")
             return
        # Use the new dialog
        action_data = self.show_action_editor() # No initial data for add
        if action_data:
            # Delegate adding to presenter (updates internal state)
            self.presenter.add_action(action_data)
        else:
             self.logger.debug("Add action cancelled by user.")

    def _on_edit_action(self, event: Optional[tk.Event] = None) -> None: # Can be called by button or double-click
        """Handle 'Edit Action' button press or double-click."""
        self.logger.debug("Edit action triggered.")
        index = self.get_selected_action_index()
        if index is not None:
            # Get current data from presenter's internal state
            current_action_data = self.presenter.get_action_data(index)
            if current_action_data:
                 # Use the new dialog with initial data
                 new_action_data = self.show_action_editor(current_action_data)
                 if new_action_data:
                      # Delegate update to presenter (updates internal state)
                      self.presenter.update_action(index, new_action_data)
                 else:
                      self.logger.debug("Edit action cancelled by user.")
            else:
                 # Error handled by get_action_data, but show msg just in case
                 self.display_error("Edit Error", f"Could not retrieve data for action at index {index}.")
        else:
             self.logger.warning("Edit action triggered but no action selected.")
             self.set_status("Please select an action to edit.")


    def _on_delete_action(self) -> None:
        """Handle 'Delete Action' button press."""
        self.logger.debug("Delete action button pressed.")
        index = self.get_selected_action_index()
        if index is not None:
            action_name_display = self.action_list_widget.get(index) if self.action_list_widget else f"Action {index+1}"
            if self.confirm_action("Confirm Delete", f"Are you sure you want to delete '{action_name_display}'?"):
                # Delegate deletion to presenter (updates internal state)
                self.presenter.delete_action(index)
        else:
             self.logger.warning("Delete action button pressed but no action selected.")
             self.set_status("Please select an action to delete.")

    # --- Widget State Management ---

    def _update_workflow_button_states(self) -> None:
        """Enable/disable workflow buttons based on selection."""
        selected = self.get_selected_workflow_name() is not None
        save_state = tk.NORMAL if selected else tk.DISABLED
        delete_state = tk.NORMAL if selected else tk.DISABLED

        if self.save_button: self.save_button.config(state=save_state)
        if self.delete_button: self.delete_button.config(state=delete_state)
        if self.new_button: self.new_button.config(state=tk.NORMAL)


    def _update_action_button_states(self, workflow_selected: Optional[bool] = None) -> None:
        """Enable/disable action buttons based on selections."""
        if workflow_selected is None:
             workflow_selected = self.get_selected_workflow_name() is not None
        action_selected = self.get_selected_action_index() is not None

        add_state = tk.NORMAL if workflow_selected else tk.DISABLED
        edit_state = tk.NORMAL if action_selected else tk.DISABLED
        delete_state = tk.NORMAL if action_selected else tk.DISABLED

        if self.add_action_button: self.add_action_button.config(state=add_state)
        if self.edit_action_button: self.edit_action_button.config(state=edit_state)
        if self.delete_action_button: self.delete_action_button.config(state=delete_state)
