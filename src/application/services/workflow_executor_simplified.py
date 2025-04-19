"""Simplified Workflow Executor for AutoQliq.

This module provides a streamlined WorkflowExecutor class that focuses on:
1. Proper resource management
2. Clear error handling
3. Simplified execution flow
4. Consistent logging

Following YAGNI principles, this implementation removes unnecessary complexity
while maintaining core functionality.
"""

import logging
import time
from typing import Dict, Any, Optional, Callable, List
import threading

from src.core.interfaces import IWebDriver, IWorkflowRepository, ICredentialRepository
from src.core.interfaces import IAction
from src.core.exceptions import WorkflowError, WebDriverError, CredentialError, ValidationError
from src.infrastructure.webdrivers.base import BrowserType
from src.core.workflow.runner_simplified import WorkflowRunner

logger = logging.getLogger(__name__)


class WorkflowExecutor:
    """
    Executes workflows by orchestrating the loading of actions, creating the driver,
    running the workflow, and cleaning up resources.
    
    This simplified implementation focuses on proper resource management,
    clear error handling, and a simplified execution flow.
    """
    
    def __init__(
        self,
        workflow_repo: IWorkflowRepository,
        credential_repo: ICredentialRepository,
        webdriver_service,  # IWebDriverService
        reporting_service = None  # Optional IReportingService
    ):
        """
        Initialize the WorkflowExecutor.
        
        Args:
            workflow_repo: Repository for workflows.
            credential_repo: Repository for credentials.
            webdriver_service: Service for creating and managing web drivers.
            reporting_service: Optional service for reporting execution results.
        """
        self.workflow_repository = workflow_repo
        self.credential_repository = credential_repo
        self.webdriver_service = webdriver_service
        self.reporting_service = reporting_service
        
        logger.info("WorkflowExecutor initialized.")
    
    def execute(
        self,
        name: str,
        credential_name: Optional[str] = None,
        browser_type: BrowserType = BrowserType.CHROME,
        log_callback: Optional[Callable[[str], None]] = None,
        stop_event: Optional[threading.Event] = None
    ) -> Dict[str, Any]:
        """
        Execute a workflow.
        
        Args:
            name: Name of the workflow to execute.
            credential_name: Optional name of the credential to use.
            browser_type: Type of browser to use.
            log_callback: Optional callback for logging.
            stop_event: Optional event to signal a stop request.
            
        Returns:
            Execution log dictionary.
            
        Raises:
            WorkflowError: If the workflow cannot be loaded or executed.
            WebDriverError: If the web driver cannot be created.
            CredentialError: If the credential cannot be loaded.
        """
        logger.info(f"EXECUTOR: Starting workflow '{name}'")
        driver: Optional[IWebDriver] = None
        execution_log: Optional[Dict[str, Any]] = None
        start_time = time.time()
        
        try:
            # Load the workflow actions
            actions = self._load_actions(name)
            
            # Create the web driver
            driver = self._create_driver(browser_type)
            
            # Create the workflow runner
            runner = WorkflowRunner(
                driver=driver,
                credential_repo=self.credential_repository,
                workflow_repo=self.workflow_repository,
                stop_event=stop_event
            )
            
            # Execute the workflow
            execution_log = runner.run(actions, workflow_name=name)
            
            # Log the result
            final_status = execution_log.get("final_status", "UNKNOWN")
            logger.info(f"EXECUTOR: Workflow '{name}' finished. Status: {final_status}")
            
            # Report the result if a reporting service is available
            if self.reporting_service:
                try:
                    self.reporting_service.report_workflow_execution(execution_log)
                except Exception as e:
                    logger.error(f"EXECUTOR: Error reporting workflow execution: {e}")
            
            return execution_log
            
        except (WorkflowError, WebDriverError, CredentialError, ValidationError) as e:
            # Handle known errors
            logger.error(f"EXECUTOR: Error executing workflow '{name}': {e}")
            
            # Create a minimal execution log for the error
            if not execution_log:
                execution_log = {
                    "workflow_name": name,
                    "start_time_iso": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(start_time)),
                    "end_time_iso": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime()),
                    "duration_seconds": time.time() - start_time,
                    "final_status": "FAILED",
                    "error_message": str(e),
                    "action_results": [],
                    "summary": {
                        "total_actions": 0,
                        "success_count": 0,
                        "failure_count": 0
                    }
                }
            
            # Re-raise the error
            raise
            
        except Exception as e:
            # Handle unexpected errors
            logger.exception(f"EXECUTOR: Unexpected error executing workflow '{name}': {e}")
            
            # Create a minimal execution log for the error
            if not execution_log:
                execution_log = {
                    "workflow_name": name,
                    "start_time_iso": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(start_time)),
                    "end_time_iso": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime()),
                    "duration_seconds": time.time() - start_time,
                    "final_status": "FAILED",
                    "error_message": f"Unexpected error: {e}",
                    "action_results": [],
                    "summary": {
                        "total_actions": 0,
                        "success_count": 0,
                        "failure_count": 0
                    }
                }
            
            # Re-raise as a WorkflowError
            raise WorkflowError(f"Unexpected error executing workflow '{name}': {e}", cause=e) from e
            
        finally:
            # Clean up resources
            if driver:
                try:
                    logger.info("EXECUTOR: Disposing of web driver")
                    self.webdriver_service.dispose_web_driver(driver)
                except Exception as e:
                    logger.error(f"EXECUTOR: Error disposing of web driver: {e}")
            
            # Return the execution log if available
            if execution_log:
                return execution_log
    
    def _load_actions(self, workflow_name: str) -> List[IAction]:
        """
        Load the actions for a workflow.
        
        Args:
            workflow_name: Name of the workflow to load.
            
        Returns:
            List of actions.
            
        Raises:
            WorkflowError: If the workflow cannot be loaded.
        """
        try:
            logger.info(f"EXECUTOR: Loading workflow '{workflow_name}'")
            workflow_data = self.workflow_repository.get_workflow(workflow_name)
            
            if not workflow_data:
                raise WorkflowError(f"Workflow '{workflow_name}' not found.")
            
            actions = workflow_data.get("actions", [])
            
            if not actions:
                logger.warning(f"EXECUTOR: Workflow '{workflow_name}' has no actions.")
            else:
                logger.info(f"EXECUTOR: Loaded {len(actions)} actions for workflow '{workflow_name}'")
            
            return actions
            
        except Exception as e:
            logger.error(f"EXECUTOR: Error loading workflow '{workflow_name}': {e}")
            raise WorkflowError(f"Error loading workflow '{workflow_name}': {e}", cause=e) from e
    
    def _create_driver(self, browser_type: BrowserType) -> IWebDriver:
        """
        Create a web driver.
        
        Args:
            browser_type: Type of browser to use.
            
        Returns:
            Web driver instance.
            
        Raises:
            WebDriverError: If the web driver cannot be created.
        """
        try:
            logger.info(f"EXECUTOR: Creating web driver for browser type '{browser_type.value}'")
            driver = self.webdriver_service.create_web_driver(browser_type_str=browser_type.value)
            logger.info(f"EXECUTOR: Web driver created for browser type '{browser_type.value}'")
            return driver
            
        except Exception as e:
            logger.error(f"EXECUTOR: Error creating web driver: {e}")
            raise WebDriverError(f"Error creating web driver: {e}", cause=e) from e
