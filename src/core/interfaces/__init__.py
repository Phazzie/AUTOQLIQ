"""Core interfaces for AutoQliq.

This package defines the core interfaces for the AutoQliq application,
providing contracts for browser automation, actions, and repositories.
"""

# Re-export all interfaces for backward compatibility
from src.core.interfaces.webdriver import IWebDriver
from src.core.interfaces.action import IAction
from src.core.interfaces.repository import IWorkflowRepository, ICredentialRepository

__all__ = [
    "IWebDriver",
    "IAction",
    "IWorkflowRepository",
    "ICredentialRepository",
]