"""Action execution module for AutoQliq.

Provides action execution functionality for the WorkflowRunner.
"""

import logging
from typing import List, Dict, Any, Optional

from src.core.interfaces import IAction
from src.core.action_result import ActionResult
from src.core.exceptions import WorkflowError, ActionError
from src.core.workflow.action_execution_helper import _execute_single_action
from src.core.workflow.action_failure_handler import handle_action_failure
from src.core.workflow.action_display_formatter import format_action_display_name
from src.core.workflow.stop_event_checker import check_stop_event

logger = logging.getLogger(__name__)


def execute_actions(
    workflow_runner,
    action_list: List[IAction],
    execution_context: Dict[str, Any],
    workflow_name: str,
    log_prefix: str,
    action_executor,
    control_flow_handlers: Dict[str, Any],
    error_strategy
) -> List[ActionResult]:
    """
    Execute a list of actions.

    Args:
        workflow_runner: The WorkflowRunner instance
        action_list: List of actions to execute
        execution_context: Execution context
        workflow_name: Name of the workflow
        log_prefix: Prefix for log messages
        action_executor: Action executor
        control_flow_handlers: Control flow handlers
        error_strategy: Error handling strategy

    Returns:
        List[ActionResult]: Results of executed actions
    """
    return _process_action_list(
        workflow_runner, action_list, execution_context, workflow_name, log_prefix,
        action_executor, control_flow_handlers, error_strategy
    )


def _process_action_list(
    workflow_runner,
    action_list: List[IAction],
    execution_context: Dict[str, Any],
    workflow_name: str,
    log_prefix: str,
    action_executor,
    control_flow_handlers: Dict[str, Any],
    error_strategy
) -> List[ActionResult]:
    """Process a list of actions."""
    execution_results = []
    has_execution_failures = False

    for action_index, current_action in enumerate(action_list):
        # Check if execution should be stopped
        check_stop_event(workflow_runner.stop_event)

        # Process the current action
        step_number = action_index + 1
        action_display_name = format_action_display_name(
            current_action, log_prefix, step_number
        )

        action_result = _execute_single_action(
            current_action, execution_context, workflow_name, log_prefix, step_number,
            action_executor, control_flow_handlers, error_strategy, action_display_name
        )

        execution_results.append(action_result)

        # Handle failure if needed
        if not action_result.is_success():
            has_execution_failures = True
            handle_action_failure(
                action_result, current_action, action_display_name,
                error_strategy, execution_context
            )

    # Mark context if there were failures
    if has_execution_failures:
        execution_context['had_action_failures'] = True

    return execution_results
