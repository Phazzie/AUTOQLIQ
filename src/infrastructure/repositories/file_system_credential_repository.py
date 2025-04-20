"""File system implementation of the credential repository.

This module provides a file system-based implementation of the ICredentialRepository interface.
"""

import json
import os
import logging
from typing import List, Optional, Dict, Any

from src.core.credentials import Credential
from src.core.interfaces import ICredentialRepository
from src.core.exceptions import RepositoryError

logger = logging.getLogger(__name__)

class FileSystemCredentialRepository(ICredentialRepository):
    """
    File system implementation of the credential repository.
    
    Stores credentials as JSON files in a specified directory.
    """
    
    def __init__(self, directory_path: str):
        """
        Initialize the repository with the directory path.
        
        Args:
            directory_path: Path to the directory where credentials will be stored.
        """
        self.directory_path = directory_path
        
        # Create directory if it doesn't exist
        os.makedirs(self.directory_path, exist_ok=True)
        
        logger.debug(f"FileSystemCredentialRepository initialized with directory: {directory_path}")
    
    def save(self, credential: Credential) -> None:
        """
        Save a credential to the file system.
        
        Args:
            credential: The credential to save.
            
        Raises:
            RepositoryError: If the credential could not be saved.
        """
        try:
            # Convert credential to dictionary
            credential_dict = self._credential_to_dict(credential)
            
            # Create file path (use name as filename)
            file_path = os.path.join(self.directory_path, f"{credential.name}.json")
            
            # Write to file
            with open(file_path, 'w') as f:
                json.dump(credential_dict, f, indent=2)
            
            logger.info(f"Saved credential '{credential.name}' to {file_path}")
        except Exception as e:
            logger.error(f"Error saving credential '{credential.name}': {e}")
            raise RepositoryError(f"Failed to save credential: {e}")
    
    def get(self, name: str) -> Optional[Credential]:
        """
        Get a credential by name.
        
        Args:
            name: The name of the credential to get.
            
        Returns:
            The credential, or None if not found.
            
        Raises:
            RepositoryError: If the credential could not be retrieved.
        """
        try:
            # Create file path
            file_path = os.path.join(self.directory_path, f"{name}.json")
            
            # Check if file exists
            if not os.path.exists(file_path):
                logger.info(f"Credential not found: {name}")
                return None
            
            # Read from file
            with open(file_path, 'r') as f:
                credential_dict = json.load(f)
            
            # Convert dictionary to credential
            credential = self._dict_to_credential(credential_dict)
            
            logger.info(f"Retrieved credential '{credential.name}' from {file_path}")
            return credential
        except Exception as e:
            logger.error(f"Error getting credential '{name}': {e}")
            raise RepositoryError(f"Failed to get credential: {e}")
    
    def list(self) -> List[Credential]:
        """
        List all credentials.
        
        Returns:
            List of all credentials.
            
        Raises:
            RepositoryError: If the credentials could not be listed.
        """
        try:
            credentials = []
            
            # Get all JSON files in the directory
            for filename in os.listdir(self.directory_path):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.directory_path, filename)
                    
                    try:
                        # Read from file
                        with open(file_path, 'r') as f:
                            credential_dict = json.load(f)
                        
                        # Convert dictionary to credential
                        credential = self._dict_to_credential(credential_dict)
                        
                        # Add to list
                        credentials.append(credential)
                    except Exception as e:
                        logger.warning(f"Error reading credential from {file_path}: {e}")
                        # Continue with next file
            
            logger.info(f"Listed {len(credentials)} credentials from {self.directory_path}")
            return credentials
        except Exception as e:
            logger.error(f"Error listing credentials: {e}")
            raise RepositoryError(f"Failed to list credentials: {e}")
    
    def delete(self, name: str) -> None:
        """
        Delete a credential by name.
        
        Args:
            name: The name of the credential to delete.
            
        Raises:
            RepositoryError: If the credential could not be deleted.
        """
        try:
            # Create file path
            file_path = os.path.join(self.directory_path, f"{name}.json")
            
            # Check if file exists
            if not os.path.exists(file_path):
                logger.info(f"Credential not found for deletion: {name}")
                return
            
            # Delete file
            os.remove(file_path)
            
            logger.info(f"Deleted credential: {name}")
        except Exception as e:
            logger.error(f"Error deleting credential '{name}': {e}")
            raise RepositoryError(f"Failed to delete credential: {e}")
    
    def _credential_to_dict(self, credential: Credential) -> Dict[str, Any]:
        """
        Convert a credential to a dictionary for serialization.
        
        Args:
            credential: The credential to convert.
            
        Returns:
            Dictionary representation of the credential.
        """
        return {
            "name": credential.name,
            "username": credential.username,
            "password": credential.password
        }
    
    def _dict_to_credential(self, credential_dict: Dict[str, Any]) -> Credential:
        """
        Convert a dictionary to a credential.
        
        Args:
            credential_dict: Dictionary representation of the credential.
            
        Returns:
            The credential.
        """
        return Credential(
            name=credential_dict.get("name", ""),
            username=credential_dict.get("username", ""),
            password=credential_dict.get("password", "")
        )
