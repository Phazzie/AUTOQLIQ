"""File system repository implementation for AutoQliq.

This module provides a file system-based implementation of the Repository interface.
"""

import os
import json
import logging
from typing import Any, Dict, TypeVar, Generic, Optional, List
from pathlib import Path

from src.core.exceptions import RepositoryError, ValidationError, SerializationError
from src.infrastructure.repositories.base.repository import Repository

# Type variable for the entity type
T = TypeVar('T')

class FileSystemRepository(Repository[T]):
    """
    Base class for file system repository implementations.

    This class provides common functionality for file system repository implementations,
    such as file operations, serialization, and error handling.

    Attributes:
        logger (logging.Logger): Logger for recording repository operations and errors
    """

    def __init__(self, logger_name: str, base_directory: str = None):
        """
        Initialize a new file system repository instance.

        Args:
            logger_name (str): Name for the repository's logger
            base_directory (str, optional): Base directory for the repository. If provided,
                the directory will be created if it doesn't exist.
        """
        super().__init__(logger_name)

        if base_directory:
            self._ensure_directory_exists(base_directory)
            self.base_directory = base_directory
            self.logger.debug(f"Repository base directory: {self.base_directory}")

    def save(self, entity_id: str, entity: T) -> None:
        """
        Save an entity to the repository.

        Args:
            entity_id (str): ID of the entity to save
            entity (T): Entity to save

        Raises:
            RepositoryError: If the operation fails
            ValidationError: If the entity or ID is invalid
        """
        try:
            self._validate_entity_id(entity_id)
            self._save_entity(entity_id, entity)
            self._log_operation("Saved entity", entity_id)
        except ValidationError as e:
            self.logger.error(f"Validation error saving entity {entity_id}: {e}")
            raise
        except Exception as e:
            error_msg = f"Failed to save entity {entity_id}: {e}"
            self.logger.error(error_msg)
            raise RepositoryError(error_msg, cause=e) from e

    def get(self, entity_id: str) -> Optional[T]:
        """
        Get an entity from the repository by its ID.

        Args:
            entity_id (str): ID of the entity to get

        Returns:
            Optional[T]: The entity if found, None otherwise

        Raises:
            RepositoryError: If the operation fails
            ValidationError: If the entity ID is invalid
        """
        try:
            self._validate_entity_id(entity_id)
            entity = self._get_entity(entity_id)
            if entity:
                self._log_operation("Retrieved entity", entity_id)
            else:
                self.logger.debug(f"Entity {entity_id} not found")
            return entity
        except ValidationError as e:
            self.logger.error(f"Validation error retrieving entity {entity_id}: {e}")
            raise
        except Exception as e:
            error_msg = f"Failed to retrieve entity {entity_id}: {e}"
            self.logger.error(error_msg)
            raise RepositoryError(error_msg, cause=e) from e

    def delete(self, entity_id: str) -> bool:
        """
        Delete an entity from the repository.

        Args:
            entity_id (str): ID of the entity to delete

        Returns:
            bool: True if the entity was deleted, False if it wasn't found

        Raises:
            RepositoryError: If the operation fails
            ValidationError: If the entity ID is invalid
        """
        try:
            self._validate_entity_id(entity_id)
            result = self._delete_entity(entity_id)
            if result:
                self._log_operation("Deleted entity", entity_id)
            else:
                self.logger.debug(f"Entity {entity_id} not found for deletion")
            return result
        except ValidationError as e:
            self.logger.error(f"Validation error deleting entity {entity_id}: {e}")
            raise
        except Exception as e:
            error_msg = f"Failed to delete entity {entity_id}: {e}"
            self.logger.error(error_msg)
            raise RepositoryError(error_msg, cause=e) from e

    def list(self) -> List[str]:
        """
        List all entity IDs in the repository.

        Returns:
            List[str]: List of entity IDs

        Raises:
            RepositoryError: If the operation fails
        """
        try:
            entity_ids = self._list_entities()
            self._log_operation("Listed entities", details=f"Found {len(entity_ids)} entities")
            return entity_ids
        except Exception as e:
            error_msg = f"Failed to list entities: {e}"
            self.logger.error(error_msg)
            raise RepositoryError(error_msg, cause=e) from e

    # --- Template Methods to be Implemented by Subclasses ---

    def _save_entity(self, entity_id: str, entity: T) -> None:
        """
        Template method for saving an entity to the file system.

        Args:
            entity_id (str): ID of the entity to save
            entity (T): Entity to save

        Raises:
            NotImplementedError: This method must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement _save_entity")

    def _get_entity(self, entity_id: str) -> Optional[T]:
        """
        Template method for retrieving an entity from the file system.

        Args:
            entity_id (str): ID of the entity to retrieve

        Returns:
            Optional[T]: The entity if found, None otherwise

        Raises:
            NotImplementedError: This method must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement _get_entity")

    def _delete_entity(self, entity_id: str) -> bool:
        """
        Template method for deleting an entity from the file system.

        Args:
            entity_id (str): ID of the entity to delete

        Returns:
            bool: True if the entity was deleted, False if it wasn't found

        Raises:
            NotImplementedError: This method must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement _delete_entity")

    def _list_entities(self) -> List[str]:
        """
        Template method for listing all entity IDs in the file system.

        Returns:
            List[str]: List of entity IDs

        Raises:
            NotImplementedError: This method must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement _list_entities")

    # --- File System Helper Methods ---

    def _ensure_directory_exists(self, directory_path: str) -> None:
        """
        Ensure that a directory exists, creating it if necessary.

        Args:
            directory_path (str): Path to the directory

        Raises:
            RepositoryError: If the directory cannot be created
        """
        if not directory_path:
            return

        try:
            os.makedirs(directory_path, exist_ok=True)
            self.logger.debug(f"Ensured directory exists: {directory_path}")
        except Exception as e:
            error_msg = f"Failed to create directory {directory_path}: {e}"
            self.logger.error(error_msg)
            raise RepositoryError(error_msg, cause=e) from e

    def _read_json_file(self, file_path: str) -> Any:
        """
        Read and parse a JSON file.

        Args:
            file_path (str): Path to the JSON file

        Returns:
            Any: Parsed JSON data

        Raises:
            RepositoryError: If the file cannot be read or parsed
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError as e:
            self.logger.debug(f"File not found: {file_path}")
            raise e
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON in file {file_path}: {e}"
            self.logger.error(error_msg)
            raise SerializationError(error_msg, cause=e) from e
        except Exception as e:
            error_msg = f"Failed to read file {file_path}: {e}"
            self.logger.error(error_msg)
            raise RepositoryError(error_msg, cause=e) from e

    def _write_json_file(self, file_path: str, data: Any) -> None:
        """
        Write data to a JSON file.

        Args:
            file_path (str): Path to the JSON file
            data (Any): Data to write

        Raises:
            RepositoryError: If the file cannot be written
        """
        try:
            # Ensure the directory exists
            directory = os.path.dirname(file_path)
            if directory:
                self._ensure_directory_exists(directory)

            # Write the file atomically using a temporary file
            temp_file = f"{file_path}.tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            # Replace the original file with the temporary file
            os.replace(temp_file, file_path)
            self.logger.debug(f"Wrote file: {file_path}")
        except Exception as e:
            error_msg = f"Failed to write file {file_path}: {e}"
            self.logger.error(error_msg)
            raise RepositoryError(error_msg, cause=e) from e

    def _file_exists(self, file_path: str) -> bool:
        """
        Check if a file exists.

        Args:
            file_path (str): Path to the file

        Returns:
            bool: True if the file exists, False otherwise
        """
        return os.path.exists(file_path) and os.path.isfile(file_path)
