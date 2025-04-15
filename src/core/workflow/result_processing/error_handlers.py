"""Error handlers for workflow execution.

This module provides error handlers for workflow execution.
"""

import logging
from typing import Tuple

from src.core.exceptions import WorkflowError, ActionError
from src.core.workflow.result_processing.interfaces import IErrorHandler

logger = logging.getLogger(__name__)


class StopRequestHandler(IErrorHandler):
    """Handler for workflow stop requests."""
    
    def can_handle(self, error: Exception) -> bool:
        """
        Determine if this handler can handle the given error.
        
        Args:
            error: The exception to handle
            
        Returns:
            bool: True if this handler can handle the error
        """
        return (isinstance(error, WorkflowError) and 
                "stopped by request" in str(error).lower())
    
    def handle(self, error: Exception) -> Tuple[str, str, str]:
        """
        Handle the error and determine the workflow status.
        
        Args:
            error: The exception to handle
            
        Returns:
            Tuple[str, str, str]: Final status, error message, and summary
        """
        return "STOPPED", "Execution stopped by user request.", "Execution stopped by user request"


class ActionErrorHandler(IErrorHandler):
    """Handler for action errors."""
    
    def can_handle(self, error: Exception) -> bool:
        """
        Determine if this handler can handle the given error.
        
        Args:
            error: The exception to handle
            
        Returns:
            bool: True if this handler can handle the error
        """
        return isinstance(error, ActionError)
    
    def handle(self, error: Exception) -> Tuple[str, str, str]:
        """
        Handle the error and determine the workflow status.
        
        Args:
            error: The exception to handle
            
        Returns:
            Tuple[str, str, str]: Final status, error message, and summary
        """
        action_error = error  # type: ActionError
        return "FAILED", str(error), f"Failed during action '{action_error.action_name}': {error}"


class WorkflowErrorHandler(IErrorHandler):
    """Handler for workflow errors."""
    
    def can_handle(self, error: Exception) -> bool:
        """
        Determine if this handler can handle the given error.
        
        Args:
            error: The exception to handle
            
        Returns:
            bool: True if this handler can handle the error
        """
        return isinstance(error, WorkflowError)
    
    def handle(self, error: Exception) -> Tuple[str, str, str]:
        """
        Handle the error and determine the workflow status.
        
        Args:
            error: The exception to handle
            
        Returns:
            Tuple[str, str, str]: Final status, error message, and summary
        """
        return "FAILED", str(error), f"Workflow error: {error}"


class GenericErrorHandler(IErrorHandler):
    """Handler for generic errors."""
    
    def can_handle(self, error: Exception) -> bool:
        """
        Determine if this handler can handle the given error.
        
        Args:
            error: The exception to handle
            
        Returns:
            bool: True if this handler can handle the error
        """
        return True  # Fallback handler for any error
    
    def handle(self, error: Exception) -> Tuple[str, str, str]:
        """
        Handle the error and determine the workflow status.
        
        Args:
            error: The exception to handle
            
        Returns:
            Tuple[str, str, str]: Final status, error message, and summary
        """
        return "FAILED", f"Unexpected error: {error}", f"Unexpected error: {error}"
