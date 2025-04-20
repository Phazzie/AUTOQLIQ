"""Enhanced workflow editor presenter implementation for AutoQliq."""

import logging
from typing import List, Dict, Any, Optional

# Core dependencies
from src.core.interfaces import IWorkflowRepository, IAction
from src.core.exceptions import WorkflowError, ActionError, ValidationError, AutoQliqError
from src.core.actions.factory import ActionFactory

# UI dependencies
from src.ui.interfaces.presenter import IWorkflowEditorPresenter
from src.ui.interfaces.view import IWorkflowEditorView
from src.ui.presenters.base_presenter import BasePresenter

logger = logging.getLogger(__name__)


class WorkflowEditorPresenterEnhanced(BasePresenter[IWorkflowEditorView], IWorkflowEditorPresenter):
    """
    Enhanced presenter for the workflow editor view. Handles logic for creating, loading,
    saving workflows, and managing their actions.
    """
    
    def __init__(self, workflow_repository: IWorkflowRepository, view: Optional[IWorkflowEditorView] = None):
        """
        Initialize the presenter.
        
        Args:
            workflow_repository: Repository for workflow persistence
            view: The associated view instance (optional)
        """
        super().__init__(view)
        self.workflow_repository = workflow_repository
        
        # Store the currently loaded workflow actions in memory
        self._current_workflow_name: Optional[str] = None
        self._current_actions: List[IAction] = []
        
        self.logger.info("WorkflowEditorPresenterEnhanced initialized")
    
    # --- IWorkflowEditorPresenter Implementation ---
    
    def get_workflow_list(self) -> List[str]:
        """
        Get the list of available workflow names.
        
        Returns:
            List of workflow names
        """
        try:
            workflow_names = self.workflow_repository.list_workflows()
            self.logger.debug(f"Retrieved {len(workflow_names)} workflows from repository")
            return workflow_names
        except Exception as e:
            self.logger.error(f"Failed to get workflow list: {e}")
            self._handle_view_error(e, "retrieving workflow list")
            return []
    
    def load_workflow(self, name: str) -> None:
        """
        Load the specified workflow into the editor view.
        
        Args:
            name: The name of the workflow to load
        """
        try:
            self.logger.info(f"Loading workflow: {name}")
            
            # Load the workflow from the repository
            actions = self.workflow_repository.load(name)
            
            # Store the loaded workflow
            self._current_workflow_name = name
            self._current_actions = actions
            
            # Update the view
            self._update_action_list()
            
            self.logger.info(f"Loaded workflow '{name}' with {len(actions)} actions")
            self._set_view_status(f"Loaded workflow: {name}")
        except Exception as e:
            self.logger.error(f"Failed to load workflow '{name}': {e}")
            self._handle_view_error(e, f"loading workflow '{name}'")
            
            # Clear the current workflow
            self._current_workflow_name = None
            self._current_actions = []
            self._update_action_list()
    
    def save_workflow(self, name: str, actions: List[Dict[str, Any]]) -> None:
        """
        Save the currently edited workflow actions under the given name.
        
        Args:
            name: The name of the workflow to save
            actions: The list of action data dictionaries to save
        """
        try:
            self.logger.info(f"Saving workflow: {name}")
            
            # Convert action data dictionaries to IAction instances
            action_instances = []
            for action_data in actions:
                try:
                    action = ActionFactory.create_action(**action_data)
                    action_instances.append(action)
                except Exception as e:
                    self.logger.error(f"Failed to create action from data: {action_data}")
                    raise ActionError(f"Failed to create action: {e}", action_name=action_data.get("name", "Unknown"), cause=e) from e
            
            # Save the workflow to the repository
            self.workflow_repository.save(name, action_instances)
            
            # Update the current workflow
            self._current_workflow_name = name
            self._current_actions = action_instances
            
            self.logger.info(f"Saved workflow '{name}' with {len(action_instances)} actions")
            self._set_view_status(f"Saved workflow: {name}")
        except Exception as e:
            self.logger.error(f"Failed to save workflow '{name}': {e}")
            self._handle_view_error(e, f"saving workflow '{name}'")
    
    def save_current_workflow(self) -> None:
        """Save the currently loaded workflow."""
        if self._current_workflow_name and self._current_actions:
            try:
                self.logger.info(f"Saving current workflow: {self._current_workflow_name}")
                
                # Save the workflow to the repository
                self.workflow_repository.save(self._current_workflow_name, self._current_actions)
                
                self.logger.info(f"Saved workflow '{self._current_workflow_name}' with {len(self._current_actions)} actions")
                self._set_view_status(f"Saved workflow: {self._current_workflow_name}")
            except Exception as e:
                self.logger.error(f"Failed to save current workflow: {e}")
                self._handle_view_error(e, "saving current workflow")
        else:
            self.logger.warning("No workflow loaded to save")
            self._set_view_status("No workflow loaded to save")
    
    def create_new_workflow(self, name: str) -> None:
        """
        Create a new, empty workflow.
        
        Args:
            name: The name of the new workflow
        """
        try:
            self.logger.info(f"Creating new workflow: {name}")
            
            # Create a new workflow in the repository
            self.workflow_repository.create_workflow(name)
            
            # Load the new workflow
            self._current_workflow_name = name
            self._current_actions = []
            
            # Update the view
            self._update_workflow_list()
            self._update_action_list()
            
            # Select the new workflow in the view
            if self.view:
                self.view.set_workflow_list(self.get_workflow_list())
                # TODO: Select the new workflow in the list
            
            self.logger.info(f"Created new workflow: {name}")
            self._set_view_status(f"Created new workflow: {name}")
        except Exception as e:
            self.logger.error(f"Failed to create new workflow '{name}': {e}")
            self._handle_view_error(e, f"creating workflow '{name}'")
    
    def delete_workflow(self, name: str) -> None:
        """
        Delete the specified workflow.
        
        Args:
            name: The name of the workflow to delete
        """
        try:
            self.logger.info(f"Deleting workflow: {name}")
            
            # Delete the workflow from the repository
            self.workflow_repository.delete(name)
            
            # Clear the current workflow if it was the one deleted
            if self._current_workflow_name == name:
                self._current_workflow_name = None
                self._current_actions = []
                self._update_action_list()
            
            # Update the workflow list
            self._update_workflow_list()
            
            self.logger.info(f"Deleted workflow: {name}")
            self._set_view_status(f"Deleted workflow: {name}")
        except Exception as e:
            self.logger.error(f"Failed to delete workflow '{name}': {e}")
            self._handle_view_error(e, f"deleting workflow '{name}'")
    
    def add_action(self, action_data: Dict[str, Any], index: Optional[int] = None) -> None:
        """
        Add a new action to the current workflow.
        
        Args:
            action_data: The action data dictionary
            index: The index at which to insert the action (default: append)
        """
        try:
            self.logger.info(f"Adding action: {action_data}")
            
            # Create an action instance from the data
            action = ActionFactory.create_action(**action_data)
            
            # Add the action to the current workflow
            if index is not None:
                self._current_actions.insert(index, action)
            else:
                self._current_actions.append(action)
            
            # Update the view
            self._update_action_list()
            
            self.logger.info(f"Added action: {action.name} ({action.action_type})")
            self._set_view_status(f"Added action: {action.name}")
        except Exception as e:
            self.logger.error(f"Failed to add action: {e}")
            self._handle_view_error(e, "adding action")
    
    def update_action(self, index: int, action_data: Dict[str, Any]) -> None:
        """
        Update the action at the specified index with new data.
        
        Args:
            index: The index of the action to update
            action_data: The new action data dictionary
        """
        try:
            self.logger.info(f"Updating action at index {index}: {action_data}")
            
            # Create an action instance from the data
            action = ActionFactory.create_action(**action_data)
            
            # Update the action in the current workflow
            if 0 <= index < len(self._current_actions):
                self._current_actions[index] = action
                
                # Update the view
                self._update_action_list()
                
                self.logger.info(f"Updated action at index {index}: {action.name} ({action.action_type})")
                self._set_view_status(f"Updated action: {action.name}")
            else:
                self.logger.warning(f"Invalid action index: {index}")
                self._set_view_status(f"Invalid action index: {index}")
        except Exception as e:
            self.logger.error(f"Failed to update action at index {index}: {e}")
            self._handle_view_error(e, f"updating action at index {index}")
    
    def delete_action(self, index: int) -> None:
        """
        Delete the action at the specified index.
        
        Args:
            index: The index of the action to delete
        """
        try:
            self.logger.info(f"Deleting action at index {index}")
            
            # Delete the action from the current workflow
            if 0 <= index < len(self._current_actions):
                action = self._current_actions.pop(index)
                
                # Update the view
                self._update_action_list()
                
                self.logger.info(f"Deleted action at index {index}: {action.name} ({action.action_type})")
                self._set_view_status(f"Deleted action: {action.name}")
            else:
                self.logger.warning(f"Invalid action index: {index}")
                self._set_view_status(f"Invalid action index: {index}")
        except Exception as e:
            self.logger.error(f"Failed to delete action at index {index}: {e}")
            self._handle_view_error(e, f"deleting action at index {index}")
    
    def get_action_data(self, index: int) -> Optional[Dict[str, Any]]:
        """
        Get the data dictionary for the action at the specified index.
        
        Args:
            index: The index of the action
            
        Returns:
            The action data dictionary, or None if the index is invalid
        """
        try:
            self.logger.debug(f"Getting action data at index {index}")
            
            # Get the action from the current workflow
            if 0 <= index < len(self._current_actions):
                action = self._current_actions[index]
                
                # Convert the action to a data dictionary
                action_data = {
                    "name": action.name,
                    "action_type": action.action_type
                }
                
                # Add action-specific properties
                for key, value in vars(action).items():
                    if not key.startswith("_") and key not in ["name", "action_type"]:
                        action_data[key] = value
                
                self.logger.debug(f"Got action data at index {index}: {action_data}")
                return action_data
            else:
                self.logger.warning(f"Invalid action index: {index}")
                return None
        except Exception as e:
            self.logger.error(f"Failed to get action data at index {index}: {e}")
            self._handle_view_error(e, f"getting action data at index {index}")
            return None
    
    # --- BasePresenter Implementation ---
    
    def initialize_view(self) -> None:
        """Initialize the associated view with necessary data."""
        if self.view:
            try:
                self.logger.debug("Initializing view")
                
                # Set the workflow list
                self._update_workflow_list()
                
                # Clear the action list
                self._update_action_list()
                
                self.logger.debug("View initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize view: {e}")
                self._handle_view_error(e, "initializing view")
    
    # --- Helper Methods ---
    
    def _update_workflow_list(self) -> None:
        """Update the workflow list in the view."""
        if self.view:
            try:
                workflow_names = self.get_workflow_list()
                self.view.set_workflow_list(workflow_names)
            except Exception as e:
                self.logger.error(f"Failed to update workflow list: {e}")
                self._handle_view_error(e, "updating workflow list")
    
    def _update_action_list(self) -> None:
        """Update the action list in the view."""
        if self.view:
            try:
                # Convert actions to display strings
                action_displays = []
                for action in self._current_actions:
                    display = self._format_action_for_display(action)
                    action_displays.append(display)
                
                self.view.set_action_list(action_displays)
            except Exception as e:
                self.logger.error(f"Failed to update action list: {e}")
                self._handle_view_error(e, "updating action list")
    
    def _format_action_for_display(self, action: IAction) -> str:
        """
        Format an action for display in the view.
        
        Args:
            action: The action to format
            
        Returns:
            A formatted string representation of the action
        """
        try:
            # Get the action type and name
            action_type = action.action_type
            action_name = action.name
            
            # Format the action based on its type
            if action_type == "Navigate":
                url = getattr(action, "url", "")
                return f"{action_name} ({action_type}): {url}"
            elif action_type == "Click":
                selector = getattr(action, "selector", "")
                return f"{action_name} ({action_type}): {selector}"
            elif action_type == "Type":
                selector = getattr(action, "selector", "")
                value_type = getattr(action, "value_type", "")
                value_key = getattr(action, "value_key", "")
                return f"{action_name} ({action_type}): {selector} - {value_type}:{value_key}"
            elif action_type == "Wait":
                duration = getattr(action, "duration_seconds", "")
                return f"{action_name} ({action_type}): {duration}s"
            elif action_type == "Screenshot":
                file_path = getattr(action, "file_path", "")
                return f"{action_name} ({action_type}): {file_path}"
            else:
                # Generic format for other action types
                return f"{action_name} ({action_type})"
        except Exception as e:
            self.logger.error(f"Failed to format action for display: {e}")
            return f"{action.name} ({action.action_type}): Error formatting"
    
    def _set_view_status(self, message: str) -> None:
        """
        Set the status message in the view.
        
        Args:
            message: The status message
        """
        if self.view:
            try:
                self.view.set_status(message)
            except Exception as e:
                self.logger.error(f"Failed to set view status: {e}")
    
    def _handle_view_error(self, error: Exception, context: str) -> None:
        """
        Handle an error by displaying it in the view.
        
        Args:
            error: The error that occurred
            context: The context in which the error occurred
        """
        if self.view:
            try:
                self.view.display_error("Error", f"An error occurred while {context}: {error}")
            except Exception as e:
                self.logger.error(f"Failed to display error in view: {e}")
                # Fall back to setting the status
                self._set_view_status(f"Error: {error}")
