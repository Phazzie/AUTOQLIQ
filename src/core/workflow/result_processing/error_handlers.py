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

        # Extract more detailed information from the action error
        action_name = getattr(action_error, 'action_name', 'Unknown')
        action_type = getattr(action_error, 'action_type', 'Unknown')

        # Log the error with detailed information
        logger.error(
            f"Action error in '{action_name}' (type: {action_type}): {error}",
            exc_info=True
        )

        # Create a more detailed error message
        error_message = str(error)
        summary = f"Failed during action '{action_name}' (type: {action_type}): {error_message}"

        return "FAILED", error_message, summary


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
        workflow_error = error  # type: WorkflowError

        # Extract workflow name if available
        workflow_name = getattr(workflow_error, 'workflow_name', 'Unknown')

        # Log the error with detailed information
        logger.error(
            f"Workflow error in '{workflow_name}': {error}",
            exc_info=True
        )

        # Create a more detailed error message
        error_message = str(error)
        summary = f"Workflow error in '{workflow_name}': {error_message}"

        return "FAILED", error_message, summary


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
        # Log the error with detailed information
        logger.error(
            f"Unexpected error of type {type(error).__name__}: {error}",
            exc_info=True
        )

        # Create a more detailed error message
        error_type = type(error).__name__
        error_message = str(error)
        summary = f"Unexpected error of type {error_type}: {error_message}"

        return "FAILED", error_message, summary
