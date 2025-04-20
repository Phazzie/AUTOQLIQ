"""WebDriver factory module for AutoQliq.

This module provides the WebDriverFactory class for creating different types of WebDriver instances.
"""

import logging
import os
from typing import Optional, Dict, Any, Union

from src.core.interfaces import IWebDriver
from src.core.exceptions import WebDriverError
from src.config import config

logger = logging.getLogger(__name__)

class WebDriverFactory:
    """
    Factory for creating WebDriver instances based on configuration.
    
    This class encapsulates the creation logic for different browser drivers,
    handling driver path resolution, configuration, and error handling.
    """
    
    @classmethod
    def create(cls, browser_type: Optional[str] = None, options: Optional[Dict[str, Any]] = None) -> IWebDriver:
        """
        Create a WebDriver instance for the specified browser type.
        
        Args:
            browser_type: Type of browser to create a driver for. If None, uses the default from config.
            options: Optional dictionary of browser-specific options.
            
        Returns:
            An instance of IWebDriver for the specified browser.
            
        Raises:
            WebDriverError: If driver creation fails or the browser type is unsupported.
        """
        # Use default browser from config if not specified
        browser_type = (browser_type or config.default_browser).lower()
        options = options or {}
        
        logger.info(f"Creating WebDriver for browser: {browser_type}")
        
        try:
            # Import implementations here to avoid circular imports
            if browser_type == "chrome":
                from src.infrastructure.webdriver.chrome_driver import ChromeDriver
                return ChromeDriver(options)
            elif browser_type == "firefox":
                from src.infrastructure.webdriver.firefox_driver import FirefoxDriver
                return FirefoxDriver(options)
            elif browser_type == "edge":
                from src.infrastructure.webdriver.edge_driver import EdgeDriver
                return EdgeDriver(options)
            elif browser_type == "safari":
                from src.infrastructure.webdriver.safari_driver import SafariDriver
                return SafariDriver(options)
            elif browser_type == "remote":
                from src.infrastructure.webdriver.remote_driver import RemoteDriver
                return RemoteDriver(options)
            elif browser_type == "mock":
                from src.infrastructure.webdriver.mock_driver import MockDriver
                return MockDriver(options)
            else:
                raise WebDriverError(f"Unsupported browser type: {browser_type}")
        except ImportError as e:
            logger.error(f"Failed to import driver module for {browser_type}: {e}")
            raise WebDriverError(f"Driver module not found for {browser_type}") from e
        except Exception as e:
            logger.error(f"Failed to create WebDriver for {browser_type}: {e}", exc_info=True)
            raise WebDriverError(f"Failed to create WebDriver for {browser_type}") from e
    
    @classmethod
    def _get_driver_path(cls, browser_type: str) -> Optional[str]:
        """
        Get the path to the browser driver executable.
        
        Args:
            browser_type: Type of browser driver to find.
            
        Returns:
            Path to the driver executable or None if not configured.
        """
        # First check the config
        driver_path = config.get_driver_path(browser_type)
        
        # If not in config, check environment variables
        if not driver_path:
            env_var = f"{browser_type.upper()}_DRIVER_PATH"
            driver_path = os.environ.get(env_var)
            
        if driver_path and os.path.exists(driver_path):
            logger.debug(f"Found {browser_type} driver at: {driver_path}")
            return driver_path
        elif driver_path:
            logger.warning(f"Configured driver path does not exist: {driver_path}")
            
        return None

# STATUS: COMPLETE ✓