"""Repositories package for AutoQliq.

This package provides repository implementations for storing and retrieving
credentials and workflows.

NOTE: The direct imports from this package are DEPRECATED and will be removed
in a future release. Use the new imports from the subpackages instead:
- Base classes: src.infrastructure.repositories.base
- Workflow repositories: src.infrastructure.repositories.workflow
- Credential repositories: src.infrastructure.repositories.credential
"""

import warnings

# Re-export base repository classes
from src.infrastructure.repositories.base.repository import Repository
from src.infrastructure.repositories.base.file_system_repository import FileSystemRepository
from src.infrastructure.repositories.base.database_repository import DatabaseRepository

# Import subpackages
from src.infrastructure.repositories import base
from src.infrastructure.repositories import workflow
from src.infrastructure.repositories import credential

# DEPRECATED: Re-export old repository implementations for backward compatibility
# These will be removed in a future release
from src.infrastructure.repositories.credential_repository import FileSystemCredentialRepository
from src.infrastructure.repositories.database_credential_repository import DatabaseCredentialRepository
from src.infrastructure.repositories.workflow_repository import FileSystemWorkflowRepository
from src.infrastructure.repositories.database_workflow_repository import DatabaseWorkflowRepository
from src.infrastructure.repositories.repository_factory import RepositoryFactory

# Show deprecation warning
warnings.warn(
    "Direct imports from src.infrastructure.repositories are deprecated. "
    "Use the new imports from the subpackages instead.",
    DeprecationWarning,
    stacklevel=2
)

__all__ = [
    # Subpackages
    "base",
    "workflow",
    "credential",

    # Base repository classes
    "Repository",
    "FileSystemRepository",
    "DatabaseRepository",

    # DEPRECATED: Old repository implementations
    "FileSystemCredentialRepository",
    "DatabaseCredentialRepository",
    "FileSystemWorkflowRepository",
    "DatabaseWorkflowRepository",
    "RepositoryFactory",
]
