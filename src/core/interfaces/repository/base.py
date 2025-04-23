"""Base repository interface for AutoQliq.

This module defines the base repository interface that all repository
implementations must adhere to. It provides a generic contract for basic
CRUD operations on entities.

IMPORTANT: This is the new consolidated repository interface. Use this
instead of the deprecated interfaces in repository.py and repository_interfaces.py.
"""

from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar

# Type variable for entity type
T = TypeVar('T')

class IBaseRepository(Generic[T], ABC):
    """Base interface for all repository implementations.
    
    This interface defines the basic CRUD operations that all repositories
    must implement. It is generic over the entity type T.
    
    All repository implementations should inherit from this interface
    to ensure a consistent API across the application.
    """
    
    @abstractmethod
    def save(self, entity_id: str, entity: T) -> None:
        """Save an entity to the repository.
        
        Args:
            entity_id: Unique identifier for the entity
            entity: The entity to save
            
        Raises:
            ValidationError: If the entity ID or entity is invalid
            RepositoryError: If the operation fails
        """
        pass
    
    @abstractmethod
    def get(self, entity_id: str) -> Optional[T]:
        """Get an entity from the repository by ID.
        
        Args:
            entity_id: Unique identifier for the entity
            
        Returns:
            The entity if found, None otherwise
            
        Raises:
            ValidationError: If the entity ID is invalid
            RepositoryError: If the operation fails
        """
        pass
    
    @abstractmethod
    def delete(self, entity_id: str) -> bool:
        """Delete an entity from the repository by ID.
        
        Args:
            entity_id: Unique identifier for the entity
            
        Returns:
            True if the entity was deleted, False if it wasn't found
            
        Raises:
            ValidationError: If the entity ID is invalid
            RepositoryError: If the operation fails
        """
        pass
    
    @abstractmethod
    def list(self) -> List[str]:
        """List all entity IDs in the repository.
        
        Returns:
            List of entity IDs
            
        Raises:
            RepositoryError: If the operation fails
        """
        pass
