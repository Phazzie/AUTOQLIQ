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
from src.core.workflow.control_flow.utils import evaluate_action_results, create_error_context

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
                catch_context = self._create_catch_context(context, try_error)

                # Execute catch block
                catch_results = self.execute_actions(
                    action.catch_actions, catch_context, workflow_name, f"{log_prefix}Catch: "
                )

                # Check if catch block succeeded
                return self._evaluate_catch_results(catch_results, try_error, log_prefix)

            except Exception as catch_error:
                logger.error(f"{log_prefix}'catch' block failed: {catch_error}", exc_info=True)

                # Raise new error indicating catch failure
                raise ActionError(
                    f"'catch' block failed after 'try' error ({try_error}): {catch_error}",
                    action_name=action.name,
                    cause=catch_error
                ) from catch_error

    def _create_catch_context(self, context: Dict[str, Any], try_error: Exception) -> Dict[str, Any]:
        """
        Create a context for the catch block with error information.

        Args:
            context: The original execution context
            try_error: The exception that occurred in the try block

        Returns:
            Dict[str, Any]: The context for the catch block
        """
        # Use the common utility function to create error context
        # Add both general error info and try_block specific error info
        catch_context = create_error_context(context, try_error)
        catch_context.update(create_error_context(context, try_error, prefix="try_block_"))
        return catch_context

    def _evaluate_catch_results(self, catch_results: List[ActionResult], try_error: Exception, log_prefix: str) -> ActionResult:
        """
        Evaluate the results of the catch block.

        Args:
            catch_results: The results of the catch block actions
            try_error: The exception that occurred in the try block
            log_prefix: Prefix for log messages

        Returns:
            ActionResult: The result of evaluating the catch block
        """
        # Use the common utility function to evaluate action results
        result = evaluate_action_results(
            results=catch_results,
            branch_name="'catch' block",
            log_prefix=log_prefix,
            success_message_template="Error handled by catch block: {error}",
            failure_message_template="Catch block had failures after try error: {error}"
        )

        # Replace {error} placeholder with actual error message
        result.message = result.message.format(error=str(try_error))
        return result

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
            error_context = self._create_error_context(context, error)

            # Execute error handling actions
            error_results = self.execute_actions(
                error_actions, error_context, workflow_name, f"{log_prefix}ErrorHandler: "
            )

            # Check if error handling succeeded
            return self._evaluate_error_results(error_results, error, log_prefix)

        except Exception as handler_error:
            logger.error(f"{log_prefix}Error handling failed: {handler_error}", exc_info=True)

            # Raise new error indicating error handling failure
            raise ActionError(
                f"Error handling failed after original error ({error}): {handler_error}",
                cause=handler_error
            ) from handler_error

    def _create_error_context(self, context: Dict[str, Any], error: Exception) -> Dict[str, Any]:
        """
        Create a context for error handling actions with error information.

        Args:
            context: The original execution context
            error: The exception that occurred

        Returns:
            Dict[str, Any]: The context for error handling actions
        """
        # Use the common utility function to create error context
        return create_error_context(context, error)

    def _evaluate_error_results(self, error_results: List[ActionResult], error: Exception, log_prefix: str) -> ActionResult:
        """
        Evaluate the results of the error handling actions.

        Args:
            error_results: The results of the error handling actions
            error: The exception that occurred
            log_prefix: Prefix for log messages

        Returns:
            ActionResult: The result of evaluating the error handling actions
        """
        # Use the common utility function to evaluate action results
        result = evaluate_action_results(
            results=error_results,
            branch_name="Error handling",
            log_prefix=log_prefix,
            success_message_template="Error handled successfully: {error}",
            failure_message_template="Error handling had failures: {error}"
        )

        # Replace {error} placeholder with actual error message
        result.message = result.message.format(error=str(error))
        return result
