"""Error handling utilities for WebDriver operations."""

import logging
import functools
import inspect
from typing import Callable, Any, Optional, Protocol

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
#     from playwright.sync_api import (
#         Error as PlaywrightError,
#         TimeoutError as PlaywrightTimeoutError
#     )
# except ImportError:
#     PlaywrightError = Exception  # Base exception fallback
#     PlaywrightTimeoutError = Exception  # Base exception fallback


logger = logging.getLogger(__name__)


class IExceptionMapper(Protocol):
    """Interface for mapping driver-specific exceptions to WebDriverError."""

    def map_exception(self,
                     exception: Exception,
                     context_message: str,
                     driver_type: Optional[str] = None) -> WebDriverError:
        """Map a driver-specific exception to a WebDriverError."""
        ...


class IExceptionHandler(Protocol):
    """Interface for handling driver-specific exceptions."""

    def create_handler(self, context_message_format: str) -> Callable:
        """Create a decorator to handle driver-specific exceptions."""
        ...


class StandardExceptionMapper(IExceptionMapper):
    """Standard implementation of IExceptionMapper."""

    def __init__(self):
        """Initialize the mapper with known exception types."""
        # Define which exceptions should be logged as warnings vs errors
        self._warning_exceptions = (
            NoSuchElementException,
            TimeoutException
            # Add others as needed
        )

    def map_exception(self,
                     exception: Exception,
                     context_message: str = "WebDriver operation failed",
                     driver_type: Optional[str] = None) -> WebDriverError:
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
        is_warning_exception = isinstance(exception, self._warning_exceptions)
        log_level = logging.WARNING if is_warning_exception else logging.ERROR

        # Log with exc_info=False initially to avoid duplicate tracebacks if handled by decorator
        logger.log(log_level, error_msg, exc_info=False)

        # Create and return a WebDriverError, preserving the original cause and adding driver type
        return WebDriverError(error_msg, driver_type=driver_type, cause=exception)


# Create a singleton instance of the mapper for backward compatibility
_default_mapper = StandardExceptionMapper()


def map_webdriver_exception(
    exception: Exception,
    context_message: str = "WebDriver operation failed",
    driver_type: Optional[str] = None
) -> WebDriverError:
    """Legacy function that uses the default mapper for backward compatibility."""
    return _default_mapper.map_exception(exception, context_message, driver_type)


class StandardExceptionHandler(IExceptionHandler):
    """Standard implementation of IExceptionHandler."""

    def __init__(self, exception_mapper: Optional[IExceptionMapper] = None):
        """Initialize the handler with an exception mapper."""
        self._mapper = exception_mapper or _default_mapper
        # Define specific exceptions to catch separately
        self._specific_exceptions = (
            NoSuchElementException,
            TimeoutException,
            ElementNotInteractableException,
            StaleElementReferenceException
            # Add others as needed
        )

    def create_handler(self, context_message_format: str) -> Callable:
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
                # Check if first argument is a driver instance with browser_type attribute
                first_arg_index = 0
                has_browser_type = args and hasattr(args[first_arg_index], 'browser_type')
                driver_instance = args[first_arg_index] if has_browser_type else None
                has_driver_instance = driver_instance is not None
                browser_type_value = driver_instance.browser_type.value if has_driver_instance else None
                driver_type_str = browser_type_value or "unknown"
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
                    warning_msg = (f"Could not format context message for {func_name}. "
                                  f"Using raw format.")
                    logger.warning(warning_msg)
                    context = context_message_format # Use the raw format string

                try:
                    return func(*args, **kwargs)
                # Catch specific, common exceptions first
                except self._specific_exceptions as e:
                    # Map these specific exceptions to WebDriverError
                    raise self._mapper.map_exception(e, context, driver_type_str) from e
                # Catch broader WebDriverException
                except WebDriverException as e:
                    # Catch Selenium's base exception
                    raise self._mapper.map_exception(e, context, driver_type_str) from e
                # Catch PlaywrightError if/when implemented
                # except PlaywrightError as e:
                #     raise self._mapper.map_exception(e, context, "playwright") from e
                # Catch AutoQliq's own WebDriverError (if raised internally by a helper)
                except WebDriverError as e:
                    logger.warning(f"Caught existing WebDriverError in {func_name}: {e}")
                    raise # Re-raise directly
                # Catch any other unexpected exception during driver operation
                except Exception as e:
                    logger.exception(f"Unexpected error during WebDriver operation in {func_name}")
                    # Map unexpected errors as well for consistency
                    unexpected_context = f"Unexpected error in {func_name}: {context}"
                    raise self._mapper.map_exception(e, unexpected_context, driver_type_str) from e
            return wrapper
        return decorator


# Create a singleton instance of the handler for backward compatibility
_default_handler = StandardExceptionHandler()


def handle_driver_exceptions(context_message_format: str) -> Callable:
    """Legacy function that uses the default handler for backward compatibility."""
    return _default_handler.create_handler(context_message_format)