"""Factory for creating repository instances."""
import logging
from typing import Any, Literal, TypeVar

from src.core.exceptions import RepositoryError, ConfigError
from src.core.interfaces import ICredentialRepository, IWorkflowRepository
# Import available repository implementations
from src.infrastructure.repositories.credential_repository import FileSystemCredentialRepository
from src.infrastructure.repositories.database_credential_repository import DatabaseCredentialRepository
from src.infrastructure.repositories.workflow_repository import FileSystemWorkflowRepository
from src.infrastructure.repositories.database_workflow_repository import DatabaseWorkflowRepository
from src.core.template.repository import TemplateRepository

# Type variables for better type hinting
T = TypeVar('T') # Generic type for repository interface

logger = logging.getLogger(__name__)

# Define allowed repository types for type hinting and validation
RepositoryType = Literal["file_system", "database"]


class RepositoryFactory:
    """
    Factory class for creating repository instances based on configuration.

    This factory decouples the application logic from the specific repository
    implementations, allowing easy switching between storage backends (e.g.,
    file system vs. database).
    """

    def __init__(self):
        """Initialize a new RepositoryFactory."""
        self.logger = logger # Use module-level logger
        self.logger.info("RepositoryFactory initialized.")

    def create_credential_repository(
        self,
        repository_type: RepositoryType = "file_system",
        path: str = "credentials.json", # Default path for file system
        **options: Any
    ) -> ICredentialRepository:
        """
        Create a credential repository instance based on the specified type.

        Args:
            repository_type: The type of repository ("file_system" or "database").
                             Defaults to "file_system".
            path: Path to the credentials file (for file_system) or database (for database).
            **options: Additional options specific to the repository type
                       (e.g., 'create_if_missing' for file_system).

        Returns:
            An instance conforming to the ICredentialRepository interface.

        Raises:
            ConfigError: If the repository_type is unsupported or required options are missing.
            RepositoryError: If the repository instantiation fails.
        """
        self.logger.info(f"Creating ICredentialRepository of type '{repository_type}' with path='{path}'")

        try:
            if repository_type == "file_system":
                # Example option: Ensure file exists on creation
                options.setdefault('create_if_missing', True) # Sensible default for file repo
                return FileSystemCredentialRepository(file_path=path, **options)
            elif repository_type == "database":
                # Database repository might need the db path, passed via 'path' argument
                return DatabaseCredentialRepository(db_path=path, **options)
            else:
                valid_types = ["file_system", "database"]
                error_msg = f"Unsupported credential repository type: '{repository_type}'. Valid types are: {valid_types}"
                self.logger.error(error_msg)
                raise ConfigError(error_msg)
        except Exception as e:
             # Catch potential errors during instantiation (e.g., invalid path, DB connection issues)
             error_msg = f"Failed to create credential repository (type={repository_type}, path={path}): {e}"
             self.logger.error(error_msg, exc_info=True)
             # Wrap unexpected errors in RepositoryError
             if not isinstance(e, (ConfigError, RepositoryError)):
                  raise RepositoryError(error_msg, repository_name="CredentialRepository", cause=e) from e
             raise # Re-raise ConfigError or RepositoryError

    def create_workflow_repository(
        self,
        repository_type: RepositoryType = "file_system",
        path: str = "workflows", # Default path for file system (directory)
        **options: Any
    ) -> IWorkflowRepository:
        """
        Create a workflow repository instance based on the specified type.

        Args:
            repository_type: The type of repository ("file_system" or "database").
                             Defaults to "file_system".
            path: Path to the workflows directory (for file_system) or database (for database).
            **options: Additional options specific to the repository type
                       (e.g., 'create_if_missing' for file_system directory).

        Returns:
            An instance conforming to the IWorkflowRepository interface.

        Raises:
            ConfigError: If the repository_type is unsupported or required options are missing.
            RepositoryError: If the repository instantiation fails.
        """
        self.logger.info(f"Creating IWorkflowRepository of type '{repository_type}' with path='{path}'")

        try:
            if repository_type == "file_system":
                # Example option: Ensure directory exists on creation
                options.setdefault('create_if_missing', True) # Sensible default for FS repo
                return FileSystemWorkflowRepository(directory_path=path, **options)
            elif repository_type == "database":
                 # Database repository might need the db path, passed via 'path' argument
                return DatabaseWorkflowRepository(db_path=path, **options)
            else:
                valid_types = ["file_system", "database"]
                error_msg = f"Unsupported workflow repository type: '{repository_type}'. Valid types are: {valid_types}"
                self.logger.error(error_msg)
                raise ConfigError(error_msg)
        except Exception as e:
             # Catch potential errors during instantiation
             error_msg = f"Failed to create workflow repository (type={repository_type}, path={path}): {e}"
             self.logger.error(error_msg, exc_info=True)
             # Wrap unexpected errors in RepositoryError
             if not isinstance(e, (ConfigError, RepositoryError)):
                  raise RepositoryError(error_msg, repository_name="WorkflowRepository", cause=e) from e
             raise # Re-raise ConfigError or RepositoryError

    def create_template_repository(
        self,
        directory_path: str = None,
        **options: Any
    ) -> TemplateRepository:
        """
        Create a template repository instance.

        Args:
            directory_path: Path to the templates directory. If None, uses the default path.
            **options: Additional options specific to the repository type.

        Returns:
            A TemplateRepository instance.

        Raises:
            RepositoryError: If the repository instantiation fails.
        """
        self.logger.info(f"Creating TemplateRepository with directory_path='{directory_path}'")

        try:
            return TemplateRepository(directory_path=directory_path)
        except Exception as e:
            # Catch potential errors during instantiation
            error_msg = f"Failed to create template repository (directory_path={directory_path}): {e}"
            self.logger.error(error_msg, exc_info=True)
            # Wrap unexpected errors in RepositoryError
            if not isinstance(e, RepositoryError):
                raise RepositoryError(error_msg, repository_name="TemplateRepository", cause=e) from e
            raise # Re-raise RepositoryError