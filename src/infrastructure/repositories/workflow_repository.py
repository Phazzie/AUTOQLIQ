"""Workflow repository implementation for AutoQliq."""
import json
import logging
import os
import re
from typing import Any, Dict, List, Optional
from datetime import datetime # Needed for metadata

# Core dependencies
from src.core.exceptions import WorkflowError, RepositoryError, ValidationError, SerializationError
# Import AutoQliqError for error handling
from src.core.exceptions import AutoQliqError
from src.core.interfaces import IAction, IWorkflowRepository

# Infrastructure dependencies
from src.infrastructure.common.error_handling import handle_exceptions
from src.infrastructure.common.logging_utils import log_method_call
from src.infrastructure.common.validators import WorkflowValidator # Workflow specific validation
from src.infrastructure.repositories.base.file_system_repository import FileSystemRepository
from src.infrastructure.repositories.serialization.action_serializer import (
    serialize_actions,
    deserialize_actions
)

logger = logging.getLogger(__name__)

class FileSystemWorkflowRepository(FileSystemRepository[List[IAction]], IWorkflowRepository):
    """Implementation of IWorkflowRepository that stores workflows and templates in JSON files."""
    WORKFLOW_EXTENSION = ".json"
    TEMPLATE_SUBDIR = "templates"

    def __init__(self, directory_path: str, **options):
        """Initialize FileSystemWorkflowRepository."""
        super().__init__(logger_name=__name__)
        if not directory_path: raise ValueError("Directory path cannot be empty.")
        self.directory_path = os.path.abspath(directory_path) # Use absolute path
        self.template_dir_path = os.path.join(self.directory_path, self.TEMPLATE_SUBDIR)
        self._create_if_missing = options.get('create_if_missing', True)

        if self._create_if_missing:
            try:
                # Use base class helper which should exist in FileSystemRepository
                super()._ensure_directory_exists(self.directory_path)
                super()._ensure_directory_exists(self.template_dir_path)
            except AttributeError: # Fallback if base class changes
                 self.logger.warning("_ensure_directory_exists not found on base, attempting manual creation.")
                 os.makedirs(self.directory_path, exist_ok=True)
                 os.makedirs(self.template_dir_path, exist_ok=True)
            except AutoQliqError as e:
                raise RepositoryError(f"Failed ensure directories exist: {directory_path}", cause=e) from e


    def _get_workflow_path(self, name: str) -> str:
        """Get the file path for a workflow."""
        return os.path.join(self.directory_path, f"{name}{self.WORKFLOW_EXTENSION}")

    def _get_template_path(self, name: str) -> str:
        """Get the file path for a template."""
        return os.path.join(self.template_dir_path, f"{name}{self.WORKFLOW_EXTENSION}")


    # --- IWorkflowRepository Implementation ---

    @log_method_call(logger)
    @handle_exceptions(WorkflowError, "Error creating workflow", reraise_types=(WorkflowError, ValidationError, RepositoryError))
    def create_workflow(self, name: str) -> None:
        """Create a new empty workflow file."""
        WorkflowValidator.validate_workflow_name(name)
        self._log_operation("Creating empty workflow", name)
        file_path = self._get_workflow_path(name)
        if super()._file_exists(file_path):
            raise RepositoryError(f"Workflow '{name}' already exists.", entity_id=name)
        try: super()._write_json_file(file_path, [])
        except (IOError, TypeError) as e: raise RepositoryError(f"Failed create empty file for workflow '{name}'", entity_id=name, cause=e) from e


    @log_method_call(logger)
    @handle_exceptions(WorkflowError, "Error saving workflow", reraise_types=(WorkflowError, ValidationError, RepositoryError, SerializationError))
    def save(self, name: str, workflow_actions: List[IAction]) -> None:
        """Save a workflow (list of actions) to a JSON file."""
        WorkflowValidator.validate_workflow_name(name)
        WorkflowValidator.validate_actions(workflow_actions)
        self._log_operation("Saving workflow", name)
        try:
            action_data_list = serialize_actions(workflow_actions) # Raises SerializationError
            file_path = self._get_workflow_path(name)
            super()._write_json_file(file_path, action_data_list) # Raises IOError, TypeError
        except (IOError, TypeError, SerializationError) as e: raise RepositoryError(f"Failed save workflow '{name}'", entity_id=name, cause=e) from e


    @log_method_call(logger)
    @handle_exceptions(WorkflowError, "Error loading workflow", reraise_types=(WorkflowError, ValidationError, RepositoryError, SerializationError))
    def load(self, name: str) -> List[IAction]:
        """Load a workflow (list of actions) from a JSON file."""
        WorkflowValidator.validate_workflow_name(name)
        self._log_operation("Loading workflow", name)
        file_path = self._get_workflow_path(name)
        try:
            action_data_list = super()._read_json_file(file_path) # Raises FileNotFoundError, JSONDecodeError, IOError
            if not isinstance(action_data_list, list): raise SerializationError(f"Workflow file '{name}' not JSON list.", entity_id=name)
            actions = deserialize_actions(action_data_list) # Raises SerializationError, ActionError
            return actions
        except FileNotFoundError as e: raise RepositoryError(f"Workflow file not found: {name}", entity_id=name, cause=e) from e
        except (json.JSONDecodeError, SerializationError, ActionError) as e: raise SerializationError(f"Failed load/deserialize workflow '{name}'", entity_id=name, cause=e) from e
        except (IOError, PermissionError) as e: raise RepositoryError(f"Failed read workflow file '{name}'", entity_id=name, cause=e) from e


    @log_method_call(logger)
    @handle_exceptions(WorkflowError, "Error deleting workflow", reraise_types=(WorkflowError, ValidationError, RepositoryError))
    def delete(self, name: str) -> bool:
        """Delete a workflow file."""
        WorkflowValidator.validate_workflow_name(name)
        self._log_operation("Deleting workflow", name)
        file_path = self._get_workflow_path(name)
        if not super()._file_exists(file_path): return False
        try: os.remove(file_path); return True
        except (IOError, OSError, PermissionError) as e: raise RepositoryError(f"Failed delete workflow file '{name}'", entity_id=name, cause=e) from e


    @log_method_call(logger)
    @handle_exceptions(WorkflowError, "Error listing workflows", reraise_types=(RepositoryError,))
    def list_workflows(self) -> List[str]:
        """List workflow files in the directory."""
        self._log_operation("Listing workflows")
        try:
            names = [ f[:-len(self.WORKFLOW_EXTENSION)]
                      for f in os.listdir(self.directory_path)
                      if f.endswith(self.WORKFLOW_EXTENSION) and os.path.isfile(os.path.join(self.directory_path, f)) ]
            return sorted(names)
        except (FileNotFoundError, PermissionError, OSError) as e: raise RepositoryError(f"Failed list workflows in '{self.directory_path}'", cause=e) from e


    @log_method_call(logger)
    @handle_exceptions(WorkflowError, "Error getting workflow metadata", reraise_types=(WorkflowError, ValidationError, RepositoryError))
    def get_metadata(self, name: str) -> Dict[str, Any]:
        """Get file system metadata for a workflow."""
        WorkflowValidator.validate_workflow_name(name)
        self._log_operation("Getting metadata", name)
        file_path = self._get_workflow_path(name)
        try:
            if not super()._file_exists(file_path): raise RepositoryError(f"Workflow not found: {name}", entity_id=name)
            stat_result = os.stat(file_path)
            return { "name": name, "source": "file_system", "path": file_path, "size_bytes": stat_result.st_size,
                     "created_at": datetime.fromtimestamp(stat_result.st_ctime).isoformat(),
                     "modified_at": datetime.fromtimestamp(stat_result.st_mtime).isoformat() }
        except (FileNotFoundError, OSError, PermissionError) as e: raise RepositoryError(f"Failed get metadata for workflow '{name}'", entity_id=name, cause=e) from e

    # --- Template Methods ---

    @log_method_call(logger)
    @handle_exceptions(RepositoryError, "Error saving template", reraise_types=(ValidationError, RepositoryError, SerializationError))
    def save_template(self, name: str, actions_data: List[Dict[str, Any]]) -> None:
        """Save an action template (serialized list) to a JSON file in templates subdir."""
        WorkflowValidator.validate_workflow_name(name) # Use same validation for names
        self._log_operation("Saving template", name)
        if not isinstance(actions_data, list) or not all(isinstance(item, dict) for item in actions_data):
             raise SerializationError("Template actions data must be list of dicts.")
        try:
            file_path = self._get_template_path(name)
            # Ensure template dir exists (might not if base dir was created empty)
            super()._ensure_directory_exists(self.template_dir_path)
            super()._write_json_file(file_path, actions_data)
        except (IOError, TypeError, AutoQliqError) as e: # Catch potential error from _ensure_directory_exists
            raise RepositoryError(f"Failed save template '{name}'", entity_id=name, cause=e) from e

    @log_method_call(logger)
    @handle_exceptions(RepositoryError, "Error loading template", reraise_types=(ValidationError, RepositoryError, SerializationError))
    def load_template(self, name: str) -> List[Dict[str, Any]]:
        """Load serialized action data for a template."""
        WorkflowValidator.validate_workflow_name(name)
        self._log_operation("Loading template", name)
        file_path = self._get_template_path(name)
        try:
            actions_data = super()._read_json_file(file_path) # Raises FileNotFoundError, JSONDecodeError, IOError
            if not isinstance(actions_data, list): raise SerializationError(f"Template file '{name}' not JSON list.", entity_id=name)
            if not all(isinstance(item, dict) for item in actions_data): raise SerializationError(f"Template file '{name}' contains non-dict items.", entity_id=name)
            return actions_data
        except FileNotFoundError as e: raise RepositoryError(f"Template file not found: {name}", entity_id=name, cause=e) from e
        except json.JSONDecodeError as e: raise SerializationError(f"Invalid JSON in template file '{name}'", entity_id=name, cause=e) from e
        except (IOError, PermissionError) as e: raise RepositoryError(f"Failed read template file '{name}'", entity_id=name, cause=e) from e


    @log_method_call(logger)
    @handle_exceptions(RepositoryError, "Error deleting template", reraise_types=(ValidationError, RepositoryError))
    def delete_template(self, name: str) -> bool:
        """Delete a template file."""
        WorkflowValidator.validate_workflow_name(name)
        self._log_operation("Deleting template", name)
        file_path = self._get_template_path(name)
        if not super()._file_exists(file_path): return False
        try: os.remove(file_path); return True
        except (IOError, OSError, PermissionError) as e: raise RepositoryError(f"Failed delete template file '{name}'", entity_id=name, cause=e) from e

    @log_method_call(logger)
    @handle_exceptions(RepositoryError, "Error listing templates")
    def list_templates(self) -> List[str]:
        """List template files in the template subdirectory."""
        self._log_operation("Listing templates")
        if not os.path.exists(self.template_dir_path): return []
        try:
            names = [ f[:-len(self.WORKFLOW_EXTENSION)]
                      for f in os.listdir(self.template_dir_path)
                      if f.endswith(self.WORKFLOW_EXTENSION) and os.path.isfile(os.path.join(self.template_dir_path, f)) ]
            return sorted(names)
        except (FileNotFoundError, PermissionError, OSError) as e: raise RepositoryError(f"Failed list templates in '{self.template_dir_path}'", cause=e) from e