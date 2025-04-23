"""Repository interfaces for AutoQliq.

This package provides interfaces for repository implementations that handle
persistence of entities in the AutoQliq application.

IMPORTANT: These are the new consolidated repository interfaces. Use these
instead of the deprecated interfaces in repository.py and repository_interfaces.py.
"""

from src.core.interfaces.repository.base import IBaseRepository
from src.core.interfaces.repository.workflow import IWorkflowRepository
from src.core.interfaces.repository.credential import ICredentialRepository
from src.core.interfaces.repository.reporting import IReportingRepository

__all__ = [
    'IBaseRepository',
    'IWorkflowRepository',
    'ICredentialRepository',
    'IReportingRepository',
]
