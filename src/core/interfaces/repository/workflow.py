"""Workflow repository interface for AutoQliq.

This module defines the workflow repository interface that all workflow
repository implementations must adhere to. It extends the base repository
interface with workflow-specific operations.

IMPORTANT: This is the new consolidated repository interface. Use this
instead of the deprecated interfaces in repository.py and repository_interfaces.py.
"""

from abc import abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from src.core.interfaces.repository.base import IBaseRepository

# Use TYPE_CHECKING to avoid circular imports
if TYPE_CHECKING:
    from src.core.interfaces.action import IAction
    from src.core.workflow.workflow_entity import Workflow

class IWorkflowRepository(IBaseRepository["Workflow"]):
    """Interface for workflow repository implementations.
    
    This interface extends the base repository interface with workflow-specific
    operations. It provides methods for managing workflows and templates.
    
    All workflow repository implementations should inherit from this interface
    to ensure a consistent API across the application.
    """
    
    @abstractmethod
    def save(self, workflow: "Workflow") -> None:
        """Save a workflow to the repository.
        
        This method overrides the base save method to accept a Workflow object
        directly instead of requiring a separate entity_id parameter.
        
        Args:
            workflow: The workflow to save
            
        Raises:
            ValidationError: If the workflow is invalid
            RepositoryError: If the operation fails
        """
        pass
    
    @abstractmethod
    def get(self, workflow_id: str) -> Optional["Workflow"]:
        """Get a workflow from the repository by ID.
        
        Args:
            workflow_id: Unique identifier for the workflow
            
        Returns:
            The workflow if found, None otherwise
            
        Raises:
            ValidationError: If the workflow ID is invalid
            RepositoryError: If the operation fails
        """
        pass
    
    @abstractmethod
    def get_by_name(self, name: str) -> Optional["Workflow"]:
        """Get a workflow from the repository by name.
        
        Args:
            name: Name of the workflow
            
        Returns:
            The workflow if found, None otherwise
            
        Raises:
            ValidationError: If the name is invalid
            RepositoryError: If the operation fails
        """
        pass
    
    @abstractmethod
    def get_metadata(self, workflow_id: str) -> Dict[str, Any]:
        """Get metadata for a workflow.
        
        Args:
            workflow_id: Unique identifier for the workflow
            
        Returns:
            Dictionary containing workflow metadata (created_at, updated_at, etc.)
            
        Raises:
            ValidationError: If the workflow ID is invalid
            RepositoryError: If the operation fails or the workflow is not found
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def list_workflows(self) -> List[Dict[str, Any]]:
        """List all workflows with basic metadata.
        
        Returns:
            List of dictionaries containing workflow ID, name, and creation date
            
        Raises:
            RepositoryError: If the operation fails
        """
        pass
    
    # Template operations
    
    @abstractmethod
    def save_template(self, name: str, actions: List["IAction"]) -> None:
        """Save a template to the repository.
        
        Args:
            name: Name of the template
            actions: List of actions in the template
            
        Raises:
            ValidationError: If the name or actions are invalid
            RepositoryError: If the operation fails
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def list_templates(self) -> List[str]:
        """List all template names in the repository.
        
        Returns:
            List of template names
            
        Raises:
            RepositoryError: If the operation fails
        """
        pass
