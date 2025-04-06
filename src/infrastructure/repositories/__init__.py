"""Repositories package for AutoQliq.

This package provides repository implementations for storing and retrieving
credentials and workflows.
"""

# Re-export repository implementations
from src.infrastructure.repositories.credential_repository import FileSystemCredentialRepository
from src.infrastructure.repositories.database_credential_repository import DatabaseCredentialRepository
from src.infrastructure.repositories.workflow_repository import FileSystemWorkflowRepository
from src.infrastructure.repositories.database_workflow_repository import DatabaseWorkflowRepository
from src.infrastructure.repositories.repository_factory import RepositoryFactory

# Re-export base repository classes
from src.infrastructure.repositories.base.repository import Repository
from src.infrastructure.repositories.base.file_system_repository import FileSystemRepository
from src.infrastructure.repositories.base.database_repository import DatabaseRepository

__all__ = [
    # Repository implementations
    "FileSystemCredentialRepository",
    "DatabaseCredentialRepository",
    "FileSystemWorkflowRepository",
    "DatabaseWorkflowRepository",
    "RepositoryFactory",

    # Base repository classes
    "Repository",
    "FileSystemRepository",
    "DatabaseRepository",
]
