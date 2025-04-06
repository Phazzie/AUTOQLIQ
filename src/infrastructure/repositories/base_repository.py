"""Base repository implementation for AutoQliq."""
import json
import logging
import os
from typing import Any, Dict, List, Optional, TypeVar, Generic

from src.core.exceptions import AutoQliqError

# Type variable for the entity type
T = TypeVar('T')

class BaseRepository(Generic[T]):
    """Base class for repository implementations.
    
    This class provides common functionality for repository implementations,
    such as file operations, serialization, and error handling.
    
    Attributes:
        logger: Logger for recording repository operations and errors
    """
    
    def __init__(self, logger_name: str):
        """Initialize a new BaseRepository.
        
        Args:
            logger_name: The name to use for the logger
        """
        self.logger = logging.getLogger(logger_name)
    
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
        """Read and parse a JSON file.
        
        Args:
            file_path: The path to the JSON file
            
        Returns:
            The parsed JSON data
            
        Raises:
            FileNotFoundError: If the file does not exist
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
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=2)
            self.logger.debug(f"Successfully wrote JSON file: {file_path}")
    
    def _file_exists(self, file_path: str) -> bool:
        """Check if a file exists.
        
        Args:
            file_path: The path to the file
            
        Returns:
            True if the file exists, False otherwise
        """
        return os.path.exists(file_path)
