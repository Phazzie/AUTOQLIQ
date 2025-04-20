"""Main presenter implementation for AutoQliq.

This module provides the MainPresenter class that coordinates the main application window.
"""

import logging
from typing import Optional, Dict, Callable

from src.ui.presenters.base_presenter import BasePresenter
from src.ui.interfaces.presenter_interfaces import IMainPresenter
from src.ui.interfaces.view_interfaces import IMainView
from src.application.interfaces.service_interfaces import IWorkflowService, ICredentialService, IExecutionService

logger = logging.getLogger(__name__)

class MainPresenter(BasePresenter, IMainPresenter):
    """
    Main application presenter that coordinates the main view and application services.
    
    Manages the application lifecycle, menu actions, and tab coordination.
    """
    
    def __init__(
        self,
        workflow_service: IWorkflowService,
        credential_service: ICredentialService,
        execution_service: IExecutionService
    ):
        """
        Initialize the main presenter.
        
        Args:
            workflow_service: The workflow service.
            credential_service: The credential service.
            execution_service: The execution service.
        """
        super().__init__()
        self.workflow_service = workflow_service
        self.credential_service = credential_service
        self.execution_service = execution_service
        self._view: Optional[IMainView] = None
        logger.debug("MainPresenter initialized")
    
    def set_view(self, view: IMainView) -> None:
        """
        Set the view for this presenter.
        
        Args:
            view: The main view implementation.
        """
        self._view = view
        logger.debug("MainPresenter linked to view")
    
    def initialize(self) -> None:
        """Initialize the presenter and prepare the view."""
        if not self._view:
            logger.error("MainPresenter initialized without a view")
            raise ValueError("View must be set before initialization")
        
        # Set window title
        self._view.set_title("AutoQliq - Web Automation Tool")
        
        # Bind menu handlers
        self._view.bind_menu_handlers({
            'exit': self.on_exit,
            'about': self.on_about,
            'open_credential_manager': self.on_open_credential_manager
        })
        
        # Set initial status
        self._view.set_status("Ready")
        
        logger.debug("MainPresenter initialized")
    
    def on_exit(self) -> None:
        """Handle application exit."""
        logger.info("Application exit requested")
        # Perform any cleanup needed before exit
        # The view will handle the actual window destruction
    
    def on_about(self) -> None:
        """Show the about dialog."""
        logger.debug("About dialog requested")
        if self._view:
            self._view.show_info("AutoQliq - Web Automation Tool\nVersion 1.0\n\nA tool for automating web tasks.")
    
    def on_open_credential_manager(self) -> None:
        """Open the credential manager dialog."""
        logger.debug("Credential manager requested")
        # This would be implemented to create and show the credential manager dialog
        if self._view:
            self._view.show_info("Credential Manager not implemented yet.")
    
    def on_open_settings(self) -> None:
        """Open the settings dialog."""
        logger.debug("Settings dialog requested")
        # This would be implemented to create and show the settings dialog
        if self._view:
            self._view.show_info("Settings dialog not implemented yet.")
