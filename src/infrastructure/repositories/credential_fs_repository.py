"""File system implementation of the credential repository."""

import os
import json
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from src.core.exceptions import RepositoryError, ValidationError
from src.core.interfaces import ICredentialRepository, IEncryptionService
from src.core.credentials import Credentials
from src.infrastructure.common.file_locking import LockedFile

logger = logging.getLogger(__name__)


class CredentialFSRepository(ICredentialRepository):
    """
    File system implementation of the credential repository.
    
    This repository stores credentials in a single JSON file.
    The credentials are encrypted using the provided encryption service.
    """
    
    def __init__(
        self,
        file_path: str,
        encryption_service: IEncryptionService,
        create_if_missing: bool = False
    ):
        """
        Initialize the repository.
        
        Args:
            file_path: Path to the JSON file where credentials are stored
            encryption_service: Service for encrypting and decrypting credentials
            create_if_missing: Whether to create the file if it doesn't exist
            
        Raises:
            RepositoryError: If the file doesn't exist and create_if_missing is False
        """
        self.file_path = os.path.abspath(file_path)
        self.encryption_service = encryption_service
        
        # Create the directory if it doesn't exist
        directory = os.path.dirname(self.file_path)
        if not os.path.exists(directory):
            if create_if_missing:
                try:
                    os.makedirs(directory, exist_ok=True)
                    logger.info(f"Created credential directory: {directory}")
                except Exception as e:
                    raise RepositoryError(
                        f"Failed to create credential directory: {e}",
                        repository_name="CredentialFSRepository",
                        cause=e
                    ) from e
            else:
                raise RepositoryError(
                    f"Credential directory does not exist: {directory}",
                    repository_name="CredentialFSRepository"
                )
        
        # Create the file if it doesn't exist
        if not os.path.exists(self.file_path):
            if create_if_missing:
                try:
                    with LockedFile(self.file_path, "w") as f:
                        json.dump([], f)
                    logger.info(f"Created credential file: {self.file_path}")
                except Exception as e:
                    raise RepositoryError(
                        f"Failed to create credential file: {e}",
                        repository_name="CredentialFSRepository",
                        cause=e
                    ) from e
            else:
                raise RepositoryError(
                    f"Credential file does not exist: {self.file_path}",
                    repository_name="CredentialFSRepository"
                )
        
        logger.debug(f"Initialized CredentialFSRepository with file: {self.file_path}")
    
    def _load_credentials(self) -> List[Dict[str, Any]]:
        """
        Load all credentials from the file.
        
        Returns:
            A list of credential dictionaries
            
        Raises:
            RepositoryError: If the credentials cannot be loaded
        """
        try:
            with LockedFile(self.file_path, "r") as f:
                data = json.load(f)
            
            logger.debug(f"Loaded {len(data)} credentials from {self.file_path}")
            return data
        except Exception as e:
            raise RepositoryError(
                f"Failed to load credentials: {e}",
                repository_name="CredentialFSRepository",
                cause=e
            ) from e
    
    def _save_credentials(self, credentials_data: List[Dict[str, Any]]) -> None:
        """
        Save all credentials to the file.
        
        Args:
            credentials_data: A list of credential dictionaries
            
        Raises:
            RepositoryError: If the credentials cannot be saved
        """
        try:
            with LockedFile(self.file_path, "w") as f:
                json.dump(credentials_data, f, indent=2)
            
            logger.debug(f"Saved {len(credentials_data)} credentials to {self.file_path}")
        except Exception as e:
            raise RepositoryError(
                f"Failed to save credentials: {e}",
                repository_name="CredentialFSRepository",
                cause=e
            ) from e
    
    def _serialize_credentials(self, credentials: Credentials) -> Dict[str, Any]:
        """
        Serialize credentials to a dictionary.
        
        Args:
            credentials: The credentials to serialize
            
        Returns:
            The serialized credentials
            
        Raises:
            RepositoryError: If the credentials cannot be serialized
        """
        try:
            # Encrypt the password
            encrypted_password = self.encryption_service.encrypt(credentials.password)
            
            return {
                "name": credentials.name,
                "username": credentials.username,
                "password": encrypted_password,
                "description": credentials.description,
                "created_at": credentials.created_at.isoformat() if credentials.created_at else None,
                "updated_at": credentials.updated_at.isoformat() if credentials.updated_at else None,
                "encrypted": True
            }
        except Exception as e:
            raise RepositoryError(
                f"Failed to serialize credentials: {e}",
                repository_name="CredentialFSRepository",
                entity_id=credentials.name,
                cause=e
            ) from e
    
    def _deserialize_credentials(self, data: Dict[str, Any]) -> Credentials:
        """
        Deserialize credentials from a dictionary.
        
        Args:
            data: The serialized credentials
            
        Returns:
            The deserialized credentials
            
        Raises:
            RepositoryError: If the credentials cannot be deserialized
        """
        try:
            # Decrypt the password if it's encrypted
            password = data.get("password", "")
            if data.get("encrypted", False):
                password = self.encryption_service.decrypt(password)
            
            # Create the credentials
            credentials = Credentials(
                name=data.get("name", ""),
                username=data.get("username", ""),
                password=password,
                description=data.get("description", "")
            )
            
            # Set the timestamps
            if data.get("created_at"):
                credentials.created_at = datetime.fromisoformat(data["created_at"])
            if data.get("updated_at"):
                credentials.updated_at = datetime.fromisoformat(data["updated_at"])
            
            return credentials
        except Exception as e:
            raise RepositoryError(
                f"Failed to deserialize credentials: {e}",
                repository_name="CredentialFSRepository",
                entity_id=data.get("name", "unknown"),
                cause=e
            ) from e
    
    def save(self, credentials: Credentials) -> None:
        """
        Save credentials to the repository.
        
        Args:
            credentials: The credentials to save
            
        Raises:
            RepositoryError: If the credentials cannot be saved
            ValidationError: If the credentials are invalid
        """
        if not credentials:
            raise ValidationError("Credentials cannot be None", field_name="credentials")
        
        if not credentials.name:
            raise ValidationError("Credential name cannot be empty", field_name="name")
        
        # Update the updated_at timestamp
        credentials.updated_at = datetime.now()
        
        # Set the created_at timestamp if it doesn't exist
        if not credentials.created_at:
            credentials.created_at = credentials.updated_at
        
        # Load all credentials
        credentials_data = self._load_credentials()
        
        # Check if the credentials already exist
        for i, cred_data in enumerate(credentials_data):
            if cred_data.get("name") == credentials.name:
                # Update the existing credentials
                credentials_data[i] = self._serialize_credentials(credentials)
                self._save_credentials(credentials_data)
                logger.debug(f"Updated credentials: {credentials.name}")
                return
        
        # Add the new credentials
        credentials_data.append(self._serialize_credentials(credentials))
        self._save_credentials(credentials_data)
        logger.debug(f"Added new credentials: {credentials.name}")
    
    def get(self, name: str) -> Optional[Credentials]:
        """
        Get credentials from the repository.
        
        Args:
            name: The credential name
            
        Returns:
            The credentials, or None if they don't exist
            
        Raises:
            RepositoryError: If the credentials cannot be retrieved
            ValidationError: If the credential name is invalid
        """
        if not name:
            raise ValidationError("Credential name cannot be empty", field_name="name")
        
        # Load all credentials
        credentials_data = self._load_credentials()
        
        # Find the credentials with the given name
        for cred_data in credentials_data:
            if cred_data.get("name") == name:
                return self._deserialize_credentials(cred_data)
        
        logger.debug(f"Credentials not found: {name}")
        return None
    
    def list(self) -> List[Credentials]:
        """
        List all credentials in the repository.
        
        Returns:
            A list of credentials
            
        Raises:
            RepositoryError: If the credentials cannot be listed
        """
        # Load all credentials
        credentials_data = self._load_credentials()
        
        # Deserialize all credentials
        credentials = []
        for cred_data in credentials_data:
            try:
                credentials.append(self._deserialize_credentials(cred_data))
            except Exception as e:
                logger.warning(f"Failed to deserialize credentials: {e}")
        
        logger.debug(f"Listed {len(credentials)} credentials")
        return credentials
    
    def delete(self, name: str) -> None:
        """
        Delete credentials from the repository.
        
        Args:
            name: The credential name
            
        Raises:
            RepositoryError: If the credentials cannot be deleted
            ValidationError: If the credential name is invalid
        """
        if not name:
            raise ValidationError("Credential name cannot be empty", field_name="name")
        
        # Load all credentials
        credentials_data = self._load_credentials()
        
        # Find and remove the credentials with the given name
        for i, cred_data in enumerate(credentials_data):
            if cred_data.get("name") == name:
                del credentials_data[i]
                self._save_credentials(credentials_data)
                logger.debug(f"Deleted credentials: {name}")
                return
        
        logger.debug(f"Credentials not found for deletion: {name}")
