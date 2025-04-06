"""Error handling utilities for WebDriver operations."""

import logging
import functools
from typing import Callable, Any

# Assuming WebDriverError is defined in core exceptions
from src.core.exceptions import WebDriverError

# Import specific exceptions from driver libraries if needed for fine-grained mapping
from selenium.common.exceptions import (
    WebDriverException, TimeoutException, NoSuchElementException,
    ElementNotInteractableException, StaleElementReferenceException
    # Add others as needed
)
# Import Playwright exceptions if/when PlaywrightDriver is fully implemented
# try:
#     from playwright.sync_api import Error as PlaywrightError, TimeoutError as PlaywrightTimeoutError
# except ImportError:
#      PlaywrightError = Exception # Base exception fallback
#      PlaywrightTimeoutError = Exception # Base exception fallback


logger = logging.getLogger(__name__)


def map_webdriver_exception(
    exception: Exception,
    context_message: str = "WebDriver operation failed",
    driver_type: Optional[str] = None
) -> WebDriverError:
    """
    Maps a driver-specific exception (e.g., Selenium) to a WebDriverError.

    Logs the original error and returns a standardized WebDriverError.

    Args:
        exception (Exception): The original exception caught from the driver library.
        context_message (str): A message describing the context of the operation.
        driver_type (Optional[str]): The type of driver (e.g., 'selenium', 'playwright').

    Returns:
        WebDriverError: A standardized error wrapping the original exception.
    """
    original_exception_type = type(exception).__name__
    # Use the exception's message directly if available, otherwise use repr
    original_message = str(exception) or repr(exception)

    # Construct the core error message
    error_msg = f"{context_message}: [{original_exception_type}] {original_message}"

    # Log appropriately based on exception type (e.g., warning for common finds)
    # Set log level based on severity - Timeout/NoSuchElement often less severe than others
    log_level = logging.WARNING if isinstance(exception, (NoSuchElementException, TimeoutException)) else logging.ERROR

    # Log with exc_info=False initially to avoid duplicate tracebacks if handled by decorator
    logger.log(log_level, error_msg, exc_info=False)

    # Create and return a WebDriverError, preserving the original cause and adding driver type
    return WebDriverError(error_msg, driver_type=driver_type, cause=exception)


def handle_driver_exceptions(context_message_format: str) -> Callable:
    """
    Decorator factory to wrap WebDriver methods with exception handling.

    Catches common WebDriver exceptions (e.g., Selenium exceptions), logs them,
    and raises a standardized WebDriverError.

    Args:
        context_message_format (str): A format string for the error context message.
                                      Can include placeholders for method arguments
                                      (e.g., "Failed to find element with selector: {selector}").

    Returns:
        Callable: The decorator function.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            driver_instance = args[0] if args and hasattr(args[0], 'browser_type') else None
            driver_type_str = driver_instance.browser_type.value if driver_instance else "unknown"
            func_name = func.__name__

            # Try to format the context message using function arguments
            try:
                # Create a dictionary of arguments, handling potential unbound args
                sig = inspect.signature(func)
                bound_args = sig.bind_partial(*args, **kwargs).arguments
                # Remove 'self' if present
                bound_args.pop('self', None)
                context = context_message_format.format(**bound_args)
            except Exception:
                # Fallback if formatting fails (e.g., unexpected args/kwargs)
                logger.warning(f"Could not format context message for {func_name}. Using raw format.")
                context = context_message_format # Use the raw format string

            try:
                return func(*args, **kwargs)
            # Catch specific, common exceptions first
            except (NoSuchElementException, TimeoutException, ElementNotInteractableException,
                    StaleElementReferenceException) as e:
                # Map these specific exceptions to WebDriverError
                raise map_webdriver_exception(e, context, driver_type_str) from e
            # Catch broader WebDriverException
            except WebDriverException as e:
                 # Catch Selenium's base exception
                raise map_webdriver_exception(e, context, driver_type_str) from e
            # Catch PlaywrightError if/when implemented
            # except PlaywrightError as e:
            #     raise map_webdriver_exception(e, context, "playwright") from e
            # Catch AutoQliq's own WebDriverError (if raised internally by a helper)
            except WebDriverError as e:
                logger.warning(f"Caught existing WebDriverError in {func_name}: {e}")
                raise # Re-raise directly
            # Catch any other unexpected exception during driver operation
            except Exception as e:
                logger.exception(f"Unexpected error during WebDriver operation in {func_name}")
                # Map unexpected errors as well for consistency
                unexpected_context = f"Unexpected error in {func_name}: {context}"
                raise map_webdriver_exception(e, unexpected_context, driver_type_str) from e
        return wrapper
    # Need to import inspect for signature binding
    import inspect
    return decorator