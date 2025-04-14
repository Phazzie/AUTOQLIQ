"""Retry on error strategy implementation.

This module implements the retry on error strategy for the WorkflowRunner.
"""

import logging
import time
from typing import Dict, Optional

from src.core.interfaces import IAction
from src.core.action_result import ActionResult
from src.core.exceptions import WorkflowError
from src.core.workflow.error_handling.base import ErrorHandlingStrategyBase
from src.core.workflow.error_handling.stop_strategy import StopOnErrorStrategy

logger = logging.getLogger(__name__)


class RetryOnErrorStrategy(ErrorHandlingStrategyBase):
    """
    Strategy that retries failed actions before continuing or stopping.
    
    When an action fails, the workflow will retry it a specified number of times
    before either continuing or stopping based on the fallback strategy.
    """
    
    def __init__(self, max_retries: int = 3, retry_delay_seconds: float = 1.0, 
                fallback_strategy: Optional[ErrorHandlingStrategyBase] = None):
        """
        Initialize the retry strategy.
        
        Args:
            max_retries: Maximum number of retry attempts
            retry_delay_seconds: Delay between retry attempts in seconds
            fallback_strategy: Strategy to use after max retries is reached
                               (defaults to StopOnErrorStrategy)
        """
        self.max_retries = max_retries
        self.retry_delay_seconds = retry_delay_seconds
        self.fallback_strategy = fallback_strategy or StopOnErrorStrategy()
        self.retry_counts: Dict[str, int] = {}  # Track retry counts by action
    
    def handle_action_error(self, error: Exception, action: IAction, 
                           action_display: str) -> ActionResult:
        """
        Handle an error by retrying the action if retries remain.
        
        Args:
            error: The exception that was caught
            action: The action that failed
            action_display: Display name of the action for logging
            
        Returns:
            ActionResult: A failure result if max retries reached
            
        Raises:
            ActionError: If fallback strategy is StopOnErrorStrategy and max retries reached
            WorkflowError: Re-raised if the original error was a WorkflowError
        """
        # Always stop on WorkflowError (e.g., stop requests)
        if isinstance(error, WorkflowError):
            raise error
        
        # Get current retry count for this action
        action_id = f"{action.name}_{id(action)}"
        current_retries = self.retry_counts.get(action_id, 0)
        
        if current_retries < self.max_retries:
            # Increment retry count
            self.retry_counts[action_id] = current_retries + 1
            
            # Log retry attempt
            logger.warning(
                f"Retrying {action_display} after error (attempt {current_retries + 1}/{self.max_retries}): {error}"
            )
            
            # Add delay if configured
            if self.retry_delay_seconds > 0:
                time.sleep(self.retry_delay_seconds)
            
            # Signal that this action should be retried
            return ActionResult.failure(
                f"Retry attempt {current_retries + 1}/{self.max_retries}",
                data={"retry": True, "retry_count": current_retries + 1}
            )
        else:
            # Max retries reached, use fallback strategy
            logger.error(f"Max retries ({self.max_retries}) reached for {action_display}")
            self.retry_counts[action_id] = 0  # Reset for potential future runs
            return self.fallback_strategy.handle_action_error(error, action, action_display)
    
    def handle_action_failure(self, result: ActionResult, action: IAction, 
                             action_display: str) -> None:
        """
        Handle a failed action result by retrying if retries remain.
        
        Args:
            result: The failed ActionResult
            action: The action that failed
            action_display: Display name of the action for logging
            
        Raises:
            ActionError: If fallback strategy is StopOnErrorStrategy and max retries reached
        """
        # Get current retry count for this action
        action_id = f"{action.name}_{id(action)}"
        current_retries = self.retry_counts.get(action_id, 0)
        
        if current_retries < self.max_retries:
            # Increment retry count
            self.retry_counts[action_id] = current_retries + 1
            
            # Log retry attempt
            logger.warning(
                f"Retrying {action_display} after failure (attempt {current_retries + 1}/{self.max_retries}): {result.message}"
            )
            
            # Add delay if configured
            if self.retry_delay_seconds > 0:
                time.sleep(self.retry_delay_seconds)
            
            # The runner will need to handle this special case
            # No exception raised, but runner should check result.data["retry"]
            result.data["retry"] = True
            result.data["retry_count"] = current_retries + 1
        else:
            # Max retries reached, use fallback strategy
            logger.error(f"Max retries ({self.max_retries}) reached for {action_display}")
            self.retry_counts[action_id] = 0  # Reset for potential future runs
            self.fallback_strategy.handle_action_failure(result, action, action_display)
