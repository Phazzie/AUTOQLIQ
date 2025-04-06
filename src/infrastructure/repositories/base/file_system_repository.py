"""File system repository implementation for AutoQliq."""
import json
import os
from typing import Any, TypeVar, Optional, List

from src.core.exceptions import AutoQliqError, RepositoryError
from src.infrastructure.repositories.base.repository import Repository

# Type variable for the entity type
T = TypeVar('T')

class FileSystemRepository(Repository[T]):
    """Base class for file system repository implementations.

    This class provides common functionality for file system repository implementations,
    such as file operations, serialization, and error handling.

    Attributes:
        logger: Logger for recording repository operations and errors
    """

    def save(self, entity_id: str, entity: T) -> None:
        """Save an entity to the repository.

        Args:
            entity_id: The ID of the entity
            entity: The entity to save

        Raises:
            RepositoryError: If the entity cannot be saved
        """
        self._validate_entity_id(entity_id)
        self._log_operation("Saving entity", entity_id)

        try:
            self._save_entity(entity_id, entity)
        except Exception as e:
            error_msg = f"Failed to save entity: {entity_id}"
            self.logger.error(error_msg, exc_info=True)
            raise RepositoryError(error_msg, entity_id=entity_id, cause=e)

    def get(self, entity_id: str) -> Optional[T]:
        """Get an entity from the repository.

        Args:
            entity_id: The ID of the entity

        Returns:
            The entity, or None if not found

        Raises:
            RepositoryError: If the entity cannot be retrieved
        """
        self._validate_entity_id(entity_id)
        self._log_operation("Getting entity", entity_id)

        try:
            return self._get_entity(entity_id)
        except Exception as e:
            error_msg = f"Failed to get entity: {entity_id}"
            self.logger.error(error_msg, exc_info=True)
            raise RepositoryError(error_msg, entity_id=entity_id, cause=e)

    def delete(self, entity_id: str) -> None:
        """Delete an entity from the repository.

        Args:
            entity_id: The ID of the entity

        Raises:
            RepositoryError: If the entity cannot be deleted
        """
        self._validate_entity_id(entity_id)
        self._log_operation("Deleting entity", entity_id)

        try:
            self._delete_entity(entity_id)
        except Exception as e:
            error_msg = f"Failed to delete entity: {entity_id}"
            self.logger.error(error_msg, exc_info=True)
            raise RepositoryError(error_msg, entity_id=entity_id, cause=e)

    def list(self) -> List[str]:
        """List all entity IDs in the repository.

        Returns:
            A list of entity IDs

        Raises:
            RepositoryError: If the entities cannot be listed
        """
        self._log_operation("Listing entities", "all")

        try:
            return self._list_entities()
        except Exception as e:
            error_msg = "Failed to list entities"
            self.logger.error(error_msg, exc_info=True)
            raise RepositoryError(error_msg, cause=e)

    def _save_entity(self, entity_id: str, entity: T) -> None:
        """Save an entity to a file.

        This method should be overridden by subclasses to implement entity-specific saving logic.

        Args:
            entity_id: The ID of the entity
            entity: The entity to save

        Raises:
            Exception: If the entity cannot be saved
        """
        raise NotImplementedError("Subclasses must implement _save_entity")

    def _get_entity(self, entity_id: str) -> Optional[T]:
        """Get an entity from a file.

        This method should be overridden by subclasses to implement entity-specific retrieval logic.

        Args:
            entity_id: The ID of the entity

        Returns:
            The entity, or None if not found

        Raises:
            Exception: If the entity cannot be retrieved
        """
        raise NotImplementedError("Subclasses must implement _get_entity")

    def _delete_entity(self, entity_id: str) -> None:
        """Delete an entity file.

        This method should be overridden by subclasses to implement entity-specific deletion logic.

        Args:
            entity_id: The ID of the entity

        Raises:
            Exception: If the entity cannot be deleted
        """
        raise NotImplementedError("Subclasses must implement _delete_entity")

    def _list_entities(self) -> List[str]:
        """List all entity IDs in the repository.

        This method should be overridden by subclasses to implement entity-specific listing logic.

        Returns:
            A list of entity IDs

        Raises:
            Exception: If the entities cannot be listed
        """
        raise NotImplementedError("Subclasses must implement _list_entities")

    def _ensure_directory_exists(self, directory_path: str) -> None:
        """Ensure a directory exists.

        Args:
            directory_path: The path to the directory

        Raises:
            AutoQliqError: If the directory cannot be created
        """
        if not os.path.exists(directory_path):
            try:
                os.makedirs(directory_path, exist_ok=True)
                self.logger.debug(f"Created directory: {directory_path}")
            except (IOError, PermissionError) as e:
                error_msg = f"Failed to create directory {directory_path}: {str(e)}"
                self.logger.error(error_msg)
                raise AutoQliqError(error_msg, cause=e)

    def _read_json_file(self, file_path: str) -> Any:
        """Read data from a JSON file.

        Args:
            file_path: The path to the JSON file

        Returns:
            The parsed JSON data

        Raises:
            FileNotFoundError: If the file doesn't exist
            json.JSONDecodeError: If the file contains invalid JSON
        """
        self.logger.debug(f"Reading JSON file: {file_path}")
        with open(file_path, 'r') as file:
            data = json.load(file)
            self.logger.debug(f"Successfully read JSON file: {file_path}")
            return data

    def _write_json_file(self, file_path: str, data: Any) -> None:
        """Write data to a JSON file.

        Args:
            file_path: The path to the JSON file
            data: The data to write

        Raises:
            IOError: If the file cannot be written
            TypeError: If the data cannot be serialized to JSON
        """
        self.logger.debug(f"Writing JSON file: {file_path}")
        try:
            with open(file_path, 'w') as file:
                json.dump(data, file, indent=2)
                self.logger.debug(f"Successfully wrote JSON file: {file_path}")
        except (IOError, PermissionError) as e:
            error_msg = f"Failed to write file {file_path}: {str(e)}"
            self.logger.error(error_msg)
            raise IOError(error_msg) from e

    def _file_exists(self, file_path: str) -> bool:
        """Check if a file exists.

        Args:
            file_path: The path to the file

        Returns:
            True if the file exists, False otherwise
        """
        return os.path.exists(file_path)
