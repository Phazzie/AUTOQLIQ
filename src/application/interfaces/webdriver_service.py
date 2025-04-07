"""WebDriver service interface for AutoQliq.

DEPRECATED: Use src.core.interfaces.service.IWebDriverService instead.
This module remains for backward compatibility.
"""
import warnings

# Re-export from the new location
from src.core.interfaces.service import IWebDriverService

__all__ = ["IWebDriverService"]

warnings.warn(
    "Importing IWebDriverService from src.application.interfaces.webdriver_service is deprecated. "
    "Import from src.core.interfaces.service instead.",
    DeprecationWarning,
    stacklevel=2
)