"""Error handling utilities for infrastructure layer."""
import functools
import logging
from typing import Any, Callable, Type, TypeVar, Tuple, Optional

# Assuming AutoQliqError and potentially other specific core errors are defined
from src.core.exceptions import AutoQliqError, RepositoryError, WebDriverError, ConfigError, SerializationError, ValidationError # Add others as needed

# Type variables for better type hinting
T = TypeVar('T') # Represents the return type of the decorated function
E = TypeVar('E', bound=AutoQliqError) # Represents the specific AutoQliqError subclass to raise

logger = logging.getLogger(__name__)

def handle_exceptions(
    error_class: Type[E],
    context_message: str,
    log_level: int = logging.ERROR,
    reraise_types: Optional[Tuple[Type[Exception], ...]] = None
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator to catch exceptions, log them, and wrap them in a specified AutoQliqError subclass.

    Args:
        error_class (Type[E]): The AutoQliqError subclass to raise (e.g., RepositoryError).
        context_message (str): A descriptive message of the operation context where the error occurred.
                               This message will prefix the original error message.
        log_level (int): The logging level to use when an exception is caught (e.g., logging.ERROR).
                         Defaults to logging.ERROR.
        reraise_types (Optional[Tuple[Type[Exception], ...]]): A tuple of exception types that should be
                                                               re-raised directly without wrapping.
                                                               By default, includes AutoQliqError and its subclasses.

    Returns:
        Callable[[Callable[..., T]], Callable[..., T]]: A decorator function.
    """
    # Default types to re-raise directly: the target error_class and any AutoQliqError
    # This prevents double-wrapping of already specific domain errors.
    if reraise_types is None:
        default_reraise = (AutoQliqError,)
    else:
        # Ensure AutoQliqError is always included unless explicitly excluded
        if not any(issubclass(rt, AutoQliqError) or rt == AutoQliqError for rt in reraise_types):
             reraise_types = reraise_types + (AutoQliqError,)
        default_reraise = reraise_types


    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return func(*args, **kwargs)
            except default_reraise as e:
                # Re-raise specified exception types directly (includes AutoQliqError and its children by default)
                # Log it first for visibility only if it hasn't likely been logged deeper
                if log_level <= logger.getEffectiveLevel(): # Check if logging is enabled at this level
                    logger.log(log_level, f"Re-raising existing {type(e).__name__} from {func.__name__}: {e}")
                raise
            except Exception as e:
                # Format the error message including context and original error
                # Ensure cause message is included
                cause_msg = str(e) if str(e) else type(e).__name__
                formatted_msg = f"{context_message}: {type(e).__name__} - {cause_msg}"
                # Log the error with traceback for unexpected exceptions
                logger.log(log_level, f"Error in {func.__name__}: {formatted_msg}", exc_info=True)
                # Create and raise the new wrapped exception
                raise error_class(formatted_msg, cause=e) from e
        return wrapper
    return decorator

# Example Usage:
#
# from src.core.exceptions import RepositoryError
#
# @handle_exceptions(RepositoryError, "Failed to load entity from file")
# def load_from_file(file_path: str) -> dict:
#     # ... file loading logic that might raise IOError, json.JSONDecodeError etc. ...
#     pass
#
# @handle_exceptions(WebDriverError, "Failed to click element", reraise_types=(TimeoutException,)) # Reraise Timeout directly
# def click_button(selector: str):
#     # ... webdriver logic ... WebDriverError will still be re-raised directly by default
#     pass