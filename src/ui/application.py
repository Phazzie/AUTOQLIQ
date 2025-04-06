"""UI application for AutoQliq.

This module provides the main UI application class for AutoQliq.
"""

import tkinter as tk
import logging
from typing import Optional, Dict, Any

from src.core.interfaces import IWorkflowRepository, ICredentialRepository
from src.infrastructure.webdrivers import WebDriverFactory
from src.infrastructure.repositories import RepositoryFactory
from src.ui.common.service_provider import ServiceProvider
from src.ui.common.component_factory_registry import ComponentFactoryRegistry
from src.ui.factories.application_factory import ApplicationFactory
from src.ui.factories.presenter_factory import PresenterFactory
from src.ui.factories.view_factory import ViewFactory


class UIApplication:
    """Main UI application for AutoQliq.
    
    This class provides the main UI application for AutoQliq, managing the
    application lifecycle and dependencies.
    
    Attributes:
        root: The root Tkinter window
        service_provider: The service provider for dependency injection
        factory_registry: The registry for component factories
        application_factory: The factory for application components
        logger: Logger for recording application operations and errors
    """
    
    def __init__(
        self,
        title: str = "AutoQliq",
        geometry: str = "800x600",
        logger: Optional[logging.Logger] = None
    ):
        """Initialize a new UIApplication.
        
        Args:
            title: The title of the application window
            geometry: The geometry of the application window
            logger: The logger for recording application operations and errors
        """
        # Create the root window
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry(geometry)
        
        # Create the logger
        self.logger = logger or logging.getLogger(__name__)
        
        # Create the service provider
        self.service_provider = ServiceProvider()
        
        # Create the factory registry
        self.factory_registry = ComponentFactoryRegistry(self.service_provider)
        
        # Register factory types
        self._register_factory_types()
        
        # Create the application factory
        self.application_factory = self._create_application_factory()
    
    def _register_factory_types(self) -> None:
        """Register factory types in the registry."""
        self.factory_registry.register("presenter", PresenterFactory)
        self.factory_registry.register("view", ViewFactory)
        self.factory_registry.register("application", ApplicationFactory)
    
    def _create_application_factory(self) -> ApplicationFactory:
        """Create the application factory.
        
        Returns:
            The application factory
        """
        # Create the presenter factory
        presenter_factory = self.factory_registry.create("presenter")
        
        # Create the view factory
        view_factory = self.factory_registry.create(
            "view", 
            presenter_factory=presenter_factory
        )
        
        # Create the application factory
        return self.factory_registry.create(
            "application",
            presenter_factory=presenter_factory,
            view_factory=view_factory
        )
    
    def register_repositories(
        self,
        repository_type: str = "file_system",
        repository_options: Optional[Dict[str, Any]] = None
    ) -> None:
        """Register repositories in the service provider.
        
        Args:
            repository_type: The type of repositories to create
            repository_options: Options for the repositories
        """
        # Create the repository factory
        repository_factory = RepositoryFactory()
        
        # Create the repositories
        workflow_repo = repository_factory.create_workflow_repository(repository_type)
        credential_repo = repository_factory.create_credential_repository(repository_type)
        
        # Create the webdriver factory
        webdriver_factory = WebDriverFactory()
        
        # Register the repositories and factories
        self.application_factory.register_services(
            workflow_repo,
            credential_repo,
            webdriver_factory
        )
    
    def create_notebook_application(self) -> None:
        """Create the notebook application."""
        self.application_factory.create("notebook_application", root=self.root)
    
    def run(self) -> None:
        """Run the application."""
        try:
            # Start the main loop
            self.logger.info("Starting main loop")
            self.root.mainloop()
        except Exception as e:
            self.logger.exception(f"Error running application: {str(e)}")
        finally:
            self.logger.info("Exiting application")
