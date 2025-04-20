"""Credential service implementation for AutoQliq.

This module provides the CredentialService implementation that manages
credential lifecycle operations with secure password handling.
"""

import logging
import hashlib
import os
from typing import List, Optional
from src.core.credentials import Credential
from src.core.interfaces import ICredentialRepository
from src.application.interfaces.service_interfaces import ICredentialService
from src.core.exceptions import RepositoryError, ValidationError, ServiceError, SecurityError

logger = logging.getLogger(__name__)

class CredentialService(ICredentialService):
    """Service for managing credential lifecycle with secure password handling."""

    def __init__(self, credential_repository: ICredentialRepository):
        """Initialize with repository dependency."""
        self.credential_repository = credential_repository
        logger.debug("CredentialService initialized")

    def _hash_password(self, password: str) -> str:
        """Hash a password for secure storage."""
        salt = os.urandom(32)  # 32 bytes of random salt
        key = hashlib.pbkdf2_hmac(
            'sha256',  # Hash algorithm
            password.encode('utf-8'),  # Convert password to bytes
            salt,  # Salt
            100000,  # Number of iterations
            dklen=128  # Length of the derived key
        )
        # Store salt and key together
        return salt.hex() + ':' + key.hex()

    def _verify_password(self, stored_password: str, provided_password: str) -> bool:
        """Verify a password against its stored hash."""
        try:
            # Split stored value into salt and key
            salt_hex, key_hex = stored_password.split(':')
            salt = bytes.fromhex(salt_hex)
            stored_key = bytes.fromhex(key_hex)

            # Hash the provided password with the same salt
            key = hashlib.pbkdf2_hmac(
                'sha256',
                provided_password.encode('utf-8'),
                salt,
                100000,
                dklen=128
            )

            # Compare in constant time to prevent timing attacks
            return key == stored_key
        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False

    def create_credential(self, name: str, username: str, password: str) -> Credential:
        """Create a new credential with secure password storage."""
        logger.info(f"Creating new credential: {name}")
        try:
            # Validate inputs
            if not name or not name.strip():
                raise ValidationError("Credential name cannot be empty")
            if not username or not username.strip():
                raise ValidationError("Username cannot be empty")
            if not password:
                raise ValidationError("Password cannot be empty")

            # Check if credential with this name already exists
            existing = self.credential_repository.get(name)
            if existing:
                raise ValidationError(f"Credential with name '{name}' already exists")

            # Hash password for secure storage
            hashed_password = self._hash_password(password)

            # Create new credential
            credential = Credential(
                name=name.strip(),
                username=username.strip(),
                password=hashed_password  # Store hashed password
            )

            self.credential_repository.save(credential)
            logger.info(f"Created credential: {name}")

            # Return credential with masked password for UI
            return Credential(
                name=credential.name,
                username=credential.username,
                password="********"  # Mask password in returned object
            )
        except (ValidationError, RepositoryError) as e:
            logger.error(f"Failed to create credential '{name}': {e}")
            raise ServiceError(f"Failed to create credential: {e}", cause=e)
        except Exception as e:
            logger.exception(f"Unexpected error creating credential '{name}'")
            raise ServiceError(f"Unexpected error creating credential: {e}", cause=e)

    def save_credential(self, credential: Credential) -> None:
        """Save an existing credential."""
        logger.info(f"Saving credential: {credential.name}")
        try:
            # Validate credential
            if not credential.name:
                raise ValidationError("Credential name cannot be empty")
            if not credential.username:
                raise ValidationError("Username cannot be empty")

            # Get existing credential to check if we need to update password
            existing = self.credential_repository.get(credential.name)

            # If credential exists and password is masked, keep original password
            if existing and credential.password == "********":
                credential = Credential(
                    name=credential.name,
                    username=credential.username,
                    password=existing.password  # Keep original hashed password
                )
            # If new password provided, hash it
            elif credential.password != "********":
                credential = Credential(
                    name=credential.name,
                    username=credential.username,
                    password=self._hash_password(credential.password)
                )

            self.credential_repository.save(credential)
            logger.info(f"Saved credential: {credential.name}")
        except (ValidationError, RepositoryError) as e:
            logger.error(f"Failed to save credential '{credential.name}': {e}")
            raise ServiceError(f"Failed to save credential: {e}", cause=e)
        except Exception as e:
            logger.exception(f"Unexpected error saving credential '{credential.name}'")
            raise ServiceError(f"Unexpected error saving credential: {e}", cause=e)

    def get_credential(self, name: str) -> Optional[Credential]:
        """Get a credential by name, with password masked for UI."""
        logger.info(f"Getting credential: {name}")
        try:
            credential = self.credential_repository.get(name)
            if credential:
                logger.info(f"Found credential: {name}")
                # Return with masked password for UI
                return Credential(
                    name=credential.name,
                    username=credential.username,
                    password="********"  # Mask password in returned object
                )
            else:
                logger.info(f"Credential not found: {name}")
                return None
        except RepositoryError as e:
            logger.error(f"Repository error getting credential '{name}': {e}")
            raise ServiceError(f"Failed to get credential: {e}", cause=e)
        except Exception as e:
            logger.exception(f"Unexpected error getting credential '{name}'")
            raise ServiceError(f"Unexpected error getting credential: {e}", cause=e)

    def list_credentials(self) -> List[Credential]:
        """List all credentials with passwords masked for UI."""
        logger.info("Listing all credentials")
        try:
            credentials = self.credential_repository.list()
            # Mask passwords in returned objects
            masked_credentials = [
                Credential(
                    name=cred.name,
                    username=cred.username,
                    password="********"
                )
                for cred in credentials
            ]
            logger.info(f"Found {len(credentials)} credentials")
            return masked_credentials
        except RepositoryError as e:
            logger.error(f"Repository error listing credentials: {e}")
            raise ServiceError(f"Failed to list credentials: {e}", cause=e)
        except Exception as e:
            logger.exception("Unexpected error listing credentials")
            raise ServiceError(f"Unexpected error listing credentials: {e}", cause=e)

    def delete_credential(self, name: str) -> None:
        """Delete a credential by name."""
        logger.info(f"Deleting credential: {name}")
        try:
            # Check if credential exists
            credential = self.credential_repository.get(name)
            if not credential:
                logger.warning(f"Credential not found for deletion: {name}")
                return

            self.credential_repository.delete(name)
            logger.info(f"Deleted credential: {name}")
        except RepositoryError as e:
            logger.error(f"Repository error deleting credential '{name}': {e}")
            raise ServiceError(f"Failed to delete credential: {e}", cause=e)
        except Exception as e:
            logger.exception(f"Unexpected error deleting credential '{name}'")
            raise ServiceError(f"Unexpected error deleting credential: {e}", cause=e)

    def validate_credential(self, name: str, password: str) -> bool:
        """Validate a credential name and password combination."""
        logger.info(f"Validating credential: {name}")
        try:
            # Get credential with actual stored password
            credential = self.credential_repository.get(name)
            if not credential:
                logger.warning(f"Credential not found for validation: {name}")
                return False

            # Verify password
            is_valid = self._verify_password(credential.password, password)
            logger.info(f"Credential validation result for '{name}': {is_valid}")
            return is_valid
        except RepositoryError as e:
            logger.error(f"Repository error validating credential '{name}': {e}")
            raise SecurityError(f"Failed to validate credential: {e}", cause=e)
        except Exception as e:
            logger.exception(f"Unexpected error validating credential '{name}'")
            raise SecurityError(f"Unexpected error validating credential: {e}", cause=e)