"""WebDriver service implementation for AutoQliq."""
import logging
from typing import Dict, Any, Optional, List

# Core dependencies
from src.core.interfaces import IWebDriver
from src.core.interfaces.service import IWebDriverService
from src.core.exceptions import WebDriverError, ConfigError, AutoQliqError

# Infrastructure dependencies
from src.infrastructure.webdrivers.factory import WebDriverFactory
from src.infrastructure.webdrivers.base import BrowserType

# Common utilities
from src.infrastructure.common.error_handling import handle_exceptions
from src.infrastructure.common.logging_utils import log_method_call
# Configuration
from src.config import config # Import configured instance

logger = logging.getLogger(__name__)


class WebDriverService(IWebDriverService):
    """
    Implementation of IWebDriverService. Manages WebDriver instances via a factory.

    Acts primarily as a facade over the WebDriverFactory, integrating configuration
    and ensuring consistent error handling and logging at the service layer.
    """

    def __init__(self, webdriver_factory: WebDriverFactory):
        """Initialize a new WebDriverService."""
        if webdriver_factory is None:
            raise ValueError("WebDriver factory cannot be None.")
        self.webdriver_factory = webdriver_factory
        logger.info("WebDriverService initialized.")

    @log_method_call(logger)
    @handle_exceptions(WebDriverError, "Failed to create web driver", reraise_types=(WebDriverError, ConfigError))
    def create_web_driver(
        self,
        browser_type_str: Optional[str] = None, # Make optional, use config default
        selenium_options: Optional[Any] = None, # Specific options object
        **kwargs: Any # Allow passing other factory options like implicit_wait_seconds
    ) -> IWebDriver:
        """Create a new web driver instance using the factory and configuration.

        Args:
            browser_type_str: Optional name of the browser type (e.g., "chrome").
                              If None, uses default from config.
            selenium_options: Specific Selenium options object (e.g., ChromeOptions).
            **kwargs: Additional arguments passed to the factory (e.g., `implicit_wait_seconds`, `webdriver_path`).

        Returns:
            A configured web driver instance conforming to IWebDriver.
        """
        browser_to_use_str = browser_type_str or config.default_browser
        logger.info(f"SERVICE: Requesting creation of Selenium driver for browser '{browser_to_use_str}'")

        try:
            # Convert string to BrowserType enum
            browser_enum = BrowserType.from_string(browser_to_use_str) # Raises ValueError
        except ValueError as e:
            # Convert ValueError to ConfigError
            raise ConfigError(str(e), cause=e) from e

        # Prepare factory arguments from config and kwargs
        factory_args = {}
        factory_args['implicit_wait_seconds'] = kwargs.get('implicit_wait_seconds', config.implicit_wait)

        webdriver_path_kwarg = kwargs.get('webdriver_path')
        if webdriver_path_kwarg:
             factory_args['webdriver_path'] = webdriver_path_kwarg
             logger.debug(f"Using provided webdriver_path: {webdriver_path_kwarg}")
        else:
             config_path = config.get_driver_path(browser_enum.value)
             if config_path:
                  factory_args['webdriver_path'] = config_path
                  logger.debug(f"Using configured webdriver_path: {config_path}")

        # Delegate creation to the factory
        driver = self.webdriver_factory.create_driver(
            browser_type=browser_enum,
            selenium_options=selenium_options,
            **factory_args
        )
        logger.info(f"SERVICE: Successfully created Selenium driver for {browser_to_use_str}.")
        return driver

    @log_method_call(logger)
    @handle_exceptions(WebDriverError, "Failed to dispose web driver")
    def dispose_web_driver(self, driver: IWebDriver) -> bool:
        """Dispose of (quit) a web driver instance."""
        if driver is None:
            logger.warning("SERVICE: dispose_web_driver called with None driver.")
            return False

        logger.info(f"SERVICE: Attempting to dispose of WebDriver instance: {type(driver).__name__}")
        try:
            driver.quit() # IWebDriver interface defines quit()
            logger.info("SERVICE: WebDriver disposed successfully.")
            return True
        except Exception as e:
             logger.error(f"SERVICE: Error disposing WebDriver: {e}", exc_info=True)
             raise # Let decorator wrap


    @log_method_call(logger)
    # No specific error handling needed here usually
    def get_available_browser_types(self) -> List[str]:
        """Get a list of available browser type names supported by the service/factory."""
        # Get names from the BrowserType enum
        available_types = [bt.value for bt in BrowserType]
        logger.debug(f"SERVICE: Returning available browser types: {available_types}")
        return available_types