"""Abstract base class for SQLite database repository implementations."""
import abc
import logging
from typing import Any, Dict, List, Optional, TypeVar, Generic

# Assuming core interfaces, exceptions, and common utilities are defined
# No direct dependency on IRepository interface here, concrete classes implement specific ones
from src.core.exceptions import RepositoryError, ValidationError
from src.infrastructure.common.database_connection import ConnectionManager
from src.infrastructure.common.logger_factory import LoggerFactory
from src.infrastructure.common.validators import EntityValidator

# Type variable for the entity type managed by the repository
T = TypeVar('T')

class DatabaseRepository(Generic[T], abc.ABC):
    """
    Abstract base class for repositories using an SQLite database backend.

    Provides common database interaction logic, connection management, and
    requires subclasses to implement entity-specific SQL operations and mappings.

    Attributes:
        db_path (str): Path to the SQLite database file.
        connection_manager (ConnectionManager): Manages database connections.
        table_name (str): Name of the primary table for the entity.
        logger (logging.Logger): Logger instance for the specific repository subclass.
    """

    def __init__(self, db_path: str, table_name: str, logger_name: Optional[str] = None):
        """
        Initialize a new DatabaseRepository.

        Args:
            db_path (str): Path to the SQLite database file.
            table_name (str): Name of the primary table for the entity.
            logger_name (Optional[str]): Name for the logger. Defaults to subclass name.

        Raises:
            ValueError: If db_path or table_name is empty.
        """
        if logger_name is None:
             logger_name = self.__class__.__name__
        self.logger = LoggerFactory.get_logger(f"repository.{logger_name}")

        if not db_path:
            self.logger.error("Database path cannot be empty.")
            raise ValueError("Database path cannot be empty.")
        if not table_name:
            self.logger.error("Table name cannot be empty.")
            raise ValueError("Table name cannot be empty.")

        self.db_path = db_path
        self.table_name = table_name
        self.connection_manager = ConnectionManager(self.db_path) # Instantiate ConnectionManager here
        self.logger.info(f"{self.__class__.__name__} for table '{table_name}' initialized with db: {db_path}")
        self._create_table_if_not_exists()

    # --- Abstract methods for subclasses to implement ---

    @abc.abstractmethod
    def _get_table_creation_sql(self) -> str:
        """
        Return the SQL statement fragment for creating the entity table columns.
        Example: "id TEXT PRIMARY KEY, name TEXT NOT NULL, data TEXT"
        """
        pass

    @abc.abstractmethod
    def _map_row_to_entity(self, row: Dict[str, Any]) -> T:
        """
        Convert a database row (dictionary) to an entity object.
        """
        pass

    @abc.abstractmethod
    def _map_entity_to_params(self, entity_id: str, entity: T) -> Dict[str, Any]:
        """
        Convert an entity object into a dictionary of parameters suitable for an INSERT or UPDATE query.
        The dictionary keys should match the column names. The entity_id should also be included.
        """
        pass

    @abc.abstractmethod
    def _get_primary_key_col(self) -> str:
        """
        Return the name of the primary key column for this repository's table.
        """
        pass

    # --- Concrete Base Methods providing core functionality ---

    def _create_table_if_not_exists(self) -> None:
        """Create the database table using SQL from subclass if it doesn't exist."""
        try:
            columns_sql = self._get_table_creation_sql()
            if not columns_sql:
                 # This indicates a programming error in the subclass
                 raise NotImplementedError(f"{self.__class__.__name__} must implement _get_table_creation_sql and return SQL.")
            self.connection_manager.create_table(self.table_name, columns_sql)
        except RepositoryError as e:
            # Log repository errors during table creation (e.g., connection issues)
            self.logger.error(f"Repository error ensuring table '{self.table_name}' exists: {e}", exc_info=False) # Don't need full traceback for expected errors
            raise # Re-raise to indicate failure
        except Exception as e:
            # Log unexpected errors
            self.logger.error(f"Unexpected error ensuring table '{self.table_name}' exists: {e}", exc_info=True)
            # Wrap in RepositoryError
            raise RepositoryError(f"Failed to initialize table '{self.table_name}'", cause=e) from e

    def save(self, entity_id: str, entity: T) -> None:
        """Save (INSERT or UPDATE) an entity to the database using UPSERT."""
        self._validate_entity_id(entity_id)
        self._log_operation("Saving", entity_id)
        try:
            params = self._map_entity_to_params(entity_id, entity)
            columns = list(params.keys())
            placeholders = ", ".join("?" * len(params))
            pk_col = self._get_primary_key_col()

            # Filter out the PK column for the UPDATE part
            update_cols = [col for col in columns if col != pk_col]
            if not update_cols:
                 # Handle case where entity might only have a PK (unlikely but possible)
                 self.logger.warning(f"Entity '{entity_id}' has no columns to update besides primary key.")
                 # Just attempt an INSERT IGNORE or similar if needed, or simply return if exists
                 # For simplicity, we'll rely on INSERT ON CONFLICT which will do nothing if only PK matches
                 pass

            updates = ", ".join(f"{col} = ?" for col in update_cols)

            # Construct the UPSERT query (SQLite specific syntax)
            query = f"""
                INSERT INTO {self.table_name} ({', '.join(columns)})
                VALUES ({placeholders})
                ON CONFLICT({pk_col}) DO UPDATE SET
                {updates}
            """
            # Prepare values: first all values for INSERT, then non-PK values for UPDATE
            values = list(params.values())
            update_values = [v for k, v in params.items() if k != pk_col]
            final_params = tuple(values + update_values)

            affected_rows = self.connection_manager.execute_modification(query, final_params)
            self.logger.info(f"Successfully saved entity '{entity_id}'. Affected rows: {affected_rows}")

        except ValidationError as e:
            # Catch validation errors from mapping/validation steps
            self.logger.error(f"Validation failed while saving entity '{entity_id}': {e}")
            raise # Re-raise validation errors directly
        except RepositoryError:
            # Re-raise repository errors (e.g., DB connection) from execute_modification
            raise
        except Exception as e:
            error_msg = f"Failed to save entity with ID: '{entity_id}'"
            self.logger.error(error_msg, exc_info=True)
            raise RepositoryError(error_msg, entity_id=entity_id, cause=e) from e

    def get(self, entity_id: str) -> Optional[T]:
        """Get an entity from the database by its primary key."""
        self._validate_entity_id(entity_id)
        self._log_operation("Getting", entity_id)
        try:
            pk_col = self._get_primary_key_col()
            query = f"SELECT * FROM {self.table_name} WHERE {pk_col} = ?"
            rows = self.connection_manager.execute_query(query, (entity_id,))

            if not rows:
                self.logger.debug(f"Entity not found with ID: '{entity_id}'")
                return None

            if len(rows) > 1:
                 # Should not happen with primary key constraint, indicates schema issue
                 self.logger.warning(f"Found multiple entities for primary key '{entity_id}'. Returning the first.")

            entity = self._map_row_to_entity(rows[0])
            self.logger.debug(f"Successfully retrieved entity with ID: '{entity_id}'")
            return entity
        except ValidationError as e:
             self.logger.error(f"Validation failed while getting entity '{entity_id}': {e}")
             raise # Re-raise validation errors directly
        except RepositoryError:
             raise # Re-raise repository errors (e.g., DB connection)
        except Exception as e:
            error_msg = f"Failed to get entity with ID: '{entity_id}'"
            self.logger.error(error_msg, exc_info=True)
            raise RepositoryError(error_msg, entity_id=entity_id, cause=e) from e

    def delete(self, entity_id: str) -> bool:
        """Delete an entity from the database by its primary key."""
        self._validate_entity_id(entity_id)
        self._log_operation("Deleting", entity_id)
        try:
            pk_col = self._get_primary_key_col()
            query = f"DELETE FROM {self.table_name} WHERE {pk_col} = ?"
            affected_rows = self.connection_manager.execute_modification(query, (entity_id,))
            deleted = affected_rows > 0

            if deleted:
                self.logger.info(f"Successfully deleted entity with ID: '{entity_id}'")
            else:
                self.logger.warning(f"Attempted to delete non-existent entity with ID: '{entity_id}'")
            return deleted
        except ValidationError as e:
             self.logger.error(f"Validation failed while deleting entity '{entity_id}': {e}")
             raise # Re-raise validation errors directly
        except RepositoryError:
             raise # Re-raise repository errors (e.g., DB connection)
        except Exception as e:
            error_msg = f"Failed to delete entity with ID: '{entity_id}'"
            self.logger.error(error_msg, exc_info=True)
            raise RepositoryError(error_msg, entity_id=entity_id, cause=e) from e

    def list(self) -> List[str]:
        """List all entity primary keys from the database."""
        self._log_operation("Listing IDs")
        try:
            pk_col = self._get_primary_key_col()
            query = f"SELECT {pk_col} FROM {self.table_name} ORDER BY {pk_col}"
            rows = self.connection_manager.execute_query(query)
            # Ensure the primary key column exists in the results
            if rows and pk_col not in rows[0]:
                 raise RepositoryError(f"Primary key column '{pk_col}' not found in query results for table '{self.table_name}'.")
            ids = [row[pk_col] for row in rows]
            self.logger.debug(f"Successfully listed {len(ids)} entity IDs.")
            return ids
        except RepositoryError:
             raise # Re-raise repository errors (e.g., DB connection)
        except Exception as e:
            error_msg = "Failed to list entity IDs"
            self.logger.error(error_msg, exc_info=True)
            raise RepositoryError(error_msg, cause=e) from e

    # --- Common Helper Methods ---

    def _validate_entity_id(self, entity_id: str, entity_type: Optional[str] = None) -> None:
        """
        Validate the entity ID using common rules.

        Args:
            entity_id (str): The ID to validate.
            entity_type (Optional[str]): The type name of the entity (for error messages).
                                         Defaults based on class name if possible, else 'Entity'.

        Raises:
            ValidationError: If the entity ID is invalid.
        """
        if entity_type is None:
            # Try to infer from class name (e.g., "Workflow" from "WorkflowRepository")
            class_name = self.__class__.__name__
            if "Repository" in class_name:
                entity_type = class_name.replace("Database", "").replace("FileSystem", "").replace("Repository", "")
            else:
                entity_type = "Entity"

        # Use EntityValidator from common utils
        EntityValidator.validate_entity_id(entity_id, entity_type=entity_type)
        # No need to log here, validator or calling method can log

    def _log_operation(self, operation: str, entity_id: Optional[str] = None) -> None:
        """
        Log a repository operation.

        Args:
            operation (str): Description of the operation (e.g., "Saving", "Loading list").
            entity_id (Optional[str]): The ID of the entity involved, if applicable.
        """
        log_message = f"{operation} {self.table_name}"
        if entity_id:
            log_message += f" ID: '{entity_id}'"
        self.logger.debug(log_message)