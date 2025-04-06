"""Credential service interface for AutoQliq.

This module defines the interface for credential management services that coordinate
between the core domain and infrastructure layers, implementing credential-related use cases.
"""
import abc
from typing import Dict, List


class ICredentialService(abc.ABC):
    """Interface for credential management services.
    
    This interface defines the contract for services that manage credentials,
    including creating, updating, deleting, and retrieving credentials.
    """
    
    @abc.abstractmethod
    def create_credential(self, name: str, username: str, password: str) -> bool:
        """Create a new credential.
        
        Args:
            name: The name of the credential
            username: The username
            password: The password
            
        Returns:
            True if the credential was created successfully
            
        Raises:
            CredentialError: If there is an error creating the credential
        """
        pass
    
    @abc.abstractmethod
    def delete_credential(self, name: str) -> bool:
        """Delete a credential.
        
        Args:
            name: The name of the credential to delete
            
        Returns:
            True if the credential was deleted successfully
            
        Raises:
            CredentialError: If there is an error deleting the credential
        """
        pass
    
    @abc.abstractmethod
    def get_credential(self, name: str) -> Dict[str, str]:
        """Get a credential by name.
        
        Args:
            name: The name of the credential to get
            
        Returns:
            A dictionary containing the credential information
            
        Raises:
            CredentialError: If there is an error retrieving the credential
        """
        pass
    
    @abc.abstractmethod
    def list_credentials(self) -> List[str]:
        """Get a list of available credentials.
        
        Returns:
            A list of credential names
            
        Raises:
            CredentialError: If there is an error retrieving the credential list
        """
        pass