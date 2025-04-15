"""Action error handler implementation.

This module provides the ActionErrorHandler class for handling action errors.
"""

import logging
import traceback
from typing import Dict, Any

from src.core.interfaces import IAction
from src.core.action_result import ActionResult
from src.core.exceptions import ActionError, ValidationError, WebDriverError
from src.core.workflow.action_execution.interfaces import IActionErrorHandler

logger = logging.getLogger(__name__)


class ActionErrorHandler(IActionErrorHandler):
    """
    Handles errors that occur during action execution.

    Responsible for creating appropriate ActionResult objects for errors.
    """

    def handle_action_error(
        self,
        error: Exception,
        action: IAction,
        action_display_name: str,
        error_strategy: str,
        context: Dict[str, Any]
    ) -> ActionResult:
        """
        Handle an error that occurred during action execution.

        Args:
            error: The exception that was raised
            action: The action that caused the error
            action_display_name: Display name of the action
            error_strategy: Error handling strategy
            context: Execution context

        Returns:
            ActionResult: A failure result with error information

        Raises:
            ActionError: If the error strategy is STOP_ON_ERROR
        """
        # Mark in the context that we had failures
        if "state" in context and isinstance(context["state"], dict):
            context["state"]["had_action_failures"] = True

        # Create a detailed error message
        error_type = type(error).__name__
        error_message = str(error)
        stack_trace = traceback.format_exc()

        # Log the error
        logger.error(
            f"Error executing {action_display_name}: {error_type}: {error_message}",
            exc_info=True
        )

        # Create a failure result
        result = ActionResult.failure(
            f"Error: {error_type}: {error_message}",
            data={
                "error_type": error_type,
                "stack_trace": stack_trace
            }
        )

        # If the error strategy is STOP_ON_ERROR, raise an ActionError
        if error_strategy == "STOP_ON_ERROR":
            # If it's already an ActionError, just re-raise it
            if isinstance(error, ActionError):
                raise error
            
            # Otherwise, wrap it in an ActionError
            raise ActionError(
                f"Error executing {action_display_name}: {error_type}: {error_message}",
                action=action,
                result=result,
                original_error=error
            )

        # Return the failure result
        return result
