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
            # Determine action type and handle accordingly
            action_type = action.action_type.lower()
            
            # Handle control flow actions
            if action_type == "conditional":
                handler = control_flow_handlers.get("conditional")
                result = handler.handle(action, context, workflow_name, f"{log_prefix}Cond {step_num}: ")
            elif action_type == "loop":
                handler = control_flow_handlers.get("loop")
                result = handler.handle(action, context, workflow_name, f"{log_prefix}Loop {step_num}: ")
            elif action_type == "errorhandling":
                handler = control_flow_handlers.get("error_handling")
                result = handler.handle(action, context, workflow_name, f"{log_prefix}ErrH {step_num}: ")
            elif action_type == "template":
                handler = control_flow_handlers.get("template")
                expanded_actions = handler.expand_template(action, context)
                action_list_copy = (
                    action_list_copy[:current_action_index] + 
                    expanded_actions + 
                    action_list_copy[current_action_index+1:]
                )
                logger.debug(f"Replaced template with {len(expanded_actions)} actions. New total: {len(action_list_copy)}")
                continue  # Restart loop for first expanded action
            else:
                # Execute regular action
                result = action_executor.execute_action(action, context)

        except ActionError as e:
            # Handle action error according to strategy
            result = error_strategy.handle_action_error(e, action, action_display)
        except WorkflowError as e:
            # Always propagate workflow errors (e.g., stop requests)
            raise e
        except Exception as e:
            # Handle unexpected errors
            logger.exception(f"Unexpected error processing {action_display}")
            result = error_strategy.handle_action_error(e, action, action_display)

        # Process result
        if result is None:
            raise WorkflowError(f"Execution returned None for {action_display}", workflow_name)

        block_results.append(result)  # Append result regardless of success for logging
        
        # Handle action failure according to strategy
        if not result.is_success():
            error_strategy.handle_action_failure(result, action, action_display)

        current_action_index += 1  # Move to next action

    return block_results
