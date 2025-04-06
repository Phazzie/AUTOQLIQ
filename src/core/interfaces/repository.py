"""Repository interfaces for AutoQliq.

This module defines the interfaces for repository implementations that provide
storage and retrieval capabilities for workflows and credentials.
"""
import abc
from typing import List, Dict, Any, Optional

# Assuming IAction is defined elsewhere
from src.core.interfaces.action import IAction


class IWorkflowRepository(abc.ABC):
    """Interface for workflow repository implementations.

    This interface defines the contract for repositories that store and retrieve
    workflows, which are sequences of actions.
    """

    @abc.abstractmethod
    def save(self, name: str, workflow_actions: List[IAction]) -> None:
        """Save (create or update) a workflow to the repository.

        Args:
            name: The unique name of the workflow.
            workflow_actions: The list of action instances in the workflow.

        Raises:
            RepositoryError: If the workflow cannot be saved (e.g., invalid name, storage error).
            SerializationError: If actions cannot be serialized.
            ValidationError: If the name or actions are invalid.
        """
        pass

    @abc.abstractmethod
    def load(self, name: str) -> List[IAction]:
        """Load a workflow from the repository by name.

        Args:
            name: The name of the workflow to load.

        Returns:
            The list of action instances in the workflow.

        Raises:
            RepositoryError: If the workflow is not found or cannot be loaded.
            SerializationError: If actions cannot be deserialized.
            ValidationError: If the name is invalid.
        """
        pass

    @abc.abstractmethod
    def delete(self, name: str) -> bool:
        """Delete a workflow from the repository by name.

        Args:
            name: The name of the workflow to delete.

        Returns:
            True if the workflow was deleted, False if it was not found.

        Raises:
            RepositoryError: If the workflow cannot be deleted.
            ValidationError: If the name is invalid.
        """
        pass

    @abc.abstractmethod
    def list_workflows(self) -> List[str]:
        """List the names of all workflows in the repository.

        Returns:
            A list of workflow names.

        Raises:
            RepositoryError: If the workflows cannot be listed.
        """
        pass

    @abc.abstractmethod
    def get_metadata(self, name: str) -> Dict[str, Any]:
        """Get metadata associated with a workflow (e.g., creation time, modification time).

        Args:
            name: The name of the workflow.

        Returns:
            A dictionary containing workflow metadata.

        Raises:
            RepositoryError: If the workflow is not found or metadata cannot be retrieved.
            ValidationError: If the name is invalid.
        """
        pass

    @abc.abstractmethod
    def create_workflow(self, name: str) -> None:
        """Create a new, typically empty, workflow entry.

        Useful for initializing a workflow before adding actions.
        Should fail if a workflow with the same name already exists.

        Args:
            name: The name for the new workflow.

        Raises:
            RepositoryError: If a workflow with that name already exists or creation fails.
            ValidationError: If the name is invalid.
        """
        pass


class ICredentialRepository(abc.ABC):
    """Interface for credential repository implementations.

    This interface defines the contract for repositories that store and retrieve
    credentials, typically used for authentication in workflows. Credentials are
    represented as dictionaries.
    """

    @abc.abstractmethod
    def save(self, credential: Dict[str, str]) -> None:
        """Save (create or update) a credential.

        The credential dictionary must contain at least a 'name' key, which is used
        as the unique identifier. Implementations should handle UPSERT logic.

        Args:
            credential: The credential dictionary to save (must include 'name', 'username', 'password').

        Raises:
            RepositoryError: If the credential cannot be saved (e.g., storage error).
            CredentialError: If the credential data is invalid (e.g., missing fields).
            ValidationError: If the credential name or data is invalid.
        """
        pass

    @abc.abstractmethod
    def get_by_name(self, name: str) -> Optional[Dict[str, str]]:
        """Get a credential by its unique name.

        Args:
            name: The name of the credential to retrieve.

        Returns:
            The credential dictionary if found, otherwise None.

        Raises:
            RepositoryError: If the credential cannot be retrieved due to storage errors.
            ValidationError: If the name is invalid.
        """
        pass

    @abc.abstractmethod
    def delete(self, name: str) -> bool:
        """Delete a credential by its name.

        Args:
            name: The name of the credential to delete.

        Returns:
            True if the credential was deleted, False if it was not found.

        Raises:
            RepositoryError: If the credential cannot be deleted due to storage errors.
            ValidationError: If the name is invalid.
        """
        pass

    @abc.abstractmethod
    def list_credentials(self) -> List[str]:
        """List the names of all stored credentials.

        Returns:
            A list of credential names.

        Raises:
            RepositoryError: If the credentials cannot be listed.
        """
        pass