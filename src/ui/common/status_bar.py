"""Status bar component for AutoQliq UI."""
import tkinter as tk
from tkinter import ttk
import logging
from typing import Optional

# Assuming UIFactory is in src/ui/common/ui_factory.py
from src.ui.common.ui_factory import UIFactory
from src.core.exceptions import UIError

logger = logging.getLogger(__name__)

class StatusBar:
    """
    A status bar component for displaying status messages and optional progress.

    Manages its own frame and internal widgets (label, progress bar).

    Attributes:
        frame (ttk.Frame): The main frame widget for the status bar.
        message_label (ttk.Label): Label to display status messages.
        progress_bar (Optional[ttk.Progressbar]): Optional progress bar widget.
    """

    def __init__(
        self,
        parent: tk.Widget,
        show_progress: bool = True,
        initial_message: str = "Ready"
    ):
        """
        Initialize the StatusBar.

        Args:
            parent: The parent widget (usually the root window or a main frame).
            show_progress: Whether to include a progress bar widget.
            initial_message: The message to display initially.

        Raises:
            UIError: If the component cannot be created.
        """
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.debug("Initializing StatusBar.")
        try:
            # Use FLAT or SUNKEN relief for status bar frame usually looks better
            # Reduce padding for a more compact status bar look
            self.frame = UIFactory.create_frame(parent, padding="3 1 3 1", relief=tk.SUNKEN, borderwidth=1)
            # Add a marker attribute for easy identification by BaseView._find_status_bar
            setattr(self.frame, '_is_status_bar_frame', True)
            setattr(parent, 'status_bar_instance', self) # Store ref on parent (e.g. root window)

            self._message_var = tk.StringVar(value=initial_message)

            # Create the message label
            self.message_label = UIFactory.create_label(
                self.frame,
                textvariable=self._message_var,
                anchor=tk.W # Left align text
            )
            self.message_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=0)

            # Create the progress bar if requested
            self.progress_bar: Optional[ttk.Progressbar] = None
            if show_progress:
                self.progress_bar = ttk.Progressbar(
                    self.frame,
                    orient=tk.HORIZONTAL,
                    mode="determinate", # Start in determinate mode
                    length=100 # Relative length
                )
                self.progress_bar.pack(side=tk.RIGHT, padx=5, pady=1)
                self.logger.debug("Progress bar created.")
            else:
                self.logger.debug("Progress bar skipped.")

            self.logger.debug("StatusBar initialized successfully.")
        except Exception as e:
            error_msg = "Failed to create StatusBar"
            self.logger.exception(error_msg) # Log with traceback
            raise UIError(error_msg, component_name="StatusBar", cause=e) from e

    def set_message(self, message: str) -> None:
        """Set the status message displayed in the label."""
        try:
            self._message_var.set(str(message))
            # self.logger.debug(f"Status message set: {message}") # Can be noisy
        except Exception as e:
            self.logger.error(f"Failed to set status message to '{message}': {e}")

    def get_message(self) -> str:
        """Get the current status message."""
        return self._message_var.get()

    def set_progress(self, value: float) -> None:
        """Set the progress value (0-100) for the determinate progress bar."""
        if not self.progress_bar: return
        try:
            if self.progress_bar.cget('mode') != 'determinate':
                 self.progress_bar.config(mode='determinate')
            clamped_value = max(0.0, min(100.0, float(value)))
            self.progress_bar['value'] = clamped_value
        except Exception as e:
            self.logger.error(f"Failed to set progress value to {value}: {e}")

    def start_progress_indeterminate(self, speed_ms: int = 10) -> None:
        """Start the progress bar in indeterminate (pulsing) mode."""
        if not self.progress_bar: return
        try:
            self.progress_bar.config(mode='indeterminate')
            self.progress_bar.start(speed_ms)
            self.logger.debug("Indeterminate progress started.")
        except Exception as e:
            self.logger.error(f"Failed to start indeterminate progress: {e}")

    def stop_progress(self) -> None:
        """Stop the progress bar (both determinate and indeterminate)."""
        if not self.progress_bar: return
        try:
            self.progress_bar.stop()
            self.progress_bar.config(mode='determinate')
            self.progress_bar['value'] = 0
            self.logger.debug("Progress stopped and reset.")
        except Exception as e:
            self.logger.error(f"Failed to stop progress: {e}")