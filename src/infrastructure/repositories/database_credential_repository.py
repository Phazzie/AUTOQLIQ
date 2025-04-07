"""Database credential repository implementation for AutoQliq."""
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

# Core dependencies
from src.core.interfaces import ICredentialRepository # Correct interface import
from src.core.exceptions import CredentialError, RepositoryError, ValidationError

# Infrastructure dependencies
from src.infrastructure.common.error_handling import handle_exceptions
from src.infrastructure.common.logging_utils import log_method_call
from src.infrastructure.common.validators import CredentialValidator # Use common validator
from src.infrastructure.repositories.base.database_repository import DatabaseRepository # Correct base class import

logger = logging.getLogger(__name__)

class DatabaseCredentialRepository(DatabaseRepository[Dict[str, str]], ICredentialRepository):
    """
    Implementation of ICredentialRepository storing credentials in an SQLite database.

    Manages CRUD operations for credentials. Assumes passwords provided to `save`
    are already appropriately hashed/encrypted by the calling service layer.

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
            **options (Any): Additional options (currently unused).
        """
        super().__init__(db_path=db_path, table_name=self._TABLE_NAME, logger_name=__name__)
        # Base constructor calls _create_table_if_not_exists

    def _get_primary_key_col(self) -> str:
        """Return the primary key column name for this repository."""
        return self._PK_COLUMN

    def _get_table_creation_sql(self) -> str:
        """Return the SQL for creating the credentials table columns."""
        # Storing password hash/value as TEXT
        return f"""
            {self._PK_COLUMN} TEXT PRIMARY KEY NOT NULL,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            created_at TEXT NOT NULL,
            modified_at TEXT NOT NULL
        """

    def _map_row_to_entity(self, row: Dict[str, Any]) -> Dict[str, str]:
        """Convert a database row to a credential dictionary."""
        name = row.get(self._PK_COLUMN)
        username = row.get("username")
        password_stored = row.get("password")

        if name is None or username is None or password_stored is None:
            missing = [col for col in [self._PK_COLUMN, "username", "password"] if row.get(col) is None]
            raise RepositoryError(f"DB row missing expected columns: {missing}", entity_id=name or "<unknown>")

        return {
            "name": str(name),
            "username": str(username),
            "password": str(password_stored) # Return the stored hash/value
        }

    def _map_entity_to_params(self, entity_id: str, entity: Dict[str, str]) -> Dict[str, Any]:
        """Convert credential dictionary (expecting prepared password) to DB parameters."""
        # Validate structure first (raises CredentialError)
        CredentialValidator.validate_credential_data(entity)
        if entity_id != entity.get("name"):
            raise ValidationError(f"Entity ID '{entity_id}' != name '{entity.get('name')}' in data.")

        password_to_store = entity["password"] # Assume this is ready for storage (e.g., hash)

        now = datetime.now().isoformat()
        return {
            self._PK_COLUMN: entity["name"],
            "username": entity["username"],
            "password": password_to_store,
            "created_at": now,
            "modified_at": now
        }

    # --- ICredentialRepository Implementation ---

    @log_method_call(logger)
    @handle_exceptions(CredentialError, "Error saving credential", reraise_types=(CredentialError, ValidationError, RepositoryError))
    def save(self, credential: Dict[str, str]) -> None:
        """Save (create or update) a credential. Assumes password in dict is prepared."""
        credential_name = credential.get('name')
        if not credential_name:
            raise ValidationError("Credential data must include a 'name'.")
        # Name validation happens in base class save -> _validate_entity_id
        # Data validation happens in _map_entity_to_params -> CredentialValidator
        super().save(credential_name, credential) # Base handles UPSERT

    @log_method_call(logger)
    @handle_exceptions(CredentialError, "Error retrieving credential", reraise_types=(CredentialError, ValidationError, RepositoryError))
    def get_by_name(self, name: str) -> Optional[Dict[str, str]]:
        """Get credential details (including password hash) by name."""
        # Base class get handles ID validation, DB query, and mapping
        return super().get(name)

    @log_method_call(logger)
    @handle_exceptions(CredentialError, "Error deleting credential", reraise_types=(CredentialError, ValidationError, RepositoryError))
    def delete(self, name: str) -> bool:
        """Delete a credential by name."""
        # Base class delete handles ID validation and DB deletion
        return super().delete(name)

    @log_method_call(logger)
    @handle_exceptions(CredentialError, "Error listing credentials", reraise_types=(RepositoryError,))
    def list_credentials(self) -> List[str]:
        """List the names of all stored credentials."""
        # Base class list handles DB query for primary key column
        return super().list()