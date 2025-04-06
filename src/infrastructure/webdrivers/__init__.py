"""Webdrivers package initialization for AutoQliq.

This package provides WebDriver implementations and related utilities
for browser automation, abstracting specific driver libraries like
Selenium or Playwright.

Exports:
    BrowserType: Enum defining supported browser types.
    WebDriverFactory: Factory for creating WebDriver instances.
    SeleniumWebDriver: WebDriver implementation using Selenium.
    PlaywrightDriver: WebDriver implementation using Playwright (placeholder).
    handle_driver_exceptions: Decorator for consistent WebDriver error handling.
    # IWebDriver interface is likely defined in src.core.interfaces
"""

from .base import BrowserType
from .factory import WebDriverFactory
from .selenium_driver import SeleniumWebDriver
from .playwright_driver import PlaywrightDriver # Assuming it implements IWebDriver
from .error_handler import handle_driver_exceptions

__all__ = [
    "BrowserType",
    "WebDriverFactory",
    "SeleniumWebDriver",
    "PlaywrightDriver",
    "handle_driver_exceptions",
]
```

```text