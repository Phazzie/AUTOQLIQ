"""WebDriver service implementation for AutoQliq."""
import logging
from typing import Dict, Any, Optional

from src.core.interfaces import IWebDriver
from src.core.exceptions import WebDriverError
from src.application.interfaces import IWebDriverService
from src.infrastructure.webdrivers.browser_type import BrowserType
from src.infrastructure.common.error_handling import handle_exceptions
from src.infrastructure.common.logging_utils import log_method_call


class WebDriverService(IWebDriverService):
    """Implementation of IWebDriverService.
    
    This class provides services for managing web drivers, including creating,
    configuring, and disposing of web driver instances.
    
    Attributes:
        web_driver_factory: Factory for creating web driver instances
        logger: Logger for recording service operations and errors
    """
    
    def __init__(self, web_driver_factory: Any):
        """Initialize a new WebDriverService.
        
        Args:
            web_driver_factory: Factory for creating web driver instances
        """
        self.web_driver_factory = web_driver_factory
        self.logger = logging.getLogger(__name__)
        
        # Map of browser type strings to BrowserType enum values
        self.browser_type_map = {
            "chrome": BrowserType.CHROME,
            "firefox": BrowserType.FIREFOX,
            "edge": BrowserType.EDGE
        }
    
    @log_method_call(logging.getLogger(__name__))
    @handle_exceptions(WebDriverError, "Failed to create web driver")
    def create_web_driver(self, browser_type: str, options: Optional[Dict[str, Any]] = None) -> IWebDriver:
        """Create a new web driver instance.
        
        Args:
            browser_type: The type of browser to create a driver for
            options: Optional dictionary of browser-specific options
            
        Returns:
            A configured web driver instance
            
        Raises:
            WebDriverError: If there is an error creating the web driver
        """
        self.logger.info(f"Creating {browser_type} web driver")
        
        # Convert browser type string to enum value
        if browser_type.lower() not in self.browser_type_map:
            error_msg = f"Unsupported browser type: {browser_type}"
            self.logger.error(error_msg)
            raise WebDriverError(error_msg)
        
        browser_enum = self.browser_type_map[browser_type.lower()]
        
        try:
            # Create the web driver
            return self.web_driver_factory.create_driver(browser_enum, options=options)
        except Exception as e:
            error_msg = f"Failed to create web driver: {str(e)}"
            self.logger.error(error_msg)
            raise WebDriverError(error_msg) from e
    
    @log_method_call(logging.getLogger(__name__))
    @handle_exceptions(WebDriverError, "Failed to dispose web driver")
    def dispose_web_driver(self, driver: IWebDriver) -> bool:
        """Dispose of a web driver instance.
        
        Args:
            driver: The web driver instance to dispose of
            
        Returns:
            True if the web driver was disposed of successfully
            
        Raises:
            WebDriverError: If there is an error disposing of the web driver
        """
        self.logger.info("Disposing of web driver")
        
        try:
            # Quit the web driver
            driver.quit()
            return True
        except Exception as e:
            error_msg = f"Failed to dispose of web driver: {str(e)}"
            self.logger.error(error_msg)
            raise WebDriverError(error_msg) from e
