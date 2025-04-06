"""Base module for AutoQliq WebDrivers.

Contains fundamental definitions used across different WebDriver implementations,
such as the supported browser types.
"""

import enum
import logging

logger = logging.getLogger(__name__)


class BrowserType(enum.Enum):
    """Enumeration of supported browser types."""
    CHROME = "chrome"
    FIREFOX = "firefox"
    EDGE = "edge"
    SAFARI = "safari"
    # Add other browser types like playwright-chromium etc. if needed

    @classmethod
    def from_string(cls, value: str) -> 'BrowserType':
        """Convert a string to a BrowserType enum member."""
        if not isinstance(value, str):
            raise TypeError(f"Browser type value must be a string, got {type(value)}")
        try:
            return cls(value.lower())
        except ValueError:
            valid_types = [member.value for member in cls]
            logger.error(f"Invalid browser type string: '{value}'. Valid types are: {valid_types}")
            raise ValueError(f"Unsupported browser type: '{value}'. Choose from {valid_types}")

# Note: The IWebDriver interface itself should ideally reside in
# src.core.interfaces/webdriver.py as it defines a core abstraction used
# by the application logic (actions, workflow runner).
# This file is for infrastructure-level base components related to webdrivers.