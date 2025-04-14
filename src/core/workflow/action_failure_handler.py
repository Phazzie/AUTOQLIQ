"""Action failure handler module for AutoQliq.

Provides functionality for handling action failures.
"""

import logging
from typing import Dict, Any

from src.core.interfaces import IAction
from src.core.action_result import ActionResult
from src.core.exceptions import ActionError

logger = logging.getLogger(__name__)


def handle_action_failure(
    action_result: ActionResult,
    current_action: IAction,
    action_display_name: str,
    error_strategy,
    execution_context: Dict[str, Any]
) -> None:
    """
    Handle a failed action result.
    
    Args:
        action_result: The failed action result
        current_action: The action that failed
        action_display_name: Display name of the action for logging
        error_strategy: Error handling strategy
        execution_context: Execution context to update
        
    Raises:
        Exception: If the error strategy decides to stop execution
    """
    # Mark the context as having failures
    execution_context['had_action_failures'] = True
    
    try:
        # Handle failure according to strategy
        error_strategy.handle_action_failure(
            action_result, current_action, action_display_name
        )
    except Exception:
        # If strategy raises an exception, it wants to stop execution
        raise


def handle_missing_result(
    current_action: IAction,
    action_display_name: str,
    error_strategy,
    execution_context: Dict[str, Any]
) -> ActionResult:
    """
    Handle a missing action result.
    
    Args:
        current_action: The action that produced no result
        action_display_name: Display name of the action for logging
        error_strategy: Error handling strategy
        execution_context: Execution context to update
        
    Returns:
        ActionResult: A failure result
        
    Raises:
        Exception: If the error strategy decides to stop execution
    """
    error_msg = f"Execution returned None for {action_display_name}"
    
    # Mark the context as having failures
    execution_context['had_action_failures'] = True
    
    try:
        # Handle missing result according to strategy
        error_strategy.handle_action_failure(
            ActionResult.failure(error_msg), current_action, action_display_name
        )
        return ActionResult.failure(error_msg)
    except Exception:
        # If strategy raises an exception, it wants to stop execution
        raise
