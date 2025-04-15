"""Error handling handler implementation.

This module implements the handler for error handling actions.
"""

import logging
from typing import Dict, Any, List, Optional

from src.core.interfaces import IAction
from src.core.action_result import ActionResult
from src.core.exceptions import ActionError, WorkflowError
from src.core.actions.error_handling_action import ErrorHandlingAction
from src.core.workflow.control_flow.base import ControlFlowHandlerBase
from src.core.workflow.control_flow.interfaces import IErrorHandlingActionHandler

logger = logging.getLogger(__name__)


class ErrorHandlingHandler(ControlFlowHandlerBase, IErrorHandlingActionHandler):
    """Handler for ErrorHandlingAction (Try/Catch) execution."""

    def handle(self, action: IAction, context: Dict[str, Any],
              workflow_name: str, log_prefix: str) -> ActionResult:
        """
        Handle an ErrorHandlingAction by executing its try block and catch block if needed.

        Args:
            action: The ErrorHandlingAction to handle
            context: The execution context
            workflow_name: Name of the workflow being executed
            log_prefix: Prefix for log messages

        Returns:
            ActionResult: The result of handling the action

        Raises:
            ActionError: If an error occurs during handling
            WorkflowError: If action is not an ErrorHandlingAction
        """
        if not isinstance(action, ErrorHandlingAction):
            raise WorkflowError(f"ErrorHandlingHandler received non-ErrorHandlingAction: {type(action).__name__}")

        logger.info(f"{log_prefix}Entering 'try' block.")
        original_error: Optional[Exception] = None

        try:
            # Execute try block
            self.execute_actions(action.try_actions, context, workflow_name, f"{log_prefix}Try: ")
            logger.info(f"{log_prefix}'try' block succeeded.")
            return ActionResult.success("Try block succeeded.")

        except Exception as try_error:
            original_error = try_error
            logger.warning(f"{log_prefix}'try' block failed: {try_error}", exc_info=False)

            if not action.catch_actions:
                logger.info(f"{log_prefix}No 'catch' block defined, re-raising error.")
                raise

            logger.info(f"{log_prefix}Entering 'catch' block.")

            try:
                # Add error information to context for catch block
                catch_context = context.copy()
                catch_context.update({
                    'error': str(try_error),
                    'error_type': type(try_error).__name__,
                    'try_block_error_message': str(try_error),
                    'try_block_error_type': type(try_error).__name__
                })

                # Execute catch block
                catch_results = self.execute_actions(
                    action.catch_actions, catch_context, workflow_name, f"{log_prefix}Catch: "
                )

                # Check if catch block succeeded
                all_success = all(result.is_success() for result in catch_results)
                if all_success:
                    logger.info(f"{log_prefix}'catch' block succeeded, error handled.")
                    return ActionResult.success(
                        f"Error handled by catch block: {str(try_error)}"
                    )
                else:
                    # If we got here with failures in catch block, we must be using CONTINUE_ON_ERROR
                    logger.warning(f"{log_prefix}'catch' block had failures.")
                    return ActionResult.failure(
                        f"Catch block had failures after try error: {str(try_error)}"
                    )

            except Exception as catch_error:
                logger.error(f"{log_prefix}'catch' block failed: {catch_error}", exc_info=True)

                # Raise new error indicating catch failure
                raise ActionError(
                    f"'catch' block failed after 'try' error ({try_error}): {catch_error}",
                    action_name=action.name,
                    cause=catch_error
                ) from catch_error

    def handle_error(
        self,
        error: Exception,
        context: Dict[str, Any],
        error_actions: List[IAction],
        workflow_name: str,
        log_prefix: str
    ) -> ActionResult:
        """
        Handle an error.

        Args:
            error: The exception that was raised
            context: The execution context
            error_actions: The actions to execute when an error occurs
            workflow_name: Name of the workflow
            log_prefix: Prefix for log messages

        Returns:
            ActionResult: The result of handling the error
        """
        if not error_actions:
            logger.info(f"{log_prefix}No error handling actions defined, re-raising error.")
            raise ActionError(
                f"Error occurred and no error handling actions defined: {error}",
                cause=error
            ) from error

        logger.info(f"{log_prefix}Handling error with {len(error_actions)} actions.")

        try:
            # Add error information to context for error handling actions
            error_context = context.copy()
            error_context.update({
                'error': str(error),
                'error_type': type(error).__name__,
                'error_message': str(error),
                'error_type_name': type(error).__name__
            })

            # Execute error handling actions
            error_results = self.execute_actions(
                error_actions, error_context, workflow_name, f"{log_prefix}ErrorHandler: "
            )

            # Check if error handling succeeded
            all_success = all(result.is_success() for result in error_results)
            if all_success:
                logger.info(f"{log_prefix}Error handling succeeded.")
                return ActionResult.success(
                    f"Error handled successfully: {str(error)}"
                )
            else:
                # If we got here with failures, we must be using CONTINUE_ON_ERROR
                logger.warning(f"{log_prefix}Error handling had failures.")
                return ActionResult.failure(
                    f"Error handling had failures: {str(error)}"
                )

        except Exception as handler_error:
            logger.error(f"{log_prefix}Error handling failed: {handler_error}", exc_info=True)

            # Raise new error indicating error handling failure
            raise ActionError(
                f"Error handling failed after original error ({error}): {handler_error}",
                cause=handler_error
            ) from handler_error
