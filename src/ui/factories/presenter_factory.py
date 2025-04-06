"""Factory for creating presenter components.

This module provides a factory for creating presenter components with proper dependencies.
"""

from typing import Any, Optional

from src.core.exceptions import UIError
from src.core.interfaces import IWorkflowRepository, ICredentialRepository
from src.infrastructure.webdrivers import WebDriverFactory
from src.ui.presenters.workflow_editor_presenter_refactored import WorkflowEditorPresenter
from src.ui.presenters.workflow_runner_presenter_refactored import WorkflowRunnerPresenter
from src.ui.common.abstract_factory import AbstractFactory


class PresenterFactory(AbstractFactory[Any]):
    """Factory for creating presenter components.

    This class provides methods for creating presenter components with proper dependencies.

    Attributes:
        service_provider: The service provider for dependency injection
        registry: The component registry for dynamic component creation
    """

    def _register_factories(self) -> None:
        """Register presenter factories in the registry."""
        self.register_factory("workflow_editor", self.create_workflow_editor_presenter)
        self.register_factory("workflow_runner", self.create_workflow_runner_presenter)

    def create_workflow_editor_presenter(
        self,
        workflow_repository: Optional[IWorkflowRepository] = None,
        view: Any = None
    ) -> WorkflowEditorPresenter:
        """Create a workflow editor presenter.

        Args:
            workflow_repository: Repository for workflow storage and retrieval
            view: The view component

        Returns:
            A configured workflow editor presenter

        Raises:
            UIError: If the presenter cannot be created
        """
        try:
            # Get the workflow repository from the service provider if not provided
            if workflow_repository is None:
                workflow_repository = self.get_service(IWorkflowRepository)

            # Create the presenter
            return WorkflowEditorPresenter(workflow_repository, view=view)
        except Exception as e:
            error_msg = "Failed to create workflow editor presenter"
            raise UIError(error_msg, component_name="WorkflowEditorPresenter", cause=e)

    def create_workflow_runner_presenter(
        self,
        workflow_repository: Optional[IWorkflowRepository] = None,
        credential_repository: Optional[ICredentialRepository] = None,
        webdriver_factory: Optional[WebDriverFactory] = None,
        view: Any = None
    ) -> WorkflowRunnerPresenter:
        """Create a workflow runner presenter.

        Args:
            workflow_repository: Repository for workflow storage and retrieval
            credential_repository: Repository for credential storage and retrieval
            webdriver_factory: Factory for creating webdriver instances
            view: The view component

        Returns:
            A configured workflow runner presenter

        Raises:
            UIError: If the presenter cannot be created
        """
        try:
            # Get dependencies from the service provider if not provided
            if workflow_repository is None:
                workflow_repository = self.get_service(IWorkflowRepository)

            if credential_repository is None:
                credential_repository = self.get_service(ICredentialRepository)

            if webdriver_factory is None:
                try:
                    webdriver_factory = self.get_service(WebDriverFactory)
                except ValueError:
                    # WebDriverFactory is optional
                    pass

            # Create the presenter
            return WorkflowRunnerPresenter(
                workflow_repository,
                credential_repository,
                webdriver_factory,
                view=view
            )
        except Exception as e:
            error_msg = "Failed to create workflow runner presenter"
            raise UIError(error_msg, component_name="WorkflowRunnerPresenter", cause=e)
