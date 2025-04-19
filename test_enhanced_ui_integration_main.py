"""Test script for the enhanced UI integration with the main application."""

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
from src.ui.application_builder import UIApplicationBuilder


def main():
    """Main entry point for the test application."""
    # Set up logging
    logger = logging.getLogger(__name__)
    logger.info("Starting AutoQliq with Enhanced UI")
    
    try:
        # Create the application using the builder
        app = (UIApplicationBuilder()
               .with_title("AutoQliq - Enhanced UI Test")
               .with_geometry("1000x700")
               .with_logger(logger)
               .with_repositories("file_system")
               .build())
        
        # Create the notebook application
        app.create_notebook_application()
        
        # Run the application
        app.run()
    except Exception as e:
        logger.exception(f"Error starting application: {str(e)}")
    finally:
        logger.info("Exiting AutoQliq")


if __name__ == "__main__":
    main()
