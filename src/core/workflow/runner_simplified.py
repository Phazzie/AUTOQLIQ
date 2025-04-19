"""Simplified Workflow Runner module for AutoQliq.

This module provides a streamlined WorkflowRunner class that focuses on:
1. Sequential execution of actions
2. Robust error handling
3. Proper resource management
4. Clear logging
5. Graceful cancellation

Following YAGNI principles, this implementation removes unnecessary complexity
while maintaining core functionality.
"""

import logging
import time
from typing import List, Dict, Any, Optional
import threading
from datetime import datetime

from src.core.interfaces import IAction, IWebDriver, ICredentialRepository, IWorkflowRepository
from src.core.action_result import ActionResult
from src.core.exceptions import WorkflowError, ActionError, ValidationError

# Import specific action types for type checking
from src.core.actions.conditional_action import ConditionalAction

logger = logging.getLogger(__name__)


class WorkflowRunner:
    """
    Executes a sequence of actions using a web driver.
    
    This simplified implementation focuses on sequential execution,
    robust error handling, and proper resource management.
    
    Attributes:
        driver (IWebDriver): The web driver instance for browser interaction.
        credential_repo (Optional[ICredentialRepository]): Repository for credentials.
        workflow_repo (Optional[IWorkflowRepository]): Repository for workflows.
        stop_event (Optional[threading.Event]): Event to signal graceful stop request.
    """
    
    def __init__(
        self,
        driver: IWebDriver,
        credential_repo: Optional[ICredentialRepository] = None,
        workflow_repo: Optional[IWorkflowRepository] = None,
        stop_event: Optional[threading.Event] = None
    ):
        """
        Initialize the WorkflowRunner.
        
        Args:
            driver: The web driver instance for browser interaction.
            credential_repo: Optional repository for credentials.
            workflow_repo: Optional repository for workflows.
            stop_event: Optional event to signal graceful stop request.
        """
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
    
    def run(self, actions: List[IAction], workflow_name: str = "Unnamed Workflow") -> Dict[str, Any]:
        """
        Execute actions sequentially, returning detailed log data.
        
        Args:
            actions: Sequence of actions to execute.
            workflow_name: Name of the workflow.
            
        Returns:
            Execution log dictionary with details about the execution.
        """
        if not isinstance(actions, list):
            raise TypeError("Actions must be a list.")
        if not workflow_name:
            workflow_name = "Unnamed Workflow"
            
        # Initialize tracking variables
        start_time = time.time()
        execution_context: Dict[str, Any] = {}
        all_action_results: List[ActionResult] = []
        final_status = "UNKNOWN"
        error_message: Optional[str] = None
        
        logger.info(f"RUNNER: Starting workflow '{workflow_name}' with {len(actions)} actions.")
        
        try:
            # Check stop event before starting
            self._check_stop_event()
            
            # Execute actions
            all_action_results = self._execute_actions(actions, execution_context, workflow_name)
            
            final_status = "SUCCESS"
            logger.info(f"RUNNER: Workflow '{workflow_name}' completed successfully.")
            
        except ActionError as e:
            final_status = "FAILED"
            error_message = str(e)
            logger.error(f"RUNNER: Workflow '{workflow_name}' failed. Error in action '{e.action_name}': {e}")
            
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
            # Calculate execution time
            end_time = time.time()
            duration_seconds = end_time - start_time
            
            # Create execution log
            execution_log = self._create_execution_log(
                workflow_name=workflow_name,
                action_results=all_action_results,
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration_seconds,
                final_status=final_status,
                error_message=error_message
            )
            
            return execution_log
    
    def _execute_actions(
        self,
        actions: List[IAction],
        context: Dict[str, Any],
        workflow_name: str,
        log_prefix: str = ""
    ) -> List[ActionResult]:
        """
        Execute a list of actions sequentially.
        
        Args:
            actions: List of actions to execute.
            context: Execution context dictionary.
            workflow_name: Name of the workflow.
            log_prefix: Prefix for log messages.
            
        Returns:
            List of ActionResult objects.
        """
        results: List[ActionResult] = []
        
        for index, action in enumerate(actions):
            # Check stop event before each action
            self._check_stop_event()
            
            step_num = index + 1
            action_display = f"{action.name} ({action.action_type})"
            logger.debug(f"{log_prefix}Step {step_num}: Executing {action_display}")
            
            try:
                # Validate action before execution
                action.validate()
                
                # Handle different action types
                if isinstance(action, ConditionalAction):
                    result = self._execute_conditional(action, context, workflow_name, f"{log_prefix}Cond {step_num}: ")
                else:
                    # Execute regular action
                    result = self._execute_single_action(action, context)
                
                # Store the result
                results.append(result)
                
                # Log the result
                if result.is_success():
                    logger.debug(f"{log_prefix}Step {step_num}: {action_display} succeeded: {result.message}")
                else:
                    logger.warning(f"{log_prefix}Step {step_num}: {action_display} failed: {result.message}")
                    # Raise an error to stop execution on failure
                    raise ActionError(
                        f"Action '{action.name}' failed: {result.message}",
                        action_name=action.name,
                        cause=result.error
                    )
                
            except ValidationError as e:
                logger.error(f"{log_prefix}Step {step_num}: {action_display} validation failed: {e}")
                # Create a failure result
                result = ActionResult.failure(
                    f"Validation failed: {e}",
                    action_name=action.name,
                    action_type=action.action_type,
                    error=e
                )
                results.append(result)
                # Raise an error to stop execution
                raise ActionError(
                    f"Action '{action.name}' validation failed: {e}",
                    action_name=action.name,
                    cause=e
                )
                
            except Exception as e:
                logger.error(f"{log_prefix}Step {step_num}: {action_display} execution error: {e}")
                # Create a failure result
                result = ActionResult.failure(
                    f"Execution error: {e}",
                    action_name=action.name,
                    action_type=action.action_type,
                    error=e
                )
                results.append(result)
                # Raise an error to stop execution
                raise ActionError(
                    f"Action '{action.name}' execution error: {e}",
                    action_name=action.name,
                    cause=e
                )
        
        return results
    
    def _execute_single_action(self, action: IAction, context: Dict[str, Any]) -> ActionResult:
        """
        Execute a single action.
        
        Args:
            action: The action to execute.
            context: Execution context dictionary.
            
        Returns:
            ActionResult object.
        """
        try:
            # Execute the action
            result = action.execute(self.driver, self.credential_repo, context)
            
            # Validate the result
            if not isinstance(result, ActionResult):
                logger.error(f"Action '{action.name}' did not return ActionResult (got {type(result).__name__}).")
                return ActionResult.failure(
                    f"Action '{action.name}' implementation error: Invalid return type.",
                    action_name=action.name,
                    action_type=action.action_type
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing action '{action.name}': {e}")
            return ActionResult.failure(
                f"Execution error: {e}",
                action_name=action.name,
                action_type=action.action_type,
                error=e
            )
    
    def _execute_conditional(
        self,
        action: ConditionalAction,
        context: Dict[str, Any],
        workflow_name: str,
        log_prefix: str
    ) -> ActionResult:
        """
        Execute a conditional action.
        
        Args:
            action: The conditional action to execute.
            context: Execution context dictionary.
            workflow_name: Name of the workflow.
            log_prefix: Prefix for log messages.
            
        Returns:
            ActionResult object.
        """
        try:
            # Evaluate the condition
            condition_result = action.evaluate_condition(self.driver, context)
            
            # Log the condition result
            if condition_result:
                logger.info(f"{log_prefix}Condition evaluated to TRUE, executing true branch.")
                # Execute the true branch
                if action.true_branch:
                    branch_results = self._execute_actions(action.true_branch, context, workflow_name, f"{log_prefix}True: ")
                    return ActionResult.success(
                        f"Condition TRUE, executed {len(branch_results)} actions in true branch.",
                        action_name=action.name,
                        action_type=action.action_type,
                        details={"branch_results": branch_results}
                    )
                else:
                    logger.info(f"{log_prefix}True branch is empty, nothing to execute.")
                    return ActionResult.success(
                        "Condition TRUE, but true branch is empty.",
                        action_name=action.name,
                        action_type=action.action_type
                    )
            else:
                logger.info(f"{log_prefix}Condition evaluated to FALSE, executing false branch.")
                # Execute the false branch
                if action.false_branch:
                    branch_results = self._execute_actions(action.false_branch, context, workflow_name, f"{log_prefix}False: ")
                    return ActionResult.success(
                        f"Condition FALSE, executed {len(branch_results)} actions in false branch.",
                        action_name=action.name,
                        action_type=action.action_type,
                        details={"branch_results": branch_results}
                    )
                else:
                    logger.info(f"{log_prefix}False branch is empty, nothing to execute.")
                    return ActionResult.success(
                        "Condition FALSE, but false branch is empty.",
                        action_name=action.name,
                        action_type=action.action_type
                    )
                    
        except Exception as e:
            logger.error(f"{log_prefix}Error executing conditional action '{action.name}': {e}")
            return ActionResult.failure(
                f"Conditional execution error: {e}",
                action_name=action.name,
                action_type=action.action_type,
                error=e
            )
    
    def _check_stop_event(self) -> None:
        """
        Check if a stop has been requested.
        
        Raises:
            WorkflowError: If a stop has been requested.
        """
        if self.stop_event and self.stop_event.is_set():
            logger.info("Stop requested during workflow execution.")
            raise WorkflowError("Workflow execution stopped by request.")
    
    def _create_execution_log(
        self,
        workflow_name: str,
        action_results: List[ActionResult],
        start_time: float,
        end_time: float,
        duration_seconds: float,
        final_status: str,
        error_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create an execution log dictionary.
        
        Args:
            workflow_name: Name of the workflow.
            action_results: List of ActionResult objects.
            start_time: Start time in seconds since epoch.
            end_time: End time in seconds since epoch.
            duration_seconds: Duration in seconds.
            final_status: Final status of the workflow.
            error_message: Optional error message.
            
        Returns:
            Execution log dictionary.
        """
        # Convert timestamps to ISO format
        start_time_iso = datetime.fromtimestamp(start_time).isoformat()
        end_time_iso = datetime.fromtimestamp(end_time).isoformat()
        
        # Count successes and failures
        success_count = sum(1 for result in action_results if result.is_success())
        failure_count = len(action_results) - success_count
        
        # Create the execution log
        execution_log = {
            "workflow_name": workflow_name,
            "start_time_iso": start_time_iso,
            "end_time_iso": end_time_iso,
            "duration_seconds": duration_seconds,
            "final_status": final_status,
            "action_results": [result.to_dict() for result in action_results],
            "summary": {
                "total_actions": len(action_results),
                "success_count": success_count,
                "failure_count": failure_count
            }
        }
        
        # Add error message if present
        if error_message:
            execution_log["error_message"] = error_message
        
        return execution_log
