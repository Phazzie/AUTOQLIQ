"""Workflow service interface for AutoQliq.

This module defines the interface for workflow management services that coordinate
between the core domain and infrastructure layers, implementing workflow-related use cases.
"""
import abc
from typing import Dict, List, Any, Optional

from src.core.interfaces import IAction


class IWorkflowService(abc.ABC):
    """Interface for workflow management services.
    
    This interface defines the contract for services that manage workflows,
    including creating, updating, deleting, and executing workflows.
    """
    
    @abc.abstractmethod
    def create_workflow(self, name: str) -> bool:
        """Create a new empty workflow.
        
        Args:
            name: The name of the workflow to create
            
        Returns:
            True if the workflow was created successfully
            
        Raises:
            WorkflowError: If there is an error creating the workflow
        """
        pass
    
    @abc.abstractmethod
    def delete_workflow(self, name: str) -> bool:
        """Delete a workflow.
        
        Args:
            name: The name of the workflow to delete
            
        Returns:
            True if the workflow was deleted successfully
            
        Raises:
            WorkflowError: If there is an error deleting the workflow
        """
        pass
    
    @abc.abstractmethod
    def list_workflows(self) -> List[str]:
        """Get a list of available workflows.
        
        Returns:
            A list of workflow names
            
        Raises:
            WorkflowError: If there is an error retrieving the workflow list
        """
        pass
    
    @abc.abstractmethod
    def get_workflow(self, name: str) -> List[IAction]:
        """Get a workflow by name.
        
        Args:
            name: The name of the workflow to get
            
        Returns:
            The list of actions in the workflow
            
        Raises:
            WorkflowError: If there is an error retrieving the workflow
        """
        pass
    
    @abc.abstractmethod
    def save_workflow(self, name: str, actions: List[IAction]) -> bool:
        """Save a workflow.
        
        Args:
            name: The name of the workflow to save
            actions: The list of actions in the workflow
            
        Returns:
            True if the workflow was saved successfully
            
        Raises:
            WorkflowError: If there is an error saving the workflow
        """
        pass
    
    @abc.abstractmethod
    def run_workflow(self, name: str, credential_name: Optional[str] = None) -> bool:
        """Run a workflow.
        
        Args:
            name: The name of the workflow to run
            credential_name: The name of the credential to use, if any
            
        Returns:
            True if the workflow was run successfully
            
        Raises:
            WorkflowError: If there is an error running the workflow
        """
        pass
    
    @abc.abstractmethod
    def get_workflow_metadata(self, name: str) -> Dict[str, Any]:
        """Get metadata for a workflow.
        
        Args:
            name: The name of the workflow to get metadata for
            
        Returns:
            A dictionary containing workflow metadata
            
        Raises:
            WorkflowError: If there is an error retrieving the workflow metadata
        """
        pass