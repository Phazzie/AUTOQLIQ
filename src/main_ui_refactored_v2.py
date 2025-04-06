"""Main UI module for AutoQliq.

This module provides the entry point for the AutoQliq UI application.
"""

import tkinter as tk
import logging

from src.infrastructure.repositories import RepositoryFactory
from src.infrastructure.webdrivers import WebDriverFactory
from src.ui.factories.application_factory import ApplicationFactory
from src.ui.common.service_provider import ServiceProvider


def setup_logging():
    """Set up logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("autoqliq.log")
        ]
    )
    return logging.getLogger(__name__)


def main():
    """Main entry point for the application."""
    # Set up logging
    logger = setup_logging()
    logger.info("Starting AutoQliq")
    
    try:
        # Create the root window
        root = tk.Tk()
        root.title("AutoQliq")
        root.geometry("800x600")
        
        # Create repositories
        logger.debug("Creating repositories")
        repository_factory = RepositoryFactory()
        workflow_repo = repository_factory.create_workflow_repository("file_system")
        credential_repo = repository_factory.create_credential_repository("file_system")
        
        # Create the webdriver factory
        logger.debug("Creating webdriver factory")
        webdriver_factory = WebDriverFactory()
        
        # Create the service provider
        logger.debug("Creating service provider")
        service_provider = ServiceProvider()
        
        # Create the application factory
        logger.debug("Creating application factory")
        app_factory = ApplicationFactory(service_provider)
        
        # Register services
        logger.debug("Registering services")
        app_factory.register_services(workflow_repo, credential_repo, webdriver_factory)
        
        # Create the application
        logger.debug("Creating application")
        app_factory.create_notebook_application(root)
        
        # Start the main loop
        logger.info("Starting main loop")
        root.mainloop()
    except Exception as e:
        logger.exception(f"Error starting application: {str(e)}")
    finally:
        logger.info("Exiting AutoQliq")


if __name__ == "__main__":
    main()
