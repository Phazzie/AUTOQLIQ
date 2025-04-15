"""Interfaces for action execution components.

This module provides interfaces for the action execution components to enable
dependency inversion and improve SOLID compliance.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

from src.core.interfaces import IAction
from src.core.action_result import ActionResult


class IActionExecutor(ABC):
    """Interface for action executors."""

    @abstractmethod
    def execute_action(self, action: IAction, context: Dict[str, Any]) -> ActionResult:
        """
        Execute a single action.

        Args:
            action: The action to execute
            context: The execution context

        Returns:
            ActionResult: The result of the action execution
        """
        pass


class IActionTypeDetector(ABC):
    """Interface for action type detectors."""

    @abstractmethod
    def detect_action_type(self, action: IAction) -> Optional[str]:
        """
        Detect the type of an action.

        Args:
            action: The action to detect the type of

        Returns:
            Optional[str]: The type of the action, or None if it's a regular action
        """
        pass


class IActionFailureHandler(ABC):
    """Interface for action failure handlers."""

    @abstractmethod
    def handle_action_failure(
        self,
        action_result: ActionResult,
        action: IAction,
        action_display_name: str,
        error_strategy: str,
        context: Dict[str, Any]
    ) -> None:
        """
        Handle an action failure.

        Args:
            action_result: The result of the failed action
            action: The action that failed
            action_display_name: Display name of the action
            error_strategy: Error handling strategy
            context: Execution context

        Raises:
            ActionError: If the error strategy is STOP_ON_ERROR
        """
        pass


class IActionErrorHandler(ABC):
    """Interface for action error handlers."""

    @abstractmethod
    def handle_action_error(
        self,
        error: Exception,
        action: IAction,
        action_display_name: str,
        error_strategy: str,
        context: Dict[str, Any]
    ) -> ActionResult:
        """
        Handle an error that occurred during action execution.

        Args:
            error: The exception that was raised
            action: The action that caused the error
            action_display_name: Display name of the action
            error_strategy: Error handling strategy
            context: Execution context

        Returns:
            ActionResult: A failure result with error information

        Raises:
            ActionError: If the error strategy is STOP_ON_ERROR
        """
        pass


class IActionDisplayFormatter(ABC):
    """Interface for action display formatters."""

    @abstractmethod
    def format_action_display_name(
        self,
        action: IAction,
        log_prefix: str,
        step_number: int
    ) -> str:
        """
        Format an action's display name for logging.

        Args:
            action: The action to format the display name for
            log_prefix: Prefix for log messages
            step_number: Step number in the workflow

        Returns:
            str: Formatted display name
        """
        pass


class IActionExecutionManager(ABC):
    """Interface for action execution managers."""

    @abstractmethod
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
        pass
