"""FileSystemCredentialRepository implementation for AutoQliq.

This module provides a file-based implementation of the ICredentialRepository interface,
with secure storage and encryption of credential information.
"""
import json
import os
import logging
from pathlib import Path
from typing import Dict, Optional, List, Any

from src.core.exceptions import RepositoryError
from src.core.interfaces.repository import ICredentialRepository
from src.core.interfaces.encryption import IEncryptionService

logger = logging.getLogger(__name__)

class FileSystemCredentialRepository(ICredentialRepository):
    """File system implementation of the credential repository.
    
    This implementation stores credentials in JSON files with encrypted 
    password values to ensure sensitive data is protected.
    """
    
    def __init__(
        self, 
        base_dir: str, 
        encryption_service: IEncryptionService
    ) -> None:
        """Initialize a new file system credential repository.
        
        Args:
            base_dir: Base directory where credentials will be stored
            encryption_service: Service used to encrypt/decrypt sensitive information
        
        Raises:
            RepositoryError: If the base directory cannot be created or accessed
        """
        self._base_dir = Path(base_dir)
        self._encryption_service = encryption_service
        
        # Create the directory if it doesn't exist
        try:
            os.makedirs(self._base_dir, exist_ok=True)
            logger.info(f"Credential repository initialized at: {self._base_dir}")
        except Exception as e:
            error_msg = f"Failed to create credential repository directory: {str(e)}"
            logger.error(error_msg)
            raise RepositoryError(error_msg) from e
    
    def _get_credential_path(self, name: str) -> Path:
        """Get the file path for a credential by name.
        
        Args:
            name: Name of the credential
            
        Returns:
            Path to the credential file
        """
        return self._base_dir / f"{name}.json"
    
    def save(self, credential: Dict[str, str]) -> None:
        """Save (create or update) a credential with encrypted password.
        
        Args:
            credential: Dictionary containing credential information
                Must include 'name' and 'password' keys
                
        Raises:
            RepositoryError: If the credential cannot be saved
            ValueError: If the credential is missing required fields
        """
        # Validate credential data
        if not credential.get("name"):
            error_msg = "Credential must have a name"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        if "password" not in credential:
            error_msg = "Credential must have a password"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        try:
            # Create a copy of the credential data
            secure_credential = credential.copy()
            
            # Encrypt the password
            plaintext_password = secure_credential["password"]
            secure_credential["password"] = self._encryption_service.encrypt(
                plaintext_password
            )
            
            # Write to file
            credential_path = self._get_credential_path(secure_credential["name"])
            with open(credential_path, "w", encoding="utf-8") as f:
                json.dump(secure_credential, f, indent=2)
                
            logger.info(f"Credential '{secure_credential['name']}' saved successfully")
        except Exception as e:
            error_msg = f"Failed to save credential: {str(e)}"
            logger.error(error_msg)
            raise RepositoryError(error_msg) from e
    
    def get_by_name(self, name: str) -> Optional[Dict[str, str]]:
        """Get credential details by name with decrypted password.
        
        Args:
            name: Name of the credential to retrieve
            
        Returns:
            Dictionary containing credential information or None if not found
            
        Raises:
            RepositoryError: If there's an error reading or decrypting the credential
        """
        credential_path = self._get_credential_path(name)
        
        if not credential_path.exists():
            logger.info(f"Credential '{name}' not found")
            return None
        
        try:
            # Read encrypted credential from file
            with open(credential_path, "r", encoding="utf-8") as f:
                secure_credential = json.load(f)
            
            # Decrypt the password
            encrypted_password = secure_credential["password"]
            secure_credential["password"] = self._encryption_service.decrypt(
                encrypted_password
            )
            
            logger.info(f"Credential '{name}' retrieved successfully")
            return secure_credential
        except Exception as e:
            error_msg = f"Failed to retrieve credential '{name}': {str(e)}"
            logger.error(error_msg)
            raise RepositoryError(error_msg) from e
    
    def delete(self, name: str) -> bool:
        """Delete a credential by name.
        
        Args:
            name: Name of the credential to delete
            
        Returns:
            True if deleted, False if not found
            
        Raises:
            RepositoryError: If there's an error deleting the credential
        """
        credential_path = self._get_credential_path(name)
        
        if not credential_path.exists():
            logger.info(f"Credential '{name}' not found, nothing to delete")
            return False
        
        try:
            os.remove(credential_path)
            logger.info(f"Credential '{name}' deleted successfully")
            return True
        except Exception as e:
            error_msg = f"Failed to delete credential '{name}': {str(e)}"
            logger.error(error_msg)
            raise RepositoryError(error_msg) from e
    
    def list_credentials(self) -> List[str]:
        """List all available credential names.
        
        Returns:
            List of credential names
            
        Raises:
            RepositoryError: If there's an error listing credentials
        """
        try:
            # Get all JSON files in the directory
            credential_files = list(self._base_dir.glob("*.json"))
            
            # Extract names (filenames without extension)
            credential_names = [file.stem for file in credential_files]
            
            logger.info(f"Listed {len(credential_names)} credentials")
            return credential_names
        except Exception as e:
            error_msg = f"Failed to list credentials: {str(e)}"
            logger.error(error_msg)
            raise RepositoryError(error_msg) from e
