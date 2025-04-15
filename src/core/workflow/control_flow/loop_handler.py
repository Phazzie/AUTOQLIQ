################################################################################
"""Loop handler implementation.

This module implements the handler for loop actions.
"""
################################################################################

import logging
from typing import Dict, Any, List, Optional, Callable, Type

from src.core.interfaces import IAction
from src.core.action_result import ActionResult
from src.core.exceptions import ActionError, WorkflowError
from src.core.actions.loop_action import LoopAction
from src.core.workflow.control_flow.base import ControlFlowHandlerBase
from src.core.workflow.control_flow.interfaces import ILoopActionHandler
from src.core.workflow.control_flow.loop_handlers import (
    CountLoopHandler,
    ForEachLoopHandler,
    WhileLoopHandler,
    BaseLoopHandler
)

logger = logging.getLogger(__name__)


class LoopHandler(ControlFlowHandlerBase, ILoopActionHandler):
    """Handler for LoopAction execution."""

    def __init__(self, *args, **kwargs):
        """Initialize the loop handler."""
        super().__init__(*args, **kwargs)
        # Create handlers for each loop type
        self.count_handler = CountLoopHandler(*args, **kwargs)
        self.foreach_handler = ForEachLoopHandler(*args, **kwargs)
        self.while_handler = WhileLoopHandler(*args, **kwargs)

        # Map loop types to their handlers
        self.loop_handlers = {
            "count": self.count_handler,
            "for_each": self.foreach_handler,
            "while": self.while_handler
        }

    def set_execute_actions_func(self, func: Callable) -> None:
        """Set the execute_actions_func for this handler and all sub-handlers.

        Args:
            func: The function to execute actions
        """
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
        # Validate action type
        self._validate_action_type(action)

        try:
            # Check if there are actions to execute
            if not action.loop_actions:
                return ActionResult.success("Loop has no actions to execute.")

            # Get the appropriate handler and execute the loop
            iterations_executed = self._execute_loop(action, context, workflow_name, log_prefix)

            # Return success result
            return self._create_success_result(iterations_executed)

        except ActionError:
            # Let the runner's error handling strategy deal with this
            raise
        except Exception as e:
            # Wrap other exceptions in ActionError
            raise self._create_action_error(action, e)

    def _validate_action_type(self, action: IAction) -> None:
        """Validate that the action is a LoopAction.

        Args:
            action: The action to validate

        Raises:
            WorkflowError: If action is not a LoopAction
        """
        if not isinstance(action, LoopAction):
            raise WorkflowError(f"LoopHandler received non-LoopAction: {type(action).__name__}")

    def _execute_loop(
        self, action: LoopAction, context: Dict[str, Any],
        workflow_name: str, log_prefix: str
    ) -> int:
        """Execute the loop using the appropriate handler.

        Args:
            action: The LoopAction to handle
            context: The execution context
            workflow_name: Name of the workflow being executed
            log_prefix: Prefix for log messages

        Returns:
            int: Number of iterations executed

        Raises:
            ActionError: If an error occurs during handling or if the loop type is unsupported
        """
        # Get the appropriate handler
        handler = self._get_loop_handler(action)

        # Execute the loop
        return handler.handle_loop(action, context, workflow_name, log_prefix)

    def _get_loop_handler(self, action: LoopAction) -> BaseLoopHandler:
        """Get the appropriate handler for the loop type.

        Args:
            action: The LoopAction to handle

        Returns:
            BaseLoopHandler: The appropriate handler

        Raises:
            ActionError: If the loop type is unsupported
        """
        if action.loop_type not in self.loop_handlers:
            raise ActionError(
                f"Unsupported loop_type '{action.loop_type}'",
                action_name=action.name
            )

        return self.loop_handlers[action.loop_type]

    def _create_success_result(self, iterations_executed: int) -> ActionResult:
        """Create a success result for the loop execution.

        Args:
            iterations_executed: Number of iterations executed

        Returns:
            ActionResult: A success result
        """
        return ActionResult.success(
            f"Loop completed successfully ({iterations_executed} iterations)"
        )

    def _create_action_error(self, action: LoopAction, error: Exception) -> ActionError:
        """Create an ActionError from an exception.

        Args:
            action: The action that caused the error
            error: The exception that caused the error

        Returns:
            ActionError: An ActionError wrapping the exception
        """
        return ActionError(
            f"Error in loop execution: {error}",
            action_name=action.name,
            action_type=action.action_type,
            cause=error
        )

    def get_loop_items(self, loop_type: str, loop_source: Any, context: Dict[str, Any]) -> List[Any]:
        """Get the items to loop over.

        Args:
            loop_type: The type of loop
            loop_source: The source of loop items
            context: The execution context

        Returns:
            List[Any]: The items to loop over
        """
        # Get the appropriate handler
        handler = self.loop_handlers.get(loop_type)
        if not handler:
            raise ActionError(f"Unsupported loop_type '{loop_type}'")

        # Delegate to the specific handler
        if loop_type == "count":
            # For count loops, create a list of integers
            try:
                count = int(loop_source)
                return list(range(count))
            except (ValueError, TypeError) as e:
                raise ActionError(f"Invalid count value: {loop_source}") from e

        elif loop_type == "for_each":
            # For for_each loops, get the items from the source
            if isinstance(loop_source, list):
                return loop_source
            elif isinstance(loop_source, str) and loop_source in context:
                items = context.get(loop_source)
                if isinstance(items, list):
                    return items
                else:
                    raise ActionError(f"Loop source '{loop_source}' is not a list")
            else:
                raise ActionError(f"Invalid for_each source: {loop_source}")

        elif loop_type == "while":
            # For while loops, we don't pre-compute the items
            # Just return an empty list as a placeholder
            return []

        # Should never get here due to the check above
        raise ActionError(f"Unsupported loop_type '{loop_type}'")
