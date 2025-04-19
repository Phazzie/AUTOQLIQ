"""Workflow editor presenter implementation for AutoQliq."""

import logging
from typing import List, Dict, Any, Optional

# Core dependencies
from src.core.interfaces import IAction
from src.core.interfaces.service import IWorkflowService # Use Service Interface
from src.core.exceptions import WorkflowError, ActionError, ValidationError, AutoQliqError

# UI dependencies
from src.ui.interfaces.presenter import IWorkflowEditorPresenter
from src.ui.interfaces.view import IWorkflowEditorView
from src.ui.presenters.base_presenter import BasePresenter
# Use ActionFactory directly for creating/validating action data from UI dialog
from src.core.actions.factory import ActionFactory


class WorkflowEditorPresenter(BasePresenter[IWorkflowEditorView], IWorkflowEditorPresenter):
    """
    Presenter for the workflow editor view. Handles logic for creating, loading,
    saving workflows, and managing their actions by interacting with the WorkflowService.
    """

    def __init__(self, workflow_service: IWorkflowService, view: Optional[IWorkflowEditorView] = None):
        """
        Initialize the presenter.

        Args:
            workflow_service: The service handling workflow business logic and persistence.
            view: The associated view instance (optional).
        """
        super().__init__(view)
        if workflow_service is None:
             raise ValueError("Workflow service cannot be None.")
        self.workflow_service = workflow_service
        # Store the currently loaded workflow actions in memory for editing
        self._current_workflow_name: Optional[str] = None
        self._current_actions: List[IAction] = [] # Presenter holds domain objects
        self.logger.info("WorkflowEditorPresenter initialized.")

    def set_view(self, view: IWorkflowEditorView) -> None:
        """Set the view and perform initial population."""
        super().set_view(view)
        self.initialize_view()

    @BasePresenter.handle_errors("Initializing editor view")
    def initialize_view(self) -> None:
        """Populate the view with initial data (workflow list)."""
        if not self.view: return
        self.logger.debug("Initializing editor view...")
        workflows = self.get_workflow_list() # Uses service
        self.view.set_workflow_list(workflows or [])
        self._update_action_list_display() # Show empty actions initially
        self.view.set_status("Editor ready. Select a workflow or create a new one.")
        self.logger.debug("Editor view initialized.")

    @BasePresenter.handle_errors("Getting workflow list")
    def get_workflow_list(self) -> List[str]:
        """Get the list of available workflow names via the service."""
        self.logger.debug("Fetching workflow list from service.")
        return self.workflow_service.list_workflows()

    @BasePresenter.handle_errors("Loading workflow")
    def load_workflow(self, name: str) -> None:
        """Load a workflow via the service and update the view."""
        if not self.view: return
        if not name:
             raise ValidationError("Workflow name cannot be empty.", field_name="workflow_name")

        self.logger.info(f"Loading workflow: {name}")
        # Service handles interaction with repository
        actions = self.workflow_service.get_workflow(name) # Raises WorkflowError if not found etc.
        self._current_workflow_name = name
        self._current_actions = actions if actions else [] # Ensure it's a list
        self._update_action_list_display()
        self.view.set_status(f"Workflow '{name}' loaded with {len(self._current_actions)} actions.")
        self.logger.info(f"Successfully loaded workflow '{name}'.")

    @BasePresenter.handle_errors("Saving workflow")
    def save_workflow(self, name: Optional[str] = None, actions_data: Optional[List[Dict[str, Any]]] = None) -> None:
        """Save the current workflow actions via the service."""
        if not self.view: return

        target_name = name or self._current_workflow_name
        if not target_name:
             raise WorkflowError("Cannot save workflow without a name. Load or create a workflow first.")

        self.logger.info(f"Attempting to save workflow: {target_name}")
        actions_to_save = self._current_actions

        # Service handles validation, serialization, saving. Decorator catches errors.
        success = self.workflow_service.save_workflow(target_name, actions_to_save)
        if success: # Service method returns bool now
            self._current_workflow_name = target_name
            self.view.set_status(f"Workflow '{target_name}' saved successfully.")
            self.logger.info(f"Successfully saved workflow '{target_name}'.")
            workflows = self.get_workflow_list()
            if self.view: self.view.set_workflow_list(workflows or [])


    @BasePresenter.handle_errors("Creating new workflow")
    def create_new_workflow(self, name: str) -> None:
        """Create a new, empty workflow via the service."""
        if not self.view: return
        if not name:
             raise ValidationError("Workflow name cannot be empty.", field_name="workflow_name")

        self.logger.info(f"Creating new workflow: {name}")
        success = self.workflow_service.create_workflow(name) # Service raises errors if exists etc.
        if success:
            self.view.set_status(f"Created new workflow: '{name}'.")
            self.logger.info(f"Successfully created workflow '{name}'.")
            workflows = self.get_workflow_list()
            if self.view:
                 self.view.set_workflow_list(workflows or [])
                 self.load_workflow(name) # Load the newly created empty workflow


    @BasePresenter.handle_errors("Deleting workflow")
    def delete_workflow(self, name: str) -> None:
        """Delete a workflow via the service."""
        if not self.view: return
        if not name:
             raise ValidationError("Workflow name cannot be empty.", field_name="workflow_name")

        self.logger.info(f"Deleting workflow: {name}")
        deleted = self.workflow_service.delete_workflow(name) # Service raises errors
        if deleted:
            self.view.set_status(f"Workflow '{name}' deleted.")
            self.logger.info(f"Successfully deleted workflow '{name}'.")
            if self._current_workflow_name == name:
                 self._current_workflow_name = None
                 self._current_actions = []
                 self._update_action_list_display()
            workflows = self.get_workflow_list()
            if self.view: self.view.set_workflow_list(workflows or [])
        else:
             # Service returned False (likely not found)
             raise WorkflowError(f"Workflow '{name}' not found, cannot delete.", workflow_name=name)


    # --- Action Management (Operate on internal state, save separately) ---

    def add_action(self, action_data: Dict[str, Any]) -> None:
        """Add a new action to the current in-memory list and update view."""
        if not self.view: return
        if self._current_workflow_name is None:
             self._handle_error(WorkflowError("No workflow loaded. Cannot add action."), "adding action")
             return

        self.logger.debug(f"Attempting to add action to '{self._current_workflow_name}': {action_data.get('type')}")
        try:
            new_action = ActionFactory.create_action(action_data) # Raises ActionError/ValidationError
            new_action.validate() # Raises ValidationError
            self._current_actions.append(new_action)
            self._update_action_list_display()
            self.view.set_status(f"Action '{new_action.name}' added to '{self._current_workflow_name}' (unsaved).")
            self.logger.info(f"Added action {new_action.action_type} to internal list for '{self._current_workflow_name}'.")
        except (ActionError, ValidationError) as e:
             self._handle_error(e, "adding action")
        except Exception as e:
             self._handle_error(AutoQliqError("Unexpected error adding action.", cause=e), "adding action")

    def insert_action(self, position: int, action_data: Dict[str, Any]) -> None:
        """Insert a new action at the specified position in the current workflow."""
        if not self.view: return
        if self._current_workflow_name is None:
             self._handle_error(WorkflowError("No workflow loaded. Cannot insert action."), "inserting action")
             return
        if not (0 <= position <= len(self._current_actions)):
             self._handle_error(IndexError(f"Invalid position for insertion: {position}"), "inserting action")
             return

        self.logger.debug(f"Attempting to insert action at position {position} in '{self._current_workflow_name}': {action_data.get('type')}")
        try:
            new_action = ActionFactory.create_action(action_data) # Raises ActionError/ValidationError
            new_action.validate() # Raises ValidationError
            self._current_actions.insert(position, new_action)
            self._update_action_list_display()
            self.view.set_status(f"Action '{new_action.name}' inserted at position {position+1} in '{self._current_workflow_name}' (unsaved).")
            self.logger.info(f"Inserted action {new_action.action_type} at position {position} in internal list for '{self._current_workflow_name}'.")
        except (ActionError, ValidationError) as e:
             self._handle_error(e, "inserting action")
        except Exception as e:
             self._handle_error(AutoQliqError("Unexpected error inserting action.", cause=e), "inserting action")


    def update_action(self, index: int, action_data: Dict[str, Any]) -> None:
        """Update an action in the current in-memory list and update view."""
        if not self.view: return
        if self._current_workflow_name is None:
             self._handle_error(WorkflowError("No workflow loaded. Cannot update action."), "updating action")
             return
        if not (0 <= index < len(self._current_actions)):
            self._handle_error(IndexError(f"Invalid action index for update: {index}"), "updating action")
            return

        self.logger.debug(f"Attempting to update action at index {index} in '{self._current_workflow_name}'")
        try:
            updated_action = ActionFactory.create_action(action_data) # Raises ActionError/ValidationError
            updated_action.validate() # Raises ValidationError
            self._current_actions[index] = updated_action
            self._update_action_list_display()
            self.view.set_status(f"Action {index+1} ('{updated_action.name}') updated in '{self._current_workflow_name}' (unsaved).")
            self.logger.info(f"Updated action at index {index} in internal list for '{self._current_workflow_name}'.")
        except (ActionError, ValidationError) as e:
            self._handle_error(e, "updating action")
        except Exception as e:
             self._handle_error(AutoQliqError("Unexpected error updating action.", cause=e), "updating action")


    def delete_action(self, index: int) -> None:
        """Delete an action from the current in-memory list and update view."""
        if not self.view: return
        if self._current_workflow_name is None:
             self._handle_error(WorkflowError("No workflow loaded. Cannot delete action."), "deleting action")
             return
        if not (0 <= index < len(self._current_actions)):
             self._handle_error(IndexError(f"Invalid action index for delete: {index}"), "deleting action")
             return

        self.logger.debug(f"Attempting to delete action at index {index} from '{self._current_workflow_name}'")
        try:
            deleted_action = self._current_actions.pop(index)
            self._update_action_list_display()
            self.view.set_status(f"Action {index+1} ('{deleted_action.name}') deleted from '{self._current_workflow_name}' (unsaved).")
            self.logger.info(f"Deleted action at index {index} from internal list for '{self._current_workflow_name}'.")
        except IndexError:
             self._handle_error(IndexError(f"Action index {index} out of range during delete."), "deleting action")
        except Exception as e:
             self._handle_error(AutoQliqError("Unexpected error deleting action.", cause=e), "deleting action")


    def get_action_data(self, index: int) -> Optional[Dict[str, Any]]:
        """Get the data dictionary for the action at the specified index."""
        if not (0 <= index < len(self._current_actions)):
            self.logger.warning(f"Attempted to get action data for invalid index: {index}")
            return None
        try:
            action = self._current_actions[index]
            return action.to_dict()
        except Exception as e:
            self._handle_error(AutoQliqError(f"Failed to get dictionary for action at index {index}", cause=e), "getting action data")
            return None

    def get_all_actions_data(self) -> List[Dict[str, Any]]:
        """Get data dictionaries for all actions in the current workflow."""
        try:
            return [action.to_dict() for action in self._current_actions]
        except Exception as e:
            self._handle_error(AutoQliqError("Failed to get dictionaries for all actions", cause=e), "getting all actions data")
            return []

    def move_action(self, from_index: int, to_index: int) -> None:
        """Move an action from one position to another in the current workflow."""
        if not self.view: return
        if self._current_workflow_name is None:
            self._handle_error(WorkflowError("No workflow loaded. Cannot move action."), "moving action")
            return
        if not (0 <= from_index < len(self._current_actions)):
            self._handle_error(IndexError(f"Invalid source index for move: {from_index}"), "moving action")
            return
        if not (0 <= to_index < len(self._current_actions)):
            self._handle_error(IndexError(f"Invalid target index for move: {to_index}"), "moving action")
            return
        if from_index == to_index:
            # No need to move if indices are the same
            return

        self.logger.debug(f"Attempting to move action from index {from_index} to {to_index} in '{self._current_workflow_name}'")
        try:
            # Remove the action from the source position
            action = self._current_actions.pop(from_index)
            # Insert it at the target position
            self._current_actions.insert(to_index, action)
            self._update_action_list_display()
            self.view.set_status(f"Action moved from position {from_index+1} to {to_index+1} in '{self._current_workflow_name}' (unsaved).")
            self.logger.info(f"Moved action from index {from_index} to {to_index} in internal list for '{self._current_workflow_name}'.")
        except IndexError:
            self._handle_error(IndexError(f"Action index out of range during move."), "moving action")
        except Exception as e:
            self._handle_error(AutoQliqError("Unexpected error moving action.", cause=e), "moving action")

    # --- Helper Methods ---

    def _update_action_list_display(self) -> None:
        """Format the current actions and tell the view to display them."""
        if not self.view: return
        try:
            # Use str(action) which should provide a user-friendly summary for legacy view
            actions_display = [f"{i+1}: {str(action)}" for i, action in enumerate(self._current_actions)]
            self.view.set_action_list(actions_display)

            # Also provide action data dictionaries for enhanced view
            try:
                actions_data = [action.to_dict() for action in self._current_actions]
                self.view.set_action_data_list(actions_data)
            except AttributeError:
                # View doesn't support set_action_data_list, which is fine for legacy views
                pass

            self.logger.debug(f"Updated action list display in view for '{self._current_workflow_name}'. Actions: {len(actions_display)}")
        except Exception as e:
            # Use the internal error handler which will log and show error in view
            from src.core.exceptions import UIError
            self._handle_error(UIError("Failed to update action list display.", cause=e), "updating action list")