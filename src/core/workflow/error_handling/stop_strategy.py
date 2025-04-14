"""Stop on error strategy implementation.

This module implements the stop on error strategy for the WorkflowRunner.
"""

import logging
from typing import Optional

from src.core.interfaces import IAction
from src.core.action_result import ActionResult
from src.core.exceptions import ActionError, WorkflowError
from src.core.workflow.error_handling.base import ErrorHandlingStrategyBase

logger = logging.getLogger(__name__)


class StopOnErrorStrategy(ErrorHandlingStrategyBase):
    """
    Strategy that stops workflow execution on the first error.
    
    When an action fails, the workflow will stop and raise an ActionError.
    """
    
    def handle_action_error(self, error: Exception, action: IAction, 
                           action_display: str) -> ActionResult:
        """
        Handle an error by raising an ActionError to stop execution.
        
        Args:
            error: The exception that was caught
            action: The action that failed
            action_display: Display name of the action for logging
            
        Raises:
            ActionError: Always raised to stop execution
            WorkflowError: Re-raised if the original error was a WorkflowError
        """
        logger.error(f"ActionError during execution of {action_display}: {error}")
        
        # Always stop on WorkflowError (e.g., stop requests)
        if isinstance(error, WorkflowError):
            raise error
        
        # With STOP_ON_ERROR, re-raise the exception to stop execution
        raise ActionError(
            f"Failure during {action_display}: {error}",
            action_name=action.name, 
            action_type=action.action_type, 
            cause=error
        ) from error
    
    def handle_action_failure(self, result: ActionResult, action: IAction, 
                             action_display: str) -> None:
        """
        Handle a failed action result by raising an ActionError.
        
        Args:
            result: The failed ActionResult
            action: The action that failed
            action_display: Display name of the action for logging
            
        Raises:
            ActionError: Always raised to stop execution
        """
        logger.error(f"Action '{action_display}' failed with message: {result.message}")
        
        # With STOP_ON_ERROR, raise ActionError to stop execution
        raise ActionError(
            result.message or f"Action '{action.name}' failed.",
            action_name=action.name, 
            action_type=action.action_type
        )
