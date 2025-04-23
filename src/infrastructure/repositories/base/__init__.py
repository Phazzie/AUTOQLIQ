"""Base repository implementations for AutoQliq.

This package provides base classes for repository implementations that handle
persistence of entities in the AutoQliq application.
"""

# Re-export base repository classes
from src.infrastructure.repositories.base.repository import Repository
from src.infrastructure.repositories.base.file_system_repository import FileSystemRepository
from src.infrastructure.repositories.base.database_repository import DatabaseRepository

__all__ = [
    "Repository",
    "FileSystemRepository",
    "DatabaseRepository"
]
