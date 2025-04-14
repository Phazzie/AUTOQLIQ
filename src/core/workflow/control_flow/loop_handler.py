"""Loop handler implementation.

This module implements the handler for loop actions.
"""

import logging
from typing import Dict, Any, List

from src.core.interfaces import IAction
from src.core.action_result import ActionResult
from src.core.exceptions import ActionError, WorkflowError
from src.core.actions.loop_action import LoopAction
from src.core.workflow.control_flow.base import ControlFlowHandlerBase
from src.core.workflow.control_flow.loop_handlers import (
    CountLoopHandler,
    ForEachLoopHandler,
    WhileLoopHandler
)

logger = logging.getLogger(__name__)


class LoopHandler(ControlFlowHandlerBase):
    """Handler for LoopAction execution."""

    def __init__(self, *args, **kwargs):
        """Initialize the loop handler."""
        super().__init__(*args, **kwargs)
        # Create handlers for each loop type
        self.count_handler = CountLoopHandler(*args, **kwargs)
        self.foreach_handler = ForEachLoopHandler(*args, **kwargs)
        self.while_handler = WhileLoopHandler(*args, **kwargs)

    def set_execute_actions_func(self, func):
        """Set the execute_actions_func for this handler and all sub-handlers."""
        super().set_execute_actions_func(func)
        self.count_handler.set_execute_actions_func(func)
        self.foreach_handler.set_execute_actions_func(func)
        self.while_handler.set_execute_actions_func(func)

    def handle(self, action: IAction, context: Dict[str, Any],
              workflow_name: str, log_prefix: str) -> ActionResult:
        """
        Handle a LoopAction by executing its actions in a loop.

        Args:
            action: The LoopAction to handle
            context: The execution context
            workflow_name: Name of the workflow being executed
            log_prefix: Prefix for log messages

        Returns:
            ActionResult: The result of handling the action

        Raises:
            ActionError: If an error occurs during handling
            WorkflowError: If action is not a LoopAction
        """
        if not isinstance(action, LoopAction):
            raise WorkflowError(f"LoopHandler received non-LoopAction: {type(action).__name__}")

        try:
            if not action.loop_actions:
                return ActionResult.success("Loop has no actions to execute.")

            # Delegate to the appropriate handler based on loop type
            if action.loop_type == "count":
                iterations_executed = self.count_handler.handle_loop(
                    action, context, workflow_name, log_prefix
                )
            elif action.loop_type == "for_each":
                iterations_executed = self.foreach_handler.handle_loop(
                    action, context, workflow_name, log_prefix
                )
            elif action.loop_type == "while":
                iterations_executed = self.while_handler.handle_loop(
                    action, context, workflow_name, log_prefix
                )
            else:
                raise ActionError(
                    f"Unsupported loop_type '{action.loop_type}'",
                    action_name=action.name
                )

            return ActionResult.success(
                f"Loop completed successfully ({iterations_executed} iterations)"
            )

        except ActionError as e:
            # Let the runner's error handling strategy deal with this
            raise
        except Exception as e:
            # Wrap other exceptions in ActionError
            raise ActionError(
                f"Error in loop execution: {e}",
                action_name=action.name,
                action_type=action.action_type,
                cause=e
            ) from e


