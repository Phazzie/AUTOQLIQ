"""Handles the orchestration of executing a specific workflow run."""

import logging
import time
import threading
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime

# Core dependencies
from src.core.interfaces import IAction, ICredentialRepository, IWorkflowRepository, IWebDriver
from src.core.interfaces.service import IWebDriverService, IReportingService
# Use the refactored runner explicitly if desired, otherwise the main runner path
from src.core.workflow.runner_refactored import WorkflowRunner
from src.core.exceptions import (
    WorkflowError, CredentialError, WebDriverError, ValidationError,
    ActionError, RepositoryError, SerializationError, ConfigError, AutoQliqError
)
from src.infrastructure.webdrivers.base import BrowserType

logger = logging.getLogger(__name__)

class WorkflowExecutor:
    """Orchestrates a single workflow execution run."""

    def __init__(self,
                 workflow_repo: IWorkflowRepository,
                 credential_repo: ICredentialRepository,
                 webdriver_service: IWebDriverService,
                 reporting_service: IReportingService):
        """Initialize the executor with necessary services/repositories."""
        if workflow_repo is None: raise ValueError("Workflow repository cannot be None.")
        if credential_repo is None: raise ValueError("Credential repository cannot be None.")
        if webdriver_service is None: raise ValueError("WebDriver service cannot be None.")
        if reporting_service is None: raise ValueError("Reporting service cannot be None.")
        self.workflow_repository = workflow_repo
        self.credential_repository = credential_repo
        self.webdriver_service = webdriver_service
        self.reporting_service = reporting_service

    def execute(self,
                name: str,
                credential_name: Optional[str] = None,
                browser_type: BrowserType = BrowserType.CHROME,
                driver_type: str = "selenium", # 'selenium' or 'playwright'
                log_callback: Optional[Callable[[str], None]] = None, # Keep for potential future use
                stop_event: Optional[threading.Event] = None
                ) -> Dict[str, Any]:
        """
        Executes the workflow run sequence: Load -> Create Driver -> Run -> Cleanup -> Save Log.

        Args:
            name: The name of the workflow to execute.
            credential_name: Optional name of the credential to use.
            browser_type: The type of browser to use (CHROME, FIREFOX, etc.).
            driver_type: The driver implementation to use ('selenium' or 'playwright').
            log_callback: Optional callback for logging (not currently used).
            stop_event: Optional event to signal a stop request.

        Returns:
            The final execution log dictionary.

        Raises:
            Specific exceptions (WorkflowError, WebDriverError, etc.) if setup or execution fails critically.
            These should be caught by the calling service.
        """
        logger.info(f"EXECUTOR: Starting run for WF='{name}'")
        driver: Optional[IWebDriver] = None
        execution_log: Optional[Dict[str, Any]] = None
        start_time = time.time()

        try:
            actions = self._load_actions(name)
            driver = self._create_driver(browser_type, driver_type)

            # Instantiate the refactored runner, passing dependencies
            runner = WorkflowRunner(
                driver=driver,
                credential_repo=self.credential_repository,
                workflow_repo=self.workflow_repository,
                stop_event=stop_event
                # ErrorHandlingStrategy can be passed if needed, defaults to STOP_ON_ERROR
            )

            # The refactored runner's run method now returns the full log dict
            execution_log = runner.run(actions, workflow_name=name) # Runner handles internal execution loop

            final_status = execution_log.get("final_status", "UNKNOWN")
            logger.info(f"EXECUTOR: Runner finished WF='{name}'. Status: {final_status}")
            # No need to manually build the log here, runner provides it
            return execution_log

        except Exception as e:
            # Log the error encountered during setup or execution
            logger.error(f"EXECUTOR: Error during WF='{name}' execution: {e}", exc_info=(not isinstance(e, AutoQliqError)))
            # Create/update log with failure details
            execution_log = self._create_error_log(name, start_time, e, execution_log)
            raise # Re-raise the original exception for the service to handle

        finally:
            # Always dispose driver and save log
            if driver: self._dispose_driver(driver)
            if execution_log: self._save_log(execution_log)
            else: logger.error(f"EXECUTOR: No execution log generated for '{name}' in finally block.")
            # If exception was raised, this return is skipped.
            # If no exception, the log from try block is returned.
            # If log is still None here (very rare), return minimal error log.
            if execution_log is None:
                logger.critical(f"EXECUTOR: CRITICAL - Returning minimal error log for '{name}' as log was None.")
                # Return rather than raise, as the operation technically "finished" even if broken.
                return self._create_error_log(name, start_time, Exception("Executor finished without log or exception"), None)

    # --- Private Helper Methods (same as before) ---

    def _load_actions(self, name: str) -> List[IAction]:
        """Loads actions, wrapping errors."""
        logger.debug(f"EXECUTOR: Loading actions for '{name}'")
        try:
            return self.workflow_repository.load(name)
        except (RepositoryError, SerializationError, ValidationError) as e:
            raise WorkflowError(f"Failed to load actions for workflow '{name}'", workflow_name=name, cause=e) from e
        except Exception as e:
            raise WorkflowError(f"Unexpected error loading actions for workflow '{name}'", workflow_name=name, cause=e) from e

    def _create_driver(self, browser_type: BrowserType, driver_type: str = "selenium") -> IWebDriver:
        """Creates driver, wrapping errors."""
        logger.debug(f"EXECUTOR: Creating {driver_type} WebDriver for {browser_type.value}")
        try:
            # Pass both browser_type and driver_type to the service
            return self.webdriver_service.create_web_driver(
                browser_type_str=browser_type.value,
                driver_type=driver_type
            )
        except (WebDriverError, ConfigError) as e:
            raise
        except Exception as e:
            raise WebDriverError(f"Unexpected error creating {driver_type} WebDriver for {browser_type.value}", cause=e) from e

    def _dispose_driver(self, driver: IWebDriver):
        """Safely disposes driver."""
        logger.debug("EXECUTOR: Disposing WebDriver.")
        try:
            self.webdriver_service.dispose_web_driver(driver)
        except Exception as e:
            logger.error(f"EXECUTOR: Error disposing WebDriver: {e}", exc_info=True)

    def _save_log(self, execution_log: Dict[str, Any]):
        """Safely saves the execution log."""
        wf_name = execution_log.get('workflow_name', 'unknown')
        logger.debug(f"EXECUTOR: Saving execution log for '{wf_name}'.")
        try:
            self.reporting_service.save_execution_log(execution_log)
        except Exception as e:
            logger.error(f"EXECUTOR: Failed save execution log for '{wf_name}': {e}", exc_info=True)

    def _create_error_log(self, name: str, start_time: float, error: Exception, existing_log: Optional[Dict[str, Any]]) -> Dict[str, Any]:
         """Creates/Updates execution log on failure."""
         end_time = time.time()
         duration = round(end_time - start_time, 2)
         error_message = str(error)
         status = "STOPPED" if isinstance(error, WorkflowError) and "stopped by" in error_message.lower() else "FAILED"

         if existing_log:
              existing_log["final_status"] = status
              existing_log["error_message"] = error_message
              existing_log["end_time_iso"] = datetime.now().isoformat()
              existing_log["duration_seconds"] = duration
              return existing_log
         else:
              return {
                  "workflow_name": name,
                  "start_time_iso": datetime.fromtimestamp(start_time).isoformat(),
                  "end_time_iso": datetime.fromtimestamp(end_time).isoformat(),
                  "duration_seconds": duration,
                  "final_status": status,
                  "error_message": error_message,
                  "action_results": [], # No actions completed successfully if error was early
                  "summary": f"Workflow {status.lower()}: {error_message}",
                  "error_strategy": "UNKNOWN", # Strategy info would be in runner log if it ran
             }
