"""Application services package for AutoQliq.

This package contains service implementations that coordinate between the core domain
and infrastructure layers, implementing application-specific use cases.

Services act as facades and orchestrators, providing a coarser-grained API
than repositories, suitable for use by presenters or other high-level components.
"""

# Re-export service classes for easier import
from .credential_service import CredentialService
from .workflow_service import WorkflowService
from .webdriver_service import WebDriverService
from .scheduler_service import SchedulerService # Include new stubs
from .reporting_service import ReportingService # Include new stubs

__all__ = [
    "CredentialService",
    "WorkflowService",
    "WebDriverService",
    "SchedulerService",
    "ReportingService",
]