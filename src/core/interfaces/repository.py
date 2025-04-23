################################################################################
"""DEPRECATED: Repository interfaces for AutoQliq.

This module is DEPRECATED and will be removed in a future release.
Use the new interfaces in src/core/interfaces/repository/ instead.

This module defines the interfaces for repository implementations that provide
storage and retrieval capabilities for workflows and credentials.
"""
import abc
import warnings
from typing import List, Dict, Any, Optional, TYPE_CHECKING

# Use TYPE_CHECKING to avoid circular imports
if TYPE_CHECKING:
    from src.core.interfaces.action import IAction


def _deprecated(cls):
    warnings.warn(
        f"{cls.__name__} is deprecated. Use the new interfaces in src.core.interfaces.repository instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return cls


@_deprecated
class IWorkflowRepository(abc.ABC):
    """DEPRECATED: Interface for workflow repository implementations.

    This interface is deprecated and will be removed in a future release.
    Use src.core.interfaces.repository.IWorkflowRepository instead.
    """

    # --- Workflow Operations ---
    @abc.abstractmethod
    def save(self, name: str, workflow_actions: List["IAction"]) -> None:
        """Save (create or update) a workflow."""
        pass

    @abc.abstractmethod
    def load(self, name: str) -> List["IAction"]:
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


@_deprecated
class ICredentialRepository(abc.ABC):
    """DEPRECATED: Interface for credential repository implementations.

    This interface is deprecated and will be removed in a future release.
    Use src.core.interfaces.repository.ICredentialRepository instead.
    """

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
@_deprecated
class IReportingRepository(abc.ABC):
    """DEPRECATED: Interface for storing and retrieving workflow execution logs/results.

    This interface is deprecated and will be removed in a future release.
    Use src.core.interfaces.repository.IReportingRepository instead.
    """

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
