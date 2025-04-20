"""Service interfaces for AutoQliq.

This module defines the interfaces for application services that orchestrate
domain operations between the UI and core layers.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from src.core.workflow.workflow_entity import Workflow
from src.core.credentials import Credential
from src.core.action_result import ActionResult

class IWorkflowService(ABC):
    """Contract for workflow management operations."""
    
    @abstractmethod
    def create(self, name: str, description: str = "") -> Workflow:
        """Create a new workflow with the given name and description."""
        pass
    
    @abstractmethod
    def save(self, workflow: Workflow) -> None:
        """Save an existing workflow."""
        pass
    
    @abstractmethod
    def get(self, workflow_id: str) -> Optional[Workflow]:
        """Get a workflow by ID."""
        pass
    
    @abstractmethod
    def list(self) -> List[Workflow]:
        """List all workflows."""
        pass
    
    @abstractmethod
    def delete(self, workflow_id: str) -> None:
        """Delete a workflow by ID."""
        pass

class ICredentialService(ABC):
    """Contract for credential management operations."""
    
    @abstractmethod
    def save(self, credential: Credential) -> None:
        """Save an existing credential."""
        pass
    
    @abstractmethod
    def get(self, name: str) -> Optional[Credential]:
        """Get a credential by name."""
        pass
    
    @abstractmethod
    def list(self) -> List[Credential]:
        """List all credentials."""
        pass
    
    @abstractmethod
    def delete(self, name: str) -> None:
        """Delete a credential by name."""
        pass

class IExecutionService(ABC):
    """Contract for workflow execution operations."""
    
    @abstractmethod
    def run_workflow(self, workflow_id: str) -> List[ActionResult]:
        """Execute a workflow by ID."""
        pass
