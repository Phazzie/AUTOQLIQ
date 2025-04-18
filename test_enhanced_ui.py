"""Test script for the enhanced workflow editor UI."""

import tkinter as tk
import logging
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

# Import required modules
from src.infrastructure.repositories.workflow_repository import FileSystemWorkflowRepository
from src.ui.factories.presenter_factory import PresenterFactory
from src.ui.factories.enhanced_view_factory import EnhancedViewFactory
from src.ui.common.service_provider import ServiceProvider


def main():
    """Run the enhanced workflow editor UI test."""
    # Create the root window
    root = tk.Tk()
    root.title("AutoQliq - Enhanced UI Test")
    root.geometry("1000x700")
    
    # Create a workflow repository
    workflow_repo = FileSystemWorkflowRepository("workflows")
    
    # Create a service provider
    service_provider = ServiceProvider()
    service_provider.register("workflow_repository", workflow_repo)
    
    # Create a presenter factory
    presenter_factory = PresenterFactory(service_provider)
    
    # Create an enhanced view factory
    view_factory = EnhancedViewFactory(presenter_factory, service_provider=service_provider)
    
    # Create the enhanced workflow editor view
    view = view_factory.create_enhanced_workflow_editor_view(root)
    
    # Start the main loop
    root.mainloop()


if __name__ == "__main__":
    main()
