"""Action error handler module for AutoQliq.

Provides functionality for handling action execution errors.
"""

import logging
from typing import Dict, Any

from src.core.interfaces import IAction
from src.core.action_result import ActionResult
from src.core.exceptions import ActionError

logger = logging.getLogger(__name__)


def handle_action_error(
    error: Exception,
    current_action: IAction,
    action_display_name: str,
    error_strategy,
    execution_context: Dict[str, Any]
) -> ActionResult:
    """
    Handle an error that occurred during action execution.
    
    Args:
        error: The exception that was caught
        current_action: The action that failed
        action_display_name: Display name of the action for logging
        error_strategy: Error handling strategy
        execution_context: Execution context to update
        
    Returns:
        ActionResult: Result to use for the failed action
        
    Raises:
        Exception: If the error strategy decides to stop execution
    """
    # Mark the context as having failures
    execution_context['had_action_failures'] = True
    
    try:
        # Handle error according to strategy
        return error_strategy.handle_action_error(
            error, current_action, action_display_name
        )
    except Exception:
        # If strategy raises an exception, it wants to stop execution
        raise
