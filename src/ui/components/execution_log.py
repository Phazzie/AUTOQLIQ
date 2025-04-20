"""Execution log component for AutoQliq UI."""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Optional, Callable, Any

from src.core.exceptions import UIError
from src.ui.components.ui_component import UIComponent

logger = logging.getLogger(__name__)


class ExecutionLog(UIComponent):
    """
    A component for displaying execution logs.
    
    This component provides a scrolled text widget for displaying logs,
    along with buttons for clearing the log and saving it to a file.
    
    Attributes:
        frame: The main frame containing all widgets
        text: The text widget for displaying logs
        scrollbar: The scrollbar for the text widget
        button_frame: The frame containing the buttons
        clear_button: Button for clearing the log
        save_button: Button for saving the log to a file
    """
    
    def __init__(
        self,
        parent: tk.Widget,
        on_clear: Optional[Callable[[], None]] = None,
        on_save: Optional[Callable[[], None]] = None,
        height: int = 15,
        width: int = 80
    ):
        """
        Initialize an ExecutionLog component.
        
        Args:
            parent: The parent widget
            on_clear: Callback when the clear button is clicked
            on_save: Callback when the save button is clicked
            height: Height of the text widget in lines
            width: Width of the text widget in characters
            
        Raises:
            UIError: If the component cannot be created
        """
        super().__init__(parent)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        try:
            # Create the main frame
            self.frame = ttk.Frame(parent)
            self._widget = self.frame
            
            # Create a label
            label = ttk.Label(self.frame, text="Execution Log:")
            label.pack(side=tk.TOP, anchor=tk.W, pady=(0, 5))
            
            # Create a frame for the text widget and scrollbar
            text_frame = ttk.Frame(self.frame)
            text_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            
            # Create the text widget
            self.text = tk.Text(
                text_frame,
                height=height,
                width=width,
                wrap=tk.WORD,
                state=tk.DISABLED
            )
            self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            # Create the scrollbar
            self.scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.text.yview)
            self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.text.config(yscrollcommand=self.scrollbar.set)
            
            # Create a frame for the buttons
            self.button_frame = ttk.Frame(self.frame)
            self.button_frame.pack(side=tk.TOP, fill=tk.X, pady=(5, 0))
            
            # Create the buttons
            self.clear_button = ttk.Button(
                self.button_frame,
                text="Clear Log",
                command=self._on_clear if on_clear else self.clear
            )
            self.clear_button.pack(side=tk.LEFT, padx=(0, 5))
            
            self.save_button = ttk.Button(
                self.button_frame,
                text="Save Log",
                command=self._on_save if on_save else lambda: None
            )
            self.save_button.pack(side=tk.LEFT)
            
            # Store the callbacks
            self._on_clear_callback = on_clear
            self._on_save_callback = on_save
            
            # Configure text tags for different log levels
            self.text.tag_configure("INFO", foreground="black")
            self.text.tag_configure("DEBUG", foreground="gray")
            self.text.tag_configure("WARNING", foreground="orange")
            self.text.tag_configure("ERROR", foreground="red")
            self.text.tag_configure("CRITICAL", foreground="red", font=("TkDefaultFont", 0, "bold"))
            
            self.logger.debug("ExecutionLog component initialized")
        except Exception as e:
            error_msg = "Failed to create ExecutionLog component"
            self.logger.exception(error_msg)
            raise UIError(error_msg, component_name="ExecutionLog", cause=e) from e
    
    def log(self, message: str, level: str = "INFO") -> None:
        """
        Add a message to the log.
        
        Args:
            message: The message to add
            level: The log level (INFO, DEBUG, WARNING, ERROR, CRITICAL)
            
        Raises:
            UIError: If the message cannot be added
        """
        try:
            # Enable editing
            self.text.config(state=tk.NORMAL)
            
            # Add the message with the appropriate tag
            self.text.insert(tk.END, message + "\n", level)
            
            # Scroll to the end
            self.text.see(tk.END)
            
            # Disable editing
            self.text.config(state=tk.DISABLED)
        except Exception as e:
            error_msg = f"Failed to add message to ExecutionLog: {message}"
            self.logger.exception(error_msg)
            raise UIError(error_msg, component_name="ExecutionLog", cause=e) from e
    
    def clear(self) -> None:
        """
        Clear the log.
        
        Raises:
            UIError: If the log cannot be cleared
        """
        try:
            # Enable editing
            self.text.config(state=tk.NORMAL)
            
            # Clear the text
            self.text.delete(1.0, tk.END)
            
            # Disable editing
            self.text.config(state=tk.DISABLED)
            
            self.logger.debug("Cleared ExecutionLog")
        except Exception as e:
            error_msg = "Failed to clear ExecutionLog"
            self.logger.exception(error_msg)
            raise UIError(error_msg, component_name="ExecutionLog", cause=e) from e
    
    def get_log_text(self) -> str:
        """
        Get the current log text.
        
        Returns:
            The log text
            
        Raises:
            UIError: If the log text cannot be retrieved
        """
        try:
            return self.text.get(1.0, tk.END)
        except Exception as e:
            error_msg = "Failed to get log text from ExecutionLog"
            self.logger.exception(error_msg)
            raise UIError(error_msg, component_name="ExecutionLog", cause=e) from e
    
    def _on_clear(self) -> None:
        """Handle clicks on the clear button."""
        try:
            # Clear the log
            self.clear()
            
            # Call the callback
            if self._on_clear_callback:
                self._on_clear_callback()
        except Exception as e:
            self.logger.error(f"Error handling clear button click: {e}")
    
    def _on_save(self) -> None:
        """Handle clicks on the save button."""
        try:
            if self._on_save_callback:
                self._on_save_callback()
        except Exception as e:
            self.logger.error(f"Error handling save button click: {e}")
