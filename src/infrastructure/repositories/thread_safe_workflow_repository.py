"""Thread-safe workflow repository implementation for AutoQliq."""

import json
import logging
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

# Core dependencies
from src.core.exceptions import WorkflowError, RepositoryError, ValidationError, SerializationError, AutoQliqError
from src.core.interfaces import IAction, IWorkflowRepository

# Infrastructure dependencies
from src.infrastructure.common.error_handling import handle_exceptions
from src.infrastructure.common.logging_utils import log_method_call
from src.infrastructure.common.validators import WorkflowValidator
from src.infrastructure.common.file_locking import LockedFile, file_lock
from src.infrastructure.repositories.base.file_system_repository import FileSystemRepository
from src.infrastructure.repositories.serialization.action_serializer import (
    serialize_actions,
    deserialize_actions
)

logger = logging.getLogger(__name__)


class ThreadSafeWorkflowRepository(FileSystemRepository[List[IAction]], IWorkflowRepository):
    """
    Thread-safe implementation of IWorkflowRepository that stores workflows and templates in JSON files.
    
    This implementation provides thread-safe access to workflow and template files,
    ensuring data integrity in multi-threaded environments.
    
    Attributes:
        directory_path: Path to the directory containing workflow files.
        template_dir_path: Path to the directory containing template files.
    """
    
    WORKFLOW_EXTENSION = ".json"
    TEMPLATE_SUBDIR = "templates"
    
    def __init__(self, directory_path: str, **options):
        """
        Initialize a new ThreadSafeWorkflowRepository.
        
        Args:
            directory_path: Path to the directory containing workflow files.
            **options: Additional options:
                create_if_missing (bool): If True, create directories if they don't exist.
                                         Defaults to True.
        
        Raises:
            ValueError: If directory_path is empty.
        """
        super().__init__(logger_name=__name__)
        
        if not directory_path:
            raise ValueError("Directory path cannot be empty.")
            
        self.directory_path = os.path.abspath(directory_path)
        self.template_dir_path = os.path.join(self.directory_path, self.TEMPLATE_SUBDIR)
        self._create_if_missing = options.get('create_if_missing', True)
        
        # Ensure directories exist
        if self._create_if_missing:
            try:
                self._ensure_directories()
            except Exception as e:
                raise RepositoryError(f"Failed to create directories: {e}", cause=e) from e
    
    def _ensure_directories(self) -> None:
        """Ensure workflow and template directories exist."""
        try:
            # Ensure workflow directory exists
            if not os.path.exists(self.directory_path):
                os.makedirs(self.directory_path, exist_ok=True)
                logger.info(f"Created workflow directory: {self.directory_path}")
            
            # Ensure template directory exists
            if not os.path.exists(self.template_dir_path):
                os.makedirs(self.template_dir_path, exist_ok=True)
                logger.info(f"Created template directory: {self.template_dir_path}")
        except (IOError, PermissionError) as e:
            error_msg = f"Failed to create directories: {e}"
            logger.error(error_msg)
            raise AutoQliqError(error_msg, cause=e) from e
    
    def _get_workflow_path(self, name: str) -> str:
        """Get the full path to a workflow file."""
        # Ensure the name has the correct extension
        if not name.endswith(self.WORKFLOW_EXTENSION):
            name = f"{name}{self.WORKFLOW_EXTENSION}"
        return os.path.join(self.directory_path, name)
    
    def _get_template_path(self, name: str) -> str:
        """Get the full path to a template file."""
        # Ensure the name has the correct extension
        if not name.endswith(self.WORKFLOW_EXTENSION):
            name = f"{name}{self.WORKFLOW_EXTENSION}"
        return os.path.join(self.template_dir_path, name)
    
    def _log_operation(self, operation: str, entity_id: Optional[str] = None) -> None:
        """Log a repository operation."""
        if entity_id:
            logger.debug(f"{operation} workflow: {entity_id}")
        else:
            logger.debug(f"{operation} workflows")
    
    # --- IWorkflowRepository Implementation ---
    
    @log_method_call(logger)
    @handle_exceptions(WorkflowError, "Error creating workflow", reraise_types=(WorkflowError, ValidationError, RepositoryError))
    def create_workflow(self, name: str) -> None:
        """
        Create a new empty workflow file.
        
        Args:
            name: The name of the workflow to create
            
        Raises:
            WorkflowError: If the workflow cannot be created
            ValidationError: If the name is invalid
            RepositoryError: If the workflow already exists or there's an issue with the repository
        """
        WorkflowValidator.validate_workflow_name(name)
        self._log_operation("Creating empty workflow", name)
        
        file_path = self._get_workflow_path(name)
        
        # Check if the workflow already exists
        with file_lock(file_path):
            if os.path.exists(file_path):
                raise RepositoryError(f"Workflow '{name}' already exists.", entity_id=name)
            
            try:
                # Ensure the directory exists
                if not os.path.exists(self.directory_path):
                    os.makedirs(self.directory_path, exist_ok=True)
                
                # Create an empty workflow file
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump([], f, indent=2)
                
                logger.info(f"Created empty workflow: {name}")
            except (IOError, TypeError) as e:
                error_msg = f"Failed to create empty workflow file for '{name}'"
                logger.error(error_msg, exc_info=True)
                raise RepositoryError(error_msg, entity_id=name, cause=e) from e
    
    @log_method_call(logger)
    @handle_exceptions(WorkflowError, "Error saving workflow", reraise_types=(WorkflowError, ValidationError, RepositoryError, SerializationError))
    def save(self, name: str, workflow_actions: List[IAction]) -> None:
        """
        Save a workflow (list of actions) to a JSON file.
        
        Args:
            name: The name of the workflow to save
            workflow_actions: The list of actions to save
            
        Raises:
            WorkflowError: If the workflow cannot be saved
            ValidationError: If the name or actions are invalid
            RepositoryError: If there's an issue with the repository
            SerializationError: If the actions cannot be serialized
        """
        WorkflowValidator.validate_workflow_name(name)
        WorkflowValidator.validate_actions(workflow_actions)
        self._log_operation("Saving workflow", name)
        
        file_path = self._get_workflow_path(name)
        
        try:
            # Serialize actions to JSON-compatible format
            action_data_list = serialize_actions(workflow_actions)
            
            # Ensure the directory exists
            if not os.path.exists(self.directory_path):
                os.makedirs(self.directory_path, exist_ok=True)
            
            # Write to file with locking
            with file_lock(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(action_data_list, f, indent=2)
            
            logger.info(f"Saved workflow: {name}")
        except SerializationError as e:
            # Re-raise serialization errors directly
            raise
        except (IOError, TypeError) as e:
            error_msg = f"Failed to save workflow '{name}'"
            logger.error(error_msg, exc_info=True)
            raise RepositoryError(error_msg, entity_id=name, cause=e) from e
    
    @log_method_call(logger)
    @handle_exceptions(WorkflowError, "Error loading workflow", reraise_types=(WorkflowError, ValidationError, RepositoryError, SerializationError))
    def load(self, name: str) -> List[IAction]:
        """
        Load a workflow (list of actions) from a JSON file.
        
        Args:
            name: The name of the workflow to load
            
        Returns:
            The list of actions in the workflow
            
        Raises:
            WorkflowError: If the workflow cannot be loaded
            ValidationError: If the name is invalid
            RepositoryError: If the workflow doesn't exist or there's an issue with the repository
            SerializationError: If the actions cannot be deserialized
        """
        WorkflowValidator.validate_workflow_name(name)
        self._log_operation("Loading workflow", name)
        
        file_path = self._get_workflow_path(name)
        
        try:
            # Read the file with locking
            with file_lock(file_path):
                if not os.path.exists(file_path):
                    raise RepositoryError(f"Workflow not found: {name}", entity_id=name)
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    action_data_list = json.load(f)
            
            # Validate the data structure
            if not isinstance(action_data_list, list):
                raise SerializationError(f"Workflow file '{name}' not JSON list.", entity_id=name)
            
            # Deserialize the actions
            actions = deserialize_actions(action_data_list)
            
            logger.info(f"Loaded workflow: {name}")
            return actions
        except (FileNotFoundError, json.JSONDecodeError, IOError) as e:
            error_msg = f"Failed to load workflow '{name}'"
            logger.error(error_msg, exc_info=True)
            raise RepositoryError(error_msg, entity_id=name, cause=e) from e
    
    @log_method_call(logger)
    @handle_exceptions(WorkflowError, "Error deleting workflow", reraise_types=(WorkflowError, ValidationError, RepositoryError))
    def delete(self, name: str) -> bool:
        """
        Delete a workflow by name.
        
        Args:
            name: The name of the workflow to delete
            
        Returns:
            True if the workflow was deleted, False if not found
            
        Raises:
            WorkflowError: If the workflow cannot be deleted
            ValidationError: If the name is invalid
            RepositoryError: If there's an issue with the repository
        """
        WorkflowValidator.validate_workflow_name(name)
        self._log_operation("Deleting workflow", name)
        
        file_path = self._get_workflow_path(name)
        
        try:
            # Delete the file with locking
            with file_lock(file_path):
                if not os.path.exists(file_path):
                    logger.debug(f"Workflow not found for deletion: {name}")
                    return False
                
                os.remove(file_path)
                logger.info(f"Deleted workflow: {name}")
                return True
        except (IOError, PermissionError) as e:
            error_msg = f"Failed to delete workflow '{name}'"
            logger.error(error_msg, exc_info=True)
            raise RepositoryError(error_msg, entity_id=name, cause=e) from e
    
    @log_method_call(logger)
    @handle_exceptions(WorkflowError, "Error listing workflows", reraise_types=(WorkflowError, RepositoryError))
    def list_workflows(self) -> List[str]:
        """
        List the names of all workflows.
        
        Returns:
            A list of workflow names
            
        Raises:
            WorkflowError: If the workflows cannot be listed
            RepositoryError: If there's an issue with the repository
        """
        self._log_operation("Listing workflows")
        
        try:
            # Ensure the directory exists
            if not os.path.exists(self.directory_path):
                if self._create_if_missing:
                    os.makedirs(self.directory_path, exist_ok=True)
                    return []
                else:
                    raise RepositoryError(f"Workflow directory not found: {self.directory_path}")
            
            # List all JSON files in the directory
            workflow_files = [f for f in os.listdir(self.directory_path)
                             if f.endswith(self.WORKFLOW_EXTENSION) and os.path.isfile(os.path.join(self.directory_path, f))]
            
            # Remove the extension from the names
            workflow_names = [os.path.splitext(f)[0] for f in workflow_files]
            
            return sorted(workflow_names)
        except (IOError, PermissionError) as e:
            error_msg = "Failed to list workflows"
            logger.error(error_msg, exc_info=True)
            raise RepositoryError(error_msg, cause=e) from e
    
    @log_method_call(logger)
    @handle_exceptions(WorkflowError, "Error getting workflow metadata", reraise_types=(WorkflowError, ValidationError, RepositoryError))
    def get_metadata(self, name: str) -> Dict[str, Any]:
        """
        Get metadata for a workflow.
        
        Args:
            name: The name of the workflow
            
        Returns:
            A dictionary containing metadata about the workflow
            
        Raises:
            WorkflowError: If the metadata cannot be retrieved
            ValidationError: If the name is invalid
            RepositoryError: If the workflow doesn't exist or there's an issue with the repository
        """
        WorkflowValidator.validate_workflow_name(name)
        self._log_operation("Getting metadata", name)
        
        file_path = self._get_workflow_path(name)
        
        try:
            # Get file metadata with locking
            with file_lock(file_path):
                if not os.path.exists(file_path):
                    raise RepositoryError(f"Workflow not found: {name}", entity_id=name)
                
                stat_result = os.stat(file_path)
                
                # Read the file to count actions
                with open(file_path, 'r', encoding='utf-8') as f:
                    action_data_list = json.load(f)
                
                action_count = len(action_data_list) if isinstance(action_data_list, list) else 0
            
            # Build metadata dictionary
            metadata = {
                "name": name,
                "source": "file_system",
                "path": file_path,
                "size_bytes": stat_result.st_size,
                "created_at": datetime.fromtimestamp(stat_result.st_ctime).isoformat(),
                "modified_at": datetime.fromtimestamp(stat_result.st_mtime).isoformat(),
                "action_count": action_count
            }
            
            return metadata
        except (IOError, json.JSONDecodeError, PermissionError) as e:
            error_msg = f"Failed to get metadata for workflow '{name}'"
            logger.error(error_msg, exc_info=True)
            raise RepositoryError(error_msg, entity_id=name, cause=e) from e
    
    # --- Template Methods ---
    
    @log_method_call(logger)
    @handle_exceptions(RepositoryError, "Error saving template", reraise_types=(ValidationError, RepositoryError, SerializationError))
    def save_template(self, name: str, actions_data: List[Dict[str, Any]]) -> None:
        """
        Save an action template (serialized list) to a JSON file.
        
        Args:
            name: The name of the template to save
            actions_data: The serialized actions data to save
            
        Raises:
            RepositoryError: If the template cannot be saved
            ValidationError: If the name is invalid
            SerializationError: If the actions data is invalid
        """
        WorkflowValidator.validate_workflow_name(name)
        self._log_operation("Saving template", name)
        
        if not isinstance(actions_data, list) or not all(isinstance(item, dict) for item in actions_data):
            raise SerializationError("Template actions data must be list of dicts.")
        
        file_path = self._get_template_path(name)
        
        try:
            # Ensure the template directory exists
            if not os.path.exists(self.template_dir_path):
                os.makedirs(self.template_dir_path, exist_ok=True)
            
            # Write to file with locking
            with file_lock(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(actions_data, f, indent=2)
            
            logger.info(f"Saved template: {name}")
        except (IOError, TypeError) as e:
            error_msg = f"Failed to save template '{name}'"
            logger.error(error_msg, exc_info=True)
            raise RepositoryError(error_msg, entity_id=name, cause=e) from e
    
    @log_method_call(logger)
    @handle_exceptions(RepositoryError, "Error loading template", reraise_types=(ValidationError, RepositoryError, SerializationError))
    def load_template(self, name: str) -> List[Dict[str, Any]]:
        """
        Load serialized action data for a template.
        
        Args:
            name: The name of the template to load
            
        Returns:
            The serialized actions data
            
        Raises:
            RepositoryError: If the template cannot be loaded
            ValidationError: If the name is invalid
            SerializationError: If the actions data is invalid
        """
        WorkflowValidator.validate_workflow_name(name)
        self._log_operation("Loading template", name)
        
        file_path = self._get_template_path(name)
        
        try:
            # Read the file with locking
            with file_lock(file_path):
                if not os.path.exists(file_path):
                    raise RepositoryError(f"Template not found: {name}", entity_id=name)
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    actions_data = json.load(f)
            
            # Validate the data structure
            if not isinstance(actions_data, list):
                raise SerializationError(f"Template file '{name}' not JSON list.", entity_id=name)
            if not all(isinstance(item, dict) for item in actions_data):
                raise SerializationError(f"Template file '{name}' contains non-dict items.", entity_id=name)
            
            logger.info(f"Loaded template: {name}")
            return actions_data
        except (FileNotFoundError, json.JSONDecodeError, IOError) as e:
            error_msg = f"Failed to load template '{name}'"
            logger.error(error_msg, exc_info=True)
            raise RepositoryError(error_msg, entity_id=name, cause=e) from e
    
    @log_method_call(logger)
    @handle_exceptions(RepositoryError, "Error deleting template", reraise_types=(ValidationError, RepositoryError))
    def delete_template(self, name: str) -> bool:
        """
        Delete a template by name.
        
        Args:
            name: The name of the template to delete
            
        Returns:
            True if the template was deleted, False if not found
            
        Raises:
            RepositoryError: If the template cannot be deleted
            ValidationError: If the name is invalid
        """
        WorkflowValidator.validate_workflow_name(name)
        self._log_operation("Deleting template", name)
        
        file_path = self._get_template_path(name)
        
        try:
            # Delete the file with locking
            with file_lock(file_path):
                if not os.path.exists(file_path):
                    logger.debug(f"Template not found for deletion: {name}")
                    return False
                
                os.remove(file_path)
                logger.info(f"Deleted template: {name}")
                return True
        except (IOError, PermissionError) as e:
            error_msg = f"Failed to delete template '{name}'"
            logger.error(error_msg, exc_info=True)
            raise RepositoryError(error_msg, entity_id=name, cause=e) from e
    
    @log_method_call(logger)
    @handle_exceptions(RepositoryError, "Error listing templates", reraise_types=(RepositoryError,))
    def list_templates(self) -> List[str]:
        """
        List the names of all templates.
        
        Returns:
            A list of template names
            
        Raises:
            RepositoryError: If the templates cannot be listed
        """
        self._log_operation("Listing templates")
        
        try:
            # Ensure the template directory exists
            if not os.path.exists(self.template_dir_path):
                if self._create_if_missing:
                    os.makedirs(self.template_dir_path, exist_ok=True)
                    return []
                else:
                    raise RepositoryError(f"Template directory not found: {self.template_dir_path}")
            
            # List all JSON files in the template directory
            template_files = [f for f in os.listdir(self.template_dir_path)
                             if f.endswith(self.WORKFLOW_EXTENSION) and os.path.isfile(os.path.join(self.template_dir_path, f))]
            
            # Remove the extension from the names
            template_names = [os.path.splitext(f)[0] for f in template_files]
            
            return sorted(template_names)
        except (IOError, PermissionError) as e:
            error_msg = "Failed to list templates"
            logger.error(error_msg, exc_info=True)
            raise RepositoryError(error_msg, cause=e) from e
