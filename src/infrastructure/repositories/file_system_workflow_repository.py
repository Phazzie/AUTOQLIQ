"""File system implementation of the workflow repository.

This module provides a file system-based implementation of the IWorkflowRepository interface.
"""

import json
import os
import logging
from typing import List, Optional, Dict, Any
import uuid

from src.core.workflow.workflow_entity import Workflow
from src.core.interfaces import IWorkflowRepository
from src.core.exceptions import RepositoryError

logger = logging.getLogger(__name__)

class FileSystemWorkflowRepository(IWorkflowRepository):
    """
    File system implementation of the workflow repository.
    
    Stores workflows as JSON files in a specified directory.
    """
    
    def __init__(self, directory_path: str):
        """
        Initialize the repository with the directory path.
        
        Args:
            directory_path: Path to the directory where workflows will be stored.
        """
        self.directory_path = directory_path
        
        # Create directory if it doesn't exist
        os.makedirs(self.directory_path, exist_ok=True)
        
        logger.debug(f"FileSystemWorkflowRepository initialized with directory: {directory_path}")
    
    def save(self, workflow: Workflow) -> None:
        """
        Save a workflow to the file system.
        
        Args:
            workflow: The workflow to save.
            
        Raises:
            RepositoryError: If the workflow could not be saved.
        """
        try:
            # Ensure workflow has an ID
            if not workflow.id:
                workflow.id = str(uuid.uuid4())
            
            # Convert workflow to dictionary
            workflow_dict = self._workflow_to_dict(workflow)
            
            # Create file path
            file_path = os.path.join(self.directory_path, f"{workflow.id}.json")
            
            # Write to file
            with open(file_path, 'w') as f:
                json.dump(workflow_dict, f, indent=2)
            
            logger.info(f"Saved workflow '{workflow.name}' to {file_path}")
        except Exception as e:
            logger.error(f"Error saving workflow '{workflow.name}': {e}")
            raise RepositoryError(f"Failed to save workflow: {e}")
    
    def get(self, workflow_id: str) -> Optional[Workflow]:
        """
        Get a workflow by ID.
        
        Args:
            workflow_id: The ID of the workflow to get.
            
        Returns:
            The workflow, or None if not found.
            
        Raises:
            RepositoryError: If the workflow could not be retrieved.
        """
        try:
            # Create file path
            file_path = os.path.join(self.directory_path, f"{workflow_id}.json")
            
            # Check if file exists
            if not os.path.exists(file_path):
                logger.info(f"Workflow not found: {workflow_id}")
                return None
            
            # Read from file
            with open(file_path, 'r') as f:
                workflow_dict = json.load(f)
            
            # Convert dictionary to workflow
            workflow = self._dict_to_workflow(workflow_dict)
            
            logger.info(f"Retrieved workflow '{workflow.name}' from {file_path}")
            return workflow
        except Exception as e:
            logger.error(f"Error getting workflow '{workflow_id}': {e}")
            raise RepositoryError(f"Failed to get workflow: {e}")
    
    def list(self) -> List[Workflow]:
        """
        List all workflows.
        
        Returns:
            List of all workflows.
            
        Raises:
            RepositoryError: If the workflows could not be listed.
        """
        try:
            workflows = []
            
            # Get all JSON files in the directory
            for filename in os.listdir(self.directory_path):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.directory_path, filename)
                    
                    try:
                        # Read from file
                        with open(file_path, 'r') as f:
                            workflow_dict = json.load(f)
                        
                        # Convert dictionary to workflow
                        workflow = self._dict_to_workflow(workflow_dict)
                        
                        # Add to list
                        workflows.append(workflow)
                    except Exception as e:
                        logger.warning(f"Error reading workflow from {file_path}: {e}")
                        # Continue with next file
            
            logger.info(f"Listed {len(workflows)} workflows from {self.directory_path}")
            return workflows
        except Exception as e:
            logger.error(f"Error listing workflows: {e}")
            raise RepositoryError(f"Failed to list workflows: {e}")
    
    def delete(self, workflow_id: str) -> None:
        """
        Delete a workflow by ID.
        
        Args:
            workflow_id: The ID of the workflow to delete.
            
        Raises:
            RepositoryError: If the workflow could not be deleted.
        """
        try:
            # Create file path
            file_path = os.path.join(self.directory_path, f"{workflow_id}.json")
            
            # Check if file exists
            if not os.path.exists(file_path):
                logger.info(f"Workflow not found for deletion: {workflow_id}")
                return
            
            # Delete file
            os.remove(file_path)
            
            logger.info(f"Deleted workflow: {workflow_id}")
        except Exception as e:
            logger.error(f"Error deleting workflow '{workflow_id}': {e}")
            raise RepositoryError(f"Failed to delete workflow: {e}")
    
    def _workflow_to_dict(self, workflow: Workflow) -> Dict[str, Any]:
        """
        Convert a workflow to a dictionary for serialization.
        
        Args:
            workflow: The workflow to convert.
            
        Returns:
            Dictionary representation of the workflow.
        """
        return {
            "id": workflow.id,
            "name": workflow.name,
            "description": workflow.description,
            "actions": [action.to_dict() for action in workflow.actions]
        }
    
    def _dict_to_workflow(self, workflow_dict: Dict[str, Any]) -> Workflow:
        """
        Convert a dictionary to a workflow.
        
        Args:
            workflow_dict: Dictionary representation of the workflow.
            
        Returns:
            The workflow.
        """
        from src.core.actions.factory import ActionFactory
        
        # Create workflow
        workflow = Workflow(
            id=workflow_dict.get("id"),
            name=workflow_dict.get("name", ""),
            description=workflow_dict.get("description", ""),
            actions=[]
        )
        
        # Add actions
        for action_dict in workflow_dict.get("actions", []):
            try:
                action = ActionFactory.create_action(action_dict)
                workflow.actions.append(action)
            except Exception as e:
                logger.warning(f"Error creating action for workflow '{workflow.name}': {e}")
                # Continue with next action
        
        return workflow
