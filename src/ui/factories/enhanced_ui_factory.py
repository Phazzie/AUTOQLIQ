"""Enhanced UI factory for AutoQliq."""

import tkinter as tk
import logging
from typing import Dict, Any, Optional

from src.core.exceptions import UIError
from src.core.interfaces import IWorkflowRepository, ICredentialRepository
from src.infrastructure.webdrivers import WebDriverFactory

from src.ui.views.workflow_runner_view_enhanced import WorkflowRunnerViewEnhanced
from src.ui.presenters.workflow_editor_presenter_enhanced import WorkflowEditorPresenterEnhanced
from src.ui.presenters.workflow_runner_presenter_enhanced import WorkflowRunnerPresenterEnhanced

logger = logging.getLogger(__name__)


class EnhancedUIFactory:
    """
    Factory for creating enhanced UI components.
    
    This class provides methods for creating enhanced UI components with proper
    dependency injection.
    """
    
    @staticmethod
    def create_workflow_editor_presenter(
        workflow_repository: IWorkflowRepository
    ) -> WorkflowEditorPresenterEnhanced:
        """
        Create a workflow editor presenter.
        
        Args:
            workflow_repository: The workflow repository
            
        Returns:
            A WorkflowEditorPresenterEnhanced instance
            
        Raises:
            UIError: If the presenter cannot be created
        """
        try:
            return WorkflowEditorPresenterEnhanced(workflow_repository)
        except Exception as e:
            error_msg = "Failed to create WorkflowEditorPresenterEnhanced"
            logger.exception(error_msg)
            raise UIError(error_msg, component_name="WorkflowEditorPresenterEnhanced", cause=e) from e
    
    @staticmethod
    def create_workflow_runner_presenter(
        workflow_repository: IWorkflowRepository,
        credential_repository: ICredentialRepository,
        webdriver_factory: WebDriverFactory
    ) -> WorkflowRunnerPresenterEnhanced:
        """
        Create a workflow runner presenter.
        
        Args:
            workflow_repository: The workflow repository
            credential_repository: The credential repository
            webdriver_factory: The WebDriver factory
            
        Returns:
            A WorkflowRunnerPresenterEnhanced instance
            
        Raises:
            UIError: If the presenter cannot be created
        """
        try:
            return WorkflowRunnerPresenterEnhanced(
                workflow_repository,
                credential_repository,
                webdriver_factory
            )
        except Exception as e:
            error_msg = "Failed to create WorkflowRunnerPresenterEnhanced"
            logger.exception(error_msg)
            raise UIError(error_msg, component_name="WorkflowRunnerPresenterEnhanced", cause=e) from e
    
    @staticmethod
    def create_workflow_runner_view(
        root: tk.Widget,
        presenter: WorkflowRunnerPresenterEnhanced
    ) -> WorkflowRunnerViewEnhanced:
        """
        Create a workflow runner view.
        
        Args:
            root: The parent widget
            presenter: The presenter
            
        Returns:
            A WorkflowRunnerViewEnhanced instance
            
        Raises:
            UIError: If the view cannot be created
        """
        try:
            return WorkflowRunnerViewEnhanced(root, presenter)
        except Exception as e:
            error_msg = "Failed to create WorkflowRunnerViewEnhanced"
            logger.exception(error_msg)
            raise UIError(error_msg, component_name="WorkflowRunnerViewEnhanced", cause=e) from e
    
    @staticmethod
    def create_enhanced_ui_components(
        root: tk.Widget,
        workflow_repository: IWorkflowRepository,
        credential_repository: ICredentialRepository,
        webdriver_factory: WebDriverFactory
    ) -> Dict[str, Any]:
        """
        Create all enhanced UI components.
        
        Args:
            root: The parent widget
            workflow_repository: The workflow repository
            credential_repository: The credential repository
            webdriver_factory: The WebDriver factory
            
        Returns:
            A dictionary containing all created components
            
        Raises:
            UIError: If any component cannot be created
        """
        try:
            # Create the presenters
            workflow_editor_presenter = EnhancedUIFactory.create_workflow_editor_presenter(
                workflow_repository
            )
            
            workflow_runner_presenter = EnhancedUIFactory.create_workflow_runner_presenter(
                workflow_repository,
                credential_repository,
                webdriver_factory
            )
            
            # Create a notebook for the views
            notebook = tk.ttk.Notebook(root)
            notebook.pack(fill=tk.BOTH, expand=True)
            
            # Create frames for each view
            runner_frame = tk.ttk.Frame(notebook)
            notebook.add(runner_frame, text="Run Workflows")
            
            # Create the views
            workflow_runner_view = EnhancedUIFactory.create_workflow_runner_view(
                runner_frame,
                workflow_runner_presenter
            )
            
            # Set the views on the presenters
            workflow_runner_presenter.set_view(workflow_runner_view)
            
            # Return all created components
            return {
                "notebook": notebook,
                "workflow_editor_presenter": workflow_editor_presenter,
                "workflow_runner_presenter": workflow_runner_presenter,
                "workflow_runner_view": workflow_runner_view
            }
        except Exception as e:
            error_msg = "Failed to create enhanced UI components"
            logger.exception(error_msg)
            raise UIError(error_msg, component_name="EnhancedUIComponents", cause=e) from e
