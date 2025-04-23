"""DEPRECATED: Core interfaces consolidation for AutoQliq.

This module is DEPRECATED and will be removed in a future release.
Use the specific interfaces in src.core.interfaces package instead.
"""

# This file serves as a central point for importing core interfaces.
# Individual interface definitions are in the src.core.interfaces package.
# This helps maintain backward compatibility if older code imports from here.

import warnings

# Ensure action_result is available directly if needed
from src.core.action_result import ActionResult
# Import specific interfaces from their modules
from src.core.interfaces.action import IAction
# Import deprecated repository interfaces for backward compatibility
from src.core.interfaces.repository import IWorkflowRepository as DeprecatedWorkflowRepository
from src.core.interfaces.repository import ICredentialRepository as DeprecatedCredentialRepository
# Import new repository interfaces
from src.core.interfaces.repository.base import IBaseRepository
from src.core.interfaces.repository.workflow import IWorkflowRepository
from src.core.interfaces.repository.credential import ICredentialRepository
from src.core.interfaces.repository.reporting import IReportingRepository
from src.core.interfaces.webdriver import IWebDriver
from src.core.interfaces.entity_interfaces import IWorkflow, ICredential


__all__ = [
    # Core interfaces
    "IAction",
    "IWebDriver",
    "IWorkflow",
    "ICredential",
    "ActionResult", # Export ActionResult as well

    # New repository interfaces
    "IBaseRepository",
    "IWorkflowRepository",
    "ICredentialRepository",
    "IReportingRepository",

    # Deprecated interfaces (for backward compatibility)
    "DeprecatedWorkflowRepository",
    "DeprecatedCredentialRepository"
]

warnings.warn(
    "This module is DEPRECATED and will be removed in a future release. "
    "Please import from the specific modules within the src.core.interfaces package "
    "(e.g., src.core.interfaces.repository.workflow).",
    DeprecationWarning,
    stacklevel=2
)
