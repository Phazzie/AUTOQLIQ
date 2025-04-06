import logging
from typing import List, Dict, Any, Optional

from src.core.interfaces import IWorkflowRepository
from src.core.actions import ActionFactory
from src.core.exceptions import WorkflowError, ActionError


class WorkflowEditorPresenter:
    """
    Presenter for the workflow editor view.
    
    This class handles the business logic for the workflow editor, mediating between
    the view and the repositories.
    
    Attributes:
        workflow_repository: Repository for workflow storage and retrieval
        action_factory: Factory for creating action objects
        logger: Logger for recording presenter operations and errors
    """
    
    def __init__(self, workflow_repository: IWorkflowRepository, action_factory: ActionFactory):
        """
        Initialize a new WorkflowEditorPresenter.
        
        Args:
            workflow_repository: Repository for workflow storage and retrieval
            action_factory: Factory for creating action objects
        """
        self.workflow_repository = workflow_repository
        self.action_factory = action_factory
        self.logger = logging.getLogger(__name__)
    
    def get_workflow_list(self) -> List[str]:
        """
        Get a list of available workflows.
        
        Returns:
            A list of workflow names
            
        Raises:
            WorkflowError: If there is an error retrieving the workflow list
        """
        self.logger.debug("Getting workflow list")
        return self.workflow_repository.get_workflow_list()
    
    def load_workflow(self, workflow_name: str) -> List[Any]:
        """
        Load a workflow by name.
        
        Args:
            workflow_name: The name of the workflow to load
            
        Returns:
            A list of actions in the workflow
            
        Raises:
            WorkflowError: If there is an error loading the workflow
        """
        self.logger.debug(f"Loading workflow: {workflow_name}")
        return self.workflow_repository.load_workflow(workflow_name)
    
    def create_workflow(self, workflow_name: str) -> bool:
        """
        Create a new workflow.
        
        Args:
            workflow_name: The name of the new workflow
            
        Returns:
            True if the workflow was created successfully
            
        Raises:
            WorkflowError: If there is an error creating the workflow
        """
        self.logger.debug(f"Creating workflow: {workflow_name}")
        self.workflow_repository.create_workflow(workflow_name)
        return True
    
    def save_workflow(self, workflow_name: str) -> bool:
        """
        Save a workflow.
        
        Args:
            workflow_name: The name of the workflow to save
            
        Returns:
            True if the workflow was saved successfully
            
        Raises:
            WorkflowError: If there is an error saving the workflow
        """
        self.logger.debug(f"Saving workflow: {workflow_name}")
        self.workflow_repository.save_workflow(workflow_name)
        return True
    
    def delete_workflow(self, workflow_name: str) -> bool:
        """
        Delete a workflow.
        
        Args:
            workflow_name: The name of the workflow to delete
            
        Returns:
            True if the workflow was deleted successfully
            
        Raises:
            WorkflowError: If there is an error deleting the workflow
        """
        self.logger.debug(f"Deleting workflow: {workflow_name}")
        self.workflow_repository.delete_workflow(workflow_name)
        return True
    
    def add_action(self, workflow_name: str, action_data: Dict[str, Any]) -> bool:
        """
        Add an action to a workflow.
        
        Args:
            workflow_name: The name of the workflow to add the action to
            action_data: The action data to add
            
        Returns:
            True if the action was added successfully
            
        Raises:
            ActionError: If there is an error creating the action
            WorkflowError: If there is an error adding the action to the workflow
        """
        self.logger.debug(f"Adding action to workflow: {workflow_name}")
        
        # Create the action
        action = self.action_factory.create_action(action_data)
        
        # Add the action to the workflow
        self.workflow_repository.add_action(workflow_name, action)
        
        return True
    
    def get_action(self, workflow_name: str, action_index: int) -> Dict[str, Any]:
        """
        Get an action from a workflow.
        
        Args:
            workflow_name: The name of the workflow
            action_index: The index of the action to get
            
        Returns:
            The action data
            
        Raises:
            WorkflowError: If there is an error getting the action
        """
        self.logger.debug(f"Getting action {action_index} from workflow: {workflow_name}")
        
        # Get the action from the workflow
        action = self.workflow_repository.get_action(workflow_name, action_index)
        
        # Convert the action to a dictionary
        return action.to_dict()
    
    def update_action(self, workflow_name: str, action_index: int, action_data: Dict[str, Any]) -> bool:
        """
        Update an action in a workflow.
        
        Args:
            workflow_name: The name of the workflow
            action_index: The index of the action to update
            action_data: The new action data
            
        Returns:
            True if the action was updated successfully
            
        Raises:
            ActionError: If there is an error creating the action
            WorkflowError: If there is an error updating the action in the workflow
        """
        self.logger.debug(f"Updating action {action_index} in workflow: {workflow_name}")
        
        # Create the action
        action = self.action_factory.create_action(action_data)
        
        # Update the action in the workflow
        self.workflow_repository.update_action(workflow_name, action_index, action)
        
        return True
    
    def delete_action(self, workflow_name: str, action_index: int) -> bool:
        """
        Delete an action from a workflow.
        
        Args:
            workflow_name: The name of the workflow
            action_index: The index of the action to delete
            
        Returns:
            True if the action was deleted successfully
            
        Raises:
            WorkflowError: If there is an error deleting the action
        """
        self.logger.debug(f"Deleting action {action_index} from workflow: {workflow_name}")
        
        # Delete the action from the workflow
        self.workflow_repository.delete_action(workflow_name, action_index)
        
        return True
