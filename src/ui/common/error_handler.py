"""Error handler for UI components."""
import logging
import tkinter as tk
from tkinter import messagebox
from typing import Optional, Callable, Dict, Any, List, Union

from src.core.exceptions import AutoQliqError, UIError, WorkflowError, CredentialError, WebDriverError, ValidationError


class ErrorHandler:
    """Handler for UI errors.

    This class provides methods for handling errors in UI components,
    including logging and displaying messages to the user.
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize an ErrorHandler.

        Args:
            logger: The logger to use for logging errors. If None, creates a default logger.
        """
        self.logger = logger or logging.getLogger(__name__)
        self.logger.debug("ErrorHandler initialized.")

    def handle_error(
        self,
        error: Exception,
        context: str,
        show_message: bool = True,
        parent: Optional[tk.Widget] = None,
        callback: Optional[Callable[[Exception], None]] = None
    ) -> None:
        """Handle a generic error, log it, and optionally show it to the user.

        Args:
            error: The error exception instance.
            context: A string describing the context where the error occurred (e.g., "loading workflow").
            show_message: If True, display an error message box to the user.
            parent: The parent widget for the message box (optional).
            callback: An optional callback function to execute after handling the error.
        """
        self.logger.debug(f"Handling error in context: {context}")
        # Log the error
        self._log_error(error, context)

        # Show a message box if requested
        if show_message:
            self._show_error_message(error, context, parent)

        # Execute the callback if provided
        if callback:
            try:
                 callback(error)
            except Exception as cb_e:
                 self.logger.error(f"Error executing error handler callback for context '{context}': {cb_e}", exc_info=True)

    def _log_error(self, error: Exception, context: str) -> None:
        """Log an error with appropriate level and context."""
        error_type = type(error).__name__
        # Use full formatted message from custom exceptions if available
        error_message = str(error) if isinstance(error, AutoQliqError) else f"{error_type}: {str(error)}"

        log_level = logging.ERROR # Default log level

        # Adjust log level for less severe or expected errors if needed
        if isinstance(error, ValidationError):
            log_level = logging.WARNING
        # Add other specific error types if needed

        # Use exc_info=True for unexpected errors to get traceback
        log_exc_info = not isinstance(error, AutoQliqError)

        self.logger.log(log_level, f"Error in {context}: {error_message}", exc_info=log_exc_info)

    def _show_error_message(self, error: Exception, context: str, parent: Optional[tk.Widget] = None) -> None:
        """Show a user-friendly error message box."""
        error_type = type(error).__name__
        error_message = str(error) # Use the formatted message from the exception

        # Create a user-friendly title and detailed message
        title = "Error"
        detailed_message = f"An error occurred while {context}.\n\nDetails:\n{error_message}"

        if isinstance(error, UIError):
            title = "UI Error"
        elif isinstance(error, WorkflowError):
            title = "Workflow Error"
        elif isinstance(error, CredentialError):
            title = "Credential Error"
        elif isinstance(error, WebDriverError):
            title = "Web Driver Error"
        elif isinstance(error, ConfigError):
             title = "Configuration Error"
        elif isinstance(error, SerializationError):
             title = "Data Error"
        elif isinstance(error, ValidationError):
             title = "Validation Error"
             detailed_message = f"Invalid input detected while {context}.\n\nDetails:\n{error_message}"
        elif isinstance(error, FileNotFoundError):
            title = "File Not Found"
            detailed_message = f"Could not find a required file while {context}.\n\nDetails:\n{error_message}"
        elif isinstance(error, PermissionError):
             title = "Permission Error"
             detailed_message = f"Permission denied while {context}.\n\nDetails:\n{error_message}"
        elif not isinstance(error, AutoQliqError):
            title = "Unexpected Error"
            detailed_message = f"An unexpected error occurred while {context}.\nPlease report this issue.\n\nDetails:\n{error_message}"

        # Show the message box
        try:
            messagebox.showerror(title, detailed_message, parent=parent)
        except Exception as mb_e:
             self.logger.error(f"Failed to show error messagebox: {mb_e}")

    def handle_validation_errors(
        self,
        errors: Dict[str, List[str]],
        context: str = "validating form",
        parent: Optional[tk.Widget] = None,
        callback: Optional[Callable[[Dict[str, List[str]]], None]] = None
    ) -> None:
        """Handle validation errors, typically from a form.

        Args:
            errors: A dictionary where keys are field names and values are lists of error messages.
            context: Description of the validation context.
            parent: The parent widget for the message box.
            callback: An optional callback to execute after handling the errors.
        """
        if not errors:
            return

        # Log the errors
        self.logger.warning(f"Validation errors occurred during {context}: {errors}")

        # Create a user-friendly message
        message = "Please correct the following errors:\n"
        for field_name, field_errors in errors.items():
             error_list = "\n - ".join(field_errors)
             message += f"\n{field_name.replace('_', ' ').title()}:\n - {error_list}"

        # Show the message box
        try:
            messagebox.showwarning("Validation Failed", message, parent=parent)
        except Exception as mb_e:
            self.logger.error(f"Failed to show validation error messagebox: {mb_e}")

        # Execute the callback if provided
        if callback:
            try:
                 callback(errors)
            except Exception as cb_e:
                 self.logger.error(f"Error executing validation error callback for context '{context}': {cb_e}", exc_info=True)

    @staticmethod
    def decorate_with_error_handling(
        logger: logging.Logger,
        context_format: Optional[str] = None # Optional format string for context
    ) -> Callable[[Callable], Callable]:
        """Decorator factory for handling errors in UI methods (e.g., event handlers).

        Args:
            logger: The logger instance to use.
            context_format: An optional format string for the context message.
                            If None, defaults to the function name. Can include
                            placeholders like {arg_name}.

        Returns:
            A decorator function.

        Example:
            ```python
            logger = logging.getLogger(__name__)
            handler = ErrorHandler(logger)

            @handler.decorate_with_error_handling(logger, "processing item {item_id}")
            def process_item(self, item_id: int):
                # Method implementation
            ```
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                # Determine context string
                context = context_format
                if context is None:
                    context = func.__name__ # Default context is function name
                else:
                     try:
                         # Try to format using available args/kwargs
                         sig = inspect.signature(func)
                         bound_args = sig.bind_partial(*args, **kwargs).arguments
                         context = context_format.format(**bound_args)
                     except Exception:
                         logger.warning(f"Could not format error context '{context_format}' for {func.__name__}. Using raw string.")
                         context = context_format # Fallback to raw format string

                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    # Create an error handler instance to handle the error
                    # Assumes 'self' is the first arg if it's a method, or uses module logger otherwise
                    instance_logger = getattr(args[0], 'logger', logger) if args else logger
                    handler = ErrorHandler(instance_logger or logger) # Use instance logger if available

                    # Handle the error using the instance's handler
                    handler.handle_error(e, context)

                    # Decide whether to re-raise or return a default value (e.g., None)
                    # Generally, for UI event handlers, swallowing the exception after logging/showing message is okay.
                    # For methods expected to return a value, re-raising might be better.
                    # Let's default to not re-raising for UI handlers.
                    return None # Or re-raise if necessary: raise
            # Need inspect for signature binding
            import inspect
            return wrapper
        return decorator