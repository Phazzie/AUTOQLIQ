"""Refactored Workflow Runner module for AutoQliq.

Provides a modular WorkflowRunner class that delegates to specialized components.
"""

import logging
from typing import List, Dict, Any, Optional
import threading

# Core components
from src.core.interfaces import IWebDriver, IAction, ICredentialRepository, IWorkflowRepository
from src.core.action_result import ActionResult

# Import specialized components
from src.core.workflow.action_executor import ActionExecutor
from src.core.workflow.context.manager import WorkflowContextManager
from src.core.workflow.result_processing.processor import ResultProcessor
from src.core.workflow.control_flow.conditional_handler import ConditionalHandler
from src.core.workflow.control_flow.loop_handler import LoopHandler
from src.core.workflow.control_flow.error_handler import ErrorHandlingHandler
from src.core.workflow.control_flow.template.handler import TemplateHandler
from src.core.workflow.error_handling import create_error_handling_strategy

# Import execution modules
from src.core.workflow.runner_execution import execute_workflow
from src.core.workflow.action_execution import execute_actions

# For backward compatibility
from src.core.workflow.error_handling.strategy_enum import ErrorHandlingStrategy

logger = logging.getLogger(__name__)


class WorkflowRunner:
    """
    Executes a given sequence of actions using a web driver.

    This refactored version delegates to specialized components for different aspects
    of workflow execution, following the Single Responsibility Principle.

    Attributes:
        driver (IWebDriver): The web driver instance for browser interaction.
        credential_repo (Optional[ICredentialRepository]): Repository for credentials.
        workflow_repo (Optional[IWorkflowRepository]): Repository for workflows/templates.
        stop_event (Optional[threading.Event]): Event to signal graceful stop request.
        error_strategy: Strategy for handling errors during execution.
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
        if driver is None:
            raise ValueError("WebDriver instance cannot be None.")

        # Validate error_strategy
        if not isinstance(error_strategy, ErrorHandlingStrategy):
            raise ValueError(
                f"Invalid error strategy: {error_strategy}. "
                f"Must be an ErrorHandlingStrategy enum value."
            )

        # Store references
        self.driver = driver
        self.credential_repo = credential_repo
        self.workflow_repo = workflow_repo
        self.stop_event = stop_event
        self.error_strategy_enum = error_strategy  # Store original enum for backward compatibility

        # Initialize components
        self.action_executor = ActionExecutor(driver, credential_repo)
        self.context_manager = WorkflowContextManager()
        self.result_processor = ResultProcessor()

        # Initialize control flow handlers
        self.control_flow_handlers = {
            "conditional": ConditionalHandler(driver, credential_repo, workflow_repo),
            "loop": LoopHandler(driver, credential_repo, workflow_repo),
            "error_handling": ErrorHandlingHandler(driver, credential_repo, workflow_repo),
            "template": TemplateHandler(driver, credential_repo, workflow_repo)
        }

        # Set execute_actions_func for all handlers
        for handler in self.control_flow_handlers.values():
            handler.set_execute_actions_func(self._execute_actions)

        # Initialize error handling strategy
        strategy_type = (
            "stop" if error_strategy == ErrorHandlingStrategy.STOP_ON_ERROR else "continue"
        )
        self.error_strategy = create_error_handling_strategy(strategy_type)

        # Log initialization
        logger.info("WorkflowRunner initialized.")
        if credential_repo:
            logger.debug(f"Using credential repository: {type(credential_repo).__name__}")
        if workflow_repo:
            logger.debug(f"Using workflow repository: {type(workflow_repo).__name__}")
        if stop_event:
            logger.debug("Stop event provided for cancellation check.")
        logger.debug(f"Using error handling strategy: {error_strategy.name}")

    def run(
        self,
        actions: List[IAction],
        workflow_name: str = "Unnamed Workflow"
    ) -> Dict[str, Any]:
        """
        Execute actions sequentially, returning detailed log data.

        Args:
            actions: Sequence of actions.
            workflow_name: Name of the workflow.

        Returns:
            Execution log dictionary with the following keys:
            - workflow_name: Name of the workflow
            - start_time_iso: ISO-formatted start time
            - end_time_iso: ISO-formatted end time
            - duration_seconds: Execution duration in seconds
            - final_status: Final status (SUCCESS, FAILED, STOPPED, COMPLETED_WITH_ERRORS)
            - error_message: Error message if applicable
            - action_results: List of action results
            - summary: Summary of execution results
        """
        return execute_workflow(
            self, actions, workflow_name, self.context_manager, self.result_processor,
            self.error_strategy_enum, self.stop_event
        )

    def _execute_actions(self, actions: List[IAction], context: Dict[str, Any],
                        workflow_name: str, log_prefix: str = "") -> List[ActionResult]:
        """
        Execute a list of actions.

        Args:
            actions: List of actions to execute
            context: Execution context
            workflow_name: Name of the workflow
            log_prefix: Prefix for log messages

        Returns:
            List[ActionResult]: Results of executed actions
        """
        return execute_actions(
            self, actions, context, workflow_name, log_prefix,
            self.action_executor, self.control_flow_handlers, self.error_strategy
        )
