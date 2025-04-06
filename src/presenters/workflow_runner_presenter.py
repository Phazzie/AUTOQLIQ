import logging
from typing import List, Dict, Any, Optional

from src.core.interfaces import IWorkflowRepository, ICredentialRepository, IWebDriver
from src.core.exceptions import WorkflowError, CredentialError, WebDriverError


class WorkflowRunnerPresenter:
    """
    Presenter for the workflow runner view.

    This class handles the business logic for running workflows, mediating between
    the view, repositories, and the workflow runner.

    Attributes:
        workflow_repository: Repository for workflow storage and retrieval
        credential_repository: Repository for credential storage and retrieval
        webdriver_factory: Factory for creating webdriver instances
        workflow_runner: Service for running workflows
        logger: Logger for recording presenter operations and errors
        _webdriver: The current webdriver instance, if any
    """

    def __init__(self, workflow_repository: IWorkflowRepository,
                 credential_repository: ICredentialRepository,
                 webdriver_factory: Any, workflow_runner: Any):
        """
        Initialize a new WorkflowRunnerPresenter.

        Args:
            workflow_repository: Repository for workflow storage and retrieval
            credential_repository: Repository for credential storage and retrieval
            webdriver_factory: Factory for creating webdriver instances
            workflow_runner: Service for running workflows
        """
        self.workflow_repository = workflow_repository
        self.credential_repository = credential_repository
        self.webdriver_factory = webdriver_factory
        self.workflow_runner = workflow_runner
        self.logger = logging.getLogger(__name__)
        self._webdriver = None

    def get_workflow_list(self) -> List[str]:
        """
        Get a list of available workflows.

        Returns:
            A list of workflow names

        Raises:
            WorkflowError: If there is an error retrieving the workflow list
        """
        self.logger.debug("Getting workflow list")
        return self.workflow_repository.get_workflow_list()

    def get_credential_list(self) -> List[Dict[str, str]]:
        """
        Get a list of available credentials.

        Returns:
            A list of credential dictionaries

        Raises:
            CredentialError: If there is an error retrieving the credential list
        """
        self.logger.debug("Getting credential list")
        return self.credential_repository.get_all()

    def run_workflow(self, workflow_name: str, credential_name: str) -> bool:
        """
        Run a workflow with the specified credential.

        Args:
            workflow_name: The name of the workflow to run
            credential_name: The name of the credential to use

        Returns:
            True if the workflow was run successfully

        Raises:
            WorkflowError: If there is an error loading the workflow
            CredentialError: If there is an error retrieving the credential
            WebDriverError: If there is an error creating the webdriver
            Exception: If there is an error running the workflow
        """
        self.logger.info(f"Running workflow: {workflow_name} with credential: {credential_name}")

        try:
            # Load the workflow
            self.logger.debug(f"Loading workflow: {workflow_name}")
            actions = self.workflow_repository.load_workflow(workflow_name)

            # Get the credential
            self.logger.debug(f"Getting credential: {credential_name}")
            credential = self.credential_repository.get_by_name(credential_name)

            if credential is None:
                error_msg = f"Credential not found: {credential_name}"
                self.logger.error(error_msg)
                raise CredentialError(error_msg)

            # Create the webdriver
            self.logger.debug("Creating webdriver")
            self._webdriver = self.webdriver_factory.create_webdriver()

            # Run the workflow
            self.logger.debug("Running workflow")
            success = self.workflow_runner.run_workflow(actions, self._webdriver, credential)

            self.logger.info(f"Workflow completed with success: {success}")
            return success
        except (WorkflowError, CredentialError, WebDriverError) as e:
            # Re-raise known exceptions
            self.logger.error(f"Error running workflow: {str(e)}")
            raise
        except Exception as e:
            # Log and re-raise unknown exceptions
            error_msg = f"Unexpected error running workflow: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise

    def stop_workflow(self) -> bool:
        """
        Stop the currently running workflow.

        Returns:
            True if the workflow was stopped successfully

        Raises:
            Exception: If there is an error stopping the workflow
        """
        self.logger.info("Stopping workflow")

        try:
            # Stop the workflow
            success = self.workflow_runner.stop_workflow()

            self.logger.info(f"Workflow stopped with success: {success}")
            return success
        except Exception as e:
            # Log and re-raise exceptions
            error_msg = f"Error stopping workflow: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise

    def cleanup(self) -> None:
        """
        Clean up resources used by the presenter.

        This method should be called when the presenter is no longer needed.
        It will close the webdriver if it is open.
        """
        self.logger.debug("Cleaning up resources")

        if self._webdriver is not None:
            try:
                self.logger.debug("Closing webdriver")
                # Call quit on the webdriver
                self._webdriver.quit()
                self._webdriver = None
            except Exception as e:
                # Log but don't re-raise exceptions during cleanup
                self.logger.error(f"Error closing webdriver: {str(e)}", exc_info=True)
