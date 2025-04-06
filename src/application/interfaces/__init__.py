"""Application service interfaces for AutoQliq.

This package defines the interfaces for application services that coordinate between
the core domain and infrastructure layers, implementing application-specific use cases.
"""

# Re-export all interfaces for backward compatibility
from src.application.interfaces.workflow_service import IWorkflowService
from src.application.interfaces.credential_service import ICredentialService
from src.application.interfaces.webdriver_service import IWebDriverService

__all__ = [
    "IWorkflowService",
    "ICredentialService",
    "IWebDriverService",
]