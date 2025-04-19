"""Factory for creating enhanced view components.

This module provides a factory for creating enhanced view components with proper dependencies.
"""

import tkinter as tk
from typing import Any, Optional

from src.core.exceptions import UIError
from src.ui.views.workflow_editor_view_enhanced import WorkflowEditorViewEnhanced
from src.ui.presenters.workflow_editor_presenter_refactored import WorkflowEditorPresenter
from src.ui.common.abstract_factory import AbstractFactory
from src.ui.factories.presenter_factory import PresenterFactory


class EnhancedViewFactory(AbstractFactory[Any]):
    """Factory for creating enhanced view components.

    This class provides methods for creating enhanced view components with proper dependencies.

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
        """Initialize a new EnhancedViewFactory.

        Args:
            presenter_factory: The factory for creating presenters
            **kwargs: Additional arguments to pass to the parent constructor
        """
        super().__init__(**kwargs)
        self.presenter_factory = presenter_factory or PresenterFactory(self.service_provider)

    def _register_factories(self) -> None:
        """Register view factories in the registry."""
        self.register_factory("enhanced_workflow_editor", self.create_enhanced_workflow_editor_view)

    def create_enhanced_workflow_editor_view(
        self,
        root: tk.Widget,
        presenter: Optional[WorkflowEditorPresenter] = None
    ) -> WorkflowEditorViewEnhanced:
        """Create an enhanced workflow editor view.

        Args:
            root: The root widget
            presenter: The presenter for the view

        Returns:
            A configured enhanced workflow editor view

        Raises:
            UIError: If the view cannot be created
        """
        try:
            # Create the presenter if not provided
            if presenter is None:
                presenter = self.presenter_factory.create("workflow_editor")

            # Create the view
            view = WorkflowEditorViewEnhanced(root, presenter)

            # Set the view on the presenter
            presenter.set_view(view)

            return view
        except Exception as e:
            error_msg = "Failed to create enhanced workflow editor view"
            raise UIError(error_msg, component_name="WorkflowEditorViewEnhanced", cause=e)
