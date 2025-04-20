"""Secure credential repository implementation for AutoQliq."""

import json
import logging
import os
from typing import Dict, List, Optional, Any
from datetime import datetime

# Core dependencies
from src.core.exceptions import CredentialError, RepositoryError, ValidationError, AutoQliqError
from src.core.interfaces import ICredentialRepository
from src.core.security.encryption import IEncryptionService

# Infrastructure dependencies
from src.infrastructure.common.error_handling import handle_exceptions
from src.infrastructure.common.logging_utils import log_method_call
from src.infrastructure.common.validators import CredentialValidator
from src.infrastructure.common.file_locking import LockedFile
from src.infrastructure.repositories.base.file_system_repository import FileSystemRepository

logger = logging.getLogger(__name__)


class SecureCredentialRepository(FileSystemRepository[Dict[str, str]], ICredentialRepository):
    """
    Implementation of ICredentialRepository that stores credentials in a JSON file with encryption.
    
    This implementation securely stores credentials with password encryption and thread-safe file access.
    
    Attributes:
        file_path: Path to the JSON file containing credentials.
        encryption_service: Service used to encrypt/decrypt sensitive data.
    """
    
    def __init__(
        self, 
        file_path: str, 
        encryption_service: IEncryptionService,
        **options
    ):
        """
        Initialize a new SecureCredentialRepository.
        
        Args:
            file_path: Path to the JSON file containing credentials.
            encryption_service: Service used to encrypt/decrypt sensitive data.
            **options: Additional options:
                create_if_missing (bool): If True, create the file with an empty list if it doesn't exist.
                                         Defaults to True.
        
        Raises:
            ValueError: If file_path is empty or encryption_service is None.
        """
        super().__init__(logger_name=__name__)
        
        if not file_path:
            raise ValueError("File path cannot be empty.")
        if encryption_service is None:
            raise ValueError("Encryption service is required.")
            
        self.file_path = file_path
        self.encryption_service = encryption_service
        self._create_if_missing = options.get('create_if_missing', True)
        
        # Create a locked file for thread-safe access
        self._locked_file = LockedFile[List[Dict[str, str]]](
            file_path=self.file_path,
            read_func=self._read_json_file,
            write_func=self._write_json_file
        )
        
        # Ensure the directory exists
        directory = os.path.dirname(self.file_path)
        if directory:
            try:
                super()._ensure_directory_exists(directory)
            except AttributeError:
                logger.warning("_ensure_directory_exists not found on base, attempting manual creation.")
                os.makedirs(directory, exist_ok=True)
            except AutoQliqError as e:
                raise RepositoryError(f"Failed to ensure directory exists: {directory}", cause=e) from e
        
        # Create the file if needed
        if self._create_if_missing and not os.path.exists(self.file_path):
            try:
                logger.info(f"Credential file not found '{self.file_path}'. Creating empty list.")
                self._locked_file.write([])
            except Exception as e:
                raise RepositoryError(f"Failed to create initial credential file '{self.file_path}'", cause=e) from e
    
    def _read_json_file(self, file_path: str) -> List[Dict[str, str]]:
        """Read and parse a JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            if not isinstance(data, list):
                raise CredentialError(f"Credential file '{file_path}' not JSON list.")
            if not all(isinstance(item, dict) for item in data):
                raise CredentialError(f"Credential file '{file_path}' contains non-dict items.")
                
            # Ensure values are strings
            stringified_data = [{str(k): str(v) for k, v in item.items()} for item in data]
            return stringified_data
        except json.JSONDecodeError as e:
            raise CredentialError(f"Invalid JSON in credential file: {file_path}", cause=e) from e
        except (IOError, PermissionError) as e:
            raise CredentialError(f"Permission/IO error reading credential file: {file_path}", cause=e) from e
    
    def _write_json_file(self, file_path: str, data: List[Dict[str, str]]) -> None:
        """Write data to a JSON file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except (IOError, TypeError, PermissionError) as e:
            raise CredentialError(f"Error writing credential file: {file_path}", cause=e) from e
    
    def _encrypt_credential(self, credential: Dict[str, str]) -> Dict[str, str]:
        """
        Encrypt sensitive fields in a credential.
        
        Args:
            credential: The credential to encrypt
            
        Returns:
            A new credential dictionary with encrypted fields
            
        Raises:
            CredentialError: If encryption fails
        """
        try:
            # Create a copy to avoid modifying the original
            encrypted = credential.copy()
            
            # Encrypt the password
            if "password" in encrypted:
                encrypted["password"] = self.encryption_service.encrypt(encrypted["password"])
            
            # Add metadata
            encrypted["encrypted"] = True
            encrypted["last_modified"] = datetime.now().isoformat()
            
            return encrypted
        except Exception as e:
            raise CredentialError(f"Failed to encrypt credential: {e}", cause=e) from e
    
    def _decrypt_credential(self, credential: Dict[str, str]) -> Dict[str, str]:
        """
        Decrypt sensitive fields in a credential.
        
        Args:
            credential: The credential to decrypt
            
        Returns:
            A new credential dictionary with decrypted fields
            
        Raises:
            CredentialError: If decryption fails
        """
        try:
            # Create a copy to avoid modifying the original
            decrypted = credential.copy()
            
            # Decrypt the password if it exists and the credential is marked as encrypted
            if "password" in decrypted and decrypted.get("encrypted", False):
                decrypted["password"] = self.encryption_service.decrypt(decrypted["password"])
            
            return decrypted
        except Exception as e:
            raise CredentialError(f"Failed to decrypt credential: {e}", cause=e) from e
    
    # --- ICredentialRepository Implementation ---
    
    @log_method_call(logger)
    @handle_exceptions(CredentialError, "Error saving credential", reraise_types=(CredentialError, ValidationError, RepositoryError))
    def save(self, credential: Dict[str, str]) -> None:
        """
        Save (create or update) a credential with encrypted password.
        
        Args:
            credential: Dictionary containing credential information.
                       Must include 'name' and 'password' keys.
                       
        Raises:
            CredentialError: If the credential cannot be saved
            ValidationError: If the credential data is invalid
            RepositoryError: If there's an issue with the repository
        """
        # Validate credential data
        CredentialValidator.validate_credential_data(credential)
        credential_name = credential['name']
        self._validate_entity_id(credential_name, entity_type="Credential")
        
        self._log_operation("Saving", credential_name)
        
        try:
            # Encrypt the credential
            encrypted_credential = self._encrypt_credential(credential)
            
            # Update the credentials list
            def update_credentials(credentials: List[Dict[str, str]]) -> List[Dict[str, str]]:
                # Find and update existing credential or add new one
                found = False
                for i, cred in enumerate(credentials):
                    if cred.get('name') == credential_name:
                        credentials[i] = encrypted_credential
                        found = True
                        logger.debug(f"Updating credential '{credential_name}'.")
                        break
                
                if not found:
                    credentials.append(encrypted_credential)
                    logger.debug(f"Adding new credential '{credential_name}'.")
                
                return credentials
            
            # Perform the update atomically
            self._locked_file.update(update_credentials, default=[])
            
            logger.info(f"Credential '{credential_name}' saved successfully.")
        except Exception as e:
            error_msg = f"Failed to save credential '{credential_name}': {e}"
            logger.error(error_msg)
            raise CredentialError(error_msg, credential_name=credential_name, cause=e) from e
    
    @log_method_call(logger)
    @handle_exceptions(CredentialError, "Error retrieving credential", reraise_types=(CredentialError, ValidationError, RepositoryError))
    def get_by_name(self, name: str) -> Optional[Dict[str, str]]:
        """
        Get credential details by name, decrypting sensitive fields.
        
        Args:
            name: The name of the credential to retrieve
            
        Returns:
            The credential dictionary, or None if not found
            
        Raises:
            CredentialError: If the credential cannot be retrieved
            ValidationError: If the name is invalid
            RepositoryError: If there's an issue with the repository
        """
        self._validate_entity_id(name, entity_type="Credential")
        self._log_operation("Getting", name)
        
        try:
            # Read all credentials
            credentials = self._locked_file.read(default=[])
            
            # Find the credential by name
            for cred in credentials:
                if cred.get('name') == name:
                    # Decrypt the credential before returning
                    return self._decrypt_credential(cred)
            
            # Not found
            return None
        except Exception as e:
            if isinstance(e, FileNotFoundError) and self._create_if_missing:
                return None
            error_msg = f"Failed to retrieve credential '{name}': {e}"
            logger.error(error_msg)
            raise CredentialError(error_msg, credential_name=name, cause=e) from e
    
    @log_method_call(logger)
    @handle_exceptions(CredentialError, "Error deleting credential", reraise_types=(CredentialError, ValidationError, RepositoryError))
    def delete(self, name: str) -> bool:
        """
        Delete a credential by name.
        
        Args:
            name: The name of the credential to delete
            
        Returns:
            True if the credential was deleted, False if not found
            
        Raises:
            CredentialError: If the credential cannot be deleted
            ValidationError: If the name is invalid
            RepositoryError: If there's an issue with the repository
        """
        self._validate_entity_id(name, entity_type="Credential")
        self._log_operation("Deleting", name)
        
        try:
            # Update the credentials list
            def update_credentials(credentials: List[Dict[str, str]]) -> List[Dict[str, str]]:
                initial_count = len(credentials)
                filtered = [c for c in credentials if c.get('name') != name]
                
                if len(filtered) < initial_count:
                    logger.debug(f"Deleted credential '{name}'.")
                    return filtered
                else:
                    logger.debug(f"Credential '{name}' not found for deletion.")
                    return credentials
            
            # Perform the update atomically
            updated = self._locked_file.update(update_credentials, default=[])
            
            # Return True if a credential was deleted
            return len(updated) < len(self._locked_file.read(default=[]))
        except Exception as e:
            if isinstance(e, FileNotFoundError) and self._create_if_missing:
                return False
            error_msg = f"Failed to delete credential '{name}': {e}"
            logger.error(error_msg)
            raise CredentialError(error_msg, credential_name=name, cause=e) from e
    
    @log_method_call(logger)
    @handle_exceptions(CredentialError, "Error listing credentials", reraise_types=(CredentialError, RepositoryError))
    def list_credentials(self) -> List[str]:
        """
        List all credential names.
        
        Returns:
            A list of credential names
            
        Raises:
            CredentialError: If the credentials cannot be listed
            RepositoryError: If there's an issue with the repository
        """
        self._log_operation("Listing names")
        
        try:
            # Read all credentials
            credentials = self._locked_file.read(default=[])
            
            # Extract and sort names
            names = [str(c['name']) for c in credentials if c.get('name')]
            return sorted(names)
        except Exception as e:
            if isinstance(e, FileNotFoundError) and self._create_if_missing:
                return []
            error_msg = f"Failed to list credentials: {e}"
            logger.error(error_msg)
            raise CredentialError(error_msg, cause=e) from e
