"""Workflow editor presenter implementation for AutoQliq."""

import logging
from typing import List, Dict, Any, Optional

# Core dependencies
from src.core.interfaces import IWorkflowRepository, IAction
from src.core.exceptions import WorkflowError, ActionError, ValidationError, AutoQliqError
from src.core.actions.factory import ActionFactory # Use the factory for creation

# UI dependencies
from src.ui.interfaces.presenter import IWorkflowEditorPresenter
from src.ui.interfaces.view import IWorkflowEditorView
from src.ui.presenters.base_presenter import BasePresenter
# Assuming ActionFormatter exists for display formatting
# from src.ui.common.data_formatter import DataFormatter


class WorkflowEditorPresenter(BasePresenter[IWorkflowEditorView], IWorkflowEditorPresenter):
    """
    Presenter for the workflow editor view. Handles logic for creating, loading,
    saving workflows, and managing their actions.
    """

    def __init__(self, workflow_repository: IWorkflowRepository, view: Optional[IWorkflowEditorView] = None):
        """
        Initialize the presenter.

        Args:
            workflow_repository: Repository for workflow persistence.
            view: The associated view instance (optional).
        """
        super().__init__(view)
        self.workflow_repository = workflow_repository
        # Store the currently loaded workflow actions in memory
        self._current_workflow_name: Optional[str] = None
        self._current_actions: List[IAction] = []
        self.logger.info("WorkflowEditorPresenter initialized.")

    def set_view(self, view: IWorkflowEditorView) -> None:
        """Set the view and perform initial population."""
        super().set_view(view)
        self.initialize_view()

    @BasePresenter.handle_errors("Initializing editor view")
    def initialize_view(self) -> None:
        """Populate the view with initial data (workflow list)."""
        if not self.view: return
        self.logger.debug("Initializing view...")
        workflows = self.get_workflow_list() # Calls method below
        self.view.set_workflow_list(workflows or [])
        self._update_action_list_display() # Show empty actions initially
        self.logger.debug("View initialized.")

    @BasePresenter.handle_errors("Getting workflow list")
    def get_workflow_list(self) -> List[str]:
        """Get the list of available workflow names from the repository."""
        self.logger.debug("Fetching workflow list from repository.")
        return self.workflow_repository.list_workflows()

    @BasePresenter.handle_errors("Loading workflow")
    def load_workflow(self, name: str) -> None:
        """Load a workflow and update the view."""
        if not self.view: return
        if not name:
             self.logger.warning("Load workflow called with empty name.")
             self._handle_error(ValidationError("Workflow name cannot be empty."), "loading workflow")
             return

        self.logger.info(f"Loading workflow: {name}")
        try:
             actions = self.workflow_repository.load(name)
             self._current_workflow_name = name
             self._current_actions = actions
             self._update_action_list_display()
             self.view.set_status(f"Workflow '{name}' loaded.")
             self.logger.info(f"Successfully loaded workflow '{name}' with {len(actions)} actions.")
        except (WorkflowError, RepositoryError, SerializationError, ValidationError) as e:
             # Let the decorator handle logging/displaying the specific error
             self._current_workflow_name = None
             self._current_actions = []
             self._update_action_list_display() # Clear action list on load failure
             raise # Re-raise for the decorator

    @BasePresenter.handle_errors("Saving workflow")
    def save_workflow(self, name: str, actions_data: Optional[List[Dict[str, Any]]] = None) -> None:
        """Save the current workflow actions under the given name."""
        if not self.view: return
        if not name:
             self.logger.warning("Save workflow called with empty name.")
             self._handle_error(ValidationError("Workflow name cannot be empty."), "saving workflow")
             return

        self.logger.info(f"Attempting to save workflow: {name}")

        # Determine which actions to save
        actions_to_save: List[IAction]
        if actions_data is not None:
             # If view provides action data directly (e.g. from a text editor)
             self.logger.debug("Saving actions based on provided data.")
             try:
                  actions_to_save = [ActionFactory.create_action(data) for data in actions_data]
                  # Update internal state if saved successfully
                  self._current_actions = actions_to_save
                  self._current_workflow_name = name
             except (ActionError, ValidationError) as e:
                   self._handle_error(e, f"parsing actions data for workflow '{name}'")
                   return # Abort save
        else:
             # Save the actions currently held by the presenter
             self.logger.debug("Saving actions currently held by the presenter.")
             actions_to_save = self._current_actions
             # Update name if saving under a different name? Assume name is the target save name.
             self._current_workflow_name = name

        try:
             self.workflow_repository.save(name, actions_to_save)
             self.view.set_status(f"Workflow '{name}' saved successfully.")
             self.logger.info(f"Successfully saved workflow '{name}'.")
             # Refresh workflow list in case it was a new save
             workflows = self.get_workflow_list()
             self.view.set_workflow_list(workflows or [])
             # Ensure the saved workflow name remains selected if possible (view logic)
        except (WorkflowError, RepositoryError, SerializationError, ValidationError) as e:
             # Let decorator handle logging/displaying
             raise # Re-raise for the decorator


    @BasePresenter.handle_errors("Creating new workflow")
    def create_new_workflow(self, name: str) -> None:
        """Create a new, empty workflow and update the view."""
        if not self.view: return
        if not name:
             self.logger.warning("Create workflow called with empty name.")
             self._handle_error(ValidationError("Workflow name cannot be empty."), "creating workflow")
             return

        self.logger.info(f"Creating new workflow: {name}")
        try:
            self.workflow_repository.create_workflow(name) # Creates an empty entry
            self.view.set_status(f"Created new workflow: '{name}'.")
            self.logger.info(f"Successfully created workflow '{name}'.")
            # Refresh the list and load the new empty workflow
            workflows = self.get_workflow_list()
            self.view.set_workflow_list(workflows or [])
            self.load_workflow(name) # Load the newly created empty workflow
        except (WorkflowError, RepositoryError, ValidationError) as e:
            # Let decorator handle
            raise


    @BasePresenter.handle_errors("Deleting workflow")
    def delete_workflow(self, name: str) -> None:
        """Delete a workflow and update the view."""
        if not self.view: return
        if not name:
             self.logger.warning("Delete workflow called with empty name.")
             self._handle_error(ValidationError("Workflow name cannot be empty."), "deleting workflow")
             return

        self.logger.info(f"Deleting workflow: {name}")
        try:
            deleted = self.workflow_repository.delete(name)
            if deleted:
                self.view.set_status(f"Workflow '{name}' deleted.")
                self.logger.info(f"Successfully deleted workflow '{name}'.")
                # Clear current state if the deleted workflow was loaded
                if self._current_workflow_name == name:
                     self._current_workflow_name = None
                     self._current_actions = []
                     self._update_action_list_display()
                # Refresh workflow list
                workflows = self.get_workflow_list()
                self.view.set_workflow_list(workflows or [])
            else:
                 self.logger.warning(f"Attempted to delete non-existent workflow: '{name}'")
                 self._handle_error(WorkflowError(f"Workflow '{name}' not found."), "deleting workflow")
        except (WorkflowError, RepositoryError, ValidationError) as e:
            # Let decorator handle
            raise

    # --- Action Management ---

    def add_action(self, action_data: Dict[str, Any]) -> None:
        """Add a new action to the current in-memory list and update view."""
        if not self.view: return
        if self._current_workflow_name is None:
             self._handle_error(WorkflowError("No workflow loaded to add action to."), "adding action")
             return

        self.logger.debug(f"Adding action to '{self._current_workflow_name}': {action_data.get('type')}")
        try:
            new_action = ActionFactory.create_action(action_data) # Raises ActionError
            self._current_actions.append(new_action)
            self._update_action_list_display()
            self.view.set_status(f"Action '{new_action.name}' added.")
            self.logger.debug(f"Added action {new_action.action_type} to internal list.")
            # Note: Changes are only in memory until save_workflow is called.
        except (ActionError, ValidationError) as e:
             self._handle_error(e, "adding action")


    def update_action(self, index: int, action_data: Dict[str, Any]) -> None:
        """Update an action in the current in-memory list and update view."""
        if not self.view: return
        if self._current_workflow_name is None:
             self._handle_error(WorkflowError("No workflow loaded to update action in."), "updating action")
             return
        if not (0 <= index < len(self._current_actions)):
            self._handle_error(IndexError(f"Invalid action index: {index}"), "updating action")
            return

        self.logger.debug(f"Updating action at index {index} in '{self._current_workflow_name}'")
        try:
            updated_action = ActionFactory.create_action(action_data) # Raises ActionError
            self._current_actions[index] = updated_action
            self._update_action_list_display()
            self.view.set_status(f"Action {index+1} ('{updated_action.name}') updated.")
            self.logger.debug(f"Updated action at index {index} in internal list.")
            # Note: Changes are only in memory until save_workflow is called.
        except (ActionError, ValidationError) as e:
            self._handle_error(e, "updating action")


    def delete_action(self, index: int) -> None:
        """Delete an action from the current in-memory list and update view."""
        if not self.view: return
        if self._current_workflow_name is None:
             self._handle_error(WorkflowError("No workflow loaded to delete action from."), "deleting action")
             return
        if not (0 <= index < len(self._current_actions)):
             self._handle_error(IndexError(f"Invalid action index: {index}"), "deleting action")
             return

        self.logger.debug(f"Deleting action at index {index} from '{self._current_workflow_name}'")
        try:
            deleted_action = self._current_actions.pop(index)
            self._update_action_list_display()
            self.view.set_status(f"Action {index+1} ('{deleted_action.name}') deleted.")
            self.logger.debug(f"Deleted action at index {index} from internal list.")
            # Note: Changes are only in memory until save_workflow is called.
        except IndexError: # Should be caught above, but defensively handle
             self._handle_error(IndexError(f"Action index {index} out of range."), "deleting action")


    def get_action_data(self, index: int) -> Optional[Dict[str, Any]]:
         """Get the data dictionary for the action at the specified index."""
         if not (0 <= index < len(self._current_actions)):
              self._handle_error(IndexError(f"Invalid action index: {index}"), "getting action data")
              return None
         try:
              action = self._current_actions[index]
              return action.to_dict()
         except Exception as e:
              self._handle_error(e, f"getting action data for index {index}")
              return None

    # --- Helper Methods ---

    def _update_action_list_display(self) -> None:
        """Format the current actions and tell the view to display them."""
        if not self.view: return
        try:
             # Use a simple string representation for display
             # A dedicated formatter might be better later
             actions_display = [f"{i+1}: {str(action)}" for i, action in enumerate(self._current_actions)]
             self.view.set_action_list(actions_display)
             self.logger.debug("Updated action list display in view.")
        except Exception as e:
            self.logger.error(f"Failed to update action list display: {e}", exc_info=True)
            # Don't raise, but maybe show an error?
            self._handle_error(UIError("Failed to update action list display.", cause=e), "updating action list")