"""Interfaces for control flow handlers.

This module provides interfaces for the control flow handlers to enable
dependency inversion and improve SOLID compliance.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

from src.core.interfaces import IAction
from src.core.action_result import ActionResult


class IControlFlowHandler(ABC):
    """Interface for control flow handlers."""

    @abstractmethod
    def handle(
        self,
        action: IAction,
        context: Dict[str, Any],
        workflow_name: str,
        log_prefix: str
    ) -> ActionResult:
        """
        Handle a control flow action.

        Args:
            action: The control flow action to handle
            context: The execution context
            workflow_name: Name of the workflow
            log_prefix: Prefix for log messages

        Returns:
            ActionResult: The result of handling the control flow action
        """
        pass


class IConditionalActionHandler(IControlFlowHandler):
    """Interface for conditional action handlers."""

    @abstractmethod
    def evaluate_condition(
        self,
        condition: str,
        context: Dict[str, Any]
    ) -> bool:
        """
        Evaluate a condition.

        Args:
            condition: The condition to evaluate
            context: The execution context

        Returns:
            bool: The result of evaluating the condition
        """
        pass


class ILoopActionHandler(IControlFlowHandler):
    """Interface for loop action handlers."""

    @abstractmethod
    def get_loop_items(
        self,
        loop_type: str,
        loop_source: Any,
        context: Dict[str, Any]
    ) -> List[Any]:
        """
        Get the items to loop over.

        Args:
            loop_type: The type of loop
            loop_source: The source of loop items
            context: The execution context

        Returns:
            List[Any]: The items to loop over
        """
        pass


class IErrorHandlingActionHandler(IControlFlowHandler):
    """Interface for error handling action handlers."""

    @abstractmethod
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
        pass


class ITemplateActionHandler(IControlFlowHandler):
    """Interface for template action handlers."""

    @abstractmethod
    def load_template(
        self,
        template_name: str,
        template_params: Dict[str, Any]
    ) -> List[IAction]:
        """
        Load a template.

        Args:
            template_name: The name of the template
            template_params: The parameters for the template

        Returns:
            List[IAction]: The actions from the template
        """
        pass
