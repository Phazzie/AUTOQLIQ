"""Logging utilities for infrastructure layer."""
import functools
import logging
from typing import Any, Callable, TypeVar

# Type variables for better type hinting
T = TypeVar('T') # Represents the return type of the decorated function

def log_method_call(logger: logging.Logger, level: int = logging.DEBUG, log_result: bool = True, log_args: bool = True) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator to log method calls, arguments, and optionally results.

    Args:
        logger (logging.Logger): The logger instance to use.
        level (int): The logging level for call/return messages (e.g., logging.DEBUG).
                     Defaults to logging.DEBUG.
        log_result (bool): Whether to log the return value of the method.
                           Defaults to True. Be cautious with sensitive data.
        log_args (bool): Whether to log the arguments passed to the method.
                         Defaults to True. Be cautious with sensitive data.

    Returns:
        Callable[[Callable[..., T]], Callable[..., T]]: A decorator function.
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            # --- Format Call Info ---
            func_name = func.__name__
            # Check if it's a method (first arg is likely 'self' or 'cls')
            is_method = args and hasattr(args[0], func_name) and callable(getattr(args[0], func_name))
            class_name = args[0].__class__.__name__ if is_method else ""
            full_name = f"{class_name}.{func_name}" if class_name else func_name

            # --- Format Arguments (if requested) ---
            signature = ""
            if log_args:
                start_index = 1 if is_method else 0
                try:
                    # Represent args, handle potential large objects or sensitive data if needed
                    # Be very careful logging args in production if they contain sensitive info
                    args_repr = [repr(a) for a in args[start_index:]]
                except Exception:
                    args_repr = ["<error representing args>"]

                try:
                    kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
                except Exception:
                    kwargs_repr = ["<error representing kwargs>"]

                # Combine args and kwargs
                signature_parts = args_repr + kwargs_repr
                # Truncate long signatures
                max_sig_len = 250
                temp_signature = ", ".join(signature_parts)
                if len(temp_signature) > max_sig_len:
                    signature = temp_signature[:max_sig_len] + "..."
                else:
                    signature = temp_signature

            # --- Log Entry ---
            if log_args:
                logger.log(level, f"Calling: {full_name}({signature})")
            else:
                logger.log(level, f"Calling: {full_name}(...)")


            # --- Execute Original Function ---
            try:
                result = func(*args, **kwargs)
                # --- Log Exit/Result ---
                result_repr = ""
                if log_result:
                    try:
                        # Represent result, handle potential large objects or sensitive data
                        result_repr = repr(result)
                        # Truncate long results if necessary
                        max_repr_len = 200
                        if len(result_repr) > max_repr_len:
                            result_repr = result_repr[:max_repr_len] + "..."
                        result_repr = f" -> {result_repr}" # Add arrow only if logging result
                    except Exception:
                        result_repr = " -> <error representing result>"

                logger.log(level, f"Finished: {full_name}{result_repr}")
                return result
            except Exception as e:
                # --- Log Exception ---
                # Log full traceback for errors
                log_level_exc = logging.ERROR if level < logging.ERROR else level
                logger.log(log_level_exc, f"Exception in {full_name}: {type(e).__name__} - {e}", exc_info=True)
                raise # Re-raise the exception after logging
        return wrapper
    return decorator

# Example Usage:
#
# logger = logging.getLogger(__name__)
#
# class MyClass:
#     @log_method_call(logger)
#     def process_data(self, data: dict, factor: int = 2) -> str:
#         # ... processing ...
#         return f"Processed {len(data)} items with factor {factor}"
#
# instance = MyClass()
# instance.process_data({"a": 1, "b": 2}, factor=3)