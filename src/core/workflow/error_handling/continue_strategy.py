"""Continue on error strategy implementation.

This module implements the continue on error strategy for the WorkflowRunner.
"""

import logging

from src.core.interfaces import IAction
from src.core.action_result import ActionResult
from src.core.exceptions import WorkflowError
from src.core.workflow.error_handling.base import ErrorHandlingStrategyBase

logger = logging.getLogger(__name__)


class ContinueOnErrorStrategy(ErrorHandlingStrategyBase):
    """
    Strategy that continues workflow execution after errors.
    
    When an action fails, the workflow will log the error but continue with the next action.
    The final status will be COMPLETED_WITH_ERRORS if any actions failed.
    """
    
    def handle_action_error(self, error: Exception, action: IAction, 
                           action_display: str) -> ActionResult:
        """
        Handle an error by logging it and returning a failure result.
        
        Args:
            error: The exception that was caught
            action: The action that failed
            action_display: Display name of the action for logging
            
        Returns:
            ActionResult: A failure result with the error message
            
        Raises:
            WorkflowError: Re-raised if the original error was a WorkflowError
        """
        # Always stop on WorkflowError (e.g., stop requests)
        if isinstance(error, WorkflowError):
            raise error
        
        # With CONTINUE_ON_ERROR, create a failure result and continue
        logger.warning(f"Continuing after error in {action_display} due to CONTINUE_ON_ERROR strategy")
        return ActionResult.failure(f"Action error: {error}")
    
    def handle_action_failure(self, result: ActionResult, action: IAction, 
                             action_display: str) -> None:
        """
        Handle a failed action result by logging it and continuing.
        
        Args:
            result: The failed ActionResult
            action: The action that failed
            action_display: Display name of the action for logging
        """
        logger.warning(f"Continuing after failure in {action_display} due to CONTINUE_ON_ERROR strategy")
        # No exception raised, execution continues
