"""Repository interfaces for AutoQliq."""
from typing import Dict, List, Optional, TypeVar, Generic

# Type variable for the entity type
T = TypeVar('T')


class IReadRepository(Generic[T]):
    """Interface for read-only repositories."""

    def get(self, entity_id: str) -> Optional[T]:
        """Get an entity from the repository.
        
        Args:
            entity_id: The ID of the entity
            
        Returns:
            The entity, or None if not found
        """
        raise NotImplementedError("Subclasses must implement get")
    
    def list(self) -> List[str]:
        """List all entity IDs in the repository.
        
        Returns:
            A list of entity IDs
        """
        raise NotImplementedError("Subclasses must implement list")


class IWriteRepository(Generic[T]):
    """Interface for write-only repositories."""

    def save(self, entity_id: str, entity: T) -> None:
        """Save an entity to the repository.
        
        Args:
            entity_id: The ID of the entity
            entity: The entity to save
        """
        raise NotImplementedError("Subclasses must implement save")
    
    def delete(self, entity_id: str) -> None:
        """Delete an entity from the repository.
        
        Args:
            entity_id: The ID of the entity
        """
        raise NotImplementedError("Subclasses must implement delete")


class IRepository(IReadRepository[T], IWriteRepository[T]):
    """Interface for repositories with read and write operations."""
    pass


class ICredentialReadRepository(IReadRepository[Dict[str, str]]):
    """Interface for credential read-only repositories."""

    def get_credential(self, name: str) -> Optional[Dict[str, str]]:
        """Get a credential from the repository.
        
        Args:
            name: The name of the credential
            
        Returns:
            The credential, or None if not found
        """
        raise NotImplementedError("Subclasses must implement get_credential")
    
    def list_credentials(self) -> List[str]:
        """List all credential names in the repository.
        
        Returns:
            A list of credential names
        """
        raise NotImplementedError("Subclasses must implement list_credentials")


class ICredentialWriteRepository(IWriteRepository[Dict[str, str]]):
    """Interface for credential write-only repositories."""

    def save_credential(self, credential: Dict[str, str]) -> None:
        """Save a credential to the repository.
        
        Args:
            credential: The credential to save
        """
        raise NotImplementedError("Subclasses must implement save_credential")
    
    def delete_credential(self, name: str) -> None:
        """Delete a credential from the repository.
        
        Args:
            name: The name of the credential
        """
        raise NotImplementedError("Subclasses must implement delete_credential")


class ICredentialRepository(ICredentialReadRepository, ICredentialWriteRepository):
    """Interface for credential repositories with read and write operations."""
    pass
