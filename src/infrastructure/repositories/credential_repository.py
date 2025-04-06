"""Credential repository implementation for AutoQliq."""
import json
import logging
import os
from typing import Dict, List, Optional

from src.core.exceptions import CredentialError
from src.core.interfaces import ICredentialRepository
from src.infrastructure.common.error_handling import handle_exceptions
from src.infrastructure.common.logging_utils import log_method_call
from src.infrastructure.common.validators import CredentialValidator
from src.infrastructure.repositories.base.file_system_repository import FileSystemRepository

class FileSystemCredentialRepository(FileSystemRepository[Dict[str, str]], ICredentialRepository):
    """Implementation of ICredentialRepository that stores credentials in a JSON file.

    This class provides methods for retrieving, saving, and deleting credentials from a JSON file.

    Attributes:
        file_path: Path to the JSON file containing credentials
        logger: Logger for recording repository operations and errors
    """

    def __init__(self, file_path: str, **options):
        """Initialize a new FileSystemCredentialRepository.

        Args:
            file_path: Path to the JSON file containing credentials
            **options: Additional options for the repository
                create_if_missing (bool): Whether to create the file if it doesn't exist
        """
        super().__init__(__name__)
        self.file_path = file_path
        self.options = options

        # Ensure the directory exists
        directory = os.path.dirname(file_path)
        if directory:
            self._ensure_directory_exists(directory)

        # Create the file if it doesn't exist and create_if_missing is True
        if options.get('create_if_missing', False) and not self._file_exists(file_path):
            self._write_json_file(file_path, [])

    @log_method_call(logging.getLogger(__name__))
    @handle_exceptions(CredentialError, "Error loading credentials")
    def get_all(self) -> List[Dict[str, str]]:
        """Get all credentials from the repository.

        Returns:
            A list of credential dictionaries

        Raises:
            CredentialError: If the credentials file cannot be read or parsed
        """
        try:
            return self._read_json_file(self.file_path)
        except FileNotFoundError as e:
            error_msg = f"Credentials file not found: {self.file_path}"
            self.logger.error(error_msg)
            raise CredentialError(error_msg) from e
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON in credentials file: {self.file_path}"
            self.logger.error(error_msg)
            raise CredentialError(error_msg) from e

    @log_method_call(logging.getLogger(__name__))
    def get_by_name(self, name: str) -> Optional[Dict[str, str]]:
        """Get a credential by name.

        Args:
            name: The name of the credential to retrieve

        Returns:
            The credential dictionary if found, None otherwise

        Raises:
            CredentialError: If the credentials file cannot be read or parsed
        """
        try:
            credentials = self.get_all()
            for credential in credentials:
                if credential.get('name') == name:
                    return credential
            return None
        except CredentialError:
            # Re-raise CredentialError from get_all
            raise

    @log_method_call(logging.getLogger(__name__))
    @handle_exceptions(CredentialError, "Error saving credential")
    def save_credential(self, credential: Dict[str, str]) -> None:
        """Save a credential to the repository.

        If a credential with the same name already exists, it will be updated.
        Otherwise, a new credential will be added.

        Args:
            credential: The credential to save

        Raises:
            CredentialError: If the credential cannot be saved or is invalid
        """
        # Validate credential
        self._validate_credential(credential)

        try:
            # Try to load existing credentials
            try:
                credentials = self.get_all()
            except CredentialError:
                # If file doesn't exist or is invalid, start with empty list
                credentials = []

            # Check if credential with same name already exists
            found = False
            for i, existing in enumerate(credentials):
                if existing.get('name') == credential.get('name'):
                    # Update existing credential
                    credentials[i] = credential
                    found = True
                    break

            # If not found, add new credential
            if not found:
                credentials.append(credential)

            # Save credentials to file
            self._write_json_file(self.file_path, credentials)
        except (IOError, PermissionError) as e:
            error_msg = f"Error saving credential: {str(e)}"
            self.logger.error(error_msg)
            raise CredentialError(error_msg) from e

    @log_method_call(logging.getLogger(__name__))
    @handle_exceptions(CredentialError, "Error deleting credential")
    def delete_credential(self, name: str) -> bool:
        """Delete a credential from the repository.

        Args:
            name: The name of the credential to delete

        Returns:
            True if the credential was deleted, False if it didn't exist

        Raises:
            CredentialError: If the credential cannot be deleted
        """
        try:
            # Load existing credentials
            credentials = self.get_all()

            # Find credential with matching name
            initial_count = len(credentials)
            credentials = [c for c in credentials if c.get('name') != name]

            # If no credential was removed, return False
            if len(credentials) == initial_count:
                return False

            # Save updated credentials to file
            self._write_json_file(self.file_path, credentials)
            return True
        except CredentialError:
            # Re-raise CredentialError from get_all
            raise

    def _validate_credential(self, credential: Dict[str, str]) -> None:
        """Validate a credential.

        Args:
            credential: The credential to validate

        Raises:
            CredentialError: If the credential is invalid
        """
        CredentialValidator.validate_credential(credential)

    @log_method_call(logging.getLogger(__name__))
    @handle_exceptions(CredentialError, "Error listing credentials")
    def list_credentials(self) -> List[str]:
        """List all credential names in the repository.

        Returns:
            A list of credential names

        Raises:
            CredentialError: If the credentials cannot be listed
        """
        try:
            # Get all credentials
            credentials = self.get_all()

            # Extract the names
            return [credential.get('name') for credential in credentials if credential.get('name')]
        except CredentialError as e:
            # If the file doesn't exist or is empty, return an empty list
            if "not found" in str(e):
                return []
            # Re-raise other errors
            raise
