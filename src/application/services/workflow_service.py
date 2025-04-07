"""Workflow service implementation for AutoQliq."""
import logging
import time
import threading # For stop event
from typing import Dict, List, Any, Optional, Callable # Added Callable

# Core dependencies
from src.core.interfaces import IAction, IWorkflowRepository, ICredentialRepository, IWebDriver
from src.core.interfaces.service import IWorkflowService, IWebDriverService, IReportingService # Added Reporting
from src.core.workflow.runner import WorkflowRunner
from src.core.exceptions import WorkflowError, CredentialError, WebDriverError, ValidationError, AutoQliqError, ActionError, RepositoryError, SerializationError, ConfigError

# Infrastructure dependencies
from src.infrastructure.webdrivers.base import BrowserType

# Common utilities
from src.infrastructure.common.error_handling import handle_exceptions
from src.infrastructure.common.logging_utils import log_method_call

logger = logging.getLogger(__name__)


class WorkflowService(IWorkflowService):
    """
    Implementation of IWorkflowService. Orchestrates workflow creation, management, and execution.
    Connects repositories, WebDriver service, Reporting service and the workflow runner.
    """

    def __init__(
        self,
        workflow_repository: IWorkflowRepository,
        credential_repository: ICredentialRepository,
        webdriver_service: IWebDriverService,
        reporting_service: IReportingService # Inject ReportingService
    ):
        """Initialize a new WorkflowService."""
        if workflow_repository is None: raise ValueError("Workflow repository cannot be None.")
        if credential_repository is None: raise ValueError("Credential repository cannot be None.")
        if webdriver_service is None: raise ValueError("WebDriver service cannot be None.")
        if reporting_service is None: raise ValueError("Reporting service cannot be None.")

        self.workflow_repository = workflow_repository
        self.credential_repository = credential_repository
        self.webdriver_service = webdriver_service
        self.reporting_service = reporting_service # Store reporting service
        logger.info("WorkflowService initialized.")

    @log_method_call(logger)
    @handle_exceptions(WorkflowError, "Failed to create workflow", reraise_types=(WorkflowError, ValidationError, RepositoryError))
    def create_workflow(self, name: str) -> bool:
        """Create a new empty workflow."""
        logger.info(f"SERVICE: Attempting to create workflow: {name}")
        self.workflow_repository.create_workflow(name)
        logger.info(f"SERVICE: Workflow '{name}' created successfully.")
        return True

    @log_method_call(logger)
    @handle_exceptions(WorkflowError, "Failed to delete workflow", reraise_types=(WorkflowError, ValidationError, RepositoryError))
    def delete_workflow(self, name: str) -> bool:
        """Delete a workflow by name."""
        logger.info(f"SERVICE: Attempting to delete workflow: {name}")
        deleted = self.workflow_repository.delete(name)
        if deleted: logger.info(f"SERVICE: Workflow '{name}' deleted successfully.")
        else: logger.warning(f"SERVICE: Workflow '{name}' not found for deletion.")
        return deleted

    @log_method_call(logger)
    @handle_exceptions(WorkflowError, "Failed to list workflows", reraise_types=(RepositoryError,))
    def list_workflows(self) -> List[str]:
        """Get a list of available workflow names."""
        logger.debug("SERVICE: Listing all workflows.")
        workflows = self.workflow_repository.list_workflows()
        logger.debug(f"SERVICE: Found {len(workflows)} workflows.")
        return workflows

    @log_method_call(logger)
    @handle_exceptions(WorkflowError, "Failed to get workflow", reraise_types=(WorkflowError, ValidationError, RepositoryError, SerializationError))
    def get_workflow(self, name: str) -> List[IAction]:
        """Get the actions for a workflow by name."""
        logger.debug(f"SERVICE: Retrieving workflow: {name}")
        actions = self.workflow_repository.load(name)
        logger.debug(f"SERVICE: Workflow '{name}' retrieved with {len(actions)} actions.")
        return actions

    @log_method_call(logger)
    @handle_exceptions(WorkflowError, "Failed to save workflow", reraise_types=(WorkflowError, ValidationError, SerializationError, RepositoryError))
    def save_workflow(self, name: str, actions: List[IAction]) -> bool:
        """Save a workflow with its actions."""
        logger.info(f"SERVICE: Attempting to save workflow: {name} with {len(actions)} actions.")
        self.workflow_repository.save(name, actions)
        logger.info(f"SERVICE: Workflow '{name}' saved successfully.")
        return True

    @log_method_call(logger)
    # Remove decorator - run manages its own logging/error handling/reporting
    def run_workflow(
        self,
        name: str,
        credential_name: Optional[str] = None,
        browser_type: BrowserType = BrowserType.CHROME,
        log_callback: Optional[Callable[[str], None]] = None, # Accept callback
        stop_event: Optional[threading.Event] = None # Accept stop event
    ) -> Dict[str, Any]:
        """Run a workflow, returning detailed execution results and logging them."""
        logger.info(f"SERVICE: Preparing run: WF='{name}', Cred='{credential_name}', Browser='{browser_type.value}'")
        driver: Optional[IWebDriver] = None
        execution_log: Optional[Dict[str, Any]] = None # Initialize log dict

        # Generate execution ID at the start (though filename depends on final status)
        # execution_id = self.reporting_service.log_execution_start(name) # If using start log

        try:
            # 1. Load Actions
            actions = self.get_workflow(name) # Uses internal method with logging/error handling

            # 2. Create Driver (using WebDriverService)
            driver = self.webdriver_service.create_web_driver(browser_type_str=browser_type.value)

            # 3. Create Runner and Execute
            runner = WorkflowRunner(driver, self.credential_repository, self.workflow_repository, stop_event)
            # Runner now returns the full log dictionary
            execution_log = runner.run(actions, workflow_name=name)

            # 4. Return results (the log dict itself)
            logger.info(f"SERVICE: Workflow '{name}' execution finished with status: {execution_log.get('final_status')}")
            return execution_log

        except (WorkflowError, CredentialError, WebDriverError, ActionError, ValidationError, RepositoryError, SerializationError, ConfigError, AutoQliqError) as e:
             # Catch known errors during setup or execution if runner re-raises them unexpectedly
             logger.error(f"SERVICE: Error during workflow '{name}' execution setup or run: {e}", exc_info=True)
             # Create a basic log dict for failure if runner didn't provide one
             if execution_log is None: # Should not happen if runner's finally block works
                  execution_log = { "workflow_name": name, "final_status": "FAILED", "error_message": str(e),
                                    "start_time_iso": datetime.now().isoformat(), "end_time_iso": datetime.now().isoformat(),
                                    "duration_seconds": 0.0, "action_results": [] }
             else: # Update existing log if runner failed but returned partial log
                  execution_log["final_status"] = "FAILED"
                  execution_log["error_message"] = str(e)
             raise # Re-raise the original error for presenter to handle

        except Exception as e:
             # Catch unexpected errors
             logger.exception(f"SERVICE: Unexpected error running workflow '{name}'")
             if execution_log is None:
                  execution_log = { "workflow_name": name, "final_status": "FAILED", "error_message": f"Unexpected error: {e}",
                                    "start_time_iso": datetime.now().isoformat(), "end_time_iso": datetime.now().isoformat(),
                                    "duration_seconds": 0.0, "action_results": [] }
             else:
                  execution_log["final_status"] = "FAILED"
                  execution_log["error_message"] = f"Unexpected error: {e}"
             # Wrap in WorkflowError before re-raising
             raise WorkflowError(f"Unexpected error running workflow '{name}'", workflow_name=name, cause=e) from e

        finally:
            # 5. Ensure WebDriver Cleanup (using WebDriverService)
            if driver:
                try: self.webdriver_service.dispose_web_driver(driver)
                except Exception as q_e: logger.error(f"SERVICE: Error disposing WebDriver: {q_e}", exc_info=True)
            # 6. Save Execution Log (using ReportingService)
            if execution_log:
                 try: self.reporting_service.save_execution_log(execution_log)
                 except Exception as log_e: logger.error(f"SERVICE: Failed to save execution log for '{name}': {log_e}", exc_info=True)
            else:
                 logger.error(f"SERVICE: No execution log generated for workflow '{name}' run, cannot save log.")


    @log_method_call(logger)
    @handle_exceptions(WorkflowError, "Failed to get workflow metadata", reraise_types=(WorkflowError, ValidationError, RepositoryError))
    def get_workflow_metadata(self, name: str) -> Dict[str, Any]:
        """Get metadata for a workflow."""
        logger.debug(f"SERVICE: Retrieving metadata for workflow: {name}")
        metadata = self.workflow_repository.get_metadata(name)
        logger.debug(f"SERVICE: Metadata retrieved for workflow '{name}'.")
        return metadata