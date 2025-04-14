"""Action execution helper module for AutoQliq.

Provides helper functions for action execution.
"""

import logging
from typing import Dict, Any

from src.core.interfaces import IAction
from src.core.action_result import ActionResult
from src.core.workflow.action_error_handler import handle_action_error
from src.core.workflow.action_failure_handler import handle_missing_result
from src.core.workflow.action_type_detector import detect_action_type, get_handler_prefix

logger = logging.getLogger(__name__)


def _execute_single_action(
    action: IAction,
    context: Dict[str, Any],
    workflow_name: str,
    log_prefix: str,
    step_num: int,
    action_executor,
    control_flow_handlers: Dict[str, Any],
    error_strategy,
    action_display: str
) -> ActionResult:
    """
    Execute a single action.

    Args:
        action: The action to execute
        context: Execution context
        workflow_name: Name of the workflow
        log_prefix: Prefix for log messages
        step_num: Step number
        action_executor: Action executor
        control_flow_handlers: Control flow handlers
        error_strategy: Error handling strategy
        action_display: Display name of the action for logging

    Returns:
        ActionResult: Result of the action execution
    """
    try:
        # Determine the appropriate handler
        action_type = detect_action_type(action)

        if action_type:
            # Use the appropriate control flow handler
            handler_prefix = get_handler_prefix(action_type, step_num, log_prefix)
            result = control_flow_handlers[action_type].handle(
                action, context, workflow_name, handler_prefix
            )
        else:
            # Execute regular action
            result = action_executor.execute_action(action, context)

    except Exception as e:
        # Handle error using the error handler
        result = handle_action_error(e, action, action_display, error_strategy, context)

    # Process result
    if result is None:
        # Handle missing result using the failure handler
        result = handle_missing_result(action, action_display, error_strategy, context)

    return result
