"""Workflow package initialization for AutoQliq.

This package contains components related to workflow definition,
execution, and management.

Exports:
    WorkflowRunner: Class responsible for executing a sequence of actions.
    Workflow: Core entity representing a sequence of actions.
    # Add other relevant exports as the package grows, e.g.,
    # WorkflowErrorHandler, CredentialManager
"""

from .runner import WorkflowRunner
from .workflow_entity import Workflow
# Placeholder imports for potentially future components
# from .error_handler import WorkflowErrorHandler
# from .credential_manager import CredentialManager

__all__ = [
    "WorkflowRunner",
    "Workflow",
    # "WorkflowErrorHandler",
    # "CredentialManager",
]
