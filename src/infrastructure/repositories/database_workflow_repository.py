"""Database workflow repository implementation for AutoQliq."""
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

# Core interfaces, exceptions, and common utilities
from src.core.interfaces.repository import IWorkflowRepository
from src.core.interfaces.action import IAction
from src.core.exceptions import WorkflowError, RepositoryError, SerializationError, ValidationError
from src.infrastructure.common.error_handling import handle_exceptions
from src.infrastructure.common.logging_utils import log_method_call
from src.infrastructure.common.validators import WorkflowValidator
from src.infrastructure.repositories.base.database_repository import DatabaseRepository
from src.infrastructure.repositories.serialization.action_serializer import (
    serialize_actions,
    deserialize_actions
)

logger = logging.getLogger(__name__)

class DatabaseWorkflowRepository(DatabaseRepository[List[IAction]], IWorkflowRepository):
    """
    Implementation of IWorkflowRepository storing workflows in an SQLite database.

    Stores workflow actions as a JSON string in a dedicated column.

    Attributes:
        db_path (str): Path to the SQLite database file.
        table_name (str): Name of the workflows table ("workflows").
    """
    _TABLE_NAME = "workflows"
    _PK_COLUMN = "name" # Primary key column name

    def __init__(self, db_path: str, **options: Any):
        """
        Initialize a new DatabaseWorkflowRepository.

        Args:
            db_path (str): Path to the SQLite database file.
            **options (Any): Additional options (currently unused).
        """
        super().__init__(db_path=db_path, table_name=self._TABLE_NAME, logger_name=__name__)
        # Base class constructor calls _create_table_if_not_exists -> _get_table_creation_sql

    def _get_primary_key_col(self) -> str:
        """Return the primary key column name for this repository."""
        return self._PK_COLUMN

    def _get_table_creation_sql(self) -> str:
        """Return the SQL for creating the workflows table columns."""
        # Store actions as JSON text
        return f"""
            {self._PK_COLUMN} TEXT PRIMARY KEY NOT NULL,
            actions_json TEXT NOT NULL,
            created_at TEXT NOT NULL,
            modified_at TEXT NOT NULL
        """

    def _map_row_to_entity(self, row: Dict[str, Any]) -> List[IAction]:
        """Convert a database row (containing actions JSON) to a list of IAction."""
        actions_json = row.get("actions_json")
        workflow_name = row.get(self._PK_COLUMN, "<unknown>") # For error context
        if actions_json is None:
            # Should not happen if column is NOT NULL, but handle defensively
            self.logger.error(f"Missing 'actions_json' data for workflow '{workflow_name}'.")
            raise RepositoryError(f"Missing action data for workflow '{workflow_name}'.", entity_id=workflow_name)

        try:
            # Deserialize the JSON string into a list of action dictionaries
            action_data_list = json.loads(actions_json)
            if not isinstance(action_data_list, list):
                 raise json.JSONDecodeError(f"Stored actions data is not a JSON list, type is {type(action_data_list).__name__}.", actions_json, 0)
            # Deserialize the list of dictionaries into IAction objects
            return deserialize_actions(action_data_list) # Raises SerializationError on failure
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON format in actions data for workflow '{workflow_name}': {e}"
            self.logger.error(error_msg)
            raise SerializationError(error_msg, cause=e) from e
        except SerializationError as e:
            # Error during action deserialization (e.g., unknown type)
            error_msg = f"Failed to deserialize actions for workflow '{workflow_name}': {e}"
            self.logger.error(error_msg)
            # Re-raise as SerializationError or wrap in RepositoryError? Stick with SerializationError.
            raise SerializationError(error_msg, cause=e.cause or e) from e
        except Exception as e:
             # Catch any other unexpected error during deserialization
             error_msg = f"Unexpected error processing actions for workflow '{workflow_name}': {e}"
             self.logger.error(error_msg, exc_info=True)
             raise RepositoryError(error_msg, entity_id=workflow_name, cause=e) from e


    def _map_entity_to_params(self, entity_id: str, entity: List[IAction]) -> Dict[str, Any]:
        """Convert a list of IAction into database parameters, serializing actions to JSON."""
        # Validate workflow name (entity_id) and actions list
        WorkflowValidator.validate_workflow_name(entity_id) # Raises ValidationError
        WorkflowValidator.validate_actions(entity) # Raises ValidationError

        try:
            # Serialize the list of actions into a list of dictionaries
            action_data_list = serialize_actions(entity) # Raises SerializationError
            # Convert the list of dictionaries to a JSON string
            actions_json = json.dumps(action_data_list)
        except SerializationError as e:
             # Error during action serialization
             error_msg = f"Failed to serialize actions for workflow '{entity_id}': {e}"
             self.logger.error(error_msg)
             raise SerializationError(error_msg, cause=e.cause or e) from e
        except TypeError as e: # Catch json.dumps errors
             error_msg = f"Data for workflow '{entity_id}' is not JSON serializable: {e}"
             self.logger.error(error_msg, exc_info=True)
             raise SerializationError(error_msg, cause=e) from e
        except Exception as e:
             # Catch other unexpected errors
             error_msg = f"Unexpected error serializing actions for workflow '{entity_id}': {e}"
             self.logger.error(error_msg, exc_info=True)
             raise SerializationError(error_msg, cause=e) from e

        now = datetime.now().isoformat()
        return {
            self._PK_COLUMN: entity_id,
            "actions_json": actions_json,
            "created_at": now, # Ignored on UPDATE by base class UPSERT logic
            "modified_at": now # Base class UPSERT uses this
        }

    # --- IWorkflowRepository Method Implementations ---

    @log_method_call(logger)
    @handle_exceptions(WorkflowError, "Error saving workflow", reraise_types=(WorkflowError, RepositoryError, SerializationError, ValidationError))
    def save(self, name: str, workflow_actions: List[IAction]) -> None:
        """Save (create or update) a workflow."""
        # Validation happens in _map_entity_to_params called by base save
        super().save(name, workflow_actions) # Uses base DatabaseRepository.save

    @log_method_call(logger)
    @handle_exceptions(WorkflowError, "Error loading workflow", reraise_types=(WorkflowError, RepositoryError, SerializationError, ValidationError))
    def load(self, name: str) -> List[IAction]:
        """Load a workflow by its unique name."""
        # Base class get handles retrieval and calls _map_row_to_entity for deserialization
        actions = super().get(name) # Uses base DatabaseRepository.get
        if actions is None:
             raise WorkflowError(f"Workflow not found: '{name}'", workflow_name=name)
        return actions

    @log_method_call(logger)
    @handle_exceptions(WorkflowError, "Error deleting workflow", reraise_types=(WorkflowError, RepositoryError, ValidationError))
    def delete(self, name: str) -> bool:
        """Delete a workflow by its name."""
        # Uses base DatabaseRepository.delete
        return super().delete(name)

    @log_method_call(logger)
    @handle_exceptions(WorkflowError, "Error listing workflows", reraise_types=(WorkflowError, RepositoryError))
    def list_workflows(self) -> List[str]:
        """List the names of all stored workflows."""
         # Uses base DatabaseRepository.list
        return super().list()

    @log_method_call(logger)
    @handle_exceptions(WorkflowError, "Error getting workflow metadata", reraise_types=(WorkflowError, RepositoryError, ValidationError))
    def get_metadata(self, name: str) -> Dict[str, Any]:
        """Get metadata for a workflow (e.g., creation/modification times)."""
        self._validate_entity_id(name, entity_type="Workflow") # Raises ValidationError
        self._log_operation("Getting metadata", name)
        try:
            # Select metadata columns
            query = f"SELECT {self._PK_COLUMN}, created_at, modified_at FROM {self.table_name} WHERE {self._PK_COLUMN} = ?"
            rows = self.connection_manager.execute_query(query, (name,))

            if not rows:
                raise WorkflowError(f"Workflow not found: '{name}'", workflow_name=name)

            metadata = dict(rows[0])
            self.logger.debug(f"Successfully retrieved metadata for workflow: '{name}'")
            return metadata
        except RepositoryError as e:
             # Error during query execution
             raise WorkflowError(f"Database error getting metadata for workflow '{name}'", workflow_name=name, cause=e.cause) from e
        except Exception as e:
            # Catch other unexpected errors
            error_msg = f"Failed to get metadata for workflow: '{name}'"
            self.logger.error(error_msg, exc_info=True)
            # Don't raise RepositoryError directly if WorkflowError is more appropriate
            if isinstance(e, WorkflowError): raise
            raise WorkflowError(error_msg, workflow_name=name, cause=e) from e

    @log_method_call(logger)
    @handle_exceptions(WorkflowError, "Error creating empty workflow", reraise_types=(WorkflowError, RepositoryError, ValidationError))
    def create_workflow(self, name: str) -> None:
        """Create a new, empty workflow entry."""
        self._validate_entity_id(name, entity_type="Workflow") # Raises ValidationError
        self._log_operation("Creating empty workflow", name)

        # Check if it already exists first to provide a clearer error
        # Need to use get() carefully to avoid raising WorkflowError if not found
        try:
            existing = super().get(name) # Use base get which returns None if not found
            if existing is not None:
                raise WorkflowError(f"Workflow '{name}' already exists.", workflow_name=name)
        except RepositoryError as e:
             # Handle potential DB error during the check
             raise WorkflowError(f"Error checking existence of workflow '{name}'", workflow_name=name, cause=e.cause) from e


        try:
            # Save with an empty list of actions. Use base save which calls _map_entity_to_params.
            super().save(name, [])
            self.logger.info(f"Successfully created empty workflow: '{name}'")
        except (RepositoryError, SerializationError, ValidationError) as e:
             # Catch potential errors from save() -> _map_entity_to_params -> validation/serialization
             error_msg = f"Failed to create empty workflow '{name}': {e}"
             # Log details if not already logged by save() or helpers
             self.logger.error(error_msg, exc_info=True)
             # Re-raise wrapped error
             raise WorkflowError(error_msg, workflow_name=name, cause=e) from e
        except Exception as e:
             # Catch other unexpected errors
             error_msg = f"Unexpected error creating empty workflow '{name}': {e}"
             self.logger.error(error_msg, exc_info=True)
             raise WorkflowError(error_msg, workflow_name=name, cause=e) from e