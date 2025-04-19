"""Base presenter class for AutoQliq UI."""
import logging
import functools
from typing import Any, Optional, Dict, List, Callable, TypeVar, Generic

from src.core.exceptions import AutoQliqError, ValidationError
from src.ui.common.error_handler import ErrorHandler
from src.ui.interfaces.presenter import IPresenter
# Import base view interface for type hinting
from src.ui.interfaces.view import IView

# Type variable for the view type
V = TypeVar('V', bound=IView)


class BasePresenter(Generic[V], IPresenter):
    """Base class for all presenters.

    Provides common functionality like view management, logging, and error handling.

    Attributes:
        _view: The view component associated with this presenter. Use property `view`.
        logger: Logger instance specific to the presenter subclass.
        error_handler: Handler for logging and potentially showing errors in the view.
    """

    def __init__(self, view: Optional[V] = None):
        """Initialize a BasePresenter.

        Args:
            view: The view component (optional at init, can be set later).
        """
        self._view: Optional[V] = view
        self.logger = logging.getLogger(f"presenter.{self.__class__.__name__}")
        # ErrorHandler can use the same logger or a dedicated one
        self.error_handler = ErrorHandler(self.logger)
        self.logger.debug(f"{self.__class__.__name__} initialized.")

    @property
    def view(self) -> Optional[V]:
        """Get the associated view instance."""
        return self._view

    def set_view(self, view: V) -> None:
        """Set the view component associated with this presenter.

        Args:
            view: The view component instance.
        """
        if not isinstance(view, IView):
            # Basic check, could be more specific if V had stricter bounds
            raise TypeError("View must implement the IView interface.")
        self._view = view
        self.logger.debug(f"View {type(view).__name__} set for presenter {self.__class__.__name__}")
        # Optionally call initialize_view after setting
        # self.initialize_view()

    def initialize_view(self) -> None:
        """Initialize the view with data. Should be overridden by subclasses."""
        self.logger.debug(f"Base initialize_view called for {self.__class__.__name__}. Subclass should implement.")
        pass # Subclasses override to populate view on startup or after view is set

    def _handle_error(self, error: Exception, context: str) -> None:
        """Internal helper to handle errors using the error_handler and update the view."""
        self.error_handler.handle_error(error, context, show_message=False) # Log first

        # Show the error in the view if available
        if self.view:
             # Extract a user-friendly title and message
             title = "Error"
             message = str(error)
             if isinstance(error, AutoQliqError):
                 # Use more specific titles for known error types
                 error_type_name = type(error).__name__.replace("Error", " Error") # Add space
                 title = error_type_name
             elif isinstance(error, FileNotFoundError):
                 title = "File Not Found"
             elif isinstance(error, PermissionError):
                 title = "Permission Error"
             else: # Unexpected errors
                 title = "Unexpected Error"
                 message = f"An unexpected error occurred: {message}"

             try:
                self.view.display_error(title, message)
             except Exception as view_e:
                  self.logger.error(f"Failed to display error in view: {view_e}")
        else:
             self.logger.warning(f"Cannot display error in view (view not set) for context: {context}")

    # Optional: Decorator within the base class for convenience
    @classmethod
    def handle_errors(cls, context: str) -> Callable[[Callable], Callable]:
        """
        Class method decorator to automatically handle errors in presenter methods.

        Logs errors and displays them in the associated view (if set).

        Args:
            context: Description of the operation being performed (for error messages).

        Returns:
            A decorator.
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(presenter_instance: 'BasePresenter', *args, **kwargs) -> Any:
                try:
                    # Execute the original presenter method
                    return func(presenter_instance, *args, **kwargs)
                except Exception as e:
                    # Use the instance's error handling method
                    presenter_instance._handle_error(e, context)
                    # Decide what to return on error. Often None or False for actions.
                    # Returning None might require callers to check.
                    # Returning False might be suitable for boolean methods.
                    # Re-raising might be needed if the caller needs to react specifically.
                    # Defaulting to returning None here.
                    return None # Or False, or re-raise specific types if needed
            return wrapper
        return decorator