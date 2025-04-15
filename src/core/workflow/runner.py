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
from src.core.action_result import ActionResult
from src.core.exceptions import WorkflowError, ActionError, ValidationError, RepositoryError, SerializationError

from src.core.actions.conditional_action import ConditionalAction
from src.core.actions.loop_action import LoopAction
from src.core.actions.error_handling_action import ErrorHandlingAction
from src.core.actions.template_action import TemplateAction
from src.core.actions.factory import ActionFactory

logger = logging.getLogger(__name__)


class WorkflowRunner:
    def __init__(
        self,
        driver: IWebDriver,
        credential_repo: Optional[ICredentialRepository] = None,
        workflow_repo: Optional[IWorkflowRepository] = None,
        stop_event: Optional[threading.Event] = None
    ):
        if driver is None:
            raise ValueError("WebDriver instance cannot be None.")
        self.driver = driver
        self.credential_repo = credential_repo
        self.workflow_repo = workflow_repo
        self.stop_event = stop_event
        logger.info("WorkflowRunner initialized.")
        if credential_repo:
            logger.debug(f"Using credential repository: {type(credential_repo).__name__}")
        if workflow_repo:
            logger.debug(f"Using workflow repository: {type(workflow_repo).__name__}")
        if stop_event:
            logger.debug("Stop event provided for cancellation check.")

    def run_single_action(self, action: IAction, context: Dict[str, Any]) -> ActionResult:
        if self.stop_event and self.stop_event.is_set():
            logger.info(f"Stop requested before executing action '{action.name}'")
            raise WorkflowError("Workflow execution stopped by request.")

        action_display_name = f"{action.name} ({action.action_type})"
        logger.debug(f"Runner executing single action: {action_display_name}")
        try:
            action.validate()
            result = action.execute(self.driver, self.credential_repo, context)
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

    def _expand_template(self, template_action: TemplateAction, context: Dict[str, Any]) -> List[IAction]:
        template_name = template_action.template_name
        logger.info(f"Expanding template '{template_name}' within action '{template_action.name}'.")
        if not self.workflow_repo:
            raise ActionError("Workflow repository required for template expansion.", action_name=template_action.name)
        try:
            actions_data = self.workflow_repo.load_template(template_name)
            if not actions_data:
                return []
            expanded_actions = [ActionFactory.create_action(data) for data in actions_data]
            logger.info(f"Expanded template '{template_name}' into {len(expanded_actions)} actions.")
            return expanded_actions
        except (RepositoryError, ActionError, SerializationError, ValidationError, TypeError) as e:
            raise ActionError(f"Failed to load/expand template '{template_name}': {e}", action_name=template_action.name, cause=e) from e
        except Exception as e:
            raise ActionError(f"Unexpected error expanding template '{template_name}': {e}", action_name=template_action.name, cause=e) from e

    def _execute_actions(self, actions: List[IAction], context: Dict[str, Any], workflow_name: str, log_prefix: str = "") -> List[ActionResult]:
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
                    expanded_actions = self._expand_template(action, context)
                    action_list_copy = action_list_copy[:current_action_index] + expanded_actions + action_list_copy[current_action_index+1:]
                    logger.debug(f"Replaced template with {len(expanded_actions)} actions. New total: {len(action_list_copy)}")
                    continue

                elif isinstance(action, ConditionalAction):
                    result = self._execute_conditional(action, context, workflow_name, f"{log_prefix}Cond {step_num}: ")
                elif isinstance(action, LoopAction):
                    result = self._execute_loop(action, context, workflow_name, f"{log_prefix}Loop {step_num}: ")
                elif isinstance(action, ErrorHandlingAction):
                    result = self._execute_error_handler(action, context, workflow_name, f"{log_prefix}ErrH {step_num}: ")
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

    def _execute_conditional(self, action: ConditionalAction, context: Dict[str, Any], workflow_name: str, log_prefix: str) -> ActionResult:
        try:
            condition_met = action._evaluate_condition(self.driver, context)
            logger.info(f"{log_prefix}Condition '{action.condition_type}' evaluated to {condition_met}")
            branch_to_run = action.true_branch if condition_met else action.false_branch
            branch_name = "'true'" if condition_met else "'false'"
            if not branch_to_run:
                return ActionResult.success(f"Cond {condition_met}, {branch_name} empty.")

            logger.info(f"{log_prefix}Executing {branch_name} branch...")
            branch_results = self._execute_actions(branch_to_run, context, workflow_name, f"{log_prefix}{branch_name}: ")
            logger.info(f"{log_prefix}Successfully executed {branch_name} branch.")
            return ActionResult.success(f"Cond {condition_met}, {branch_name} executed ({len(branch_results)} actions).")
        except Exception as e:
            logger.error(f"{log_prefix}Conditional failed: {e}", exc_info=False)
            raise ActionError(f"Conditional failed: {e}", action_name=action.name, action_type=action.action_type, cause=e) from e

    def _execute_loop(self, action: LoopAction, context: Dict[str, Any], workflow_name: str, log_prefix: str) -> ActionResult:
        iterations_executed = 0
        try:
            if action.loop_type == "count":
                iterations_total = action.count or 0
                logger.info(f"{log_prefix}Starting 'count' loop for {iterations_total} iterations.")
                for i in range(iterations_total):
                    iteration_num = i + 1
                    iter_log_prefix = f"{log_prefix}Iter {iteration_num}: "
                    logger.info(f"{iter_log_prefix}Starting.")
                    iter_context = context.copy()
                    iter_context.update({'loop_index': i, 'loop_iteration': iteration_num, 'loop_total': iterations_total})
                    self._execute_actions(action.loop_actions, iter_context, workflow_name, iter_log_prefix)
                    iterations_executed = iteration_num
            elif action.loop_type == "for_each":
                if not action.list_variable_name:
                    raise ActionError("list_variable_name missing", action.name)
                target_list = context.get(action.list_variable_name)
                if not isinstance(target_list, list):
                    raise ActionError(f"Context var '{action.list_variable_name}' not list.", action.name)
                iterations_total = len(target_list)
                logger.info(f"{log_prefix}Starting 'for_each' over '{action.list_variable_name}' ({iterations_total} items).")
                for i, item in enumerate(target_list):
                    iteration_num = i + 1
                    iter_log_prefix = f"{log_prefix}Item {iteration_num}: "
                    logger.info(f"{iter_log_prefix}Starting.")
                    iter_context = context.copy()
                    iter_context.update({'loop_index': i, 'loop_iteration': iteration_num, 'loop_total': iterations_total, 'loop_item': item})
                    self._execute_actions(action.loop_actions, iter_context, workflow_name, iter_log_prefix)
                    iterations_executed = iteration_num
            elif action.loop_type == "while":
                logger.info(f"{log_prefix}Starting 'while' loop.")
                max_while = 1000
                i = 0
                while i < max_while:
                    iteration_num = i + 1
                    iter_log_prefix = f"{log_prefix}While Iter {iteration_num}: "
                    logger.debug(f"{iter_log_prefix}Evaluating condition...")
                    if self.stop_event and self.stop_event.is_set():
                        raise WorkflowError("Stop requested during while loop.")
                    condition_met = action._evaluate_while_condition(self.driver, context)
                    if not condition_met:
                        logger.info(f"{iter_log_prefix}Condition false. Exiting loop.")
                        break
                    logger.info(f"{iter_log_prefix}Condition true. Starting iteration.")
                    iter_context = context.copy()
                    iter_context.update({'loop_index': i, 'loop_iteration': iteration_num})
                    self._execute_actions(action.loop_actions, iter_context, workflow_name, iter_log_prefix)
                    iterations_executed = iteration_num
                    i += 1
                else:
                    raise ActionError(f"While loop exceeded max iterations ({max_while}).", action.name)
            else:
                raise ActionError(f"Unsupported loop_type '{action.loop_type}'", action.name)

            logger.info(f"{log_prefix}Loop completed {iterations_executed} iterations.")
            return ActionResult.success(f"Loop completed {iterations_executed} iterations.")
        except Exception as e:
            logger.error(f"{log_prefix}Loop failed: {e}", exc_info=False)
            raise ActionError(f"Loop failed: {e}", action_name=action.name, action_type=action.action_type, cause=e) from e

    def _execute_error_handler(self, action: ErrorHandlingAction, context: Dict[str, Any], workflow_name: str, log_prefix: str) -> ActionResult:
        logger.info(f"{log_prefix}Entering 'try' block.")
        original_error: Optional[Exception] = None
        try:
            self._execute_actions(action.try_actions, context, workflow_name, f"{log_prefix}Try: ")
            logger.info(f"{log_prefix}'try' block succeeded.")
            return ActionResult.success("Try block succeeded.")
        except Exception as try_error:
            original_error = try_error
            logger.warning(f"{log_prefix}'try' block failed: {try_error}", exc_info=False)
            if not action.catch_actions:
                logger.warning(f"{log_prefix}No 'catch' block. Error not handled.")
                raise
            else:
                logger.info(f"{log_prefix}Executing 'catch' block...")
                catch_context = context.copy()
                catch_context['try_block_error_message'] = str(try_error)
                catch_context['try_block_error_type'] = type(try_error).__name__
                try:
                    self._execute_actions(action.catch_actions, catch_context, workflow_name, f"{log_prefix}Catch: ")
                    logger.info(f"{log_prefix}'catch' block succeeded after handling error.")
                    return ActionResult.success(f"Error handled by 'catch': {str(try_error)[:100]}")
                except Exception as catch_error:
                    logger.error(f"{log_prefix}'catch' block failed: {catch_error}", exc_info=True)
                    raise ActionError(f"'catch' block failed after 'try' error ({try_error}): {catch_error}",
                                      action_name=action.name, cause=catch_error) from catch_error

    def run(self, actions: List[IAction], workflow_name: str = "Unnamed Workflow") -> Dict[str, Any]:
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
