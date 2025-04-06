"""UI factory for AutoQliq.

This module provides a factory for creating UI components.
"""

import tkinter as tk
from typing import Dict, Any, Optional

from src.core.exceptions import UIError
from src.core.interfaces import IWorkflowRepository, ICredentialRepository
from src.infrastructure.webdrivers import WebDriverFactory
from src.ui.views.workflow_editor_view_refactored import WorkflowEditorView
from src.ui.views.workflow_runner_view_refactored import WorkflowRunnerView
from src.ui.presenters.workflow_editor_presenter_refactored import WorkflowEditorPresenter
from src.ui.presenters.workflow_runner_presenter_refactored import WorkflowRunnerPresenter


class UIFactory:
    """Factory for creating UI components.
    
    This class provides methods for creating UI components with consistent
    configuration and dependencies.
    """
    
    @staticmethod
    def create_workflow_editor_view(
        root: tk.Tk,
        workflow_repository: IWorkflowRepository
    ) -> WorkflowEditorView:
        """Create a workflow editor view.
        
        Args:
            root: The root Tkinter window
            workflow_repository: Repository for workflow storage and retrieval
            
        Returns:
            A configured workflow editor view
            
        Raises:
            UIError: If the view cannot be created
        """
        try:
            # Create the presenter
            presenter = UIFactory.create_workflow_editor_presenter(workflow_repository)
            
            # Create the view
            view = WorkflowEditorView(root, presenter)
            
            # Set the view on the presenter
            presenter.set_view(view)
            
            return view
        except Exception as e:
            error_msg = "Failed to create workflow editor view"
            raise UIError(error_msg, component_name="WorkflowEditorView", cause=e)
    
    @staticmethod
    def create_workflow_runner_view(
        root: tk.Tk,
        workflow_repository: IWorkflowRepository,
        credential_repository: ICredentialRepository,
        webdriver_factory: Optional[WebDriverFactory] = None
    ) -> WorkflowRunnerView:
        """Create a workflow runner view.
        
        Args:
            root: The root Tkinter window
            workflow_repository: Repository for workflow storage and retrieval
            credential_repository: Repository for credential storage and retrieval
            webdriver_factory: Factory for creating webdriver instances
            
        Returns:
            A configured workflow runner view
            
        Raises:
            UIError: If the view cannot be created
        """
        try:
            # Create the presenter
            presenter = UIFactory.create_workflow_runner_presenter(
                workflow_repository,
                credential_repository,
                webdriver_factory
            )
            
            # Create the view
            view = WorkflowRunnerView(root, presenter)
            
            # Set the view on the presenter
            presenter.set_view(view)
            
            return view
        except Exception as e:
            error_msg = "Failed to create workflow runner view"
            raise UIError(error_msg, component_name="WorkflowRunnerView", cause=e)
    
    @staticmethod
    def create_workflow_editor_presenter(
        workflow_repository: IWorkflowRepository,
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
            return WorkflowEditorPresenter(workflow_repository, view=view)
        except Exception as e:
            error_msg = "Failed to create workflow editor presenter"
            raise UIError(error_msg, component_name="WorkflowEditorPresenter", cause=e)
    
    @staticmethod
    def create_workflow_runner_presenter(
        workflow_repository: IWorkflowRepository,
        credential_repository: ICredentialRepository,
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
            return WorkflowRunnerPresenter(
                workflow_repository,
                credential_repository,
                webdriver_factory,
                view=view
            )
        except Exception as e:
            error_msg = "Failed to create workflow runner presenter"
            raise UIError(error_msg, component_name="WorkflowRunnerPresenter", cause=e)
