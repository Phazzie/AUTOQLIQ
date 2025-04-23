"""Base repository abstract class for AutoQliq.

This module defines the abstract base class for all repository implementations,
providing common functionality and enforcing a consistent interface.

This class implements the IBaseRepository interface from src.core.interfaces.repository.base.
"""

import abc
import logging
from typing import TypeVar, Generic, Optional, List, Any

from src.core.exceptions import RepositoryError, ValidationError
from src.core.interfaces.repository.base import IBaseRepository
from src.infrastructure.common.logger_factory import LoggerFactory

# Type variable for the entity type managed by the repository
T = TypeVar('T')

class Repository(IBaseRepository[T], abc.ABC, Generic[T]):
    """
    Abstract base class for repository implementations.

    This class defines the common interface and behavior for all repositories
    in the system. It provides shared functionality and enforces a consistent
    approach to repository operations.

    Attributes:
        logger (logging.Logger): Logger for recording repository operations and errors
    """

    def __init__(self, logger_name: str):
        """
        Initialize a new repository instance.

        Args:
            logger_name (str): Name for the repository's logger
        """
        self.logger = logging.getLogger(logger_name)
        self.logger.info(f"Initializing {self.__class__.__name__}")

    # --- Abstract Methods ---

    @abc.abstractmethod
    def save(self, entity_id: str, entity: T) -> None:
        """
        Save an entity to the repository.

        Args:
            entity_id (str): Unique identifier for the entity
            entity (T): Entity to save

        Raises:
            RepositoryError: If the operation fails
            ValidationError: If the entity or ID is invalid
        """
        pass

    @abc.abstractmethod
    def get(self, entity_id: str) -> Optional[T]:
        """
        Get an entity from the repository by its ID.

        Args:
            entity_id (str): ID of the entity to get

        Returns:
            Optional[T]: The entity if found, None otherwise

        Raises:
            RepositoryError: If the operation fails
        """
        pass

    @abc.abstractmethod
    def delete(self, entity_id: str) -> bool:
        """
        Delete an entity from the repository.

        Args:
            entity_id (str): ID of the entity to delete

        Returns:
            bool: True if the entity was deleted, False if it wasn't found

        Raises:
            RepositoryError: If the operation fails
        """
        pass

    @abc.abstractmethod
    def list(self) -> List[str]:
        """
        List all entity IDs in the repository.

        Returns:
            List[str]: List of entity IDs

        Raises:
            RepositoryError: If the operation fails
        """
        pass

    # --- Helper Methods ---

    def _validate_entity_id(self, entity_id: str) -> None:
        """
        Validate an entity ID.

        Args:
            entity_id (str): ID to validate

        Raises:
            ValidationError: If the ID is invalid
        """
        if not entity_id:
            raise ValidationError("Entity ID cannot be empty")

        if not isinstance(entity_id, str):
            raise ValidationError(f"Entity ID must be a string, got {type(entity_id).__name__}")

        # Add additional validation rules if needed
        if len(entity_id) > 255:
            raise ValidationError("Entity ID is too long (max 255 characters)")

    def _log_operation(self, operation: str, entity_id: Optional[str] = None,
                      details: Optional[str] = None) -> None:
        """
        Log a repository operation.

        Args:
            operation (str): Name of the operation
            entity_id (Optional[str]): ID of the affected entity, if any
            details (Optional[str]): Additional operation details
        """
        message = f"{operation}"
        if entity_id:
            message += f" {entity_id}"
        if details:
            message += f": {details}"

        self.logger.info(message)