"""Utility functions for control flow handlers.

This module provides common utility functions used by multiple control flow handlers.
"""

import logging
from typing import List, Dict, Any

from src.core.action_result import ActionResult

logger = logging.getLogger(__name__)


def evaluate_action_results(
    results: List[ActionResult], 
    branch_name: str, 
    log_prefix: str = "",
    success_message_template: str = "{branch_name} executed successfully ({action_count} actions)",
    failure_message_template: str = "{branch_name} had failures ({action_count} actions)"
) -> ActionResult:
    """
    Evaluate a list of action results and return a single ActionResult.
    
    This is a common utility used by various control flow handlers to determine
    the overall success or failure of a branch of actions.
    
    Args:
        results: List of ActionResult objects to evaluate
        branch_name: Name of the branch or block being evaluated (e.g., 'true', 'catch')
        log_prefix: Prefix for log messages
        success_message_template: Template for success message
        failure_message_template: Template for failure message
        
    Returns:
        ActionResult: A single ActionResult representing the overall result
    """
    all_success = all(result.is_success() for result in results)
    action_count = len(results)
    
    if all_success:
        logger.info(f"{log_prefix}{branch_name} block succeeded.")
        return ActionResult.success(
            success_message_template.format(branch_name=branch_name, action_count=action_count)
        )
    else:
        # If we got here with failures, we must be using CONTINUE_ON_ERROR
        logger.warning(f"{log_prefix}{branch_name} block had failures.")
        return ActionResult.failure(
            failure_message_template.format(branch_name=branch_name, action_count=action_count)
        )


def create_error_context(context: Dict[str, Any], error: Exception, prefix: str = "") -> Dict[str, Any]:
    """
    Create a context with error information.
    
    This is a common utility used by error handling mechanisms to add error
    information to the context for error handling actions.
    
    Args:
        context: The original execution context
        error: The exception that occurred
        prefix: Optional prefix for error keys (e.g., 'try_block_' for catch blocks)
        
    Returns:
        Dict[str, Any]: The context with added error information
    """
    error_context = context.copy()
    error_context.update({
        f'{prefix}error': str(error),
        f'{prefix}error_type': type(error).__name__,
        f'{prefix}error_message': str(error),
        f'{prefix}error_type_name': type(error).__name__
    })
    return error_context
