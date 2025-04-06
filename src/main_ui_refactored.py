"""Main UI module for AutoQliq.

This module provides the entry point for the AutoQliq UI application.
"""

import tkinter as tk
import logging
from tkinter import ttk

from src.infrastructure.repositories import RepositoryFactory
from src.infrastructure.webdrivers import WebDriverFactory
from src.ui.ui_factory import UIFactory


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


def create_notebook(root: tk.Tk) -> ttk.Notebook:
    """Create a notebook for the application.
    
    Args:
        root: The root Tkinter window
        
    Returns:
        A configured notebook
    """
    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True)
    return notebook


def main():
    """Main entry point for the application."""
    # Set up logging
    logger = setup_logging()
    logger.info("Starting AutoQliq")
    
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
    
    # Create a notebook for the application
    logger.debug("Creating notebook")
    notebook = create_notebook(root)
    
    # Create the editor view
    logger.debug("Creating editor view")
    editor_frame = ttk.Frame(notebook)
    notebook.add(editor_frame, text="Workflow Editor")
    editor_view = UIFactory.create_workflow_editor_view(editor_frame, workflow_repo)
    
    # Create the runner view
    logger.debug("Creating runner view")
    runner_frame = ttk.Frame(notebook)
    notebook.add(runner_frame, text="Workflow Runner")
    runner_view = UIFactory.create_workflow_runner_view(
        runner_frame, 
        workflow_repo, 
        credential_repo, 
        webdriver_factory
    )
    
    # Start the main loop
    logger.info("Starting main loop")
    root.mainloop()
    
    logger.info("Exiting AutoQliq")


if __name__ == "__main__":
    main()
