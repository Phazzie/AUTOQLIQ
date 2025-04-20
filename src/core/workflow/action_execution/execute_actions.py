"""Action execution module for AutoQliq workflows.

This module provides the execute_actions function for the WorkflowRunner.
"""

import logging
from typing import List, Dict, Any, Optional

from src.core.interfaces import IAction
from src.core.action_result import ActionResult
from src.core.exceptions import WorkflowError, ActionError
from src.core.workflow.stop_event_checker import check_stop_event

logger = logging.getLogger(__name__)


def execute_actions(
    runner,
    actions: List[IAction],
    context: Dict[str, Any],
    workflow_name: str,
    log_prefix: str,
    action_executor,
    control_flow_handlers,
    error_strategy
) -> List[ActionResult]:
    """
    Execute a list of actions.

    Args:
        runner: The WorkflowRunner instance
        actions: List of actions to execute
        context: Execution context
        workflow_name: Name of the workflow
        log_prefix: Prefix for log messages
        action_executor: Action executor component
        control_flow_handlers: Dictionary of control flow handlers
        error_strategy: Error handling strategy

    Returns:
        List[ActionResult]: Results of executed actions
    """
    if not isinstance(actions, list):
        raise TypeError("Actions must be list.")

    block_results = []
    current_action_index = 0
    action_list_copy = list(actions)  # Operate on a copy

    while current_action_index < len(action_list_copy):
        # Check stop flag before every action attempt
        check_stop_event(runner.stop_event)

        action = action_list_copy[current_action_index]
        step_num = current_action_index + 1
        action_display = f"{action.name} ({action.action_type}, {log_prefix}Step {step_num})"

        result = None
        try:
            # Detect action type
            action_type = action.action_type.lower()

            # Handle control flow actions
            if action_type == "conditional":
                result = control_flow_handlers["conditional"].handle(
                    action, context, workflow_name, f"{log_prefix}Cond {step_num}: "
                )
            elif action_type == "loop":
                result = control_flow_handlers["loop"].handle(
                    action, context, workflow_name, f"{log_prefix}Loop {step_num}: "
                )
            elif action_type == "error_handling":
                result = control_flow_handlers["error_handling"].handle(
                    action, context, workflow_name, f"{log_prefix}ErrH {step_num}: "
                )
            elif action_type == "template":
                # Handle template expansion
                expanded_actions = control_flow_handlers["template"].expand_template(action, context)
                action_list_copy = (
                    action_list_copy[:current_action_index] +
                    expanded_actions +
                    action_list_copy[current_action_index+1:]
                )
                logger.debug(
                    f"Replaced template with {len(expanded_actions)} actions. "
                    f"New total: {len(action_list_copy)}"
                )
                continue  # Restart loop for first expanded action
            else:
                # Execute regular action
                result = action_executor.execute(action, context)

        except ActionError as e:
            logger.error(f"ActionError during execution of {action_display}: {e}")
            # Let the error strategy decide what to do
            if not error_strategy.should_continue_after_error(e):
                raise
            # If we continue, create a failure result
            result = ActionResult.failure(str(e))

        except WorkflowError as e:
            # Workflow errors (like stop requests) should always propagate
            raise

        except Exception as e:
            # Catch unexpected errors
            logger.exception(f"Unexpected error processing {action_display}")
            error = ActionError(
                f"Unexpected error processing {action_display}: {e}",
                action_name=action.name,
                action_type=action.action_type,
                cause=e
            )
            # Let the error strategy decide what to do
            if not error_strategy.should_continue_after_error(error):
                raise error
            # If we continue, create a failure result
            result = ActionResult.failure(str(error))

        # Process result
        if result is None:
            raise WorkflowError(f"Execution returned None for {action_display}", workflow_name)

        block_results.append(result)  # Append result regardless of success for logging

        # Handle failure based on error strategy
        if not result.is_success() and not error_strategy.should_continue_after_failure(result):
            logger.error(f"Action '{action_display}' failed. Stopping block.")
            raise ActionError(
                result.message or f"Action '{action.name}' failed.",
                action_name=action.name,
                action_type=action.action_type
            )

        current_action_index += 1  # Move to next action

    return block_results
