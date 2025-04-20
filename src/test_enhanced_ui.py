"""Test script for the enhanced UI components."""

import tkinter as tk
import logging
import os
import sys
from typing import Dict, Any
import pytest

# Skip interactive UI test during pytest collection
pytest.skip("Skipping interactive enhanced UI test script.", allow_module_level=True)

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the necessary modules
from src.core.exceptions import UIError
from src.infrastructure.repositories.thread_safe_workflow_repository import ThreadSafeWorkflowRepository
from src.infrastructure.repositories.secure_credential_repository import SecureCredentialRepository
from src.infrastructure.encryption.simple_encryption_service import SimpleEncryptionService
from src.infrastructure.webdrivers import WebDriverFactory, BrowserType
from src.ui.factories.enhanced_ui_factory import EnhancedUIFactory


def setup_logging() -> None:
    """Set up logging for the application."""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('test_enhanced_ui.log', mode='w')
        ]
    )


def create_repositories() -> Dict[str, Any]:
    """Create the repositories for the application."""
    # Create the directories if they don't exist
    os.makedirs('data/workflows', exist_ok=True)
    os.makedirs('data/credentials', exist_ok=True)
    
    # Create the encryption service
    encryption_service = SimpleEncryptionService('test_key')
    
    # Create the repositories
    workflow_repository = ThreadSafeWorkflowRepository(
        directory_path='data/workflows',
        create_if_missing=True
    )
    
    credential_repository = SecureCredentialRepository(
        file_path='data/credentials/credentials.json',
        encryption_service=encryption_service,
        create_if_missing=True
    )
    
    # Create the WebDriver factory
    webdriver_factory = WebDriverFactory()
    
    return {
        'workflow_repository': workflow_repository,
        'credential_repository': credential_repository,
        'webdriver_factory': webdriver_factory
    }


def main() -> None:
    """Main function for the test script."""
    # Set up logging
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting test_enhanced_ui.py")
    
    try:
        # Create the repositories
        repos = create_repositories()
        logger.info("Repositories created")
        
        # Create the root window
        root = tk.Tk()
        root.title("AutoQliq Enhanced UI Test")
        root.geometry("1024x768")
        
        # Create the enhanced UI components
        components = EnhancedUIFactory.create_enhanced_ui_components(
            root,
            repos['workflow_repository'],
            repos['credential_repository'],
            repos['webdriver_factory']
        )
        logger.info("Enhanced UI components created")
        
        # Start the main loop
        root.mainloop()
    except UIError as e:
        logger.error(f"UI Error: {e}")
        if hasattr(e, 'cause') and e.cause:
            logger.error(f"Caused by: {e.cause}")
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")


if __name__ == '__main__':
    main()
