"""Credential service implementation for AutoQliq."""
import logging
from typing import Dict, List, Any, Optional

# Use werkzeug for hashing - ensure it's in requirements.txt
try:
    from werkzeug.security import generate_password_hash, check_password_hash
    WERKZEUG_AVAILABLE = True
except ImportError:
    logging.getLogger(__name__).critical(
        "Werkzeug library not found. Password hashing disabled. Install using: pip install werkzeug"
    )
    WERKZEUG_AVAILABLE = False
    # Define dummy functions if werkzeug is not installed to avoid crashing
    # WARNING: This is insecure and only for preventing startup failure.
    def generate_password_hash(password: str, method: str = 'plaintext', salt_length: int = 0) -> str: # type: ignore
        logging.error("Werkzeug not found. Storing password as plain text (INSECURE).")
        return f"plaintext:{password}"
    def check_password_hash(pwhash: Optional[str], password: str) -> bool: # type: ignore
        logging.error("Werkzeug not found. Checking password against plain text (INSECURE).")
        if pwhash is None: return False
        if pwhash.startswith("plaintext:"):
             return pwhash[len("plaintext:"):] == password
        return False # Cannot check real hashes without werkzeug

# Core dependencies
from src.core.interfaces import ICredentialRepository
from src.core.interfaces.service import ICredentialService
from src.core.exceptions import CredentialError, ValidationError, AutoQliqError, RepositoryError

# Common utilities
from src.infrastructure.common.error_handling import handle_exceptions
from src.infrastructure.common.logging_utils import log_method_call
# Configuration
from src.config import config # Import configured instance

logger = logging.getLogger(__name__)


class CredentialService(ICredentialService):
    """
    Implementation of ICredentialService. Manages credential lifecycle including hashing.
    Uses werkzeug for password hashing if available.
    """

    def __init__(self, credential_repository: ICredentialRepository):
        """Initialize a new CredentialService."""
        if credential_repository is None:
            raise ValueError("Credential repository cannot be None.")
        self.credential_repository = credential_repository
        # Load hashing config only if werkzeug is available
        self.hash_method = config.password_hash_method if WERKZEUG_AVAILABLE else 'plaintext'
        self.salt_length = config.password_salt_length if WERKZEUG_AVAILABLE else 0
        logger.info(f"CredentialService initialized. Hashing available: {WERKZEUG_AVAILABLE}")
        if not WERKZEUG_AVAILABLE:
             logger.critical("SECURITY WARNING: Werkzeug not installed, passwords stored/checked as plaintext.")

    @log_method_call(logger)
    @handle_exceptions(CredentialError, "Failed to create credential", reraise_types=(CredentialError, ValidationError, RepositoryError))
    def create_credential(self, name: str, username: str, password: str) -> bool:
        """Create a new credential, storing a hashed password."""
        logger.info(f"Attempting to create credential: {name}")
        if not name or not username or not password:
             raise ValidationError("Credential name, username, and password cannot be empty.")

        # Check if credential already exists
        existing = self.credential_repository.get_by_name(name) # Repo handles name validation
        if existing:
             raise CredentialError(f"Credential '{name}' already exists.", credential_name=name)

        try:
            # Hash the password before saving
            hashed_password = generate_password_hash(password, method=self.hash_method, salt_length=self.salt_length)
            logger.debug(f"Password hashed for credential '{name}'.")
        except Exception as hash_e:
             logger.error(f"Password hashing failed for credential '{name}': {hash_e}", exc_info=True)
             raise CredentialError(f"Failed to secure password for credential '{name}'.", credential_name=name, cause=hash_e) from hash_e

        credential_data = {"name": name, "username": username, "password": hashed_password}
        # Repository save handles actual storage and potential underlying errors
        self.credential_repository.save(credential_data)
        logger.info(f"Credential '{name}' created successfully.")
        return True

    @log_method_call(logger)
    @handle_exceptions(CredentialError, "Failed to delete credential", reraise_types=(CredentialError, ValidationError, RepositoryError))
    def delete_credential(self, name: str) -> bool:
        """Delete a credential by name."""
        logger.info(f"Attempting to delete credential: {name}")
        deleted = self.credential_repository.delete(name) # Repo handles validation and storage
        if deleted:
            logger.info(f"Credential '{name}' deleted successfully.")
        else:
            logger.warning(f"Credential '{name}' not found for deletion.")
        return deleted

    @log_method_call(logger)
    @handle_exceptions(CredentialError, "Failed to retrieve credential details", reraise_types=(CredentialError, ValidationError, RepositoryError))
    def get_credential(self, name: str) -> Optional[Dict[str, str]]:
        """Get credential details (including password hash) by name."""
        logger.debug(f"Retrieving credential details (incl. hash): {name}")
        credential = self.credential_repository.get_by_name(name) # Repo handles validation
        if credential:
             logger.debug(f"Credential '{name}' details found.")
        else:
             logger.debug(f"Credential '{name}' not found.")
        # WARNING: Returns the HASH, not the plain password
        return credential

    @log_method_call(logger)
    @handle_exceptions(CredentialError, "Failed to list credentials", reraise_types=(RepositoryError,))
    def list_credentials(self) -> List[str]:
        """Get a list of available credential names."""
        logger.debug("Listing all credentials.")
        names = self.credential_repository.list_credentials() # Repo handles storage interaction
        logger.debug(f"Found {len(names)} credentials.")
        return names

    @log_method_call(logger)
    @handle_exceptions(CredentialError, "Failed to verify credential", reraise_types=(CredentialError, ValidationError, RepositoryError))
    def verify_credential(self, name: str, password_to_check: str) -> bool:
        """Verify if the provided password matches the stored hash for the credential."""
        logger.info(f"Verifying password for credential: {name}")
        if not password_to_check:
             logger.warning(f"Password check for '{name}' attempted with empty password.")
             return False

        # Get the stored credential (contains the hash)
        credential_data = self.credential_repository.get_by_name(name) # Repo handles name validation
        if not credential_data:
             logger.warning(f"Credential '{name}' not found for verification.")
             return False

        stored_hash = credential_data.get("password")
        if not stored_hash:
             logger.error(f"Stored credential '{name}' is missing password hash.")
             return False

        try:
             # Use check_password_hash to compare
             is_match = check_password_hash(stored_hash, password_to_check)
             if is_match:
                 logger.info(f"Password verification successful for credential '{name}'.")
             else:
                 logger.warning(f"Password verification failed for credential '{name}'.")
             return is_match
        except Exception as check_e:
            # Handle potential errors during hash checking (e.g., malformed hash, library errors)
            logger.error(f"Error during password hash check for credential '{name}': {check_e}", exc_info=True)
            # Treat check errors as verification failure
            return False