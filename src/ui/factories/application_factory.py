"""Factory for creating application components.

This module provides a factory for creating application components with proper dependencies.
"""

import tkinter as tk
from tkinter import ttk
from typing import Any, Optional

from src.core.exceptions import UIError
from src.core.interfaces import IWorkflowRepository, ICredentialRepository
from src.infrastructure.webdrivers import WebDriverFactory
from src.ui.views.workflow_editor_view_refactored import WorkflowEditorView
from src.ui.views.workflow_runner_view_refactored import WorkflowRunnerView
from src.ui.common.abstract_factory import AbstractFactory
from src.ui.factories.view_factory import ViewFactory
from src.ui.factories.presenter_factory import PresenterFactory


class ApplicationFactory(AbstractFactory[Any]):
    """Factory for creating application components.

    This class provides methods for creating application components with proper dependencies.

    Attributes:
        service_provider: The service provider for dependency injection
        view_factory: The factory for creating views
        presenter_factory: The factory for creating presenters
    """

    def __init__(
        self,
        view_factory: Optional[ViewFactory] = None,
        presenter_factory: Optional[PresenterFactory] = None,
        **kwargs
    ):
        """Initialize a new ApplicationFactory.

        Args:
            view_factory: The factory for creating views
            presenter_factory: The factory for creating presenters
            **kwargs: Additional arguments to pass to the parent constructor
        """
        super().__init__(**kwargs)
        self.presenter_factory = presenter_factory or PresenterFactory(self.service_provider)
        self.view_factory = view_factory or ViewFactory(self.service_provider, presenter_factory=self.presenter_factory)

    def _register_factories(self) -> None:
        """Register application factories in the registry."""
        self.register_factory("workflow_editor", self.create_workflow_editor)
        self.register_factory("workflow_runner", self.create_workflow_runner)
        self.register_factory("notebook_application", self.create_notebook_application)

    def register_services(
        self,
        workflow_repository: IWorkflowRepository,
        credential_repository: ICredentialRepository,
        webdriver_factory: Optional[WebDriverFactory] = None
    ) -> None:
        """Register services in the service provider.

        Args:
            workflow_repository: Repository for workflow storage and retrieval
            credential_repository: Repository for credential storage and retrieval
            webdriver_factory: Factory for creating webdriver instances
        """
        self.register_service(IWorkflowRepository, workflow_repository)
        self.register_service(ICredentialRepository, credential_repository)

        if webdriver_factory:
            self.register_service(WebDriverFactory, webdriver_factory)

    def create_workflow_editor(self, root: tk.Widget) -> WorkflowEditorView:
        """Create a complete workflow editor with view and presenter.

        Args:
            root: The root widget

        Returns:
            A configured workflow editor view

        Raises:
            UIError: If the workflow editor cannot be created
        """
        try:
            return self.view_factory.create("workflow_editor", root=root)
        except Exception as e:
            error_msg = "Failed to create workflow editor"
            raise UIError(error_msg, component_name="WorkflowEditor", cause=e)

    def create_workflow_runner(self, root: tk.Widget) -> WorkflowRunnerView:
        """Create a complete workflow runner with view and presenter.

        Args:
            root: The root widget

        Returns:
            A configured workflow runner view

        Raises:
            UIError: If the workflow runner cannot be created
        """
        try:
            return self.view_factory.create("workflow_runner", root=root)
        except Exception as e:
            error_msg = "Failed to create workflow runner"
            raise UIError(error_msg, component_name="WorkflowRunner", cause=e)

    def create_notebook_application(self, root: tk.Tk) -> ttk.Notebook:
        """Create a notebook application with workflow editor and runner.

        Args:
            root: The root Tkinter window

        Returns:
            A configured notebook

        Raises:
            UIError: If the notebook application cannot be created
        """
        try:
            # Create a notebook
            notebook = ttk.Notebook(root)
            notebook.pack(fill=tk.BOTH, expand=True)

            # Create the editor view
            editor_frame = ttk.Frame(notebook)
            notebook.add(editor_frame, text="Workflow Editor")
            self.create("workflow_editor", root=editor_frame)

            # Create the runner view
            runner_frame = ttk.Frame(notebook)
            notebook.add(runner_frame, text="Workflow Runner")
            self.create("workflow_runner", root=runner_frame)

            return notebook
        except Exception as e:
            error_msg = "Failed to create notebook application"
            raise UIError(error_msg, component_name="NotebookApplication", cause=e)
