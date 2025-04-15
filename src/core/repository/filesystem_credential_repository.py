"""File system implementation of credential repository."""

import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Any

from src.core.interfaces.repository import ICredentialRepository
from src.core.security.encryption import IEncryptionService
from src.core.exceptions import RepositoryError


logger = logging.getLogger(__name__)


class FileSystemCredentialRepository(ICredentialRepository):
    """
    Implementation of ICredentialRepository that stores credentials in the filesystem.
    
    This implementation stores each credential as a separate JSON file, with the
    password field encrypted using the provided encryption service.
    """
    
    def __init__(self, base_dir: str, encryption_service: IEncryptionService):
        """
        Initialize the repository with a base directory and encryption service.
        
        Args:
            base_dir: The base directory where credentials will be stored
            encryption_service: Service used to encrypt/decrypt sensitive data
            
        Raises:
            ValueError: If encryption_service is None
        """
        if encryption_service is None:
            raise ValueError("Encryption service is required for credential repository")
        
        self._encryption_service = encryption_service
        self._base_dir = Path(base_dir)
        self._credentials_dir = self._base_dir / "credentials"
        
        # Ensure directories exist
        self._credentials_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Initialized credential repository at {self._credentials_dir}")
    
    def save(self, credential: Dict[str, str]) -> None:
        """
        Save (create or update) a credential.
        
        Args:
            credential: Dictionary containing credential data with 'name', 'username', 
                       and 'password' fields
                       
        Raises:
            RepositoryError: If saving fails due to validation or IO errors
        """
        # Validate required fields
        if not self._validate_credential_data(credential):
            raise RepositoryError("Credential data is missing required fields")
        
        try:
            # Create a copy to avoid modifying the original
            cred_to_save = credential.copy()
            
            # Encrypt the password
            try:
                cred_to_save["password"] = self._encryption_service.encrypt(credential["password"])
            except Exception as e:
                logger.error(f"Failed to encrypt password for credential '{credential['name']}': {e}")
                raise RepositoryError(f"Failed to encrypt password: {e}")
            
            # Save to file
            file_path = self._get_credential_path(credential["name"])
            with open(file_path, 'w') as f:
                json.dump(cred_to_save, f, indent=2)
                
            logger.info(f"Saved credential '{credential['name']}'")
            
        except PermissionError as e:
            logger.error(f"Permission denied when saving credential '{credential['name']}': {e}")
            raise RepositoryError(f"Permission denied when saving credential: {e}")
        except IOError as e:
            logger.error(f"IO error when saving credential '{credential['name']}': {e}")
            raise RepositoryError(f"Failed to save credential: {e}")
    
    def get_by_name(self, name: str) -> Optional[Dict[str, str]]:
        """
        Get credential details by name.
        
        Args:
            name: The name of the credential to retrieve
            
        Returns:
            A dictionary with credential details or None if not found
        """
        file_path = self._get_credential_path(name)
        
        if not file_path.exists():
            logger.debug(f"Credential '{name}' not found")
            return None
        
        try:
            with open(file_path, 'r') as f:
                credential = json.load(f)
            
            # Decrypt the password
            try:
                credential["password"] = self._encryption_service.decrypt(credential["password"])
            except Exception as e:
                logger.error(f"Failed to decrypt password for credential '{name}': {e}")
                return None
                
            logger.debug(f"Retrieved credential '{name}'")
            return credential
            
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Error reading credential '{name}': {e}")
            return None
    
    def delete(self, name: str) -> bool:
        """
        Delete a credential by name.
        
        Args:
            name: The name of the credential to delete
            
        Returns:
            True if deleted, False if not found
        """
        file_path = self._get_credential_path(name)
        
        if not file_path.exists():
            logger.debug(f"Cannot delete credential '{name}': not found")
            return False
        
        try:
            os.remove(file_path)
            logger.info(f"Deleted credential '{name}'")
            return True
        except (IOError, PermissionError) as e:
            logger.error(f"Error deleting credential '{name}': {e}")
            return False
    
    def list_credentials(self) -> List[str]:
        """
        List the names of all stored credentials.
        
        Returns:
            A list of credential names
        """
        credentials = []
        
        try:
            # List all JSON files in the credentials directory
            for file_path in self._credentials_dir.glob("*.json"):
                # Extract the name (filename without .json extension)
                name = file_path.stem
                credentials.append(name)
                
            logger.debug(f"Listed {len(credentials)} credentials")
            return sorted(credentials)
            
        except IOError as e:
            logger.error(f"Error listing credentials: {e}")
            return []
    
    def _validate_credential_data(self, credential: Dict[str, Any]) -> bool:
        """
        Validate that credential data contains all required fields.
        
        Args:
            credential: The credential data to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ["name", "username", "password"]
        return all(field in credential and credential[field] for field in required_fields)
    
    def _get_credential_path(self, name: str) -> Path:
        """
        Get the file path for a credential.
        
        Args:
            name: The name of the credential
            
        Returns:
            Path object for the credential file
        """
        return self._credentials_dir / f"{name}.json"
