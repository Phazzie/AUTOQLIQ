"""Credential repository interface for AutoQliq.

This module defines the credential repository interface that all credential
repository implementations must adhere to. It extends the base repository
interface with credential-specific operations.

IMPORTANT: This is the new consolidated repository interface. Use this
instead of the deprecated interfaces in repository.py and repository_interfaces.py.
"""

from abc import abstractmethod
from typing import Dict, List, Optional, TYPE_CHECKING

from src.core.interfaces.repository.base import IBaseRepository

# Use TYPE_CHECKING to avoid circular imports
if TYPE_CHECKING:
    from src.core.credentials import Credentials

class ICredentialRepository(IBaseRepository["Credentials"]):
    """Interface for credential repository implementations.
    
    This interface extends the base repository interface with credential-specific
    operations. It provides methods for managing credentials securely.
    
    All credential repository implementations should inherit from this interface
    to ensure a consistent API across the application.
    """
    
    @abstractmethod
    def save(self, credential: "Credentials") -> None:
        """Save a credential to the repository.
        
        This method overrides the base save method to accept a Credentials object
        directly instead of requiring a separate entity_id parameter.
        
        Args:
            credential: The credential to save
            
        Raises:
            ValidationError: If the credential is invalid
            RepositoryError: If the operation fails
        """
        pass
    
    @abstractmethod
    def get(self, credential_id: str) -> Optional["Credentials"]:
        """Get a credential from the repository by ID.
        
        Args:
            credential_id: Unique identifier for the credential
            
        Returns:
            The credential if found, None otherwise
            
        Raises:
            ValidationError: If the credential ID is invalid
            RepositoryError: If the operation fails
        """
        pass
    
    @abstractmethod
    def get_by_name(self, name: str) -> Optional["Credentials"]:
        """Get a credential from the repository by name.
        
        Args:
            name: Name of the credential
            
        Returns:
            The credential if found, None otherwise
            
        Raises:
            ValidationError: If the name is invalid
            RepositoryError: If the operation fails
        """
        pass
    
    @abstractmethod
    def list_credentials(self) -> List[Dict[str, str]]:
        """List all credentials with basic information (excluding sensitive data).
        
        Returns:
            List of dictionaries containing credential ID, name, and username
            
        Raises:
            RepositoryError: If the operation fails
        """
        pass
