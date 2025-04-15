"""Action execution manager implementation.

This module provides the ActionExecutionManager class for managing action execution.
"""

import logging
from typing import Dict, Any, List, Optional

from src.core.interfaces import IAction
from src.core.action_result import ActionResult
from src.core.exceptions import WorkflowError
from src.core.workflow.action_execution.interfaces import (
    IActionExecutionManager,
    IActionExecutor,
    IActionTypeDetector,
    IActionDisplayFormatter,
    IActionFailureHandler,
    IActionErrorHandler
)
from src.core.workflow.action_execution.action_type_detector import ActionTypeDetector
from src.core.workflow.action_execution.action_display_formatter import ActionDisplayFormatter
from src.core.workflow.action_execution.action_failure_handler import ActionFailureHandler
from src.core.workflow.action_execution.action_error_handler import ActionErrorHandler

logger = logging.getLogger(__name__)


class ActionExecutionManager(IActionExecutionManager):
    """
    Manages the execution of actions.

    Responsible for coordinating the execution of a list of actions.
    """

    def __init__(
        self,
        action_type_detector: Optional[IActionTypeDetector] = None,
        action_display_formatter: Optional[IActionDisplayFormatter] = None,
        action_failure_handler: Optional[IActionFailureHandler] = None,
        action_error_handler: Optional[IActionErrorHandler] = None,
        stop_event: Optional[object] = None
    ):
        """
        Initialize the action execution manager.

        Args:
            action_type_detector: Optional action type detector
            action_display_formatter: Optional action display formatter
            action_failure_handler: Optional action failure handler
            action_error_handler: Optional action error handler
            stop_event: Optional event to signal graceful stop request
        """
        self.action_type_detector = action_type_detector or ActionTypeDetector()
        self.action_display_formatter = action_display_formatter or ActionDisplayFormatter()
        self.action_failure_handler = action_failure_handler or ActionFailureHandler()
        self.action_error_handler = action_error_handler or ActionErrorHandler()
        self.stop_event = stop_event

    def execute_actions(
        self,
        action_list: List[IAction],
        execution_context: Dict[str, Any],
        workflow_name: str,
        log_prefix: str,
        action_executor: IActionExecutor,
        control_flow_handlers: Dict[str, Any],
        error_strategy: str
    ) -> List[ActionResult]:
        """
        Execute a list of actions.

        Args:
            action_list: List of actions to execute
            execution_context: Execution context
            workflow_name: Name of the workflow
            log_prefix: Prefix for log messages
            action_executor: Action executor
            control_flow_handlers: Control flow handlers
            error_strategy: Error handling strategy

        Returns:
            List[ActionResult]: Results of the executed actions
        """
        # Initialize the execution results
        execution_results = []
        has_execution_failures = False

        # Log the start of execution
        logger.info(
            f"{log_prefix}Executing {len(action_list)} actions for workflow '{workflow_name}'"
        )

        # Execute each action in the list
        for action_index, current_action in enumerate(action_list):
            # Check if execution should be stopped
            self._check_stop_event()

            # Process the current action
            step_number = action_index + 1
            action_display_name = self.action_display_formatter.format_action_display_name(
                current_action, log_prefix, step_number
            )

            # Execute the action
            action_result = self._execute_single_action(
                current_action,
                execution_context,
                workflow_name,
                log_prefix,
                step_number,
                action_executor,
                control_flow_handlers,
                error_strategy,
                action_display_name
            )

            # Add the result to the execution results
            execution_results.append(action_result)

            # Handle failure if needed
            if not action_result.is_success():
                has_execution_failures = True
                self.action_failure_handler.handle_action_failure(
                    action_result,
                    current_action,
                    action_display_name,
                    error_strategy,
                    execution_context
                )

        # Log the completion of execution
        self._log_execution_completion(
            log_prefix, len(action_list), has_execution_failures
        )

        return execution_results

    def _execute_single_action(
        self,
        action: IAction,
        context: Dict[str, Any],
        workflow_name: str,
        log_prefix: str,
        step_num: int,
        action_executor: IActionExecutor,
        control_flow_handlers: Dict[str, Any],
        error_strategy: str,
        action_display: str
    ) -> ActionResult:
        """
        Execute a single action.

        Args:
            action: The action to execute
            context: The execution context
            workflow_name: Name of the workflow
            log_prefix: Prefix for log messages
            step_num: Step number in the workflow
            action_executor: Action executor
            control_flow_handlers: Control flow handlers
            error_strategy: Error handling strategy
            action_display: Display name of the action

        Returns:
            ActionResult: Result of the action execution
        """
        try:
            # Determine the appropriate handler
            action_type = self.action_type_detector.detect_action_type(action)

            if action_type:
                # Use the appropriate control flow handler
                handler_prefix = self._get_handler_prefix(action_type, step_num, log_prefix)
                result = control_flow_handlers[action_type].handle(
                    action, context, workflow_name, handler_prefix
                )
            else:
                # Execute regular action
                result = action_executor.execute_action(action, context)

            return result

        except Exception as e:
            # Handle error using the error handler
            return self.action_error_handler.handle_action_error(
                e, action, action_display, error_strategy, context
            )

    def _check_stop_event(self) -> None:
        """
        Check if execution should be stopped.

        Raises:
            WorkflowError: If the stop event is set
        """
        if self.stop_event and hasattr(self.stop_event, "is_set") and self.stop_event.is_set():
            logger.info("Stop requested during action execution.")
            raise WorkflowError("Workflow execution stopped by request.")

    def _get_handler_prefix(self, action_type: str, step_num: int, log_prefix: str) -> str:
        """
        Get the log prefix for a control flow handler.

        Args:
            action_type: Type of the action
            step_num: Step number in the workflow
            log_prefix: Prefix for log messages

        Returns:
            str: Handler log prefix
        """
        return f"{log_prefix}Step {step_num} ({action_type}): "

    def _log_execution_completion(
        self,
        log_prefix: str,
        action_count: int,
        has_failures: bool
    ) -> None:
        """
        Log the completion of action execution.

        Args:
            log_prefix: Prefix for log messages
            action_count: Number of actions executed
            has_failures: Whether there were any failures
        """
        if has_failures:
            logger.warning(
                f"{log_prefix}Completed execution of {action_count} actions with failures."
            )
        else:
            logger.info(
                f"{log_prefix}Successfully completed execution of {action_count} actions."
            )
