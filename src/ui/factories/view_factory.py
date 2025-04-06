"""Factory for creating view components.

This module provides a factory for creating view components with proper dependencies.
"""

import tkinter as tk
from typing import Any, Optional

from src.core.exceptions import UIError
from src.ui.views.workflow_editor_view_refactored import WorkflowEditorView
from src.ui.views.workflow_runner_view_refactored import WorkflowRunnerView
from src.ui.presenters.workflow_editor_presenter_refactored import WorkflowEditorPresenter
from src.ui.presenters.workflow_runner_presenter_refactored import WorkflowRunnerPresenter
from src.ui.common.abstract_factory import AbstractFactory
from src.ui.factories.presenter_factory import PresenterFactory


class ViewFactory(AbstractFactory[Any]):
    """Factory for creating view components.

    This class provides methods for creating view components with proper dependencies.

    Attributes:
        service_provider: The service provider for dependency injection
        registry: The component registry for dynamic component creation
        presenter_factory: The factory for creating presenters
    """

    def __init__(
        self,
        presenter_factory: Optional[PresenterFactory] = None,
        **kwargs
    ):
        """Initialize a new ViewFactory.

        Args:
            presenter_factory: The factory for creating presenters
            **kwargs: Additional arguments to pass to the parent constructor
        """
        super().__init__(**kwargs)
        self.presenter_factory = presenter_factory or PresenterFactory(self.service_provider)

    def _register_factories(self) -> None:
        """Register view factories in the registry."""
        self.register_factory("workflow_editor", self.create_workflow_editor_view)
        self.register_factory("workflow_runner", self.create_workflow_runner_view)

    def create_workflow_editor_view(
        self,
        root: tk.Widget,
        presenter: Optional[WorkflowEditorPresenter] = None
    ) -> WorkflowEditorView:
        """Create a workflow editor view.

        Args:
            root: The root widget
            presenter: The presenter for the view

        Returns:
            A configured workflow editor view

        Raises:
            UIError: If the view cannot be created
        """
        try:
            # Create the presenter if not provided
            if presenter is None:
                presenter = self.presenter_factory.create("workflow_editor")

            # Create the view
            view = WorkflowEditorView(root, presenter)

            # Set the view on the presenter
            presenter.set_view(view)

            return view
        except Exception as e:
            error_msg = "Failed to create workflow editor view"
            raise UIError(error_msg, component_name="WorkflowEditorView", cause=e)

    def create_workflow_runner_view(
        self,
        root: tk.Widget,
        presenter: Optional[WorkflowRunnerPresenter] = None
    ) -> WorkflowRunnerView:
        """Create a workflow runner view.

        Args:
            root: The root widget
            presenter: The presenter for the view

        Returns:
            A configured workflow runner view

        Raises:
            UIError: If the view cannot be created
        """
        try:
            # Create the presenter if not provided
            if presenter is None:
                presenter = self.presenter_factory.create("workflow_runner")

            # Create the view
            view = WorkflowRunnerView(root, presenter)

            # Set the view on the presenter
            presenter.set_view(view)

            return view
        except Exception as e:
            error_msg = "Failed to create workflow runner view"
            raise UIError(error_msg, component_name="WorkflowRunnerView", cause=e)
