"""File system credential repository implementation for AutoQliq.

This module provides a file system-based implementation of the ICredentialRepository
interface for storing and retrieving credentials securely.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, TYPE_CHECKING

from src.core.exceptions import RepositoryError, ValidationError, SerializationError
from src.core.interfaces.repository.credential import ICredentialRepository
from src.core.interfaces.security import IEncryptionService
from src.infrastructure.repositories.base.file_system_repository import FileSystemRepository

# Use TYPE_CHECKING to avoid circular imports
if TYPE_CHECKING:
    from src.core.credentials import Credentials

logger = logging.getLogger(__name__)

class FileSystemCredentialRepository(FileSystemRepository["Credentials"], ICredentialRepository):
    """File system implementation of the credential repository.
    
    This class provides a file system-based implementation of the ICredentialRepository
    interface. It stores credentials as encrypted JSON files.
    
    Attributes:
        base_directory (str): Base directory for storing credential files
        encryption_service (IEncryptionService): Service for encrypting and decrypting credentials
    """
    
    CREDENTIAL_EXTENSION = ".json"
    
    def __init__(
        self, 
        directory_path: str, 
        encryption_service: IEncryptionService,
        create_if_missing: bool = True
    ):
        """Initialize a new FileSystemCredentialRepository.
        
        Args:
            directory_path: Path to the directory where credentials are stored
            encryption_service: Service for encrypting and decrypting credentials
            create_if_missing: Whether to create the directory if it doesn't exist
                
        Raises:
            RepositoryError: If the directory cannot be created or accessed
            ValueError: If encryption_service is None
        """
        super().__init__("credential_repository", directory_path)
        
        if not encryption_service:
            raise ValueError("Encryption service cannot be None")
        
        self.encryption_service = encryption_service
        
        if create_if_missing:
            self._ensure_directory_exists(self.base_directory)
            logger.info(f"Initialized credential repository at {self.base_directory}")
        elif not os.path.exists(self.base_directory):
            raise RepositoryError(
                f"Credential directory does not exist: {self.base_directory}",
                repository_name="CredentialRepository"
            )
    
    def save(self, credential: "Credentials") -> None:
        """Save a credential to the repository.
        
        Args:
            credential: The credential to save
            
        Raises:
            ValidationError: If the credential is invalid
            RepositoryError: If the operation fails
        """
        if not credential:
            raise ValidationError("Credential cannot be None")
        
        if not credential.name:
            raise ValidationError("Credential name cannot be empty")
        
        # Update the credential's updated_at timestamp
        credential.updated_at = datetime.now()
        
        # If this is a new credential, set the created_at timestamp
        if not credential.created_at:
            credential.created_at = credential.updated_at
        
        # Save the credential
        super().save(credential.name, credential)
    
    def get(self, credential_id: str) -> Optional["Credentials"]:
        """Get a credential from the repository by ID.
        
        Args:
            credential_id: ID of the credential to get
            
        Returns:
            The credential if found, None otherwise
            
        Raises:
            ValidationError: If the credential ID is invalid
            RepositoryError: If the operation fails
        """
        return super().get(credential_id)
    
    def get_by_name(self, name: str) -> Optional["Credentials"]:
        """Get a credential from the repository by name.
        
        Args:
            name: Name of the credential to get
            
        Returns:
            The credential if found, None otherwise
            
        Raises:
            ValidationError: If the name is invalid
            RepositoryError: If the operation fails
        """
        return self.get(name)
    
    def list_credentials(self) -> List[Dict[str, str]]:
        """List all credentials with basic information (excluding sensitive data).
        
        Returns:
            List of dictionaries containing credential ID, name, and username
            
        Raises:
            RepositoryError: If the operation fails
        """
        try:
            # Get all credential IDs
            credential_ids = self._list_entities()
            
            # Get basic information for each credential
            credentials = []
            for credential_id in credential_ids:
                try:
                    credential = self.get(credential_id)
                    if credential:
                        credentials.append({
                            "id": credential.name,
                            "name": credential.name,
                            "username": credential.username,
                            "description": credential.description,
                            "created_at": credential.created_at.isoformat() if credential.created_at else None,
                            "updated_at": credential.updated_at.isoformat() if credential.updated_at else None
                        })
                except Exception as e:
                    logger.warning(f"Error getting credential {credential_id}: {e}")
            
            return credentials
        except Exception as e:
            error_msg = f"Failed to list credentials: {e}"
            logger.error(error_msg)
            raise RepositoryError(error_msg, repository_name="CredentialRepository", cause=e) from e
    
    # Implementation of abstract methods from FileSystemRepository
    
    def _save_entity(self, entity_id: str, entity: "Credentials") -> None:
        """Save a credential entity to the file system.
        
        Args:
            entity_id: ID of the credential
            entity: Credential to save
            
        Raises:
            RepositoryError: If the operation fails
        """
        try:
            # Serialize the credential
            credential_data = self._serialize_credential(entity)
            
            # Save the credential to a file
            file_path = self._get_credential_path(entity_id)
            self._write_json_file(file_path, credential_data)
            
            logger.debug(f"Saved credential {entity_id} to {file_path}")
        except Exception as e:
            error_msg = f"Failed to save credential {entity_id}: {e}"
            logger.error(error_msg)
            raise RepositoryError(error_msg, repository_name="CredentialRepository", entity_id=entity_id, cause=e) from e
    
    def _get_entity(self, entity_id: str) -> Optional["Credentials"]:
        """Get a credential entity from the file system.
        
        Args:
            entity_id: ID of the credential
            
        Returns:
            The credential if found, None otherwise
            
        Raises:
            RepositoryError: If the operation fails
        """
        try:
            # Get the credential file path
            file_path = self._get_credential_path(entity_id)
            
            # Check if the credential exists
            if not os.path.exists(file_path):
                logger.debug(f"Credential not found: {entity_id}")
                return None
            
            # Load the credential data
            credential_data = self._read_json_file(file_path)
            
            # Deserialize the credential
            credential = self._deserialize_credential(credential_data)
            
            logger.debug(f"Loaded credential {entity_id} from {file_path}")
            return credential
        except FileNotFoundError:
            logger.debug(f"Credential not found: {entity_id}")
            return None
        except Exception as e:
            error_msg = f"Failed to load credential {entity_id}: {e}"
            logger.error(error_msg)
            raise RepositoryError(error_msg, repository_name="CredentialRepository", entity_id=entity_id, cause=e) from e
    
    def _delete_entity(self, entity_id: str) -> bool:
        """Delete a credential entity from the file system.
        
        Args:
            entity_id: ID of the credential
            
        Returns:
            True if the credential was deleted, False if it wasn't found
            
        Raises:
            RepositoryError: If the operation fails
        """
        try:
            # Get the credential file path
            file_path = self._get_credential_path(entity_id)
            
            # Check if the credential exists
            if not os.path.exists(file_path):
                logger.debug(f"Credential not found: {entity_id}")
                return False
            
            # Delete the credential
            os.remove(file_path)
            
            logger.debug(f"Deleted credential {entity_id} from {file_path}")
            return True
        except FileNotFoundError:
            logger.debug(f"Credential not found: {entity_id}")
            return False
        except Exception as e:
            error_msg = f"Failed to delete credential {entity_id}: {e}"
            logger.error(error_msg)
            raise RepositoryError(error_msg, repository_name="CredentialRepository", entity_id=entity_id, cause=e) from e
    
    def _list_entities(self) -> List[str]:
        """List all credential IDs in the file system.
        
        Returns:
            List of credential IDs
            
        Raises:
            RepositoryError: If the operation fails
        """
        try:
            # Get all credential files
            credential_files = []
            for file in os.listdir(self.base_directory):
                if file.endswith(self.CREDENTIAL_EXTENSION) and os.path.isfile(os.path.join(self.base_directory, file)):
                    credential_files.append(file)
            
            # Extract credential IDs
            credential_ids = []
            for file in credential_files:
                credential_id = file[:-len(self.CREDENTIAL_EXTENSION)]
                credential_ids.append(credential_id)
            
            logger.debug(f"Listed {len(credential_ids)} credentials")
            return credential_ids
        except Exception as e:
            error_msg = f"Failed to list credentials: {e}"
            logger.error(error_msg)
            raise RepositoryError(error_msg, repository_name="CredentialRepository", cause=e) from e
    
    # Helper methods
    
    def _get_credential_path(self, credential_id: str) -> str:
        """Get the file path for a credential.
        
        Args:
            credential_id: ID of the credential
            
        Returns:
            Path to the credential file
        """
        return os.path.join(self.base_directory, f"{credential_id}{self.CREDENTIAL_EXTENSION}")
    
    def _serialize_credential(self, credential: "Credentials") -> Dict:
        """Serialize a credential to a dictionary.
        
        Args:
            credential: Credential to serialize
            
        Returns:
            Dictionary representation of the credential
            
        Raises:
            SerializationError: If the credential cannot be serialized
        """
        try:
            # Start with the basic properties
            data = {
                "name": credential.name,
                "username": credential.username,
                "description": credential.description or "",
                "created_at": credential.created_at.isoformat() if credential.created_at else None,
                "updated_at": credential.updated_at.isoformat() if credential.updated_at else None,
                "encrypted": True  # Flag to indicate that the password is encrypted
            }
            
            # Encrypt the password
            if credential.password:
                data["password"] = self.encryption_service.encrypt(credential.password)
            else:
                data["password"] = None
            
            return data
        except Exception as e:
            error_msg = f"Failed to serialize credential: {e}"
            logger.error(error_msg)
            raise SerializationError(error_msg, cause=e) from e
    
    def _deserialize_credential(self, data: Dict) -> "Credentials":
        """Deserialize a credential from a dictionary.
        
        Args:
            data: Dictionary representation of the credential
            
        Returns:
            Deserialized credential
            
        Raises:
            SerializationError: If the credential cannot be deserialized
        """
        try:
            # Import here to avoid circular imports
            from src.core.credentials import Credentials
            
            # Get the basic properties
            name = data.get("name")
            username = data.get("username")
            description = data.get("description", "")
            created_at_str = data.get("created_at")
            updated_at_str = data.get("updated_at")
            
            # Parse dates
            created_at = datetime.fromisoformat(created_at_str) if created_at_str else None
            updated_at = datetime.fromisoformat(updated_at_str) if updated_at_str else None
            
            # Decrypt the password
            password = None
            if data.get("password"):
                if data.get("encrypted", False):
                    password = self.encryption_service.decrypt(data.get("password"))
                else:
                    password = data.get("password")
            
            # Create the credential
            credential = Credentials(
                name=name,
                username=username,
                password=password,
                description=description,
                created_at=created_at,
                updated_at=updated_at
            )
            
            return credential
        except Exception as e:
            error_msg = f"Failed to deserialize credential: {e}"
            logger.error(error_msg)
            raise SerializationError(error_msg, cause=e) from e
