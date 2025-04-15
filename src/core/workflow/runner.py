"""Workflow Runner module for AutoQliq.

Provides the WorkflowRunner class responsible for executing a sequence of actions,
managing context, and handling control flow actions like Loop, Conditional,
and ErrorHandling, plus Template expansion.
"""

import logging
import time
from typing import List, Optional, Dict, Any
import threading
from datetime import datetime

from src.core.interfaces import IWebDriver, IAction, ICredentialRepository, IWorkflowRepository
from src.core.action_result import ActionResult, ActionStatus
from src.core.exceptions import WorkflowError, ActionError, AutoQliqError, ValidationError, RepositoryError, SerializationError

from src.core.actions.conditional_action import ConditionalAction
from src.core.actions.loop_action import LoopAction
from src.core.actions.error_handling_action import ErrorHandlingAction
from src.core.actions.template_action import TemplateAction
from src.core.actions.factory import ActionFactory

from src.core.workflow.action_executor import ActionExecutor
from src.core.workflow.context_manager import ContextManager
from src.core.workflow.result_processing.processor import ResultProcessor
from src.core.workflow.control_flow.conditional_handler import ConditionalHandler
from src.core.workflow.control_flow.loop_handler import LoopHandler
from src.core.workflow.control_flow.error_handler import ErrorHandlingHandler
from src.core.workflow.control_flow.template.handler import TemplateHandler
from src.core.workflow.error_handling import create_error_handling_strategy

logger = logging.getLogger(__name__)


class WorkflowRunner:
    """
    Executes a given sequence of actions using a web driver.

    Handles iterating through actions, passing context (driver, repo),
    managing execution context (e.g., loop variables), handling control flow actions,
    and expanding TemplateActions. Now returns a detailed execution log dictionary.

    Attributes:
        driver (IWebDriver): The web driver instance for browser interaction.
        credential_repo (Optional[ICredentialRepository]): Repository for credentials.
        workflow_repo (Optional[IWorkflowRepository]): Repository for workflows/templates (needed for template expansion).
        stop_event (Optional[threading.Event]): Event to signal graceful stop request.
    """

    def __init__(
        self,
        driver: IWebDriver,
        credential_repo: Optional[ICredentialRepository] = None,
        workflow_repo: Optional[IWorkflowRepository] = None,
        stop_event: Optional[threading.Event] = None,
        error_strategy: str = "STOP_ON_ERROR"
    ):
        """Initialize the WorkflowRunner."""
        if driver is None:
            raise ValueError("WebDriver instance cannot be None.")

        self.driver = driver
        self.credential_repo = credential_repo
        self.workflow_repo = workflow_repo
        self.stop_event = stop_event

        self.action_executor = ActionExecutor(driver, credential_repo)
        self.context_manager = ContextManager()
        self.result_processor = ResultProcessor()

        self.control_flow_handlers = {
            "conditional": ConditionalHandler(driver, credential_repo, workflow_repo),
            "loop": LoopHandler(driver, credential_repo, workflow_repo),
            "error_handling": ErrorHandlingHandler(driver, credential_repo, workflow_repo),
            "template": TemplateHandler(driver, credential_repo, workflow_repo)
        }

        for handler in self.control_flow_handlers.values():
            handler.set_execute_actions_func(self._execute_actions)

        self.error_strategy = create_error_handling_strategy(error_strategy)

        logger.info("WorkflowRunner initialized.")
        if credential_repo:
            logger.debug(f"Using credential repository: {type(credential_repo).__name__}")
        if workflow_repo:
            logger.debug(f"Using workflow repository: {type(workflow_repo).__name__}")
        if stop_event:
            logger.debug("Stop event provided for cancellation check.")
        logger.debug(f"Using error handling strategy: {error_strategy}")

    def run_single_action(self, action: IAction, context: Dict[str, Any]) -> ActionResult:
        """Executes a single action within a given context, handling its exceptions."""
        if self.stop_event and self.stop_event.is_set():
            logger.info(f"Stop requested before executing action '{action.name}'")
            raise WorkflowError("Workflow execution stopped by request.")

        action_display_name = f"{action.name} ({action.action_type})"
        logger.debug(f"Runner executing single action: {action_display_name}")
        try:
            action.validate()
            result = self.action_executor.execute_action(action, context)
            if not isinstance(result, ActionResult):
                logger.error(f"Action '{action_display_name}' did not return ActionResult (got {type(result).__name__}).")
                return ActionResult.failure(f"Action '{action.name}' implementation error: Invalid return type.")
            if not result.is_success():
                logger.warning(f"Action '{action_display_name}' returned failure: {result.message}")
            else:
                logger.debug(f"Action '{action_display_name}' returned success.")
            return result
        except ValidationError as e:
            logger.error(f"Validation failed for action '{action_display_name}': {e}")
            return ActionResult.failure(f"Action validation failed: {e}")
        except ActionError as e:
            logger.error(f"ActionError during execution of action '{action_display_name}': {e}")
            return ActionResult.failure(f"Action execution error: {e}")
        except Exception as e:
            logger.exception(f"Unexpected exception during execution of action '{action_display_name}'")
            wrapped_error = ActionError(f"Unexpected exception: {e}", action_name=action.name, action_type=action.action_type, cause=e)
            return ActionResult.failure(str(wrapped_error))

    def _execute_actions(self, actions: List[IAction], context: Dict[str, Any], workflow_name: str, log_prefix: str = "") -> List[ActionResult]:
        """Internal helper to execute actions, handling control flow, context, templates, stop events."""
        block_results: List[ActionResult] = []
        current_action_index = 0
        action_list_copy = list(actions)

        while current_action_index < len(action_list_copy):
            if self.stop_event and self.stop_event.is_set():
                logger.info(f"{log_prefix}Stop requested before Step {current_action_index + 1}.")
                raise WorkflowError("Workflow execution stopped by request.")

            action = action_list_copy[current_action_index]
            step_num = current_action_index + 1
            action_display = f"{action.name} ({action.action_type}, {log_prefix}Step {step_num})"

            result: Optional[ActionResult] = None
            try:
                if isinstance(action, TemplateAction):
                    logger.debug(f"Runner expanding template action: {action_display}")
                    expanded_actions = self.control_flow_handlers["template"].expand_template(action, context)
                    action_list_copy = action_list_copy[:current_action_index] + expanded_actions + action_list_copy[current_action_index+1:]
                    logger.debug(f"Replaced template with {len(expanded_actions)} actions. New total: {len(action_list_copy)}")
                    continue

                elif isinstance(action, ConditionalAction):
                    result = self.control_flow_handlers["conditional"].execute(action, context, workflow_name, f"{log_prefix}Cond {step_num}: ")
                elif isinstance(action, LoopAction):
                    result = self.control_flow_handlers["loop"].execute(action, context, workflow_name, f"{log_prefix}Loop {step_num}: ")
                elif isinstance(action, ErrorHandlingAction):
                    result = self.control_flow_handlers["error_handling"].execute(action, context, workflow_name, f"{log_prefix}ErrH {step_num}: ")
                elif isinstance(action, IAction):
                    result = self.run_single_action(action, context)
                else:
                    raise WorkflowError(f"Invalid item at {log_prefix}Step {step_num}: {type(action).__name__}.")

            except ActionError as e:
                logger.error(f"ActionError during execution of {action_display}: {e}")
                raise ActionError(f"Failure during {action_display}: {e}", action_name=action.name, action_type=action.action_type, cause=e) from e
            except WorkflowError as e:
                raise e
            except Exception as e:
                logger.exception(f"Unexpected error processing {action_display}")
                raise ActionError(f"Unexpected error processing {action_display}: {e}", action.name, action.action_type, cause=e) from e

            if result is None:
                raise WorkflowError(f"Execution returned None for {action_display}", workflow_name)

            block_results.append(result)
            if not result.is_success():
                logger.error(f"Action '{action_display}' failed. Stopping block.")
                raise ActionError(result.message or f"Action '{action.name}' failed.", action_name=action.name, action_type=action.action_type)

            current_action_index += 1

        return block_results

    def run(self, actions: List[IAction], workflow_name: str = "Unnamed Workflow") -> Dict[str, Any]:
        """
        Execute actions sequentially, returning detailed log data.

        Args:
            actions: Sequence of actions.
            workflow_name: Name of the workflow.

        Returns: Execution log dictionary.
        """
        if not isinstance(actions, list):
            raise TypeError("Actions must be list.")
        if not workflow_name:
            workflow_name = "Unnamed Workflow"

        logger.info(f"RUNNER: Starting workflow '{workflow_name}' with {len(actions)} top-level actions.")
        execution_context: Dict[str, Any] = {}
        all_action_results: List[ActionResult] = []
        start_time = time.time()
        final_status = "UNKNOWN"
        error_message: Optional[str] = None

        try:
            if self.stop_event and self.stop_event.is_set():
                raise WorkflowError("Workflow execution stopped by request before start.")

            all_action_results = self._execute_actions(actions, execution_context, workflow_name, log_prefix="")
            final_status = "SUCCESS"
            logger.info(f"RUNNER: Workflow '{workflow_name}' completed successfully.")

        except ActionError as e:
            final_status = "FAILED"
            error_message = str(e)
            logger.error(f"RUNNER: Workflow '{workflow_name}' failed. Last error in action '{e.action_name}': {e}", exc_info=False)
        except WorkflowError as e:
            if "stopped by request" in str(e).lower():
                final_status = "STOPPED"
                error_message = "Execution stopped by user request."
            else:
                final_status = "FAILED"
                error_message = str(e)
            logger.error(f"RUNNER: Workflow '{workflow_name}' stopped or failed: {error_message}")
        except Exception as e:
            final_status = "FAILED"
            error_message = f"Unexpected runner error: {e}"
            logger.exception(f"RUNNER: Unexpected error during workflow '{workflow_name}' execution.")
        finally:
            end_time = time.time()
            duration = end_time - start_time
            logger.info(f"RUNNER: Workflow '{workflow_name}' finished. Status: {final_status}, Duration: {duration:.2f}s")
            execution_log = {
                "workflow_name": workflow_name,
                "start_time_iso": datetime.fromtimestamp(start_time).isoformat(),
                "end_time_iso": datetime.fromtimestamp(end_time).isoformat(),
                "duration_seconds": round(duration, 2),
                "final_status": final_status,
                "error_message": error_message,
                "action_results": [{"status": res.status.value, "message": res.message} for res in all_action_results]
            }
            return execution_log
