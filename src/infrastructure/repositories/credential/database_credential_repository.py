"""Database credential repository implementation for AutoQliq.

This module provides a database-based implementation of the ICredentialRepository
interface for storing and retrieving credentials securely.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from src.core.exceptions import RepositoryError, ValidationError, SerializationError
from src.core.interfaces.repository.credential import ICredentialRepository
from src.core.interfaces.security import IEncryptionService
from src.infrastructure.repositories.base.database_repository import DatabaseRepository

# Use TYPE_CHECKING to avoid circular imports
if TYPE_CHECKING:
    from src.core.credentials import Credentials

logger = logging.getLogger(__name__)

class DatabaseCredentialRepository(DatabaseRepository["Credentials"], ICredentialRepository):
    """Database implementation of the credential repository.
    
    This class provides a database-based implementation of the ICredentialRepository
    interface. It stores credentials in a SQLite database with encrypted passwords.
    
    Attributes:
        db_path (str): Path to the SQLite database file
        connection_manager: Manager for database connections
        encryption_service (IEncryptionService): Service for encrypting and decrypting credentials
    """
    
    _TABLE_NAME = "credentials"
    _PK_COLUMN = "name"
    
    def __init__(
        self, 
        db_path: str, 
        encryption_service: IEncryptionService,
        **options: Any
    ):
        """Initialize a new DatabaseCredentialRepository.
        
        Args:
            db_path: Path to the SQLite database file
            encryption_service: Service for encrypting and decrypting credentials
            **options: Additional options
                
        Raises:
            RepositoryError: If the database cannot be created or accessed
            ValueError: If encryption_service is None
        """
        super().__init__(db_path, self._TABLE_NAME, "credential_repository")
        
        if not encryption_service:
            raise ValueError("Encryption service cannot be None")
        
        self.encryption_service = encryption_service
        logger.info(f"Initialized credential repository with database: {db_path}")
    
    def save(self, credential: "Credentials") -> None:
        """Save a credential to the repository.
        
        Args:
            credential: The credential to save
            
        Raises:
            ValidationError: If the credential is invalid
            RepositoryError: If the operation fails
        """
        if not credential:
            raise ValidationError("Credential cannot be None")
        
        if not credential.name:
            raise ValidationError("Credential name cannot be empty")
        
        # Update the credential's updated_at timestamp
        credential.updated_at = datetime.now()
        
        # If this is a new credential, set the created_at timestamp
        if not credential.created_at:
            credential.created_at = credential.updated_at
        
        # Save the credential
        super().save(credential.name, credential)
    
    def get(self, credential_id: str) -> Optional["Credentials"]:
        """Get a credential from the repository by ID.
        
        Args:
            credential_id: ID of the credential to get
            
        Returns:
            The credential if found, None otherwise
            
        Raises:
            ValidationError: If the credential ID is invalid
            RepositoryError: If the operation fails
        """
        return super().get(credential_id)
    
    def get_by_name(self, name: str) -> Optional["Credentials"]:
        """Get a credential from the repository by name.
        
        Args:
            name: Name of the credential to get
            
        Returns:
            The credential if found, None otherwise
            
        Raises:
            ValidationError: If the name is invalid
            RepositoryError: If the operation fails
        """
        return self.get(name)
    
    def list_credentials(self) -> List[Dict[str, str]]:
        """List all credentials with basic information (excluding sensitive data).
        
        Returns:
            List of dictionaries containing credential ID, name, and username
            
        Raises:
            RepositoryError: If the operation fails
        """
        try:
            query = f"""
                SELECT 
                    {self._PK_COLUMN}, 
                    username, 
                    description, 
                    created_at, 
                    updated_at
                FROM {self._TABLE_NAME}
                ORDER BY {self._PK_COLUMN}
            """
            rows = self.connection_manager.execute_query(query)
            
            credentials = []
            for row in rows:
                credentials.append({
                    "id": row.get(self._PK_COLUMN),
                    "name": row.get(self._PK_COLUMN),
                    "username": row.get("username"),
                    "description": row.get("description"),
                    "created_at": row.get("created_at"),
                    "updated_at": row.get("updated_at")
                })
            
            return credentials
        except Exception as e:
            error_msg = f"Failed to list credentials: {e}"
            logger.error(error_msg)
            raise RepositoryError(error_msg, repository_name="CredentialRepository", cause=e) from e
    
    # Implementation of abstract methods from DatabaseRepository
    
    def _get_table_creation_sql(self) -> str:
        """Get the SQL for creating the credentials table.
        
        Returns:
            SQL statement for creating the table
        """
        return f"""
            {self._PK_COLUMN} TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT,
            description TEXT,
            created_at TEXT,
            updated_at TEXT
        """
    
    def _map_row_to_entity(self, row: Dict[str, Any]) -> "Credentials":
        """Map a database row to a credential entity.
        
        Args:
            row: Database row
            
        Returns:
            Credential entity
            
        Raises:
            SerializationError: If the row cannot be mapped to a credential
        """
        try:
            # Import here to avoid circular imports
            from src.core.credentials import Credentials
            
            # Get the credential data
            name = row.get(self._PK_COLUMN)
            username = row.get("username")
            encrypted_password = row.get("password")
            description = row.get("description")
            created_at_str = row.get("created_at")
            updated_at_str = row.get("updated_at")
            
            # Parse dates
            created_at = datetime.fromisoformat(created_at_str) if created_at_str else None
            updated_at = datetime.fromisoformat(updated_at_str) if updated_at_str else None
            
            # Decrypt the password
            password = None
            if encrypted_password:
                password = self.encryption_service.decrypt(encrypted_password)
            
            # Create the credential
            credential = Credentials(
                name=name,
                username=username,
                password=password,
                description=description,
                created_at=created_at,
                updated_at=updated_at
            )
            
            return credential
        except Exception as e:
            error_msg = f"Failed to map row to credential: {e}"
            logger.error(error_msg)
            raise SerializationError(error_msg, cause=e) from e
    
    def _map_entity_to_params(self, entity_id: str, entity: "Credentials") -> Dict[str, Any]:
        """Map a credential entity to database parameters.
        
        Args:
            entity_id: ID of the credential
            entity: Credential entity
            
        Returns:
            Dictionary of database parameters
            
        Raises:
            SerializationError: If the credential cannot be mapped to parameters
        """
        try:
            # Encrypt the password
            encrypted_password = None
            if entity.password:
                encrypted_password = self.encryption_service.encrypt(entity.password)
            
            # Map to parameters
            params = {
                self._PK_COLUMN: entity_id,
                "username": entity.username,
                "password": encrypted_password,
                "description": entity.description,
                "created_at": entity.created_at.isoformat() if entity.created_at else None,
                "updated_at": entity.updated_at.isoformat() if entity.updated_at else None
            }
            
            return params
        except Exception as e:
            error_msg = f"Failed to map credential to parameters: {e}"
            logger.error(error_msg)
            raise SerializationError(error_msg, cause=e) from e
    
    def _get_primary_key_col(self) -> str:
        """Get the primary key column name.
        
        Returns:
            Name of the primary key column
        """
        return self._PK_COLUMN
