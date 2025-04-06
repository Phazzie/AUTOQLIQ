"""Base view class for AutoQliq UI."""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import logging
from typing import Optional, Any

from src.ui.interfaces.view import IView
from src.ui.common.error_handler import ErrorHandler

class BaseView(IView):
    """
    Base class for all view components in the application.

    Provides common functionality like holding the root widget, presenter reference,
    logger, error handler, and basic UI interaction methods.

    Attributes:
        root (tk.Widget): The parent widget for this view.
        presenter (Any): The presenter associated with this view.
        logger (logging.Logger): Logger instance for the view subclass.
        error_handler (ErrorHandler): Utility for displaying errors.
        main_frame (ttk.Frame): The primary frame holding the view's content.
    """
    def __init__(self, root: tk.Widget, presenter: Any):
        """
        Initialize the BaseView.

        Args:
            root (tk.Widget): The parent widget (e.g., root window, notebook tab).
            presenter (Any): The presenter instance handling the logic for this view.
        """
        if root is None:
            raise ValueError("Root widget cannot be None for BaseView.")
        if presenter is None:
             raise ValueError("Presenter cannot be None for BaseView.")

        self.root = root
        self.presenter = presenter
        self.logger = logging.getLogger(f"view.{self.__class__.__name__}")
        self.error_handler = ErrorHandler(self.logger)

        # Create the main frame where subclasses will place their widgets
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.logger.debug(f"{self.__class__.__name__} initialized.")

    @property
    def widget(self) -> tk.Widget:
        """Returns the main widget managed by this view (the main_frame)."""
        return self.main_frame

    def display_error(self, title: str, message: str) -> None:
        """Display an error message box."""
        self.logger.warning(f"Displaying error: Title='{title}', Message='{message}'")
        messagebox.showerror(title, message, parent=self.root)

    def display_message(self, title: str, message: str) -> None:
        """Display an informational message box."""
        self.logger.info(f"Displaying message: Title='{title}', Message='{message}'")
        messagebox.showinfo(title, message, parent=self.root)

    def confirm_action(self, title: str, message: str) -> bool:
        """Display a confirmation dialog and return the user's choice."""
        self.logger.debug(f"Requesting confirmation: Title='{title}', Message='{message}'")
        response = messagebox.askyesno(title, message, parent=self.root)
        self.logger.debug(f"Confirmation response: {response}")
        return response

    def prompt_for_input(self, title: str, prompt: str, initial_value: str = "") -> Optional[str]:
        """Display a simple input dialog and return the user's input."""
        self.logger.debug(f"Requesting input: Title='{title}', Prompt='{prompt}'")
        result = simpledialog.askstring(title, prompt, initialvalue=initial_value, parent=self.root)
        self.logger.debug(f"Input dialog result: {'<cancelled>' if result is None else '<input provided>'}")
        return result

    def set_status(self, message: str) -> None:
        """Update the status bar message (if a status bar exists)."""
        # Base implementation does nothing. Subclasses or the main window
        # should override or provide a way to access a shared status bar.
        self.logger.debug(f"Status update requested (not implemented in BaseView): {message}")
        pass

    def clear(self) -> None:
        """Clear or reset the view's state. Needs implementation in subclasses."""
        self.logger.debug(f"Base clear called for {self.__class__.__name__}.")
        # Subclasses should clear their specific widgets (listboxes, entries, etc.)
        pass

    def update(self) -> None:
        """Force an update of the UI. Generally not needed unless managing complex state."""
        self.root.update_idletasks()
        self.logger.debug(f"Base update called for {self.__class__.__name__}.")
        pass