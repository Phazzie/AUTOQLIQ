"""Credential service for managing user credentials."""

import logging
import re
from typing import Dict, List, Optional, Any

from src.core.exceptions import CredentialError, ValidationError
from src.core.interfaces.service import ICredentialService
from src.core.interfaces import ICredentialRepository
from src.application.security.password_handler import IPasswordHandler, WerkzeugPasswordHandler


class CredentialService(ICredentialService):
    """Service for managing user credentials.

    This service handles the management of credentials, including creation, retrieval,
    and validation. It uses a password handler to securely hash and verify passwords.
    """

    def __init__(self, credential_repository: ICredentialRepository,
                 password_handler: Optional[IPasswordHandler] = None):
        """Initialize the credential service.

        Args:
            credential_repository: Repository for storing credentials
            password_handler: Handler for password hashing and verification
        """
        self.logger = logging.getLogger(__name__)
        self.repository = credential_repository
        # Use provided handler or create default WerkzeugPasswordHandler
        self.password_handler = password_handler or WerkzeugPasswordHandler()

    def list_credentials(self) -> List[str]:
        """List all credential names.

        Returns:
            List of credential names
        """
        return self.repository.list_credentials()

    def get_credential(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a credential by name.

        Args:
            name: The name of the credential

        Returns:
            The credential dictionary or None if not found
            Note: Password hash is removed from the returned data for security
        """
        credential = self.repository.get_by_name(name)
        if credential and 'password' in credential:
            # Remove password hash from returned data for security
            credential = credential.copy()
            del credential['password']
        return credential

    def create_credential(self, name: str, username: str, password: str) -> bool:
        """Create a new credential.

        Args:
            name: The name of the credential
            username: The username
            password: The password (will be hashed)

        Returns:
            True if the credential was created successfully

        Raises:
            ValidationError: If any required field is empty
            CredentialError: If a credential with the same name already exists
        """
        # Validate inputs
        if not name or not username or not password:
            raise ValidationError("Name, username, and password cannot be empty")

        # Check if credential already exists
        existing = self.repository.get_by_name(name)
        if existing:
            raise CredentialError(f"Credential '{name}' already exists.")

        # Hash the password using the password handler
        hashed_password = self.password_handler.hash_password(password)

        # Save credential
        credential_data = {
            "name": name,
            "username": username,
            "password": hashed_password
        }
        self.repository.save(credential_data)
        return True

    def delete_credential(self, name: str) -> bool:
        """Delete a credential.

        Args:
            name: The name of the credential to delete

        Returns:
            True if the credential was deleted successfully
        """
        return self.repository.delete(name)

    def verify_credential(self, name: str, password: str) -> bool:
        """Verify a credential's password.

        Args:
            name: The name of the credential
            username: The username
            password: The password to verify

        Returns:
            True if the credential is valid
        """
        # Empty password is always invalid
        if not password:
            return False

        # Get the credential
        credential = self.repository.get_by_name(name)
        if not credential:
            return False

        # Get the stored password hash
        stored_hash = credential.get('password')
        if not stored_hash:
            return False

        # Verify the password using the password handler
        return self.password_handler.verify_password(stored_hash, password)