"""Database workflow repository implementation for AutoQliq."""
import json
import logging
import sqlite3 # Import sqlite3 for specific DB errors if needed
from datetime import datetime
from typing import Any, Dict, List, Optional

# Core dependencies
from src.core.interfaces import IAction, IWorkflowRepository
from src.core.exceptions import WorkflowError, RepositoryError, SerializationError, ValidationError

# Infrastructure dependencies
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
    Implementation of IWorkflowRepository storing workflows and templates in SQLite.
    """
    _WF_TABLE_NAME = "workflows"
    _WF_PK_COLUMN = "name"
    _TMPL_TABLE_NAME = "templates"
    _TMPL_PK_COLUMN = "name"

    def __init__(self, db_path: str, **options: Any):
        """Initialize DatabaseWorkflowRepository."""
        super().__init__(db_path=db_path, table_name=self._WF_TABLE_NAME, logger_name=__name__)
        self._create_templates_table_if_not_exists()

    # --- Configuration for Workflows Table (via Base Class) ---
    def _get_primary_key_col(self) -> str: return self._WF_PK_COLUMN
    def _get_table_creation_sql(self) -> str:
        return f"{self._WF_PK_COLUMN} TEXT PRIMARY KEY NOT NULL, actions_json TEXT NOT NULL, created_at TEXT NOT NULL, modified_at TEXT NOT NULL"

    # --- Configuration and Creation for Templates Table ---
    def _get_templates_table_creation_sql(self) -> str:
         """Return SQL for creating the templates table."""
         # Added modified_at for templates as well
         return f"{self._TMPL_PK_COLUMN} TEXT PRIMARY KEY NOT NULL, actions_json TEXT NOT NULL, created_at TEXT NOT NULL, modified_at TEXT NOT NULL"

    def _create_templates_table_if_not_exists(self) -> None:
        """Create the templates table."""
        logger.debug("Ensuring templates table exists.")
        sql = self._get_templates_table_creation_sql()
        try: self.connection_manager.create_table(self._TMPL_TABLE_NAME, sql)
        except Exception as e: logger.error(f"Failed ensure table '{self._TMPL_TABLE_NAME}': {e}", exc_info=True)


    # --- Mapping for Workflows (Base Class uses these) ---
    def _map_row_to_entity(self, row: Dict[str, Any]) -> List[IAction]:
        """Convert a workflow table row to a list of IAction."""
        actions_json = row.get("actions_json"); name = row.get(self._WF_PK_COLUMN, "<unknown>")
        if actions_json is None: raise RepositoryError(f"Missing action data for workflow '{name}'.", entity_id=name)
        try:
            action_data_list = json.loads(actions_json)
            if not isinstance(action_data_list, list): raise json.JSONDecodeError("Not JSON list.", actions_json, 0)
            return deserialize_actions(action_data_list) # Raises SerializationError
        except json.JSONDecodeError as e: raise SerializationError(f"Invalid JSON in workflow '{name}': {e}", entity_id=name, cause=e) from e
        except Exception as e:
             if isinstance(e, SerializationError): raise
             raise RepositoryError(f"Error processing actions for workflow '{name}': {e}", entity_id=name, cause=e) from e

    def _map_entity_to_params(self, entity_id: str, entity: List[IAction]) -> Dict[str, Any]:
        """Convert list of IAction to workflow DB parameters."""
        WorkflowValidator.validate_workflow_name(entity_id)
        WorkflowValidator.validate_actions(entity)
        try:
            action_data_list = serialize_actions(entity) # Raises SerializationError
            actions_json = json.dumps(action_data_list)
        except (SerializationError, TypeError) as e: raise SerializationError(f"Failed serialize actions for workflow '{entity_id}'", entity_id=entity_id, cause=e) from e
        now = datetime.now().isoformat()
        return { self._WF_PK_COLUMN: entity_id, "actions_json": actions_json, "created_at": now, "modified_at": now }

    # --- IWorkflowRepository Implementation (using Base Class methods) ---
    @log_method_call(logger)
    @handle_exceptions(WorkflowError, "Error saving workflow", reraise_types=(WorkflowError, ValidationError, RepositoryError, SerializationError))
    def save(self, name: str, workflow_actions: List[IAction]) -> None: super().save(name, workflow_actions)

    @log_method_call(logger)
    @handle_exceptions(WorkflowError, "Error loading workflow", reraise_types=(WorkflowError, ValidationError, RepositoryError, SerializationError))
    def load(self, name: str) -> List[IAction]:
        actions = super().get(name)
        if actions is None: raise RepositoryError(f"Workflow not found: '{name}'", entity_id=name)
        return actions

    @log_method_call(logger)
    @handle_exceptions(WorkflowError, "Error deleting workflow", reraise_types=(WorkflowError, ValidationError, RepositoryError))
    def delete(self, name: str) -> bool: return super().delete(name)

    @log_method_call(logger)
    @handle_exceptions(WorkflowError, "Error listing workflows", reraise_types=(RepositoryError,))
    def list_workflows(self) -> List[str]: return super().list()

    @log_method_call(logger)
    @handle_exceptions(WorkflowError, "Error getting workflow metadata", reraise_types=(WorkflowError, ValidationError, RepositoryError))
    def get_metadata(self, name: str) -> Dict[str, Any]:
        self._validate_entity_id(name, entity_type="Workflow")
        self._log_operation("Getting metadata", name)
        try:
            query = f"SELECT {self._WF_PK_COLUMN}, created_at, modified_at FROM {self._WF_TABLE_NAME} WHERE {self._WF_PK_COLUMN} = ?"
            rows = self.connection_manager.execute_query(query, (name,))
            if not rows: raise RepositoryError(f"Workflow not found: {name}", entity_id=name)
            metadata = dict(rows[0]); metadata["source"] = "database"
            return metadata
        except RepositoryError: raise
        except Exception as e: raise RepositoryError(f"Failed get metadata for workflow '{name}'", entity_id=name, cause=e) from e

    @log_method_call(logger)
    @handle_exceptions(WorkflowError, "Error creating empty workflow", reraise_types=(WorkflowError, ValidationError, RepositoryError))
    def create_workflow(self, name: str) -> None:
        WorkflowValidator.validate_workflow_name(name)
        self._log_operation("Creating empty workflow", name)
        if super().get(name) is not None: raise RepositoryError(f"Workflow '{name}' already exists.", entity_id=name)
        try: super().save(name, []) # Save empty list
        except Exception as e: raise WorkflowError(f"Failed create empty workflow '{name}'", workflow_name=name, cause=e) from e

    # --- Template Methods (DB Implementation) ---

    @log_method_call(logger)
    @handle_exceptions(RepositoryError, "Error saving template", reraise_types=(ValidationError, RepositoryError, SerializationError))
    def save_template(self, name: str, actions_data: List[Dict[str, Any]]) -> None:
        """Save/Update an action template (serialized list) to the DB."""
        self._validate_entity_id(name, entity_type="Template") # Use base validator
        self._log_operation("Saving template", name)
        if not isinstance(actions_data, list) or not all(isinstance(item, dict) for item in actions_data):
             raise SerializationError("Template actions data must be list of dicts.")
        try: actions_json = json.dumps(actions_data)
        except TypeError as e: raise SerializationError(f"Data for template '{name}' not JSON serializable", entity_id=name, cause=e) from e

        now = datetime.now().isoformat()
        pk_col = self._TMPL_PK_COLUMN
        # Include modified_at for templates table as well
        params = {pk_col: name, "actions_json": actions_json, "created_at": now, "modified_at": now}
        columns = list(params.keys()); placeholders = ", ".join("?" * len(params))
        # Update actions_json and modified_at on conflict
        update_cols = ["actions_json", "modified_at"]
        updates = ", ".join(f"{col} = ?" for col in update_cols)
        query = f"""
            INSERT INTO {self._TMPL_TABLE_NAME} ({', '.join(columns)}) VALUES ({placeholders})
            ON CONFLICT({pk_col}) DO UPDATE SET {updates}
        """
        # Values: name, json, created, modified, json_update, modified_update
        final_params = (name, actions_json, now, now, actions_json, now)
        try:
            self.connection_manager.execute_modification(query, final_params)
            self.logger.info(f"Successfully saved template: '{name}'")
        except Exception as e: raise RepositoryError(f"DB error saving template '{name}'", entity_id=name, cause=e) from e


    @log_method_call(logger)
    @handle_exceptions(RepositoryError, "Error loading template", reraise_types=(ValidationError, RepositoryError, SerializationError))
    def load_template(self, name: str) -> List[Dict[str, Any]]:
        """Load serialized action data for a template from the DB."""
        self._validate_entity_id(name, entity_type="Template")
        self._log_operation("Loading template", name)
        query = f"SELECT actions_json FROM {self._TMPL_TABLE_NAME} WHERE {self._TMPL_PK_COLUMN} = ?"
        try:
            rows = self.connection_manager.execute_query(query, (name,))
            if not rows: raise RepositoryError(f"Template not found: {name}", entity_id=name)
            actions_json = rows[0]["actions_json"]
            actions_data = json.loads(actions_json) # Raises JSONDecodeError
            if not isinstance(actions_data, list): raise SerializationError(f"Stored template '{name}' not JSON list.", entity_id=name)
            if not all(isinstance(item, dict) for item in actions_data): raise SerializationError(f"Stored template '{name}' contains non-dict items.", entity_id=name)
            return actions_data
        except RepositoryError: raise
        except json.JSONDecodeError as e: raise SerializationError(f"Invalid JSON in template '{name}'", entity_id=name, cause=e) from e
        except Exception as e: raise RepositoryError(f"DB error loading template '{name}'", entity_id=name, cause=e) from e


    @log_method_call(logger)
    @handle_exceptions(RepositoryError, "Error deleting template", reraise_types=(ValidationError, RepositoryError))
    def delete_template(self, name: str) -> bool:
        """Delete a template from the DB."""
        self._validate_entity_id(name, entity_type="Template")
        self._log_operation("Deleting template", name)
        query = f"DELETE FROM {self._TMPL_TABLE_NAME} WHERE {self._TMPL_PK_COLUMN} = ?"
        try:
            affected_rows = self.connection_manager.execute_modification(query, (name,))
            deleted = affected_rows > 0
            if deleted: self.logger.info(f"Successfully deleted template: '{name}'")
            else: self.logger.warning(f"Template not found for deletion: '{name}'")
            return deleted
        except Exception as e: raise RepositoryError(f"DB error deleting template '{name}'", entity_id=name, cause=e) from e


    @log_method_call(logger)
    @handle_exceptions(RepositoryError, "Error listing templates")
    def list_templates(self) -> List[str]:
        """List the names of all saved templates."""
        self._log_operation("Listing templates")
        query = f"SELECT {self._TMPL_PK_COLUMN} FROM {self._TMPL_TABLE_NAME} ORDER BY {self._TMPL_PK_COLUMN}"
        try:
            rows = self.connection_manager.execute_query(query)
            names = [row[self._TMPL_PK_COLUMN] for row in rows]
            return names
        except Exception as e: raise RepositoryError(f"DB error listing templates", cause=e) from e