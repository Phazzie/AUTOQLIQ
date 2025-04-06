"""Workflow editor presenter module for AutoQliq.

This module provides the presenter component for the workflow editor.
"""

import logging
from typing import List, Dict, Any, Optional

from src.core.interfaces import IWorkflowRepository, IAction
from src.core.exceptions import WorkflowError, ActionError


class WorkflowEditorPresenter:
    """
    Presenter for the workflow editor view.
    
    This class handles the business logic for the workflow editor, mediating between
    the view and the repositories.
    
    Attributes:
        workflow_repository: Repository for workflow storage and retrieval
        action_factory: Factory for creating action objects
        view: The view component
        logger: Logger for recording presenter operations and errors
    """
    
    def __init__(self, workflow_repository: IWorkflowRepository, action_factory: Any):
        """
        Initialize a new WorkflowEditorPresenter.
        
        Args:
            workflow_repository: Repository for workflow storage and retrieval
            action_factory: Factory for creating action objects
        """
        self.workflow_repository = workflow_repository
        self.action_factory = action_factory
        self.view = None
        self.logger = logging.getLogger(__name__)

    def get_workflow_list(self) -> List[str]:
        """
        Get a list of available workflows.
        
        Returns:
            A list of workflow names
        """
        try:
            return self.workflow_repository.list_workflows()
        except WorkflowError as e:
            self.logger.error(f"Error getting workflow list: {str(e)}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error getting workflow list: {str(e)}", exc_info=True)
            return []

    def create_workflow(self, name: str) -> bool:
        """
        Create a new workflow.
        
        Args:
            name: The name of the workflow to create
            
        Returns:
            True if the workflow was created successfully, False otherwise
        """
        try:
            self.workflow_repository.create_workflow(name)
            self.logger.info(f"Created workflow: {name}")
            return True
        except WorkflowError as e:
            self.logger.error(f"Error creating workflow: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error creating workflow: {str(e)}", exc_info=True)
            return False

    def delete_workflow(self, name: str) -> bool:
        """
        Delete a workflow.
        
        Args:
            name: The name of the workflow to delete
            
        Returns:
            True if the workflow was deleted successfully, False otherwise
        """
        try:
            result = self.workflow_repository.delete(name)
            if result:
                self.logger.info(f"Deleted workflow: {name}")
            else:
                self.logger.warning(f"Workflow not found: {name}")
            return result
        except WorkflowError as e:
            self.logger.error(f"Error deleting workflow: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error deleting workflow: {str(e)}", exc_info=True)
            return False

    def load_workflow(self, name: str) -> Optional[List[IAction]]:
        """
        Load a workflow.
        
        Args:
            name: The name of the workflow to load
            
        Returns:
            The list of actions in the workflow, or None if the workflow could not be loaded
        """
        try:
            actions = self.workflow_repository.load(name)
            self.logger.info(f"Loaded workflow: {name}")
            return actions
        except WorkflowError as e:
            self.logger.error(f"Error loading workflow: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error loading workflow: {str(e)}", exc_info=True)
            return None

    def save_workflow(self, name: str, actions: Optional[List[IAction]] = None) -> bool:
        """
        Save a workflow.
        
        Args:
            name: The name of the workflow to save
            actions: The list of actions to save, or None to use the currently loaded actions
            
        Returns:
            True if the workflow was saved successfully, False otherwise
        """
        try:
            # If actions are not provided, load them from the repository
            if actions is None:
                actions = self.workflow_repository.load(name)
                
            # Save the workflow
            self.workflow_repository.save(name, actions)
            self.logger.info(f"Saved workflow: {name}")
            return True
        except WorkflowError as e:
            self.logger.error(f"Error saving workflow: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error saving workflow: {str(e)}", exc_info=True)
            return False

    def add_action(self, workflow_name: str, action_data: Dict[str, Any]) -> bool:
        """
        Add an action to a workflow.
        
        Args:
            workflow_name: The name of the workflow to add the action to
            action_data: The data for the action to add
            
        Returns:
            True if the action was added successfully, False otherwise
        """
        try:
            # Load the workflow
            actions = self.workflow_repository.load(workflow_name)
            
            # Create the action
            action = self.action_factory.create_action(action_data)
            
            # Add the action to the workflow
            actions.append(action)
            
            # Save the workflow
            self.workflow_repository.save(workflow_name, actions)
            
            self.logger.info(f"Added action to workflow: {workflow_name}")
            return True
        except (WorkflowError, ActionError) as e:
            self.logger.error(f"Error adding action to workflow: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error adding action to workflow: {str(e)}", exc_info=True)
            return False

    def update_action(self, workflow_name: str, action_index: int, action_data: Dict[str, Any]) -> bool:
        """
        Update an action in a workflow.
        
        Args:
            workflow_name: The name of the workflow to update the action in
            action_index: The index of the action to update
            action_data: The new data for the action
            
        Returns:
            True if the action was updated successfully, False otherwise
        """
        try:
            # Load the workflow
            actions = self.workflow_repository.load(workflow_name)
            
            # Check that the action index is valid
            if action_index < 0 or action_index >= len(actions):
                self.logger.error(f"Invalid action index: {action_index}")
                return False
                
            # Create the new action
            new_action = self.action_factory.create_action(action_data)
            
            # Replace the action in the workflow
            actions[action_index] = new_action
            
            # Save the workflow
            self.workflow_repository.save(workflow_name, actions)
            
            self.logger.info(f"Updated action in workflow: {workflow_name}")
            return True
        except (WorkflowError, ActionError) as e:
            self.logger.error(f"Error updating action in workflow: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error updating action in workflow: {str(e)}", exc_info=True)
            return False

    def delete_action(self, workflow_name: str, action_index: int) -> bool:
        """
        Delete an action from a workflow.
        
        Args:
            workflow_name: The name of the workflow to delete the action from
            action_index: The index of the action to delete
            
        Returns:
            True if the action was deleted successfully, False otherwise
        """
        try:
            # Load the workflow
            actions = self.workflow_repository.load(workflow_name)
            
            # Check that the action index is valid
            if action_index < 0 or action_index >= len(actions):
                self.logger.error(f"Invalid action index: {action_index}")
                return False
                
            # Remove the action from the workflow
            del actions[action_index]
            
            # Save the workflow
            self.workflow_repository.save(workflow_name, actions)
            
            self.logger.info(f"Deleted action from workflow: {workflow_name}")
            return True
        except WorkflowError as e:
            self.logger.error(f"Error deleting action from workflow: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error deleting action from workflow: {str(e)}", exc_info=True)
            return False

    def get_action(self, workflow_name: str, action_index: int) -> Optional[Dict[str, Any]]:
        """
        Get an action from a workflow.
        
        Args:
            workflow_name: The name of the workflow to get the action from
            action_index: The index of the action to get
            
        Returns:
            The action data, or None if the action could not be retrieved
        """
        try:
            # Load the workflow
            actions = self.workflow_repository.load(workflow_name)
            
            # Check that the action index is valid
            if action_index < 0 or action_index >= len(actions):
                self.logger.error(f"Invalid action index: {action_index}")
                return None
                
            # Get the action
            action = actions[action_index]
            
            # Convert the action to a dictionary
            return action.to_dict()
        except WorkflowError as e:
            self.logger.error(f"Error getting action from workflow: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error getting action from workflow: {str(e)}", exc_info=True)
            return None
