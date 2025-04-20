"""Base repository abstract class for AutoQliq."""
import abc
import logging
from typing import TypeVar, Generic, Optional, List

# Assuming core interfaces, exceptions, and common utilities are defined
# No direct dependency on IRepository interfaces here, concrete classes implement specific ones
from src.core.exceptions import RepositoryError, ValidationError
from src.infrastructure.common.logger_factory import LoggerFactory
from src.infrastructure.common.validators import EntityValidator

# Type variable for the entity type managed by the repository
T = TypeVar('T')

class Repository(abc.ABC, Generic[T]):
    """
    Abstract base class for repository implementations.

    Provides common infrastructure like logging and basic ID validation.
    Concrete subclasses must implement specific repository interfaces
    (e.g., IWorkflowRepository, ICredentialRepository).

    Attributes:
        logger (logging.Logger): Logger instance specific to the repository implementation.
    """

    def __init__(self, logger_name: Optional[str] = None):
        """
        Initialize a new Repository instance.

        Args:
            logger_name (Optional[str]): The name for the logger. If None, defaults
                                         to the name of the concrete subclass.
        """
        if logger_name is None:
            logger_name = self.__class__.__name__ # Use subclass name if not provided
        self.logger = LoggerFactory.get_logger(f"repository.{logger_name}")
        self.logger.info(f"{self.__class__.__name__} initialized.")

    # Note: Abstract methods for save, get, delete, list are NOT defined here.
    # Concrete implementations should implement methods defined in the specific
    # core interfaces (IWorkflowRepository, ICredentialRepository).
    # This base class provides shared utilities.

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
        try:
             EntityValidator.validate_entity_id(entity_id, entity_type=entity_type)
             # self.logger.debug(f"Validated {entity_type} ID: '{entity_id}'") # Logging done by caller if needed
        except ValidationError as e:
             # Log the validation error before re-raising
             self.logger.warning(f"Invalid {entity_type} ID validation: {e}")
             raise # Re-raise the original ValidationError


    def _log_operation(self, operation: str, entity_id: Optional[str] = None, details: str = "") -> None:
        """
        Log a repository operation.

        Args:
            operation (str): Description of the operation (e.g., "Saving", "Loading list").
            entity_id (Optional[str]): The ID of the entity involved, if applicable.
            details (str): Optional additional details for the log message.
        """
        log_message = operation
        if entity_id:
            log_message += f" ID: '{entity_id}'"
        if details:
             log_message += f" ({details})"
        self.logger.debug(log_message)