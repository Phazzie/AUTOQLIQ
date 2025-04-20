"""Repository factory for AutoQliq."""

import logging
import os
from typing import Dict, Any, Optional, Type, Union

# Core dependencies
from src.core.exceptions import ConfigError
from src.core.interfaces import IWorkflowRepository, ICredentialRepository
from src.core.security.encryption import IEncryptionService

# Infrastructure dependencies
from src.infrastructure.repositories.thread_safe_workflow_repository import ThreadSafeWorkflowRepository
from src.infrastructure.repositories.secure_credential_repository import SecureCredentialRepository
from src.core.security.simple_encryption import SimpleEncryptionService

# Optional database repositories
try:
    from src.infrastructure.repositories.database_workflow_repository import DatabaseWorkflowRepository
    from src.infrastructure.repositories.database_credential_repository import DatabaseCredentialRepository
    from src.infrastructure.common.connection_manager import ConnectionManager
    DATABASE_SUPPORT = True
except ImportError:
    DATABASE_SUPPORT = False

logger = logging.getLogger(__name__)


class RepositoryFactory:
    """
    Factory for creating repository instances.
    
    This factory creates and configures repository instances based on the provided options.
    It supports both file system and database repositories, with appropriate configuration
    for each type.
    """
    
    # Repository type constants
    FILE_SYSTEM = "file_system"
    DATABASE = "database"
    
    @staticmethod
    def create_workflow_repository(
        repo_type: str = FILE_SYSTEM,
        **options
    ) -> IWorkflowRepository:
        """
        Create a workflow repository instance.
        
        Args:
            repo_type: The type of repository to create (file_system or database)
            **options: Additional options for the repository:
                - directory_path: Path to the directory for file system repositories
                - db_path: Path to the database file for database repositories
                - create_if_missing: Whether to create directories/tables if missing
                
        Returns:
            An IWorkflowRepository implementation
            
        Raises:
            ConfigError: If the repository type is unsupported or required options are missing
        """
        logger.info(f"Creating workflow repository of type: {repo_type}")
        
        if repo_type == RepositoryFactory.FILE_SYSTEM:
            # Get directory path from options
            directory_path = options.get('directory_path')
            if not directory_path:
                raise ConfigError("directory_path is required for file system workflow repository")
            
            # Create file system repository
            return ThreadSafeWorkflowRepository(
                directory_path=directory_path,
                create_if_missing=options.get('create_if_missing', True)
            )
            
        elif repo_type == RepositoryFactory.DATABASE:
            # Check if database support is available
            if not DATABASE_SUPPORT:
                raise ConfigError("Database repository support not available")
            
            # Get database path from options
            db_path = options.get('db_path')
            if not db_path:
                raise ConfigError("db_path is required for database workflow repository")
            
            # Create connection manager
            connection_manager = ConnectionManager(db_path)
            
            # Create database repository
            return DatabaseWorkflowRepository(
                connection_manager=connection_manager,
                create_if_missing=options.get('create_if_missing', True)
            )
            
        else:
            raise ConfigError(f"Unsupported workflow repository type: {repo_type}")
    
    @staticmethod
    def create_credential_repository(
        repo_type: str = FILE_SYSTEM,
        encryption_service: Optional[IEncryptionService] = None,
        **options
    ) -> ICredentialRepository:
        """
        Create a credential repository instance.
        
        Args:
            repo_type: The type of repository to create (file_system or database)
            encryption_service: Service for encrypting/decrypting credentials
            **options: Additional options for the repository:
                - file_path: Path to the credentials file for file system repositories
                - db_path: Path to the database file for database repositories
                - create_if_missing: Whether to create files/tables if missing
                - encryption_key: Key for the default encryption service (if no service provided)
                
        Returns:
            An ICredentialRepository implementation
            
        Raises:
            ConfigError: If the repository type is unsupported or required options are missing
        """
        logger.info(f"Creating credential repository of type: {repo_type}")
        
        # Create encryption service if not provided
        if encryption_service is None:
            encryption_key = options.get('encryption_key')
            if not encryption_key:
                raise ConfigError("encryption_key is required when no encryption_service is provided")
            
            encryption_service = SimpleEncryptionService(encryption_key)
            logger.debug("Created default SimpleEncryptionService")
        
        if repo_type == RepositoryFactory.FILE_SYSTEM:
            # Get file path from options
            file_path = options.get('file_path')
            if not file_path:
                raise ConfigError("file_path is required for file system credential repository")
            
            # Create file system repository
            return SecureCredentialRepository(
                file_path=file_path,
                encryption_service=encryption_service,
                create_if_missing=options.get('create_if_missing', True)
            )
            
        elif repo_type == RepositoryFactory.DATABASE:
            # Check if database support is available
            if not DATABASE_SUPPORT:
                raise ConfigError("Database repository support not available")
            
            # Get database path from options
            db_path = options.get('db_path')
            if not db_path:
                raise ConfigError("db_path is required for database credential repository")
            
            # Create connection manager
            connection_manager = ConnectionManager(db_path)
            
            # Create database repository
            return DatabaseCredentialRepository(
                connection_manager=connection_manager,
                encryption_service=encryption_service,
                create_if_missing=options.get('create_if_missing', True)
            )
            
        else:
            raise ConfigError(f"Unsupported credential repository type: {repo_type}")
    
    @staticmethod
    def create_repositories_from_config(config: Dict[str, Any]) -> Dict[str, Union[IWorkflowRepository, ICredentialRepository]]:
        """
        Create repositories from a configuration dictionary.
        
        Args:
            config: Configuration dictionary with repository settings
            
        Returns:
            Dictionary with 'workflow_repo' and 'credential_repo' keys
            
        Raises:
            ConfigError: If the configuration is invalid
        """
        logger.info("Creating repositories from config")
        
        # Extract repository configuration
        repo_config = config.get('repositories', {})
        
        # Get repository type
        repo_type = repo_config.get('type', RepositoryFactory.FILE_SYSTEM)
        
        # Create repositories based on type
        if repo_type == RepositoryFactory.FILE_SYSTEM:
            # Get base directory
            base_dir = repo_config.get('base_directory')
            if not base_dir:
                raise ConfigError("base_directory is required for file system repositories")
            
            # Create workflow repository
            workflow_dir = os.path.join(base_dir, repo_config.get('workflow_subdir', 'workflows'))
            workflow_repo = RepositoryFactory.create_workflow_repository(
                repo_type=RepositoryFactory.FILE_SYSTEM,
                directory_path=workflow_dir,
                create_if_missing=repo_config.get('create_if_missing', True)
            )
            
            # Create credential repository
            credential_file = os.path.join(base_dir, repo_config.get('credential_file', 'credentials.json'))
            encryption_key = repo_config.get('encryption_key')
            if not encryption_key:
                raise ConfigError("encryption_key is required for credential repository")
            
            credential_repo = RepositoryFactory.create_credential_repository(
                repo_type=RepositoryFactory.FILE_SYSTEM,
                file_path=credential_file,
                encryption_key=encryption_key,
                create_if_missing=repo_config.get('create_if_missing', True)
            )
            
        elif repo_type == RepositoryFactory.DATABASE:
            # Check if database support is available
            if not DATABASE_SUPPORT:
                raise ConfigError("Database repository support not available")
            
            # Get database path
            db_path = repo_config.get('db_path')
            if not db_path:
                raise ConfigError("db_path is required for database repositories")
            
            # Create workflow repository
            workflow_repo = RepositoryFactory.create_workflow_repository(
                repo_type=RepositoryFactory.DATABASE,
                db_path=db_path,
                create_if_missing=repo_config.get('create_if_missing', True)
            )
            
            # Create credential repository
            encryption_key = repo_config.get('encryption_key')
            if not encryption_key:
                raise ConfigError("encryption_key is required for credential repository")
            
            credential_repo = RepositoryFactory.create_credential_repository(
                repo_type=RepositoryFactory.DATABASE,
                db_path=db_path,
                encryption_key=encryption_key,
                create_if_missing=repo_config.get('create_if_missing', True)
            )
            
        else:
            raise ConfigError(f"Unsupported repository type: {repo_type}")
        
        return {
            'workflow_repo': workflow_repo,
            'credential_repo': credential_repo
        }
