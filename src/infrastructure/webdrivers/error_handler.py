"""Error handling utilities for WebDriver implementations.

This module provides decorators and utilities for handling errors consistently
across different WebDriver implementations.
"""
import functools
import logging
from typing import Callable, TypeVar, Any, Type, Union, Optional

# Core imports
from src.core.exceptions import WebDriverError

logger = logging.getLogger(__name__)

# Generic type for function return value
T = TypeVar('T')

def handle_driver_exceptions(error_message_template: str) -> Callable:
    """
    Decorator that catches exceptions from WebDriver operations and wraps them 
    in WebDriverError with context information.
    
    Args:
        error_message_template: A template string that can include parameter names in braces.
            Example: "Failed to find element with selector: {selector}"
    
    Returns:
        Decorated function that handles WebDriver exceptions consistently.
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return func(*args, **kwargs)
            except WebDriverError:
                # Already a WebDriverError, re-raise without wrapping
                raise
            except Exception as e:
                # Format the error message with parameter values
                try:
                    error_message = error_message_template.format(**kwargs)
                except (KeyError, ValueError):
                    # If formatting fails, use the template as is
                    error_message = error_message_template
                
                # Log and raise a WebDriverError with the original exception as cause
                logger.error(f"{error_message}: {str(e)}", exc_info=True)
                raise WebDriverError(error_message, cause=e) from e
        return wrapper
    return decorator

def map_webdriver_exception(exception: Exception) -> WebDriverError:
    """
    Maps a WebDriver-specific exception to an appropriate WebDriverError.
    This allows for consistent error handling regardless of the underlying driver.
    
    Args:
        exception: The original exception from the WebDriver implementation.
        
    Returns:
        A WebDriverError with appropriate context information.
    """
    # Extract the original exception name and module for categorization
    exception_type = type(exception).__name__
    exception_module = type(exception).__module__
    
    # Default messages for common error categories
    error_categories = {
        "NoSuchElementException": "Element not found",
        "ElementNotVisibleException": "Element not visible",
        "ElementNotInteractableException": "Element not interactable",
        "StaleElementReferenceException": "Element is stale (page changed)",
        "TimeoutException": "Operation timed out",
        "UnexpectedAlertPresentException": "Unexpected alert present",
        "NoAlertPresentException": "No alert present",
        "NoSuchFrameException": "Frame not found",
        "InvalidSelectorException": "Invalid selector syntax",
        "WebDriverException": "WebDriver error"
    }
    
    # Find the best category match
    category = "Unknown error"
    for error_type, message in error_categories.items():
        if error_type in exception_type:
            category = message
            break
    
    # Create descriptive message
    error_message = f"{category}: {str(exception)}"
    
    # Create and return the mapped error
    return WebDriverError(
        message=error_message,
        driver_type=exception_module.split('.')[-1] if '.' in exception_module else None,
        cause=exception
    )

# STATUS: COMPLETE ✓