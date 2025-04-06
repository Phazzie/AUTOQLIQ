"""WebDriver service interface for AutoQliq.

This module defines the interface for web driver services that coordinate
between the core domain and infrastructure layers, implementing browser automation use cases.
"""
import abc
from typing import Dict, Any, Optional, List

from src.core.interfaces import IWebDriver


class IWebDriverService(abc.ABC):
    """Interface for web driver services.

    This interface defines the contract for services that manage web drivers,
    including creating, configuring, and disposing of web driver instances.
    """

    @abc.abstractmethod
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
        pass

    @abc.abstractmethod
    def dispose_web_driver(self, driver: IWebDriver) -> bool:
        """Dispose of a web driver instance.

        Args:
            driver: The web driver instance to dispose of

        Returns:
            True if the web driver was disposed of successfully

        Raises:
            WebDriverError: If there is an error disposing of the web driver
        """
        pass

    @abc.abstractmethod
    def get_available_browser_types(self) -> List[str]:
        """Get a list of available browser types.

        Returns:
            A list of browser type names

        Raises:
            WebDriverError: If there is an error retrieving the browser types
        """
        pass