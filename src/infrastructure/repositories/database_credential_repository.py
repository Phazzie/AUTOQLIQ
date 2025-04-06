"""Database credential repository implementation for AutoQliq."""
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

# Core interfaces, exceptions, and common utilities
from src.core.interfaces.repository import ICredentialRepository
from src.core.exceptions import CredentialError, RepositoryError, ValidationError
from src.infrastructure.common.error_handling import handle_exceptions
from src.infrastructure.common.logging_utils import log_method_call
from src.infrastructure.common.validators import CredentialValidator
from src.infrastructure.repositories.base.database_repository import DatabaseRepository

logger = logging.getLogger(__name__)

class DatabaseCredentialRepository(DatabaseRepository[Dict[str, str]], ICredentialRepository):
    """
    Implementation of ICredentialRepository storing credentials in an SQLite database.

    Manages CRUD operations for credentials. Passwords are stored as plain text
    currently and require hashing/encryption for production use.

    Attributes:
        db_path (str): Path to the SQLite database file.
        table_name (str): Name of the credentials table ("credentials").
    """
    _TABLE_NAME = "credentials"
    _PK_COLUMN = "name" # Primary key column name

    def __init__(self, db_path: str, **options: Any):
        """
        Initialize a new DatabaseCredentialRepository.

        Args:
            db_path (str): Path to the SQLite database file.
            **options (Any): Additional options (currently unused but kept for signature consistency).
        """
        # Pass db_path, table name, and logger name to the base class
        super().__init__(db_path=db_path, table_name=self._TABLE_NAME, logger_name=__name__)
        # Base class constructor calls _create_table_if_not_exists -> _get_table_creation_sql

    def _get_primary_key_col(self) -> str:
        """Return the primary key column name for this repository."""
        return self._PK_COLUMN

    def _get_table_creation_sql(self) -> str:
        """Return the SQL for creating the credentials table columns."""
        # Using TEXT for password, assuming it will be hashed/encrypted later
        return f"""
            {self._PK_COLUMN} TEXT PRIMARY KEY NOT NULL,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            created_at TEXT NOT NULL,
            modified_at TEXT NOT NULL
        """

    def _map_row_to_entity(self, row: Dict[str, Any]) -> Dict[str, str]:
        """Convert a database row to a credential dictionary."""
        # Ensure all expected columns are present
        name = row.get(self._PK_COLUMN)
        username = row.get("username")
        password = row.get("password") # Retrieve stored password

        if name is None or username is None or password is None:
            missing = [col for col in [self._PK_COLUMN, "username", "password"] if row.get(col) is None]
            raise RepositoryError(f"Database row is missing expected columns: {missing}", entity_id=name or "<unknown>")

        return {
            "name": str(name),
            "username": str(username),
            "password": str(password)
            # We don't typically return created_at/modified_at in the entity dict
        }

    def _map_entity_to_params(self, entity_id: str, entity: Dict[str, str]) -> Dict[str, Any]:
        """Convert a credential dictionary to database parameters, including timestamps."""
        # Validate before mapping (raises CredentialError/ValidationError if invalid)
        CredentialValidator.validate_credential_data(entity)
        # Ensure entity_id matches the name in the dictionary
        if entity_id != entity.get("name"):
            raise ValidationError(f"Entity ID '{entity_id}' does not match name '{entity.get('name')}' in credential data.")

        now = datetime.now().isoformat()
        # WARNING: Storing password directly! Needs hashing/encryption in production.
        # password_to_store = hash_password(entity["password"]) # Replace with actual hashing
        password_to_store = entity["password"]
        logger.warning(f"Storing credential '{entity_id}' password in plain text. Implement hashing.")

        return {
            self._PK_COLUMN: entity["name"],
            "username": entity["username"],
            "password": password_to_store,
            "created_at": now, # Base class UPSERT ignores this on conflict
            "modified_at": now # Base class UPSERT uses this
        }

    # --- ICredentialRepository Method Implementations ---

    @log_method_call(logger)
    @handle_exceptions(CredentialError, "Error saving credential", reraise_types=(CredentialError, RepositoryError, ValidationError))
    def save(self, credential: Dict[str, str]) -> None:
        """Save (create or update) a credential."""
        # Validate first (also done in _map_entity_to_params, but good practice here too)
        CredentialValidator.validate_credential_data(credential) # Raises CredentialError
        credential_name = credential['name']
        # Use the base class save method which handles UPSERT and logging
        # _map_entity_to_params within base save will handle final validation and mapping
        super().save(credential_name, credential)

    @log_method_call(logger)
    @handle_exceptions(CredentialError, "Error retrieving credential", reraise_types=(CredentialError, RepositoryError, ValidationError))
    def get_by_name(self, name: str) -> Optional[Dict[str, str]]:
        """Get a credential by its unique name."""
        # Use the base class get method; it validates ID and handles RepositoryError
        # _map_row_to_entity handles conversion
        return super().get(name) # Raises ValidationError if name invalid

    @log_method_call(logger)
    @handle_exceptions(CredentialError, "Error deleting credential", reraise_types=(CredentialError, RepositoryError, ValidationError))
    def delete(self, name: str) -> bool:
        """Delete a credential by its name."""
        # Use the base class delete method; it validates ID and handles RepositoryError
        return super().delete(name) # Raises ValidationError if name invalid

    @log_method_call(logger)
    @handle_exceptions(CredentialError, "Error listing credentials", reraise_types=(CredentialError, RepositoryError))
    def list_credentials(self) -> List[str]:
        """List the names of all stored credentials."""
        # Use the base class list method; it handles RepositoryError
        return super().list()