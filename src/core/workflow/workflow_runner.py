"""Workflow Runner module for AutoQliq.

This module provides the WorkflowRunner class for executing workflow actions.
"""

import logging
import time
from typing import List, Dict, Any, Optional, Set
from src.core.interfaces import IWebDriver, IWorkflow, IAction, ICredentialRepository
from src.core.action_result import ActionResult
from src.core.exceptions import WorkflowError, ActionError, ValidationError, WebDriverError

logger = logging.getLogger(__name__)


class WorkflowRunner:
    """
    Executes a sequence of actions defined in a Workflow using the provided IWebDriver.
    Stops on first failure and wraps unexpected exceptions in WorkflowError.
    
    Attributes:
        driver (IWebDriver): The web driver instance to use for browser operations.
        credential_repo (Optional[ICredentialRepository]): Optional repository for credentials.
        context (Dict[str, Any]): Context data shared between actions during execution.
    """
    
    def __init__(
        self, 
        driver: IWebDriver, 
        credential_repo: Optional[ICredentialRepository] = None,
        initial_context: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a WorkflowRunner.
        
        Args:
            driver: WebDriver instance for browser control.
            credential_repo: Optional repository for retrieving credentials.
            initial_context: Optional initial context data for the workflow.
        """
        self.driver = driver
        self.credential_repo = credential_repo
        self.context = initial_context or {}
        self.logger = logging.getLogger(__name__)
        self.executed_action_ids: Set[str] = set()  # Track executed action IDs
        
        self.logger.info("WorkflowRunner initialized with driver type: %s", type(driver).__name__)

    def run(self, workflow: IWorkflow) -> List[ActionResult]:
        """
        Run all actions in the workflow sequentially.

        Args:
            workflow: The workflow entity containing actions.

        Returns:
            A list of ActionResult for each executed action.

        Raises:
            WorkflowError: If an action fails or an unexpected error occurs.
        """
        # Reset execution context and tracking
        self.executed_action_ids.clear()
        self.context["workflow_name"] = workflow.name
        self.context["workflow_start_time"] = time.time()
        
        results: List[ActionResult] = []
        total = len(workflow.actions)
        self.logger.info(f"Starting workflow '{workflow.name}' with {total} actions.")
        
        try:
            # Validate the entire workflow before execution
            if hasattr(workflow, 'validate'):
                workflow.validate()
            
            for idx, action in enumerate(workflow.actions, start=1):
                action_id = f"{action.name}_{id(action)}"
                self.executed_action_ids.add(action_id)
                self.context["current_action_index"] = idx - 1
                self.context["current_action_name"] = action.name
                
                try:
                    self.logger.info(f"Executing action {idx}/{total}: '{action.name}' ({action.action_type}).")
                    
                    # Validate action before execution
                    if hasattr(action, 'validate'):
                        action.validate()
                    
                    # Execute the action with context
                    result = action.execute(self.driver, self.credential_repo, self.context)
                    results.append(result)
                    
                    # Update execution context with result data if successful
                    if result.is_success() and result.data:
                        for key, value in result.data.items():
                            self.context[f"result_{action.name}_{key}"] = value
                    
                    # If action failed, raise a WorkflowError to stop execution
                    if not result.is_success():
                        self.logger.error(f"Action '{action.name}' failed: {result.message}")
                        raise WorkflowError(
                            f"Action failed during workflow execution: {result.message}",
                            workflow_name=workflow.name,
                            action_name=action.name,
                            cause=result.cause  # Pass along the original exception if available
                        )
                        
                except ValidationError as e:
                    self.logger.error(f"Validation error in action '{action.name}': {e}")
                    raise WorkflowError(
                        f"Validation error in action: {e}",
                        workflow_name=workflow.name,
                        action_name=action.name,
                        cause=e
                    ) from e
                    
                except ActionError as e:
                    self.logger.error(f"Action error in '{action.name}': {e}")
                    raise WorkflowError(
                        f"Action error: {e}",
                        workflow_name=workflow.name,
                        action_name=action.name,
                        cause=e
                    ) from e
                    
                except WebDriverError as e:
                    self.logger.error(f"WebDriver error during '{action.name}': {e}")
                    raise WorkflowError(
                        f"WebDriver error: {e}",
                        workflow_name=workflow.name,
                        action_name=action.name,
                        cause=e
                    ) from e
                    
                except WorkflowError:
                    # Don't wrap WorkflowErrors again - propagate them directly
                    raise
                    
                except Exception as e:
                    self.logger.error(
                        f"Unexpected error in workflow '{workflow.name}', action '{action.name}': {e}",
                        exc_info=True
                    )
                    raise WorkflowError(
                        f"Unexpected error during workflow execution: {e}",
                        workflow_name=workflow.name,
                        action_name=action.name,
                        cause=e
                    ) from e
                    
            # Record successful completion
            self.context["workflow_end_time"] = time.time()
            self.context["workflow_execution_time"] = self.context["workflow_end_time"] - self.context["workflow_start_time"]
            self.logger.info(
                f"Workflow '{workflow.name}' completed successfully in {self.context['workflow_execution_time']:.2f} seconds."
            )
            
        except WorkflowError as e:
            # Record failure time
            self.context["workflow_end_time"] = time.time()
            self.context["workflow_execution_time"] = self.context["workflow_end_time"] - self.context["workflow_start_time"]
            self.context["workflow_failed"] = True
            self.context["workflow_error"] = str(e)
            
            self.logger.error(
                f"Workflow '{workflow.name}' failed after {self.context['workflow_execution_time']:.2f} seconds: {e}"
            )
            raise
            
        return results

    def _execute_actions(
        self, 
        actions: List[IAction], 
        context: Dict[str, Any], 
        workflow_name: str, 
        log_prefix: str = ""
    ) -> List[ActionResult]:
        """
        Helper to execute a list of actions sequentially with context and prefix logging.
        
        Args:
            actions: List of actions to execute.
            context: Context data for the actions.
            workflow_name: Name of the parent workflow for error reporting.
            log_prefix: Prefix for log messages to identify nested action execution.
            
        Returns:
            List of ActionResult objects from each action.
            
        Raises:
            ActionError: If any nested action fails.
        """
        results: List[ActionResult] = []
        total = len(actions)
        nested_context = context.copy()  # Create a copy to avoid modifying the parent context
        
        try:
            for idx, action in enumerate(actions, start=1):
                action_id = f"{action.name}_{id(action)}"
                if action_id in self.executed_action_ids:
                    self.logger.warning(
                        f"{log_prefix}Action '{action.name}' appears to have been executed previously. "
                        "This might indicate a circular reference."
                    )
                
                self.executed_action_ids.add(action_id)
                nested_context["current_nested_action_index"] = idx - 1
                nested_context["current_nested_action_name"] = action.name
                
                self.logger.info(f"{log_prefix}Executing nested action {idx}/{total}: '{action.name}' ({action.action_type}).")
                
                # Validate action before execution
                if hasattr(action, 'validate'):
                    try:
                        action.validate()
                    except ValidationError as e:
                        self.logger.error(f"{log_prefix}Validation failed for action '{action.name}': {e}")
                        raise ActionError(
                            f"Nested action validation failed: {e}", 
                            workflow_name=workflow_name, 
                            action_name=action.name,
                            cause=e
                        ) from e
                
                # Execute the action        
                try:
                    result = action.execute(self.driver, self.credential_repo, nested_context)
                    results.append(result)
                    
                    # Update nested context with result data
                    if result.is_success() and result.data:
                        for key, value in result.data.items():
                            nested_context[f"result_{action.name}_{key}"] = value
                    
                    # If action failed, raise ActionError
                    if not result.is_success():
                        self.logger.error(f"{log_prefix}Nested action '{action.name}' failed: {result.message}")
                        raise ActionError(
                            f"Nested action failed: {result.message}",
                            workflow_name=workflow_name,
                            action_name=action.name,
                            cause=result.cause  # Pass along the original exception if available
                        )
                        
                except (ValidationError, ActionError, WebDriverError) as e:
                    self.logger.error(f"{log_prefix}Error executing nested action '{action.name}': {e}")
                    raise ActionError(
                        f"Nested action error: {e}", 
                        workflow_name=workflow_name, 
                        action_name=action.name,
                        cause=e
                    ) from e
                    
                except Exception as e:
                    self.logger.error(
                        f"{log_prefix}Unexpected error in nested action '{action.name}': {e}",
                        exc_info=True
                    )
                    raise ActionError(
                        f"Unexpected error in nested action: {e}", 
                        workflow_name=workflow_name, 
                        action_name=action.name,
                        cause=e
                    ) from e
                
                self.logger.debug(f"{log_prefix}Nested action '{action.name}' completed successfully.")
                
        except ActionError:
            # Don't wrap ActionErrors again - propagate them directly
            raise
            
        return results
    
    def reset_context(self) -> None:
        """Reset the execution context to its initial state."""
        self.context = {}
        self.executed_action_ids.clear()
        self.logger.debug("Workflow execution context has been reset.")
