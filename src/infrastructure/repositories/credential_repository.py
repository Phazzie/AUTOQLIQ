"""Credential repository implementation for AutoQliq."""
import json
import logging
import os
from typing import Dict, List, Optional

# Core dependencies
from src.core.exceptions import CredentialError, RepositoryError, ValidationError
from src.core.interfaces import ICredentialRepository # Correct interface import

# Infrastructure dependencies
from src.infrastructure.common.error_handling import handle_exceptions
from src.infrastructure.common.logging_utils import log_method_call
from src.infrastructure.common.validators import CredentialValidator
from src.infrastructure.repositories.base.file_system_repository import FileSystemRepository # Correct base class import

logger = logging.getLogger(__name__)

class FileSystemCredentialRepository(FileSystemRepository[Dict[str, str]], ICredentialRepository):
    """Implementation of ICredentialRepository that stores credentials in a JSON file.

    Manages CRUD operations for credentials stored in a single JSON file.
    Passwords are read/written as stored (expects hashes from service layer).

    Attributes:
        file_path: Path to the JSON file containing credentials.
    """

    def __init__(self, file_path: str, **options):
        """Initialize a new FileSystemCredentialRepository.

        Args:
            file_path: Path to the JSON file containing credentials.
            **options: Additional options:
                create_if_missing (bool): If True, create the file with an empty list if it doesn't exist. Defaults to False.
        """
        super().__init__(logger_name=__name__) # Pass logger name to base
        if not file_path:
            raise ValueError("File path cannot be empty.")
        self.file_path = file_path
        # Store option, default to True is safer for usability
        self._create_if_missing = options.get('create_if_missing', True)

        # Ensure the directory exists
        directory = os.path.dirname(self.file_path)
        if directory:
            try:
                 # Use helper method now expected in FileSystemRepository base
                 super()._ensure_directory_exists(directory)
            except AttributeError:
                 self.logger.warning("_ensure_directory_exists not found on base, attempting manual creation.")
                 os.makedirs(directory, exist_ok=True) # Simple fallback
            except AutoQliqError as e: # Base might raise AutoQliqError
                 raise RepositoryError(f"Failed to ensure directory exists: {directory}", cause=e) from e

        # Create the file if needed AFTER ensuring directory exists
        if self._create_if_missing and not super()._file_exists(self.file_path):
            try:
                self.logger.info(f"Cred file not found '{self.file_path}'. Creating empty list.")
                super()._write_json_file(self.file_path, [])
            except (IOError, TypeError) as e:
                raise RepositoryError(f"Failed to create initial cred file '{self.file_path}'", cause=e) from e


    def _load_all_credentials(self) -> List[Dict[str, str]]:
        """Loads all credentials from the JSON file. Internal helper."""
        try:
            # Use base class helper
            data = super()._read_json_file(self.file_path)
            if not isinstance(data, list):
                 raise CredentialError(f"Cred file '{self.file_path}' not JSON list.", credential_name=None)
            if not all(isinstance(item, dict) for item in data):
                 raise CredentialError(f"Cred file '{self.file_path}' contains non-dict items.", credential_name=None)
            # Ensure values are strings
            stringified_data = [{str(k): str(v) for k, v in item.items()} for item in data]
            return stringified_data
        except FileNotFoundError as e:
            if self._create_if_missing: return []
            else: raise CredentialError(f"Cred file not found: {self.file_path}", cause=e) from e
        except json.JSONDecodeError as e: raise CredentialError(f"Invalid JSON in cred file: {self.file_path}", cause=e) from e
        except (IOError, PermissionError) as e: raise CredentialError(f"Permission/IO error reading cred file: {self.file_path}", cause=e) from e

    def _save_all_credentials(self, credentials: List[Dict[str, str]]) -> None:
        """Saves the entire list of credentials back to the JSON file."""
        try:
            super()._write_json_file(self.file_path, credentials)
        except (IOError, TypeError, PermissionError) as e:
            raise CredentialError(f"Error writing cred file: {self.file_path}", cause=e) from e


    # --- ICredentialRepository Implementation ---

    @log_method_call(logger)
    @handle_exceptions(CredentialError, "Error saving credential", reraise_types=(CredentialError, ValidationError, RepositoryError))
    def save(self, credential: Dict[str, str]) -> None:
        """Save (create or update) a credential."""
        CredentialValidator.validate_credential_data(credential) # Raises CredentialError
        credential_name = credential['name']
        self._validate_entity_id(credential_name, entity_type="Credential") # Raises ValidationError

        self._log_operation("Saving", credential_name)
        all_creds = self._load_all_credentials() # Load current data

        found_index = -1
        for i, existing in enumerate(all_creds):
            if existing.get('name') == credential_name:
                found_index = i
                break

        if found_index != -1:
            all_creds[found_index] = credential # Update existing (replace whole dict)
            self.logger.debug(f"Updating credential '{credential_name}'.")
        else:
            all_creds.append(credential) # Add new
            self.logger.debug(f"Adding new credential '{credential_name}'.")

        self._save_all_credentials(all_creds)


    @log_method_call(logger)
    @handle_exceptions(CredentialError, "Error retrieving credential", reraise_types=(CredentialError, ValidationError, RepositoryError))
    def get_by_name(self, name: str) -> Optional[Dict[str, str]]:
        """Get credential details (including password hash) by name."""
        self._validate_entity_id(name, entity_type="Credential") # Validate name
        self._log_operation("Getting", name)
        all_creds = self._load_all_credentials()
        for cred in all_creds:
            if cred.get('name') == name:
                return cred
        return None


    @log_method_call(logger)
    @handle_exceptions(CredentialError, "Error deleting credential", reraise_types=(CredentialError, ValidationError, RepositoryError))
    def delete(self, name: str) -> bool:
        """Delete a credential by name."""
        self._validate_entity_id(name, entity_type="Credential")
        self._log_operation("Deleting", name)
        all_creds = self._load_all_credentials()

        initial_count = len(all_creds)
        creds_to_keep = [c for c in all_creds if c.get('name') != name]

        if len(creds_to_keep) < initial_count:
            self._save_all_credentials(creds_to_keep)
            return True
        else:
            return False


    @log_method_call(logger)
    @handle_exceptions(CredentialError, "Error listing credentials", reraise_types=(CredentialError, RepositoryError))
    def list_credentials(self) -> List[str]:
        """List all credential names."""
        self._log_operation("Listing names")
        all_creds = self._load_all_credentials()
        names = [str(c['name']) for c in all_creds if c.get('name')] # Ensure name exists and convert just in case
        return sorted(names)