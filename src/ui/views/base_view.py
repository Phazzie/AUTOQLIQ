"""Base view class for AutoQliq UI."""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import logging
from typing import Optional, Any

from src.ui.interfaces.view import IView
from src.ui.common.error_handler import ErrorHandler
from src.ui.common.status_bar import StatusBar # Import StatusBar

class BaseView(IView):
    """
    Base class for all view components in the application.

    Provides common functionality like holding the root widget, presenter reference,
    logger, error handler, status bar integration, and basic UI interaction methods.

    Attributes:
        root (tk.Widget): The parent widget for this view (e.g., a tab frame).
        presenter (Any): The presenter associated with this view.
        logger (logging.Logger): Logger instance for the view subclass.
        error_handler (ErrorHandler): Utility for displaying errors.
        main_frame (ttk.Frame): The primary frame holding the view's specific content.
        status_bar (Optional[StatusBar]): Reference to the status bar instance (shared via root).
    """
    def __init__(self, root: tk.Widget, presenter: Any):
        """
        Initialize the BaseView.

        Args:
            root (tk.Widget): The parent widget (e.g., a frame within a tab).
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
        self.status_bar: Optional[StatusBar] = None # Initialize status_bar attribute

        # --- Main Frame Setup ---
        # This frame fills the parent widget (e.g., the tab frame provided by main_ui)
        # Subclasses will add their widgets to this frame.
        self.main_frame = ttk.Frame(self.root, padding="5")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Find the status bar - assumes status bar is attached to the toplevel window
        # and registered on it by main_ui.py
        self._find_status_bar()

        self.logger.debug(f"{self.__class__.__name__} initialized.")

    def _find_status_bar(self):
        """Tries to find a StatusBar instance attached to the toplevel window."""
        try:
             toplevel = self.main_frame.winfo_toplevel() # Get the main Tk window
             if hasattr(toplevel, 'status_bar_instance') and isinstance(toplevel.status_bar_instance, StatusBar):
                  self.status_bar = toplevel.status_bar_instance
                  self.logger.debug("Found StatusBar instance on toplevel window.")
             else:
                  self.logger.warning("StatusBar instance not found on toplevel window.")
        except Exception as e:
             self.logger.warning(f"Could not find status bar: {e}")


    @property
    def widget(self) -> tk.Widget:
        """Returns the main content widget managed by this view (the main_frame)."""
        return self.main_frame

    def display_error(self, title: str, message: str) -> None:
        """Display an error message box."""
        self.logger.warning(f"Displaying error: Title='{title}', Message='{message}'")
        try:
            parent_window = self.main_frame.winfo_toplevel()
            messagebox.showerror(title, message, parent=parent_window)
        except Exception as e:
             self.logger.error(f"Failed to display error message box: {e}")
        # Also update status bar
        self.set_status(f"Error: {message[:100]}")

    def display_message(self, title: str, message: str) -> None:
        """Display an informational message box."""
        self.logger.info(f"Displaying message: Title='{title}', Message='{message}'")
        try:
            parent_window = self.main_frame.winfo_toplevel()
            messagebox.showinfo(title, message, parent=parent_window)
            self.set_status(message)
        except Exception as e:
            self.logger.error(f"Failed to display info message box: {e}")

    def confirm_action(self, title: str, message: str) -> bool:
        """Display a confirmation dialog and return the user's choice."""
        self.logger.debug(f"Requesting confirmation: Title='{title}', Message='{message}'")
        try:
            parent_window = self.main_frame.winfo_toplevel()
            response = messagebox.askyesno(title, message, parent=parent_window)
            self.logger.debug(f"Confirmation response: {response}")
            return response
        except Exception as e:
             self.logger.error(f"Failed to display confirmation dialog: {e}")
             return False

    def prompt_for_input(self, title: str, prompt: str, initial_value: str = "") -> Optional[str]:
        """Display a simple input dialog and return the user's input."""
        self.logger.debug(f"Requesting input: Title='{title}', Prompt='{prompt}'")
        try:
            parent_window = self.main_frame.winfo_toplevel()
            result = simpledialog.askstring(title, prompt, initialvalue=initial_value, parent=parent_window)
            log_result = '<cancelled>' if result is None else '<input provided>'
            self.logger.debug(f"Input dialog result: {log_result}")
            return result
        except Exception as e:
             self.logger.error(f"Failed to display input dialog: {e}")
             return None

    def set_status(self, message: str) -> None:
        """Update the status bar message."""
        if not self.status_bar: self._find_status_bar() # Try finding again

        if self.status_bar:
            # Schedule the update using 'after' to ensure it runs on the main thread
            try:
                 if self.status_bar.frame.winfo_exists():
                      self.status_bar.frame.after(0, lambda msg=message: self.status_bar.set_message(msg))
                 else: self.logger.warning("StatusBar frame no longer exists.")
            except Exception as e: self.logger.error(f"Failed to schedule status update: {e}")
        else: self.logger.debug(f"Status update requested (no status bar found): {message}")


    def clear(self) -> None:
        """Clear or reset the view's state. Needs implementation in subclasses."""
        self.logger.debug(f"Base clear called for {self.__class__.__name__}.")
        self.set_status("Ready.") # Reset status bar
        if self.status_bar:
            try:
                 if self.status_bar.frame.winfo_exists():
                      self.status_bar.frame.after(0, self.status_bar.stop_progress)
            except Exception as e: self.logger.error(f"Error stopping progress bar during clear: {e}")


    def update(self) -> None:
        """Force an update of the UI. Generally not needed unless managing complex state."""
        try:
             # Use the main_frame's toplevel window for update_idletasks
             toplevel = self.main_frame.winfo_toplevel()
             if toplevel.winfo_exists():
                  toplevel.update_idletasks()
                  # self.logger.debug(f"Base update called for {self.__class__.__name__}.") # Can be noisy
        except Exception as e:
             self.logger.error(f"Error during UI update: {e}")