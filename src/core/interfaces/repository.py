################################################################################
"""Repository interfaces for AutoQliq.

This module defines the interfaces for repository implementations that provide
storage and retrieval capabilities for workflows and credentials.
"""
import abc
from typing import List, Dict, Any, Optional

# Assuming IAction is defined elsewhere
from src.core.interfaces.action import IAction


class IWorkflowRepository(abc.ABC):
    """Interface for workflow repository implementations."""

    # --- Workflow Operations ---
    @abc.abstractmethod
    def save(self, name: str, workflow_actions: List[IAction]) -> None:
        """Save (create or update) a workflow."""
        pass

    @abc.abstractmethod
    def load(self, name: str) -> List[IAction]:
        """Load a workflow by name. Raises RepositoryError if not found."""
        pass

    @abc.abstractmethod
    def delete(self, name: str) -> bool:
        """Delete a workflow by name. Returns True if deleted, False if not found."""
        pass

    @abc.abstractmethod
    def list_workflows(self) -> List[str]:
        """List the names of all workflows."""
        pass

    @abc.abstractmethod
    def get_metadata(self, name: str) -> Dict[str, Any]:
        """Get metadata for a workflow (e.g., created_at, modified_at). Raises RepositoryError if not found."""
        pass

    @abc.abstractmethod
    def create_workflow(self, name: str) -> None:
        """Create a new, empty workflow entry. Raises RepositoryError if name exists."""
        pass

    # --- Template Operations (New) ---
    @abc.abstractmethod
    def save_template(self, name: str, actions_data: List[Dict[str, Any]]) -> None:
        """Save (create or update) an action template. Stores serialized action data."""
        pass

    @abc.abstractmethod
    def load_template(self, name: str) -> List[Dict[str, Any]]:
        """Load the serialized action data for a template by name. Raises RepositoryError if not found."""
        pass

    @abc.abstractmethod
    def delete_template(self, name: str) -> bool:
        """Delete a template by name. Returns True if deleted, False if not found."""
        pass

    @abc.abstractmethod
    def list_templates(self) -> List[str]:
        """List the names of all saved templates."""
        pass


class ICredentialRepository(abc.ABC):
    """Interface for credential repository implementations."""

    @abc.abstractmethod
    def save(self, credential: Dict[str, str]) -> None:
        """Save (create or update) a credential. Assumes value for 'password' is prepared (e.g., hashed)."""
        pass

    @abc.abstractmethod
    def get_by_name(self, name: str) -> Optional[Dict[str, str]]:
        """Get credential details (including stored password/hash) by name."""
        pass

    @abc.abstractmethod
    def delete(self, name: str) -> bool:
        """Delete a credential by name. Returns True if deleted, False if not found."""
        pass

    @abc.abstractmethod
    def list_credentials(self) -> List[str]:
        """List the names of all stored credentials."""
        pass

# --- New Reporting Repository Interface ---
class IReportingRepository(abc.ABC):
    """Interface for storing and retrieving workflow execution logs/results."""

    @abc.abstractmethod
    def save_execution_log(self, execution_log: Dict[str, Any]) -> None:
        """Saves the results and metadata of a single workflow execution."""
        pass

    @abc.abstractmethod
    def get_execution_log(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves the log data for a specific execution ID."""
        pass

    @abc.abstractmethod
    def list_execution_summaries(self, workflow_name: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Lists summary information (ID, name, start time, status, duration) for past executions."""
        pass

    # Optional: Methods for querying based on date range, status, etc.
    # Optional: Method for cleaning up old logs

################################################################################