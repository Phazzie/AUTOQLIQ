"""Workflow service interface for AutoQliq.

DEPRECATED: Use src.core.interfaces.service.IWorkflowService instead.
This module remains for backward compatibility.
"""
import warnings

# Re-export from the new location
from src.core.interfaces.service import IWorkflowService

__all__ = ["IWorkflowService"]

warnings.warn(
    "Importing IWorkflowService from src.application.interfaces.workflow_service is deprecated. "
    "Import from src.core.interfaces.service instead.",
    DeprecationWarning,
    stacklevel=2
)