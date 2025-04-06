"""Base repository implementations."""

# Re-export base repository classes
from src.infrastructure.repositories.base.file_system_repository import FileSystemRepository
from src.infrastructure.repositories.base.repository import Repository

__all__ = [
    "Repository",
    "FileSystemRepository"
]
