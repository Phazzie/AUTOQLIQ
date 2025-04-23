"""DEPRECATED: Repository interfaces for AutoQliq.

This module is DEPRECATED and will be removed in a future release.
Use the new interfaces in src/core/interfaces/repository/ instead.

This module defines the interfaces for repository operations.
"""

from abc import ABC, abstractmethod
import warnings
from typing import List, Optional, TypeVar, Generic

# Use type hints without direct imports to avoid circular dependencies
T = TypeVar('T')  # Generic type for entities
W = TypeVar('W')  # Specific type for Workflow
C = TypeVar('C')  # Specific type for Credentials

def _deprecated(cls):
    warnings.warn(
        f"{cls.__name__} is deprecated. Use the new interfaces in src.core.interfaces.repository instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return cls


@_deprecated
class IRepository(Generic[T], ABC):
    """DEPRECATED: Interface for basic repository operations.

    This interface is deprecated and will be removed in a future release.
    Use src.core.interfaces.repository.IBaseRepository instead.
    """

    @abstractmethod
    def save(self, entity_id: str, entity: T) -> None:
        """
        Save an entity to the repository.

        Args:
            entity_id (str): ID of the entity
            entity (T): Entity to save

        Raises:
            ValidationError: If the entity ID is invalid
            RepositoryError: If the operation fails
        """
        pass

    @abstractmethod
    def get(self, entity_id: str) -> Optional[T]:
        """
        Get an entity from the repository.

        Args:
            entity_id (str): ID of the entity

        Returns:
            Optional[T]: The entity if found, None otherwise

        Raises:
            ValidationError: If the entity ID is invalid
            RepositoryError: If the operation fails
        """
        pass

    @abstractmethod
    def delete(self, entity_id: str) -> None:
        """
        Delete an entity from the repository.

        Args:
            entity_id (str): ID of the entity

        Raises:
            ValidationError: If the entity ID is invalid
            RepositoryError: If the operation fails
        """
        pass

    @abstractmethod
    def list(self) -> List[str]:
        """
        List all entity IDs in the repository.

        Returns:
            List[str]: List of entity IDs

        Raises:
            RepositoryError: If the operation fails
        """
        pass


@_deprecated
class IWorkflowRepository(IRepository[W]):
    """DEPRECATED: Interface for workflow repository operations.

    This interface is deprecated and will be removed in a future release.
    Use src.core.interfaces.repository.IWorkflowRepository instead.
    """

    @abstractmethod
    def save(self, workflow_id: str, workflow: W) -> None:
        """
        Save a workflow to the repository.

        Args:
            workflow_id (str): ID of the workflow
            workflow (Workflow): Workflow to save

        Raises:
            ValidationError: If the workflow ID is invalid
            RepositoryError: If the operation fails
        """
        pass

    @abstractmethod
    def get(self, workflow_id: str) -> Optional[W]:
        """
        Get a workflow from the repository.

        Args:
            workflow_id (str): ID of the workflow

        Returns:
            Optional[Workflow]: The workflow if found, None otherwise

        Raises:
            ValidationError: If the workflow ID is invalid
            RepositoryError: If the operation fails
        """
        pass


@_deprecated
class ICredentialRepository(IRepository[C]):
    """DEPRECATED: Interface for credential repository operations.

    This interface is deprecated and will be removed in a future release.
    Use src.core.interfaces.repository.ICredentialRepository instead.
    """

    @abstractmethod
    def save(self, credential: C) -> None:
        """
        Save credentials to the repository.

        Args:
            credential (Credentials): Credential object to save

        Raises:
            ValidationError: If the credentials are invalid
            RepositoryError: If the operation fails
        """
        pass

    @abstractmethod
    def get(self, name: str) -> Optional[C]:
        """
        Get credentials from the repository by name.

        Args:
            name (str): Name of the credentials to get

        Returns:
            Optional[Credentials]: The credentials if found, None otherwise

        Raises:
            ValidationError: If the name is invalid
            RepositoryError: If the operation fails
        """
        pass

    @abstractmethod
    def list(self) -> List[C]:
        """
        List all credentials in the repository.

        Returns:
            List[Credentials]: List of credentials

        Raises:
            RepositoryError: If the operation fails
        """
        pass