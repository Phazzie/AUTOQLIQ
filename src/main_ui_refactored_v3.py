"""Main UI module for AutoQliq.

This module provides the entry point for the AutoQliq UI application.
"""

import logging

from src.ui.application import UIApplication


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
        # Create the application
        app = UIApplication(logger=logger)
        
        # Register repositories
        app.register_repositories()
        
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
