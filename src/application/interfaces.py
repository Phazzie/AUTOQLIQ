"""Application service interfaces for AutoQliq.

This module is maintained for backward compatibility. New code should
use the interfaces package directly.
"""

import warnings

# Re-export all interfaces for backward compatibility
from src.application.interfaces.workflow_service import IWorkflowService
from src.application.interfaces.credential_service import ICredentialService
from src.application.interfaces.webdriver_service import IWebDriverService

__all__ = [
    "IWorkflowService",
    "ICredentialService",
    "IWebDriverService",
]

# Issue deprecation warnings
warnings.warn(
    "The interfaces module is deprecated. Use the interfaces package directly.",
    DeprecationWarning,
    stacklevel=2
)