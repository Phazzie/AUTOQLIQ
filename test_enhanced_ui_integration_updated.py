"""Test script for the enhanced UI integration with the updated code."""

import logging
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import required modules
from src.ui.application_builder import UIApplicationBuilder


def setup_logging(config_file='logging.conf'):
    """Set up logging for the application using a configuration file."""
    try:
        # Try to load logging configuration from file
        import logging.config
        logging.config.fileConfig(config_file)
        logger = logging.getLogger(__name__)
        logger.info(f"Loaded logging configuration from {config_file}")
        return logger
    except Exception as e:
        # Fall back to basic configuration if file loading fails
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler("test_enhanced_ui.log")
            ]
        )
        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to load logging configuration from {config_file}: {e}")
        logger.info("Using default logging configuration")
        return logger


def main():
    """Main entry point for the test application."""
    # Set up logging
    logger = setup_logging()
    logger.info("Starting AutoQliq with Enhanced UI")
    
    try:
        # Create the application using the centralized builder method
        app = UIApplicationBuilder.create_default_application(logger)
        
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
