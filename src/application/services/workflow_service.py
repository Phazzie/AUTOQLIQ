################################################################################
"""Workflow service implementation for AutoQliq."""
import logging
import time
import threading # For stop event
from typing import Dict, List, Any, Optional, Callable # Added Callable

# Core dependencies
from src.core.interfaces import IAction, IWorkflowRepository, ICredentialRepository, IWebDriver
from src.core.interfaces.service import IWorkflowService, IWebDriverService, IReportingService # Added Reporting
from src.core.exceptions import WorkflowError, CredentialError, WebDriverError, ValidationError, AutoQliqError, ActionError, RepositoryError, SerializationError, ConfigError

# Infrastructure dependencies
from src.infrastructure.webdrivers.base import BrowserType

# Application dependencies
from src.application.services.workflow_executor import WorkflowExecutor

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
    def run_workflow(
        self,
        name: str,
        credential_name: Optional[str] = None,
        browser_type: BrowserType = BrowserType.CHROME,
        driver_type: str = "selenium", # 'selenium' or 'playwright'
        log_callback: Optional[Callable[[str], None]] = None, # Accept callback
        stop_event: Optional[threading.Event] = None # Accept stop event
    ) -> Dict[str, Any]:
        """Run a workflow, returning detailed execution results and logging them.

        This method delegates the actual execution to the WorkflowExecutor, which handles
        the orchestration of loading actions, creating the driver, running the workflow,
        and cleaning up resources.

        Args:
            name: The name of the workflow to execute
            credential_name: Optional name of credential to use
            browser_type: The type of browser to use
            driver_type: The driver implementation to use ('selenium' or 'playwright')
            log_callback: Optional callback for logging (not currently used)
            stop_event: Optional event to signal a stop request

        Returns:
            A dictionary containing the execution results

        Raises:
            WorkflowError: If the workflow execution fails
            WebDriverError: If there's an error with the WebDriver
            Other specific exceptions based on the failure type
        """
        logger.info(f"SERVICE: Preparing run: WF='{name}', Cred='{credential_name}', Browser='{browser_type.value}', Driver='{driver_type}'")

        try:
            # Create a workflow executor for this run
            executor = WorkflowExecutor(
                workflow_repo=self.workflow_repository,
                credential_repo=self.credential_repository,
                webdriver_service=self.webdriver_service,
                reporting_service=self.reporting_service
            )

            # Execute the workflow and get the results
            execution_log = executor.execute(
                name=name,
                credential_name=credential_name,
                browser_type=browser_type,
                driver_type=driver_type,
                log_callback=log_callback,
                stop_event=stop_event
            )

            # Log the result and return
            logger.info(f"SERVICE: Workflow '{name}' execution finished with status: {execution_log.get('final_status')}")
            return execution_log

        except (WorkflowError, WebDriverError, CredentialError, ValidationError,
                ActionError, RepositoryError, SerializationError, ConfigError, AutoQliqError) as e:
            # Log the error and re-raise for the presenter to handle
            logger.error(f"SERVICE: Error during workflow '{name}' execution: {e}", exc_info=True)
            raise

        except Exception as e:
            # For unexpected errors, wrap in a WorkflowError
            logger.exception(f"SERVICE: Unexpected error running workflow '{name}'")
            raise WorkflowError(f"Unexpected error running workflow '{name}'", workflow_name=name, cause=e) from e


    @log_method_call(logger)
    @handle_exceptions(WorkflowError, "Failed to get workflow metadata", reraise_types=(WorkflowError, ValidationError, RepositoryError))
    def get_workflow_metadata(self, name: str) -> Dict[str, Any]:
        """Get metadata for a workflow."""
        logger.debug(f"SERVICE: Retrieving metadata for workflow: {name}")
        metadata = self.workflow_repository.get_metadata(name)
        logger.debug(f"SERVICE: Metadata retrieved for workflow '{name}'.")
        return metadata

# No longer need datetime import since execution_log handling is in WorkflowExecutor

################################################################################