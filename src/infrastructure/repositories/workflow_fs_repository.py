"""File system implementation of the workflow repository."""

import os
import json
import logging
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime

from src.core.exceptions import RepositoryError, ValidationError
from src.core.interfaces import IWorkflowRepository
from src.core.workflow.workflow_entity import Workflow
from src.infrastructure.common.file_locking import LockedFile

logger = logging.getLogger(__name__)


class WorkflowFSRepository(IWorkflowRepository):
    """
    File system implementation of the workflow repository.
    
    This repository stores workflows as JSON files in a directory.
    Each workflow is stored in a separate file named {workflow_id}.json.
    """
    
    def __init__(self, directory_path: str, create_if_missing: bool = False):
        """
        Initialize the repository.
        
        Args:
            directory_path: Path to the directory where workflows are stored
            create_if_missing: Whether to create the directory if it doesn't exist
            
        Raises:
            RepositoryError: If the directory doesn't exist and create_if_missing is False
        """
        self.directory_path = os.path.abspath(directory_path)
        
        if not os.path.exists(self.directory_path):
            if create_if_missing:
                try:
                    os.makedirs(self.directory_path, exist_ok=True)
                    logger.info(f"Created workflow directory: {self.directory_path}")
                except Exception as e:
                    raise RepositoryError(
                        f"Failed to create workflow directory: {e}",
                        repository_name="WorkflowFSRepository",
                        cause=e
                    ) from e
            else:
                raise RepositoryError(
                    f"Workflow directory does not exist: {self.directory_path}",
                    repository_name="WorkflowFSRepository"
                )
        
        logger.debug(f"Initialized WorkflowFSRepository with directory: {self.directory_path}")
    
    def _get_file_path(self, workflow_id: str) -> str:
        """
        Get the file path for a workflow.
        
        Args:
            workflow_id: The workflow ID
            
        Returns:
            The file path
            
        Raises:
            ValidationError: If the workflow ID is invalid
        """
        if not workflow_id:
            raise ValidationError("Workflow ID cannot be empty", field_name="workflow_id")
        
        # Sanitize the workflow ID to ensure it's a valid filename
        sanitized_id = workflow_id.replace("/", "_").replace("\\", "_")
        
        return os.path.join(self.directory_path, f"{sanitized_id}.json")
    
    def _serialize_workflow(self, workflow: Workflow) -> Dict[str, Any]:
        """
        Serialize a workflow to a dictionary.
        
        Args:
            workflow: The workflow to serialize
            
        Returns:
            The serialized workflow
            
        Raises:
            RepositoryError: If the workflow cannot be serialized
        """
        try:
            return {
                "id": workflow.id,
                "name": workflow.name,
                "description": workflow.description,
                "created_at": workflow.created_at.isoformat() if workflow.created_at else None,
                "updated_at": workflow.updated_at.isoformat() if workflow.updated_at else None,
                "actions": [action.to_dict() for action in workflow.actions]
            }
        except Exception as e:
            raise RepositoryError(
                f"Failed to serialize workflow: {e}",
                repository_name="WorkflowFSRepository",
                entity_id=workflow.id,
                cause=e
            ) from e
    
    def _deserialize_workflow(self, data: Dict[str, Any]) -> Workflow:
        """
        Deserialize a workflow from a dictionary.
        
        Args:
            data: The serialized workflow
            
        Returns:
            The deserialized workflow
            
        Raises:
            RepositoryError: If the workflow cannot be deserialized
        """
        try:
            from src.core.actions.factory import ActionFactory
            
            # Create the workflow
            workflow = Workflow(
                id=data.get("id", str(uuid.uuid4())),
                name=data.get("name", ""),
                description=data.get("description", "")
            )
            
            # Set the timestamps
            if data.get("created_at"):
                workflow.created_at = datetime.fromisoformat(data["created_at"])
            if data.get("updated_at"):
                workflow.updated_at = datetime.fromisoformat(data["updated_at"])
            
            # Add the actions
            for action_data in data.get("actions", []):
                action = ActionFactory.create_from_dict(action_data)
                workflow.add_action(action)
            
            return workflow
        except Exception as e:
            raise RepositoryError(
                f"Failed to deserialize workflow: {e}",
                repository_name="WorkflowFSRepository",
                entity_id=data.get("id", "unknown"),
                cause=e
            ) from e
    
    def save(self, workflow: Workflow) -> None:
        """
        Save a workflow to the repository.
        
        Args:
            workflow: The workflow to save
            
        Raises:
            RepositoryError: If the workflow cannot be saved
            ValidationError: If the workflow is invalid
        """
        if not workflow:
            raise ValidationError("Workflow cannot be None", field_name="workflow")
        
        if not workflow.id:
            workflow.id = str(uuid.uuid4())
        
        # Update the updated_at timestamp
        workflow.updated_at = datetime.now()
        
        # Set the created_at timestamp if it doesn't exist
        if not workflow.created_at:
            workflow.created_at = workflow.updated_at
        
        # Serialize the workflow
        data = self._serialize_workflow(workflow)
        
        # Save the workflow to a file
        file_path = self._get_file_path(workflow.id)
        
        try:
            with LockedFile(file_path, "w") as f:
                json.dump(data, f, indent=2)
            
            logger.debug(f"Saved workflow {workflow.id} to {file_path}")
        except Exception as e:
            raise RepositoryError(
                f"Failed to save workflow: {e}",
                repository_name="WorkflowFSRepository",
                entity_id=workflow.id,
                cause=e
            ) from e
    
    def get(self, workflow_id: str) -> Optional[Workflow]:
        """
        Get a workflow from the repository.
        
        Args:
            workflow_id: The workflow ID
            
        Returns:
            The workflow, or None if it doesn't exist
            
        Raises:
            RepositoryError: If the workflow cannot be retrieved
            ValidationError: If the workflow ID is invalid
        """
        file_path = self._get_file_path(workflow_id)
        
        if not os.path.exists(file_path):
            logger.debug(f"Workflow {workflow_id} not found at {file_path}")
            return None
        
        try:
            with LockedFile(file_path, "r") as f:
                data = json.load(f)
            
            workflow = self._deserialize_workflow(data)
            logger.debug(f"Retrieved workflow {workflow_id} from {file_path}")
            return workflow
        except Exception as e:
            raise RepositoryError(
                f"Failed to get workflow: {e}",
                repository_name="WorkflowFSRepository",
                entity_id=workflow_id,
                cause=e
            ) from e
    
    def list(self) -> List[Workflow]:
        """
        List all workflows in the repository.
        
        Returns:
            A list of workflows
            
        Raises:
            RepositoryError: If the workflows cannot be listed
        """
        workflows = []
        
        try:
            # Get all JSON files in the directory
            for filename in os.listdir(self.directory_path):
                if filename.endswith(".json"):
                    # Extract the workflow ID from the filename
                    workflow_id = filename[:-5]  # Remove the .json extension
                    
                    # Get the workflow
                    workflow = self.get(workflow_id)
                    if workflow:
                        workflows.append(workflow)
            
            logger.debug(f"Listed {len(workflows)} workflows from {self.directory_path}")
            return workflows
        except Exception as e:
            raise RepositoryError(
                f"Failed to list workflows: {e}",
                repository_name="WorkflowFSRepository",
                cause=e
            ) from e
    
    def delete(self, workflow_id: str) -> None:
        """
        Delete a workflow from the repository.
        
        Args:
            workflow_id: The workflow ID
            
        Raises:
            RepositoryError: If the workflow cannot be deleted
            ValidationError: If the workflow ID is invalid
        """
        file_path = self._get_file_path(workflow_id)
        
        if not os.path.exists(file_path):
            logger.debug(f"Workflow {workflow_id} not found at {file_path}")
            return
        
        try:
            os.remove(file_path)
            logger.debug(f"Deleted workflow {workflow_id} from {file_path}")
        except Exception as e:
            raise RepositoryError(
                f"Failed to delete workflow: {e}",
                repository_name="WorkflowFSRepository",
                entity_id=workflow_id,
                cause=e
            ) from e
