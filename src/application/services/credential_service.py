"""Credential service implementation for AutoQliq."""
import logging
from typing import Dict, List, Any

from src.core.interfaces import ICredentialRepository
from src.core.exceptions import CredentialError
from src.application.interfaces import ICredentialService
from src.infrastructure.common.error_handling import handle_exceptions
from src.infrastructure.common.logging_utils import log_method_call


class CredentialService(ICredentialService):
    """Implementation of ICredentialService.

    This class provides services for managing credentials, including creating,
    updating, deleting, and retrieving credentials.

    Attributes:
        credential_repository: Repository for credential storage and retrieval
        logger: Logger for recording service operations and errors
    """

    def __init__(self, credential_repository: ICredentialRepository):
        """Initialize a new CredentialService.

        Args:
            credential_repository: Repository for credential storage and retrieval
        """
        self.credential_repository = credential_repository
        self.logger = logging.getLogger(__name__)

    @log_method_call(logging.getLogger(__name__))
    @handle_exceptions(CredentialError, "Failed to create credential")
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
        self.logger.info(f"Creating credential: {name}")

        # Create the credential dictionary
        credential = {
            "name": name,
            "username": username,
            "password": password
        }

        # Save the credential
        self.credential_repository.save(credential)
        return True

    @log_method_call(logging.getLogger(__name__))
    @handle_exceptions(CredentialError, "Failed to update credential")
    def update_credential(self, name: str, username: str, password: str) -> bool:
        """Update an existing credential.

        Args:
            name: The name of the credential to update
            username: The new username
            password: The new password

        Returns:
            True if the credential was updated successfully

        Raises:
            CredentialError: If there is an error updating the credential
        """
        self.logger.info(f"Updating credential: {name}")

        # Check if the credential exists
        self.credential_repository.get_by_name(name)

        # Create the updated credential dictionary
        credential = {
            "name": name,
            "username": username,
            "password": password
        }

        # Save the updated credential
        self.credential_repository.save(credential)
        return True

    @log_method_call(logging.getLogger(__name__))
    @handle_exceptions(CredentialError, "Failed to delete credential")
    def delete_credential(self, name: str) -> bool:
        """Delete a credential.

        Args:
            name: The name of the credential to delete

        Returns:
            True if the credential was deleted successfully

        Raises:
            CredentialError: If there is an error deleting the credential
        """
        self.logger.info(f"Deleting credential: {name}")
        return self.credential_repository.delete(name)

    @log_method_call(logging.getLogger(__name__))
    @handle_exceptions(CredentialError, "Failed to get credential")
    def get_credential(self, name: str) -> Dict[str, str]:
        """Get a credential by name.

        Args:
            name: The name of the credential to get

        Returns:
            A dictionary containing the credential information

        Raises:
            CredentialError: If there is an error retrieving the credential
        """
        self.logger.debug(f"Getting credential: {name}")
        return self.credential_repository.get_by_name(name)

    @log_method_call(logging.getLogger(__name__))
    @handle_exceptions(CredentialError, "Failed to list credentials")
    def list_credentials(self) -> List[str]:
        """Get a list of available credentials.

        Returns:
            A list of credential names

        Raises:
            CredentialError: If there is an error retrieving the credential list
        """
        self.logger.debug("Listing credentials")

        # Get all credentials using list_credentials method from the repository
        credential_names = self.credential_repository.list_credentials()
        return credential_names
