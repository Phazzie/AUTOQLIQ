"""Core interfaces for AutoQliq.

This package defines the core interfaces for the AutoQliq application,
providing contracts for browser automation, actions, and repositories.
"""

# Re-export all interfaces for backward compatibility
from src.core.interfaces.webdriver import IWebDriver
from src.core.interfaces.action import IAction
# Import deprecated repository interfaces for backward compatibility
from src.core.interfaces.repository import IWorkflowRepository as DeprecatedWorkflowRepository
from src.core.interfaces.repository import ICredentialRepository as DeprecatedCredentialRepository
from src.core.interfaces.entity_interfaces import IWorkflow, ICredential

# Import new repository interfaces
from src.core.interfaces.repository.base import IBaseRepository
from src.core.interfaces.repository.workflow import IWorkflowRepository
from src.core.interfaces.repository.credential import ICredentialRepository
from src.core.interfaces.repository.reporting import IReportingRepository

__all__ = [
    # Core interfaces
    "IWebDriver",
    "IAction",
    "IWorkflow",
    "ICredential",

    # New repository interfaces
    "IBaseRepository",
    "IWorkflowRepository",
    "ICredentialRepository",
    "IReportingRepository",

    # Deprecated interfaces (for backward compatibility)
    "DeprecatedWorkflowRepository",
    "DeprecatedCredentialRepository",
]
