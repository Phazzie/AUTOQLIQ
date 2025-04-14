"""Backward compatibility layer for WorkflowRunner.

This module provides backward compatibility for the refactored WorkflowRunner.
"""

import logging
from typing import Dict, Any, List, Optional
import threading

from src.core.interfaces import IWebDriver, IAction, ICredentialRepository, IWorkflowRepository
from src.core.action_result import ActionResult
from src.core.workflow.runner import ErrorHandlingStrategy
from src.core.workflow.runner_refactored import WorkflowRunner as RefactoredWorkflowRunner
from src.core.workflow.template_expander import expand_template

logger = logging.getLogger(__name__)


class WorkflowRunner(RefactoredWorkflowRunner):
    """
    Backward-compatible WorkflowRunner.

    This class extends the refactored WorkflowRunner to provide backward compatibility
    with the original WorkflowRunner interface.
    """

    def __init__(
        self,
        driver: IWebDriver,
        credential_repo: Optional[ICredentialRepository] = None,
        workflow_repo: Optional[IWorkflowRepository] = None,
        stop_event: Optional[threading.Event] = None,
        error_strategy: ErrorHandlingStrategy = ErrorHandlingStrategy.STOP_ON_ERROR
    ):
        """
        Initialize the WorkflowRunner.

        Args:
            driver: The web driver instance for browser interaction.
            credential_repo: Optional repository for credentials.
            workflow_repo: Optional repository for workflows/templates.
            stop_event: Optional event to signal graceful stop request.
            error_strategy: Strategy for handling errors during execution.
                STOP_ON_ERROR (default): Stop workflow execution on first error.
                CONTINUE_ON_ERROR: Continue workflow execution after errors.
        """
        super().__init__(driver, credential_repo, workflow_repo, stop_event, error_strategy)

    def run_single_action(self, action: IAction, context: Dict[str, Any]) -> ActionResult:
        """
        Execute a single action with error handling.

        Args:
            action: The action to execute
            context: The execution context

        Returns:
            ActionResult: The result of the action execution
        """
        return self.action_executor.execute_action(action, context)

    def _execute_conditional(self, action: IAction, context: Dict[str, Any],
                           workflow_name: str, log_prefix: str) -> ActionResult:
        """
        Execute a conditional action.

        Args:
            action: The conditional action to execute
            context: The execution context
            workflow_name: Name of the workflow
            log_prefix: Prefix for log messages

        Returns:
            ActionResult: The result of the action execution
        """
        return self.control_flow_handlers["conditional"].handle(
            action, context, workflow_name, log_prefix
        )

    def _execute_loop(self, action: IAction, context: Dict[str, Any],
                    workflow_name: str, log_prefix: str) -> ActionResult:
        """
        Execute a loop action.

        Args:
            action: The loop action to execute
            context: The execution context
            workflow_name: Name of the workflow
            log_prefix: Prefix for log messages

        Returns:
            ActionResult: The result of the action execution
        """
        return self.control_flow_handlers["loop"].handle(
            action, context, workflow_name, log_prefix
        )

    def _execute_error_handler(self, action: IAction, context: Dict[str, Any],
                             workflow_name: str, log_prefix: str) -> ActionResult:
        """
        Execute an error handling action.

        Args:
            action: The error handling action to execute
            context: The execution context
            workflow_name: Name of the workflow
            log_prefix: Prefix for log messages

        Returns:
            ActionResult: The result of the action execution
        """
        return self.control_flow_handlers["error_handling"].handle(
            action, context, workflow_name, log_prefix
        )

    def _expand_template(self, action: IAction, context: Dict[str, Any]) -> List[IAction]:
        """
        Expand a template action.

        Args:
            action: The template action to expand
            context: The execution context

        Returns:
            List[IAction]: The expanded actions
        """
        # Use the template expander to expand the template
        return expand_template(action, self.workflow_repo)
