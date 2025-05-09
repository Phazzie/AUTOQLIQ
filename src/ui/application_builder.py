"""Application builder for AutoQliq UI.

This module provides a builder for the AutoQliq UI application.
"""

import logging
from typing import Optional, Dict, Any

from src.ui.application import UIApplication


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
    """
    
    def __init__(self):
        """Initialize a new UIApplicationBuilder."""
        self._title = "AutoQliq"
        self._geometry = "800x600"
        self._logger = None
        self._repository_type = "file_system"
        self._repository_options = None
    
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
        
        return app
