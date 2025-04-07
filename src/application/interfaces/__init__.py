"""Application service interfaces for AutoQliq.

DEPRECATED: Interfaces are now defined in src.core.interfaces.service.py
This package remains for backward compatibility.
"""
import warnings

# Re-export from the new location
from src.core.interfaces.service import (
    IService, IWorkflowService, ICredentialService, IWebDriverService,
    ISchedulerService, IReportingService # Include new ones
)


__all__ = [
    "IService",
    "IWorkflowService",
    "ICredentialService",
    "IWebDriverService",
    "ISchedulerService",
    "IReportingService",
]

warnings.warn(
    "Importing from src.application.interfaces is deprecated. "
    "Import service interfaces from src.core.interfaces.service instead.",
    DeprecationWarning,
    stacklevel=2
)