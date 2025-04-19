"""Enhanced workflow editor view implementation with visual action list."""

import tkinter as tk
from tkinter import ttk
import logging
from typing import List, Dict, Any, Optional, Callable

# Core / Infrastructure
from src.core.exceptions import UIError

# UI elements
from src.ui.interfaces.presenter import IWorkflowEditorPresenter
from src.ui.interfaces.view import IWorkflowEditorView
from src.ui.views.base_view import BaseView
from src.ui.common.ui_factory import UIFactory
from src.ui.dialogs.action_editor_dialog import ActionEditorDialog
from src.ui.components.workflow_action_list import WorkflowActionList


class WorkflowEditorViewEnhanced(BaseView, IWorkflowEditorView):
    """
    Enhanced view component for the workflow editor with visual action list.
    Displays workflows and actions with a more intuitive interface,
    and forwards user interactions to the WorkflowEditorPresenter.
    """

    def __init__(self, root: tk.Widget, presenter: IWorkflowEditorPresenter):
        """
        Initialize the enhanced workflow editor view.

        Args:
            root: The parent widget (e.g., a frame in a notebook).
            presenter: The presenter handling the logic for this view.
        """
        super().__init__(root, presenter)
        self.presenter: IWorkflowEditorPresenter  # Type hint

        # Widgets specific to this view
        self.workflow_list_widget: Optional[tk.Listbox] = None
        self.action_list: Optional[WorkflowActionList] = None

        # Buttons
        self.new_button: Optional[ttk.Button] = None
        self.save_button: Optional[ttk.Button] = None
        self.delete_button: Optional[ttk.Button] = None

        try:
            self._create_widgets()
            self.logger.info("Enhanced WorkflowEditorView initialized successfully.")
        except Exception as e:
            error_msg = "Failed to create Enhanced WorkflowEditorView widgets"
            self.logger.exception(error_msg)
            self.display_error("Initialization Error", f"{error_msg}: {e}")
            raise UIError(error_msg, component_name="WorkflowEditorViewEnhanced", cause=e) from e

    def _create_widgets(self) -> None:
        """Create the UI elements for the enhanced editor view."""
        self.logger.debug("Creating enhanced editor widgets.")

        # Configure grid weights for main_frame resizing
        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=0)
        self.main_frame.columnconfigure(0, weight=1, minsize=150)
        self.main_frame.columnconfigure(1, weight=3, minsize=350)

        # --- Workflow List Section ---
        wf_list_frame = UIFactory.create_label_frame(self.main_frame, text="Workflows")
        wf_list_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=(0, 5), pady=(0, 5))
        wf_list_frame.rowconfigure(0, weight=1)
        wf_list_frame.columnconfigure(0, weight=1)

        # Workflow listbox with scrollbar
        wf_scrolled_list = UIFactory.create_scrolled_listbox(wf_list_frame, height=15)
        self.workflow_list_widget = wf_scrolled_list["listbox"]
        wf_scrolled_list["frame"].grid(row=0, column=0, sticky=tk.NSEW)

        # Bind selection event
        self.workflow_list_widget.bind('<<ListboxSelect>>', self._on_workflow_selected)

        # Workflow buttons
        wf_button_frame = UIFactory.create_frame(wf_list_frame, padding="5 5 5 0")
        wf_button_frame.grid(row=1, column=0, sticky=tk.EW)

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

        # Create the visual action list
        self.action_list = WorkflowActionList(
            action_list_frame,
            on_insert=self._on_insert_action,
            on_edit=self._on_edit_action,
            on_delete=self._on_delete_action,
            on_move=self._on_move_action
        )
        self.action_list.pack(fill=tk.BOTH, expand=True)

        # Status bar at the bottom
        status_frame = UIFactory.create_frame(self.main_frame, padding="0 5 0 0")
        status_frame.grid(row=1, column=0, columnspan=2, sticky=tk.EW)

        self.status_var = tk.StringVar(value="Ready")
        status_label = UIFactory.create_label(status_frame, textvariable=self.status_var, anchor=tk.W)
        status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.logger.debug("Enhanced editor widgets created.")

    # --- IWorkflowEditorView Implementation ---

    def set_workflow_list(self, workflow_names: List[str]) -> None:
        """Display the list of available workflows."""
        if not self.workflow_list_widget:
            return

        self.logger.debug(f"Setting workflow list with {len(workflow_names)} items.")

        # Remember the currently selected workflow
        current_selection = self.get_selected_workflow_name()

        # Update the list
        self.workflow_list_widget.delete(0, tk.END)
        for name in workflow_names:
            self.workflow_list_widget.insert(tk.END, name)

        # Restore selection if possible
        if current_selection and current_selection in workflow_names:
            index = workflow_names.index(current_selection)
            self.workflow_list_widget.selection_set(index)
            self.workflow_list_widget.see(index)

        # Update button states
        self._update_workflow_button_states()

    def set_action_list(self, actions_display: List[str]) -> None:
        """
        Display the actions for the current workflow.

        This method is called by the presenter with string representations of actions.
        We need to convert these to action data dictionaries for our visual list.
        """
        # This is a compatibility method for the existing presenter
        # In a real implementation, we would update the presenter to pass action data directly
        self.logger.debug(f"Setting action list with {len(actions_display)} items.")

        # Convert string representations to dummy action data
        # This is a temporary solution until the presenter is updated
        action_data_list = []
        for i, display_text in enumerate(actions_display):
            # Parse the display text to extract action type and parameters
            action_data = self._parse_action_display(display_text)
            action_data_list.append(action_data)

        # Update the visual action list
        self.action_list.update_actions(action_data_list)

    def set_action_data_list(self, actions_data: List[Dict[str, Any]]) -> None:
        """
        Display the actions for the current workflow using action data dictionaries.

        This method is called by the enhanced presenter with action data dictionaries.
        """
        self.logger.debug(f"Setting action data list with {len(actions_data)} items.")

        # Update the visual action list with the action data
        self.action_list.update_actions(actions_data)

    def _parse_action_display(self, display_text: str) -> Dict[str, Any]:
        """
        Parse a display text string into an action data dictionary.

        This is a temporary solution until the presenter is updated to pass action data directly.

        Args:
            display_text: The display text string

        Returns:
            An action data dictionary
        """
        # Default action data
        action_data = {"type": "Unknown", "name": "Unknown Action"}

        # Try to parse the display text
        try:
            # Common format: "ActionType: parameter"
            if ": " in display_text:
                action_type, params = display_text.split(": ", 1)
                action_data["type"] = action_type
                action_data["name"] = action_type

                # Add parameters based on action type
                if action_type == "Navigate":
                    action_data["url"] = params
                elif action_type == "Click":
                    action_data["selector"] = params
                elif action_type == "Type":
                    if " = " in params:
                        selector, value = params.split(" = ", 1)
                        action_data["selector"] = selector
                        action_data["value_key"] = value
                elif action_type == "Wait":
                    if params.endswith(" seconds"):
                        duration = params.replace(" seconds", "")
                        action_data["duration_seconds"] = duration
                elif action_type == "Screenshot":
                    action_data["file_path"] = params
            else:
                # Just use the display text as the action type
                action_data["type"] = display_text
                action_data["name"] = display_text
        except Exception as e:
            self.logger.warning(f"Error parsing action display text: {e}")

        return action_data

    def set_status(self, message: str) -> None:
        """Display a status message."""
        if hasattr(self, 'status_var'):
            self.status_var.set(message)
            self.logger.debug(f"Status set: {message}")

    def get_selected_workflow_name(self) -> Optional[str]:
        """Get the name of the currently selected workflow."""
        if not self.workflow_list_widget:
            return None

        selection = self.workflow_list_widget.curselection()
        if not selection:
            return None

        return self.workflow_list_widget.get(selection[0])

    def get_selected_action_index(self) -> Optional[int]:
        """Get the index of the currently selected action."""
        if not self.action_list:
            return None

        return self.action_list.get_selected_index()

    def prompt_for_workflow_name(self, title: str, prompt: str) -> Optional[str]:
        """Prompt the user for a workflow name."""
        return UIFactory.show_input_dialog(title, prompt, parent=self.root)

    def confirm_action(self, title: str, message: str) -> bool:
        """Ask the user to confirm an action."""
        return UIFactory.show_confirmation_dialog(title, message, parent=self.root)

    def display_message(self, title: str, message: str) -> None:
        """Display an informational message to the user."""
        UIFactory.show_message_dialog(title, message, parent=self.root)

    def display_error(self, title: str, message: str) -> None:
        """Display an error message to the user."""
        UIFactory.show_error_dialog(title, message, parent=self.root)

    def show_action_editor(self, action_data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Show the dedicated ActionEditorDialog to add/edit an action."""
        self.logger.debug(f"Showing ActionEditorDialog. Initial data: {action_data}")
        try:
            # Use the custom dialog, passing main_frame as parent
            dialog = ActionEditorDialog(self.main_frame, initial_data=action_data)
            result_data = dialog.show()  # show() blocks and returns data or None
            self.logger.debug(f"ActionEditorDialog returned: {result_data}")
            return result_data
        except Exception as e:
            self.logger.error(f"Error showing ActionEditorDialog: {e}", exc_info=True)
            self.display_error("Dialog Error", f"Could not open action editor: {e}")
            return None

    def show_action_selection_dialog(self) -> Optional[str]:
        """Show the action selection dialog. Returns the selected action type or None if cancelled."""
        self.logger.debug("Showing ActionSelectionDialog")
        try:
            # Import here to avoid circular imports
            from src.ui.dialogs.action_selection_dialog import ActionSelectionDialog

            # Create and show the dialog
            dialog = ActionSelectionDialog(self.main_frame)
            action_type = dialog.show()  # show() blocks and returns action type or None

            self.logger.debug(f"ActionSelectionDialog returned: {action_type}")
            return action_type
        except Exception as e:
            self.logger.error(f"Error showing ActionSelectionDialog: {e}", exc_info=True)
            self.display_error("Dialog Error", f"Could not open action selection dialog: {e}")
            return None

    # --- Internal Event Handlers ---

    def _on_workflow_selected(self, event: Optional[tk.Event] = None) -> None:
        """Callback when a workflow is selected."""
        selected_name = self.get_selected_workflow_name()
        self.logger.debug(f"Workflow selected: {selected_name}")
        self._update_workflow_button_states()
        if selected_name:
            try:
                self.presenter.load_workflow(selected_name)
                # Update the status bar
                self.set_status(f"Workflow '{selected_name}' loaded.")
            except Exception as e:
                self.logger.error(f"Error loading workflow: {e}", exc_info=True)
                self.display_error("Load Error", f"Could not load workflow '{selected_name}': {e}")
        else:
            # Clear action list if no workflow selected
            self.set_action_list([])

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
            self.presenter.save_workflow(name)
        else:
            self.logger.warning("Save button pressed but no workflow selected.")
            self.set_status("Please select a workflow to save.")

    def _on_delete_workflow(self) -> None:
        """Handle 'Delete Workflow' button press."""
        self.logger.debug("Delete workflow button pressed.")
        name = self.get_selected_workflow_name()
        if name:
            if self.confirm_action("Confirm Delete", f"Are you sure you want to delete workflow '{name}'?"):
                self.presenter.delete_workflow(name)
        else:
            self.display_message("Delete Error", "No workflow selected to delete.")

    def _on_insert_action(self, position: int) -> None:
        """
        Handle inserting an action at the specified position.

        Args:
            position: The position to insert the action at
        """
        self.logger.debug(f"Insert action at position {position} requested.")
        if self.get_selected_workflow_name() is None:
            self.display_message("Add Action", "Please select or create a workflow first.")
            return

        # First, show the action selection dialog to choose the action type
        action_type = self.show_action_selection_dialog()
        if not action_type:
            self.logger.debug("Action selection cancelled by user.")
            return

        # Create initial action data with the selected type
        initial_data = {"type": action_type}

        # Show the action editor dialog with the initial data
        action_data = self.show_action_editor(initial_data)
        if action_data:
            # Use the presenter's insert_action method to insert at the specified position
            self.presenter.insert_action(position, action_data)
            self.logger.debug(f"Action inserted at position {position}.")
            self.set_status(f"Action inserted at position {position+1}.")
        else:
            self.logger.debug("Add action cancelled by user.")

    def _on_edit_action(self, index: int) -> None:
        """
        Handle editing an action.

        Args:
            index: The index of the action to edit
        """
        self.logger.debug(f"Edit action at index {index} requested.")

        # Get current data from presenter's internal state
        current_action_data = self.presenter.get_action_data(index)
        if current_action_data:
            # Use the dialog with initial data
            new_action_data = self.show_action_editor(current_action_data)
            if new_action_data:
                # Delegate update to presenter
                self.presenter.update_action(index, new_action_data)
            else:
                self.logger.debug("Edit action cancelled by user.")
        else:
            # Error handled by get_action_data, but show message just in case
            self.display_error("Edit Error", f"Could not retrieve data for action at index {index}.")

    def _on_delete_action(self, index: int) -> None:
        """
        Handle deleting an action.

        Args:
            index: The index of the action to delete
        """
        self.logger.debug(f"Delete action at index {index} requested.")

        # Confirm deletion
        if self.confirm_action("Confirm Delete", f"Are you sure you want to delete this action?"):
            # Delegate deletion to presenter
            self.presenter.delete_action(index)
        else:
            self.logger.debug("Delete action cancelled by user.")

    def _on_move_action(self, from_index: int, to_index: int) -> None:
        """
        Handle moving an action from one position to another.

        Args:
            from_index: The current index of the action
            to_index: The target index for the action
        """
        self.logger.debug(f"Move action from index {from_index} to {to_index} requested.")

        # Use the presenter's move_action method to move the action
        try:
            self.presenter.move_action(from_index, to_index)
            self.logger.debug(f"Action moved from index {from_index} to {to_index}.")
        except Exception as e:
            self.logger.error(f"Error moving action: {e}", exc_info=True)
            self.display_error("Move Error", f"Could not move action: {e}")
            self.set_status(f"Error moving action from position {from_index+1} to {to_index+1}.")


    def _update_workflow_button_states(self) -> None:
        """Update the enabled/disabled state of workflow buttons."""
        has_selection = self.get_selected_workflow_name() is not None

        if self.save_button:
            self.save_button.configure(state=tk.NORMAL if has_selection else tk.DISABLED)

        if self.delete_button:
            self.delete_button.configure(state=tk.NORMAL if has_selection else tk.DISABLED)
