"""File system workflow repository implementation for AutoQliq.

This module provides a file system-based implementation of the IWorkflowRepository
interface for storing and retrieving workflows.
"""

import os
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from src.core.exceptions import RepositoryError, ValidationError, SerializationError
from src.core.interfaces.repository.workflow import IWorkflowRepository
from src.infrastructure.repositories.base.file_system_repository import FileSystemRepository

# Use TYPE_CHECKING to avoid circular imports
if TYPE_CHECKING:
    from src.core.interfaces.action import IAction
    from src.core.workflow.workflow_entity import Workflow

logger = logging.getLogger(__name__)

class FileSystemWorkflowRepository(FileSystemRepository["Workflow"], IWorkflowRepository):
    """File system implementation of the workflow repository.
    
    This class provides a file system-based implementation of the IWorkflowRepository
    interface. It stores workflows as JSON files in a directory structure.
    
    Attributes:
        base_directory (str): Base directory for storing workflow files
        templates_dir (str): Directory for storing workflow templates
    """
    
    WORKFLOW_EXTENSION = ".json"
    TEMPLATE_SUBDIR = "templates"
    
    def __init__(self, directory_path: str, create_if_missing: bool = True):
        """Initialize a new FileSystemWorkflowRepository.
        
        Args:
            directory_path: Path to the directory where workflows are stored
            create_if_missing: Whether to create the directory if it doesn't exist
                
        Raises:
            RepositoryError: If the directory cannot be created or accessed
        """
        super().__init__("workflow_repository", directory_path)
        
        # Create the templates directory
        self.templates_dir = os.path.join(self.base_directory, self.TEMPLATE_SUBDIR)
        
        if create_if_missing:
            self._ensure_directory_exists(self.base_directory)
            self._ensure_directory_exists(self.templates_dir)
            logger.info(f"Initialized workflow repository at {self.base_directory}")
        elif not os.path.exists(self.base_directory):
            raise RepositoryError(
                f"Workflow directory does not exist: {self.base_directory}",
                repository_name="WorkflowRepository"
            )
    
    def save(self, workflow: "Workflow") -> None:
        """Save a workflow to the repository.
        
        Args:
            workflow: The workflow to save
            
        Raises:
            ValidationError: If the workflow is invalid
            RepositoryError: If the operation fails
        """
        if not workflow:
            raise ValidationError("Workflow cannot be None")
        
        if not workflow.id:
            raise ValidationError("Workflow ID cannot be empty")
        
        # Update the workflow's updated_at timestamp
        workflow.updated_at = datetime.now()
        
        # If this is a new workflow, set the created_at timestamp
        if not workflow.created_at:
            workflow.created_at = workflow.updated_at
        
        # Save the workflow
        super().save(workflow.id, workflow)
    
    def get(self, workflow_id: str) -> Optional["Workflow"]:
        """Get a workflow from the repository by ID.
        
        Args:
            workflow_id: ID of the workflow to get
            
        Returns:
            The workflow if found, None otherwise
            
        Raises:
            ValidationError: If the workflow ID is invalid
            RepositoryError: If the operation fails
        """
        return super().get(workflow_id)
    
    def get_by_name(self, name: str) -> Optional["Workflow"]:
        """Get a workflow from the repository by name.
        
        Args:
            name: Name of the workflow to get
            
        Returns:
            The workflow if found, None otherwise
            
        Raises:
            ValidationError: If the name is invalid
            RepositoryError: If the operation fails
        """
        if not name:
            raise ValidationError("Workflow name cannot be empty")
        
        # List all workflows
        workflows = self.list_workflows()
        
        # Find the workflow with the given name
        for workflow_info in workflows:
            if workflow_info.get("name") == name:
                return self.get(workflow_info.get("id"))
        
        return None
    
    def get_metadata(self, workflow_id: str) -> Dict[str, Any]:
        """Get metadata for a workflow.
        
        Args:
            workflow_id: ID of the workflow
            
        Returns:
            Dictionary containing workflow metadata
            
        Raises:
            ValidationError: If the workflow ID is invalid
            RepositoryError: If the operation fails or the workflow is not found
        """
        self._validate_entity_id(workflow_id)
        
        workflow = self.get(workflow_id)
        if not workflow:
            raise RepositoryError(
                f"Workflow not found: {workflow_id}",
                repository_name="WorkflowRepository",
                entity_id=workflow_id
            )
        
        return {
            "id": workflow.id,
            "name": workflow.name,
            "description": workflow.description,
            "created_at": workflow.created_at.isoformat() if workflow.created_at else None,
            "updated_at": workflow.updated_at.isoformat() if workflow.updated_at else None,
            "action_count": len(workflow.actions) if workflow.actions else 0,
            "source": "file_system"
        }
    
    def create_empty(self, name: str) -> "Workflow":
        """Create a new empty workflow.
        
        Args:
            name: Name for the new workflow
            
        Returns:
            The newly created workflow
            
        Raises:
            ValidationError: If the name is invalid
            RepositoryError: If the operation fails or a workflow with the same name already exists
        """
        if not name:
            raise ValidationError("Workflow name cannot be empty")
        
        # Check if a workflow with this name already exists
        existing = self.get_by_name(name)
        if existing:
            raise RepositoryError(
                f"Workflow with name '{name}' already exists",
                repository_name="WorkflowRepository"
            )
        
        # Import here to avoid circular imports
        from src.core.workflow.workflow_entity import Workflow
        
        # Create a new workflow
        workflow = Workflow(
            name=name,
            description=f"Workflow created on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            actions=[]
        )
        
        # Save the workflow
        self.save(workflow)
        
        return workflow
    
    def list_workflows(self) -> List[Dict[str, Any]]:
        """List all workflows with basic metadata.
        
        Returns:
            List of dictionaries containing workflow ID, name, and creation date
            
        Raises:
            RepositoryError: If the operation fails
        """
        try:
            # Get all workflow IDs
            workflow_ids = self._list_entities()
            
            # Get metadata for each workflow
            workflows = []
            for workflow_id in workflow_ids:
                try:
                    workflow = self.get(workflow_id)
                    if workflow:
                        workflows.append({
                            "id": workflow.id,
                            "name": workflow.name,
                            "description": workflow.description,
                            "created_at": workflow.created_at.isoformat() if workflow.created_at else None,
                            "updated_at": workflow.updated_at.isoformat() if workflow.updated_at else None,
                            "action_count": len(workflow.actions) if workflow.actions else 0
                        })
                except Exception as e:
                    logger.warning(f"Error getting workflow {workflow_id}: {e}")
            
            return workflows
        except Exception as e:
            error_msg = f"Failed to list workflows: {e}"
            logger.error(error_msg)
            raise RepositoryError(error_msg, repository_name="WorkflowRepository", cause=e) from e
    
    def save_template(self, name: str, actions: List["IAction"]) -> None:
        """Save a template to the repository.
        
        Args:
            name: Name of the template
            actions: List of actions in the template
            
        Raises:
            ValidationError: If the name or actions are invalid
            RepositoryError: If the operation fails
        """
        if not name:
            raise ValidationError("Template name cannot be empty")
        
        if not actions:
            raise ValidationError("Template actions cannot be empty")
        
        try:
            # Serialize the actions
            actions_data = []
            for action in actions:
                actions_data.append(action.to_dict())
            
            # Create the template data
            template_data = {
                "name": name,
                "actions": actions_data,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            # Save the template
            template_path = os.path.join(self.templates_dir, f"{name}{self.WORKFLOW_EXTENSION}")
            self._write_json_file(template_path, template_data)
            
            logger.info(f"Saved template: {name}")
        except Exception as e:
            error_msg = f"Failed to save template {name}: {e}"
            logger.error(error_msg)
            raise RepositoryError(error_msg, repository_name="WorkflowRepository", entity_id=name, cause=e) from e
    
    def get_template(self, name: str) -> Optional[List["IAction"]]:
        """Get a template from the repository by name.
        
        Args:
            name: Name of the template
            
        Returns:
            List of actions in the template if found, None otherwise
            
        Raises:
            ValidationError: If the name is invalid
            RepositoryError: If the operation fails
        """
        if not name:
            raise ValidationError("Template name cannot be empty")
        
        try:
            # Get the template file path
            template_path = os.path.join(self.templates_dir, f"{name}{self.WORKFLOW_EXTENSION}")
            
            # Check if the template exists
            if not os.path.exists(template_path):
                logger.debug(f"Template not found: {name}")
                return None
            
            # Load the template data
            template_data = self._read_json_file(template_path)
            
            # Deserialize the actions
            actions = []
            
            # Import here to avoid circular imports
            from src.core.actions import ActionFactory
            
            for action_data in template_data.get("actions", []):
                action = ActionFactory.create_from_dict(action_data)
                actions.append(action)
            
            logger.info(f"Loaded template: {name}")
            return actions
        except FileNotFoundError:
            logger.debug(f"Template not found: {name}")
            return None
        except Exception as e:
            error_msg = f"Failed to load template {name}: {e}"
            logger.error(error_msg)
            raise RepositoryError(error_msg, repository_name="WorkflowRepository", entity_id=name, cause=e) from e
    
    def delete_template(self, name: str) -> bool:
        """Delete a template from the repository by name.
        
        Args:
            name: Name of the template
            
        Returns:
            True if the template was deleted, False if it wasn't found
            
        Raises:
            ValidationError: If the name is invalid
            RepositoryError: If the operation fails
        """
        if not name:
            raise ValidationError("Template name cannot be empty")
        
        try:
            # Get the template file path
            template_path = os.path.join(self.templates_dir, f"{name}{self.WORKFLOW_EXTENSION}")
            
            # Check if the template exists
            if not os.path.exists(template_path):
                logger.debug(f"Template not found: {name}")
                return False
            
            # Delete the template
            os.remove(template_path)
            
            logger.info(f"Deleted template: {name}")
            return True
        except FileNotFoundError:
            logger.debug(f"Template not found: {name}")
            return False
        except Exception as e:
            error_msg = f"Failed to delete template {name}: {e}"
            logger.error(error_msg)
            raise RepositoryError(error_msg, repository_name="WorkflowRepository", entity_id=name, cause=e) from e
    
    def list_templates(self) -> List[str]:
        """List all template names in the repository.
        
        Returns:
            List of template names
            
        Raises:
            RepositoryError: If the operation fails
        """
        try:
            # Get all template files
            template_files = []
            for file in os.listdir(self.templates_dir):
                if file.endswith(self.WORKFLOW_EXTENSION):
                    template_files.append(file)
            
            # Extract template names
            template_names = []
            for file in template_files:
                template_name = file[:-len(self.WORKFLOW_EXTENSION)]
                template_names.append(template_name)
            
            logger.info(f"Listed {len(template_names)} templates")
            return template_names
        except Exception as e:
            error_msg = f"Failed to list templates: {e}"
            logger.error(error_msg)
            raise RepositoryError(error_msg, repository_name="WorkflowRepository", cause=e) from e
    
    # Implementation of abstract methods from FileSystemRepository
    
    def _save_entity(self, entity_id: str, entity: "Workflow") -> None:
        """Save a workflow entity to the file system.
        
        Args:
            entity_id: ID of the workflow
            entity: Workflow to save
            
        Raises:
            RepositoryError: If the operation fails
        """
        try:
            # Serialize the workflow
            workflow_data = entity.to_dict()
            
            # Save the workflow to a file
            file_path = self._get_workflow_path(entity_id)
            self._write_json_file(file_path, workflow_data)
            
            logger.debug(f"Saved workflow {entity_id} to {file_path}")
        except Exception as e:
            error_msg = f"Failed to save workflow {entity_id}: {e}"
            logger.error(error_msg)
            raise RepositoryError(error_msg, repository_name="WorkflowRepository", entity_id=entity_id, cause=e) from e
    
    def _get_entity(self, entity_id: str) -> Optional["Workflow"]:
        """Get a workflow entity from the file system.
        
        Args:
            entity_id: ID of the workflow
            
        Returns:
            The workflow if found, None otherwise
            
        Raises:
            RepositoryError: If the operation fails
        """
        try:
            # Get the workflow file path
            file_path = self._get_workflow_path(entity_id)
            
            # Check if the workflow exists
            if not os.path.exists(file_path):
                logger.debug(f"Workflow not found: {entity_id}")
                return None
            
            # Load the workflow data
            workflow_data = self._read_json_file(file_path)
            
            # Deserialize the workflow
            from src.core.workflow.workflow_entity import Workflow
            workflow = Workflow.from_dict(workflow_data)
            
            logger.debug(f"Loaded workflow {entity_id} from {file_path}")
            return workflow
        except FileNotFoundError:
            logger.debug(f"Workflow not found: {entity_id}")
            return None
        except Exception as e:
            error_msg = f"Failed to load workflow {entity_id}: {e}"
            logger.error(error_msg)
            raise RepositoryError(error_msg, repository_name="WorkflowRepository", entity_id=entity_id, cause=e) from e
    
    def _delete_entity(self, entity_id: str) -> bool:
        """Delete a workflow entity from the file system.
        
        Args:
            entity_id: ID of the workflow
            
        Returns:
            True if the workflow was deleted, False if it wasn't found
            
        Raises:
            RepositoryError: If the operation fails
        """
        try:
            # Get the workflow file path
            file_path = self._get_workflow_path(entity_id)
            
            # Check if the workflow exists
            if not os.path.exists(file_path):
                logger.debug(f"Workflow not found: {entity_id}")
                return False
            
            # Delete the workflow
            os.remove(file_path)
            
            logger.debug(f"Deleted workflow {entity_id} from {file_path}")
            return True
        except FileNotFoundError:
            logger.debug(f"Workflow not found: {entity_id}")
            return False
        except Exception as e:
            error_msg = f"Failed to delete workflow {entity_id}: {e}"
            logger.error(error_msg)
            raise RepositoryError(error_msg, repository_name="WorkflowRepository", entity_id=entity_id, cause=e) from e
    
    def _list_entities(self) -> List[str]:
        """List all workflow IDs in the file system.
        
        Returns:
            List of workflow IDs
            
        Raises:
            RepositoryError: If the operation fails
        """
        try:
            # Get all workflow files
            workflow_files = []
            for file in os.listdir(self.base_directory):
                if file.endswith(self.WORKFLOW_EXTENSION) and os.path.isfile(os.path.join(self.base_directory, file)):
                    workflow_files.append(file)
            
            # Extract workflow IDs
            workflow_ids = []
            for file in workflow_files:
                workflow_id = file[:-len(self.WORKFLOW_EXTENSION)]
                workflow_ids.append(workflow_id)
            
            logger.debug(f"Listed {len(workflow_ids)} workflows")
            return workflow_ids
        except Exception as e:
            error_msg = f"Failed to list workflows: {e}"
            logger.error(error_msg)
            raise RepositoryError(error_msg, repository_name="WorkflowRepository", cause=e) from e
    
    # Helper methods
    
    def _get_workflow_path(self, workflow_id: str) -> str:
        """Get the file path for a workflow.
        
        Args:
            workflow_id: ID of the workflow
            
        Returns:
            Path to the workflow file
        """
        return os.path.join(self.base_directory, f"{workflow_id}{self.WORKFLOW_EXTENSION}")
