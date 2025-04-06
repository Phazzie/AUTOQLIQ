"""Workflow service implementation for AutoQliq."""
import logging
from typing import Dict, List, Any, Optional

from src.core.interfaces import IAction, IWebDriver, IWorkflowRepository, ICredentialRepository
from src.core.workflow import WorkflowRunner
from src.core.exceptions import WorkflowError, CredentialError, WebDriverError
from src.application.interfaces import IWorkflowService
from src.infrastructure.common.error_handling import handle_exceptions
from src.infrastructure.common.logging_utils import log_method_call


class WorkflowService(IWorkflowService):
    """Implementation of IWorkflowService.

    This class provides services for managing workflows, including creating,
    updating, deleting, and executing workflows.

    Attributes:
        workflow_repository: Repository for workflow storage and retrieval
        credential_repository: Repository for credential storage and retrieval
        web_driver_factory: Factory for creating web driver instances
        logger: Logger for recording service operations and errors
    """

    def __init__(self, workflow_repository: IWorkflowRepository,
                 credential_repository: ICredentialRepository,
                 web_driver_factory: Any):
        """Initialize a new WorkflowService.

        Args:
            workflow_repository: Repository for workflow storage and retrieval
            credential_repository: Repository for credential storage and retrieval
            web_driver_factory: Factory for creating web driver instances
        """
        self.workflow_repository = workflow_repository
        self.credential_repository = credential_repository
        self.web_driver_factory = web_driver_factory
        self.logger = logging.getLogger(__name__)

    @log_method_call(logging.getLogger(__name__))
    @handle_exceptions(WorkflowError, "Failed to create workflow")
    def create_workflow(self, name: str) -> bool:
        """Create a new empty workflow.

        Args:
            name: The name of the workflow to create

        Returns:
            True if the workflow was created successfully

        Raises:
            WorkflowError: If there is an error creating the workflow
        """
        self.logger.info(f"Creating workflow: {name}")
        # Create an empty workflow
        self.workflow_repository.save(name, [])
        return True

    @log_method_call(logging.getLogger(__name__))
    @handle_exceptions(WorkflowError, "Failed to delete workflow")
    def delete_workflow(self, name: str) -> bool:
        """Delete a workflow.

        Args:
            name: The name of the workflow to delete

        Returns:
            True if the workflow was deleted successfully

        Raises:
            WorkflowError: If there is an error deleting the workflow
        """
        self.logger.info(f"Deleting workflow: {name}")
        return self.workflow_repository.delete(name)

    @log_method_call(logging.getLogger(__name__))
    @handle_exceptions(WorkflowError, "Failed to list workflows")
    def list_workflows(self) -> List[str]:
        """Get a list of available workflows.

        Returns:
            A list of workflow names

        Raises:
            WorkflowError: If there is an error retrieving the workflow list
        """
        self.logger.debug("Listing workflows")
        return self.workflow_repository.list_workflows()

    @log_method_call(logging.getLogger(__name__))
    @handle_exceptions(WorkflowError, "Failed to get workflow")
    def get_workflow(self, name: str) -> List[IAction]:
        """Get a workflow by name.

        Args:
            name: The name of the workflow to get

        Returns:
            The list of actions in the workflow

        Raises:
            WorkflowError: If there is an error retrieving the workflow
        """
        self.logger.debug(f"Getting workflow: {name}")
        return self.workflow_repository.load(name)

    @log_method_call(logging.getLogger(__name__))
    @handle_exceptions(WorkflowError, "Failed to save workflow")
    def save_workflow(self, name: str, actions: List[IAction]) -> bool:
        """Save a workflow.

        Args:
            name: The name of the workflow to save
            actions: The list of actions in the workflow

        Returns:
            True if the workflow was saved successfully

        Raises:
            WorkflowError: If there is an error saving the workflow
        """
        self.logger.info(f"Saving workflow: {name} with {len(actions)} actions")
        return self.workflow_repository.save(name, actions)

    @log_method_call(logging.getLogger(__name__))
    def run_workflow(self, name: str, credential_name: Optional[str] = None) -> bool:
        """Run a workflow.

        Args:
            name: The name of the workflow to run
            credential_name: The name of the credential to use, if any

        Returns:
            True if the workflow was run successfully

        Raises:
            WorkflowError: If there is an error running the workflow
        """
        self.logger.info(f"Running workflow: {name} with credential: {credential_name}")

        try:
            # Load the workflow
            self.logger.debug(f"Loading workflow: {name}")
            actions = self.workflow_repository.load(name)

            # Get the credential if specified
            credential = None
            if credential_name:
                self.logger.debug(f"Getting credential: {credential_name}")
                credential = self.credential_repository.get_by_name(credential_name)

            # Create a web driver
            self.logger.debug("Creating web driver")
            web_driver = self.web_driver_factory.create_web_driver("chrome")

            try:
                # Create a workflow runner
                self.logger.debug("Creating workflow runner")
                workflow_runner = WorkflowRunner(
                    driver=web_driver,
                    credential_repo=self.credential_repository,
                    workflow_repo=self.workflow_repository
                )

                # Run the workflow
                self.logger.debug("Running workflow")
                success = workflow_runner.run_workflow(name)

                self.logger.info(f"Workflow completed with success: {success}")
                return success
            finally:
                # Always dispose of the web driver
                self.logger.debug("Disposing of web driver")
                web_driver.quit()
        except (WorkflowError, CredentialError, WebDriverError) as e:
            # Re-raise known exceptions
            self.logger.error(f"Error running workflow: {str(e)}")
            raise
        except Exception as e:
            # Log and re-raise unknown exceptions as WorkflowError
            error_msg = f"Unexpected error running workflow: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise WorkflowError(error_msg) from e

    @log_method_call(logging.getLogger(__name__))
    @handle_exceptions(WorkflowError, "Failed to get workflow metadata")
    def get_workflow_metadata(self, name: str) -> Dict[str, Any]:
        """Get metadata for a workflow.

        Args:
            name: The name of the workflow to get metadata for

        Returns:
            A dictionary containing workflow metadata

        Raises:
            WorkflowError: If there is an error retrieving the workflow metadata
        """
        self.logger.debug(f"Getting metadata for workflow: {name}")
        return self.workflow_repository.get_metadata(name)
