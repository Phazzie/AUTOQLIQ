"""Simplified Workflow Service for AutoQliq.

This module provides a streamlined WorkflowService class that focuses on:
1. Simplified interface for running workflows
2. Clear error handling
3. Proper resource management
4. Consistent logging

Following YAGNI principles, this implementation removes unnecessary complexity
while maintaining core functionality.
"""

import logging
import threading
from typing import Dict, Any, Optional, Callable, List

from src.core.interfaces import IWorkflowRepository, ICredentialRepository
from src.core.exceptions import WorkflowError, WebDriverError, CredentialError, ValidationError
from src.infrastructure.webdrivers.base import BrowserType
from src.infrastructure.common.error_handling import handle_exceptions
from src.infrastructure.common.logging_utils import log_method_call
from src.application.services.workflow_executor_simplified import WorkflowExecutor

logger = logging.getLogger(__name__)


class WorkflowService:
    """
    Service for managing and executing workflows.
    
    This simplified implementation focuses on providing a clean interface
    for running workflows and managing resources properly.
    """
    
    def __init__(
        self,
        workflow_repository: IWorkflowRepository,
        credential_repository: ICredentialRepository,
        webdriver_service,  # IWebDriverService
        reporting_service = None  # Optional IReportingService
    ):
        """
        Initialize the WorkflowService.
        
        Args:
            workflow_repository: Repository for workflows.
            credential_repository: Repository for credentials.
            webdriver_service: Service for creating and managing web drivers.
            reporting_service: Optional service for reporting execution results.
        """
        if workflow_repository is None:
            raise ValueError("Workflow repository cannot be None.")
        if credential_repository is None:
            raise ValueError("Credential repository cannot be None.")
        if webdriver_service is None:
            raise ValueError("WebDriver service cannot be None.")
            
        self.workflow_repository = workflow_repository
        self.credential_repository = credential_repository
        self.webdriver_service = webdriver_service
        self.reporting_service = reporting_service
        
        logger.info("WorkflowService initialized.")
    
    @log_method_call(logger)
    def get_workflow_list(self) -> List[str]:
        """
        Get a list of available workflow names.
        
        Returns:
            List of workflow names.
        """
        try:
            workflow_names = self.workflow_repository.get_all_workflow_names()
            logger.debug(f"Retrieved {len(workflow_names)} workflows.")
            return workflow_names
        except Exception as e:
            logger.error(f"Error retrieving workflow list: {e}")
            raise WorkflowError(f"Error retrieving workflow list: {e}", cause=e) from e
    
    @log_method_call(logger)
    def get_workflow(self, name: str) -> Dict[str, Any]:
        """
        Get a workflow by name.
        
        Args:
            name: Name of the workflow to get.
            
        Returns:
            Workflow data.
            
        Raises:
            WorkflowError: If the workflow cannot be found.
        """
        try:
            workflow_data = self.workflow_repository.get_workflow(name)
            if not workflow_data:
                raise WorkflowError(f"Workflow '{name}' not found.")
            return workflow_data
        except Exception as e:
            logger.error(f"Error retrieving workflow '{name}': {e}")
            raise WorkflowError(f"Error retrieving workflow '{name}': {e}", cause=e) from e
    
    @log_method_call(logger)
    @handle_exceptions(WorkflowError, "Error running workflow", reraise_types=(WorkflowError, WebDriverError, CredentialError))
    def run_workflow(
        self,
        name: str,
        credential_name: Optional[str] = None,
        browser_type: BrowserType = BrowserType.CHROME,
        log_callback: Optional[Callable[[str], None]] = None,
        stop_event: Optional[threading.Event] = None
    ) -> Dict[str, Any]:
        """
        Run a workflow.
        
        Args:
            name: Name of the workflow to run.
            credential_name: Optional name of the credential to use.
            browser_type: Type of browser to use.
            log_callback: Optional callback for logging.
            stop_event: Optional event to signal a stop request.
            
        Returns:
            Execution log dictionary.
            
        Raises:
            WorkflowError: If the workflow cannot be run.
            WebDriverError: If the web driver cannot be created.
            CredentialError: If the credential cannot be loaded.
        """
        logger.info(f"SERVICE: Running workflow '{name}'")
        
        try:
            # Create a workflow executor for this run
            executor = WorkflowExecutor(
                workflow_repo=self.workflow_repository,
                credential_repo=self.credential_repository,
                webdriver_service=self.webdriver_service,
                reporting_service=self.reporting_service
            )
            
            # Execute the workflow
            execution_log = executor.execute(
                name=name,
                credential_name=credential_name,
                browser_type=browser_type,
                log_callback=log_callback,
                stop_event=stop_event
            )
            
            # Log the result
            final_status = execution_log.get("final_status", "UNKNOWN")
            logger.info(f"SERVICE: Workflow '{name}' execution finished with status: {final_status}")
            
            return execution_log
            
        except (WorkflowError, WebDriverError, CredentialError, ValidationError) as e:
            # Handle known errors
            logger.error(f"SERVICE: Error running workflow '{name}': {e}")
            raise
            
        except Exception as e:
            # Handle unexpected errors
            logger.exception(f"SERVICE: Unexpected error running workflow '{name}': {e}")
            raise WorkflowError(f"Unexpected error running workflow '{name}': {e}", cause=e) from e
    
    @log_method_call(logger)
    def stop_workflow(self, stop_event: threading.Event) -> bool:
        """
        Request to stop a running workflow.
        
        Args:
            stop_event: Event to signal a stop request.
            
        Returns:
            True if the stop request was set, False otherwise.
        """
        if not stop_event:
            logger.warning("SERVICE: Stop workflow called with no stop event.")
            return False
            
        logger.info("SERVICE: Setting stop event to request workflow cancellation.")
        stop_event.set()
        return True
