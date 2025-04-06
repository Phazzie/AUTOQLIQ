"""Workflow repository implementation for AutoQliq."""
import json
import logging
import os
import re
from typing import Any, Dict, List, Optional

from src.core.exceptions import WorkflowError
from src.core.interfaces import IAction, IWorkflowRepository
from src.infrastructure.common.error_handling import handle_exceptions
from src.infrastructure.common.logging_utils import log_method_call
from src.infrastructure.repositories.base.file_system_repository import FileSystemRepository
from src.infrastructure.repositories.serialization.action_serializer import (
    serialize_actions,
    deserialize_actions
)
from src.infrastructure.repositories.serialization.workflow_metadata_serializer import (
    extract_workflow_metadata,
    extract_workflow_actions
)

class FileSystemWorkflowRepository(FileSystemRepository[List[IAction]], IWorkflowRepository):
    """Implementation of IWorkflowRepository that stores workflows in JSON files.

    This class provides methods for saving, loading, and managing workflows stored as JSON files.

    Attributes:
        directory_path: Path to the directory containing workflow files
        logger: Logger for recording repository operations and errors
    """

    # Regular expression for validating workflow names
    # Only allow alphanumeric characters, underscores, and hyphens
    VALID_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9_-]+$')

    def __init__(self, directory_path: str, **options):
        """Initialize a new FileSystemWorkflowRepository.

        Args:
            directory_path: Path to the directory containing workflow files
            **options: Additional options for the repository
                create_if_missing (bool): Whether to create the directory if it doesn't exist
        """
        super().__init__(__name__)
        self.directory_path = directory_path
        self.options = options

        # Ensure the directory exists
        self._ensure_directory_exists(directory_path)

    @log_method_call(logging.getLogger(__name__))
    @handle_exceptions(WorkflowError, "Error creating workflow")
    def create_workflow(self, name: str) -> None:
        """Create a new empty workflow.

        Args:
            name: The name of the workflow to create

        Raises:
            WorkflowError: If the workflow cannot be created or the name is invalid
        """
        # Validate workflow name
        self._validate_workflow_name(name)

        # Check if workflow already exists
        file_path = self._get_workflow_path(name)
        if os.path.exists(file_path):
            error_msg = f"Workflow already exists: {name}"
            self.logger.error(error_msg)
            raise WorkflowError(error_msg)

        # Create empty workflow file
        self._write_json_file(file_path, [])

    @log_method_call(logging.getLogger(__name__))
    @handle_exceptions(WorkflowError, "Error saving workflow")
    def save(self, name: str, workflow_actions: List[IAction]) -> None:
        """Save a workflow to the repository.

        Args:
            name: The name of the workflow
            workflow_actions: The list of actions in the workflow

        Raises:
            WorkflowError: If the workflow cannot be saved or the name is invalid
        """
        # Validate workflow name
        self._validate_workflow_name(name)

        # Validate workflow actions
        if not workflow_actions:
            error_msg = "Workflow must contain at least one action"
            self.logger.error(error_msg)
            raise WorkflowError(error_msg)

        # Serialize actions
        action_data = serialize_actions(workflow_actions)

        # Save workflow to file
        file_path = self._get_workflow_path(name)
        self._write_json_file(file_path, action_data)

    @log_method_call(logging.getLogger(__name__))
    @handle_exceptions(WorkflowError, "Error loading workflow")
    def load(self, name: str) -> List[IAction]:
        """Load a workflow from the repository.

        Args:
            name: The name of the workflow to load

        Returns:
            The list of actions in the workflow

        Raises:
            WorkflowError: If the workflow cannot be loaded
        """
        file_path = self._get_workflow_path(name)

        try:
            # Read workflow data from file
            workflow_data = self._read_json_file(file_path)

            # Extract action data
            actions_data = extract_workflow_actions(workflow_data)

            # Deserialize actions
            return deserialize_actions(actions_data)
        except FileNotFoundError as e:
            error_msg = f"Workflow not found: {name}"
            self.logger.error(error_msg)
            raise WorkflowError(error_msg) from e
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON in workflow file: {name}"
            self.logger.error(error_msg)
            raise WorkflowError(error_msg) from e

    @log_method_call(logging.getLogger(__name__))
    @handle_exceptions(WorkflowError, "Error listing workflows")
    def list_workflows(self) -> List[str]:
        """List all workflows in the repository.

        Returns:
            A list of workflow names

        Raises:
            WorkflowError: If the workflow directory cannot be read
        """
        try:
            workflow_files = [f for f in os.listdir(self.directory_path) if f.endswith('.json')]
            workflow_names = [f.split('.')[0] for f in workflow_files]
            return workflow_names
        except PermissionError as e:
            error_msg = f"Permission denied when listing workflows in {self.directory_path}"
            self.logger.error(error_msg)
            raise WorkflowError(error_msg) from e
        except FileNotFoundError as e:
            error_msg = f"Workflow directory not found: {self.directory_path}"
            self.logger.error(error_msg)
            raise WorkflowError(error_msg) from e

    @log_method_call(logging.getLogger(__name__))
    @handle_exceptions(WorkflowError, "Error deleting workflow")
    def delete(self, name: str) -> bool:
        """Delete a workflow from the repository.

        Args:
            name: The name of the workflow to delete

        Returns:
            True if the workflow was deleted, False if it didn't exist

        Raises:
            WorkflowError: If the workflow cannot be deleted
        """
        file_path = self._get_workflow_path(name)
        if not os.path.exists(file_path):
            return False

        try:
            os.remove(file_path)
            return True
        except PermissionError as e:
            error_msg = f"Permission denied when deleting workflow: {name}"
            self.logger.error(error_msg)
            raise WorkflowError(error_msg) from e

    @log_method_call(logging.getLogger(__name__))
    @handle_exceptions(WorkflowError, "Error getting workflow metadata")
    def get_metadata(self, name: str) -> Dict[str, Any]:
        """Get metadata for a workflow.

        Args:
            name: The name of the workflow

        Returns:
            A dictionary containing workflow metadata

        Raises:
            WorkflowError: If the workflow cannot be loaded
        """
        file_path = self._get_workflow_path(name)

        try:
            # Read workflow data from file
            workflow_data = self._read_json_file(file_path)

            # Extract metadata
            return extract_workflow_metadata(workflow_data, name)
        except FileNotFoundError as e:
            error_msg = f"Workflow not found: {name}"
            self.logger.error(error_msg)
            raise WorkflowError(error_msg) from e
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON in workflow file: {name}"
            self.logger.error(error_msg)
            raise WorkflowError(error_msg) from e

    def _get_workflow_path(self, name: str) -> str:
        """Get the file path for a workflow.

        Args:
            name: The name of the workflow

        Returns:
            The file path for the workflow
        """
        return os.path.join(self.directory_path, f"{name}.json")

    def _validate_workflow_name(self, name: str) -> None:
        """Validate a workflow name.

        Args:
            name: The name to validate

        Raises:
            WorkflowError: If the name is invalid
        """
        if not name:
            error_msg = "Workflow name cannot be empty"
            self.logger.error(error_msg)
            raise WorkflowError(error_msg)

        if not self.VALID_NAME_PATTERN.match(name):
            error_msg = f"Invalid workflow name: {name}. Only alphanumeric characters, underscores, and hyphens are allowed."
            self.logger.error(error_msg)
            raise WorkflowError(error_msg)
