"""Application builder for AutoQliq UI.

This module provides a builder for the AutoQliq UI application.
"""

import logging
from typing import Optional, Dict, Any

from src.ui.application import UIApplication
from src.ui.common.error_handler import ErrorHandler


class UIApplicationBuilder:
    """Builder for the AutoQliq UI application.

    This class provides a builder for the AutoQliq UI application, allowing
    flexible configuration of the application.

    Attributes:
        _title: The title of the application window
        _geometry: The geometry of the application window
        _logger: The logger for recording application operations and errors
        _repository_type: The type of repositories to create
        _repository_options: Options for the repositories
        _services: A dictionary to hold registered services
    """

    def __init__(self):
        """Initialize a new UIApplicationBuilder."""
        self._title = "AutoQliq"
        self._geometry = "800x600"
        self._logger = None
        self._repository_type = "file_system"
        self._repository_options = None
        self._services = {}

    def with_title(self, title: str) -> 'UIApplicationBuilder':
        """Set the title of the application window.

        Args:
            title: The title of the application window

        Returns:
            This builder
        """
        self._title = title
        return self

    def with_geometry(self, geometry: str) -> 'UIApplicationBuilder':
        """Set the geometry of the application window.

        Args:
            geometry: The geometry of the application window

        Returns:
            This builder
        """
        self._geometry = geometry
        return self

    def with_logger(self, logger: logging.Logger) -> 'UIApplicationBuilder':
        """Set the logger for recording application operations and errors.

        Args:
            logger: The logger for recording application operations and errors

        Returns:
            This builder
        """
        self._logger = logger
        return self

    def with_repositories(self, repository_type: str, options: Optional[Dict[str, Any]] = None) -> 'UIApplicationBuilder':
        """Set the type of repositories to create.

        Args:
            repository_type: The type of repositories to create
            options: Options for the repositories

        Returns:
            This builder
        """
        self._repository_type = repository_type
        self._repository_options = options
        return self

    def register_service(self, service_type: Any, service_instance: Any) -> 'UIApplicationBuilder':
        """Register a service to be used by the application.

        This method allows registering services by their type, which is more robust
        than using string names. It supports both concrete classes and interfaces.

        Args:
            service_type: The type of the service (class or interface)
            service_instance: The instance of the service

        Returns:
            This builder
        """
        self._services[service_type] = service_instance
        return self

    def register_service_by_name(self, service_name: str, service_instance: Any) -> 'UIApplicationBuilder':
        """Register a service by name to be used by the application.

        This method is provided for backward compatibility and for cases where
        a service doesn't have a well-defined type.

        Args:
            service_name: The name of the service
            service_instance: The instance of the service

        Returns:
            This builder
        """
        self._services[service_name] = service_instance
        return self

    def build(self) -> UIApplication:
        """Build the application.

        Returns:
            The built application
        """
        # Create the application
        app = UIApplication(
            title=self._title,
            geometry=self._geometry,
            logger=self._logger
        )

        # Register repositories
        app.register_repositories(
            repository_type=self._repository_type,
            repository_options=self._repository_options
        )

        # Register services
        for service_name, service_instance in self._services.items():
            app.service_provider.register(service_name, service_instance)

        return app

    @staticmethod
    def create_default_application(logger: Optional[logging.Logger] = None) -> UIApplication:
        """Create a default application with standard configuration.

        This method provides a centralized way to create a default application
        with standard configuration, avoiding duplication of configuration logic
        across the codebase.

        Args:
            logger: The logger for recording application operations and errors

        Returns:
            The configured application
        """
        return (
            UIApplicationBuilder()
            .with_title("AutoQliq")
            .with_geometry("800x600")
            .with_logger(logger)
            .with_repositories("file_system")
            .build()
        )
