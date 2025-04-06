"""Status bar component for AutoQliq UI."""
import tkinter as tk
from tkinter import ttk
from typing import Optional

from src.core.exceptions import UIError
from src.ui.common.ui_factory import UIFactory


class StatusBar:
    """A status bar component for displaying status messages.
    
    This component provides a status bar with a message label and optional progress bar.
    
    Attributes:
        frame: The frame containing the status bar
        message_label: The label for displaying status messages
        progress_bar: The progress bar for displaying progress
    """
    
    def __init__(
        self, 
        parent: tk.Widget, 
        show_progress: bool = True,
        initial_message: str = "Ready"
    ):
        """Initialize a StatusBar.
        
        Args:
            parent: The parent widget
            show_progress: Whether to show a progress bar
            initial_message: The initial status message
            
        Raises:
            UIError: If the component cannot be created
        """
        try:
            # Create the frame
            self.frame = UIFactory.create_frame(parent)
            
            # Create the message label
            self.message_label = UIFactory.create_label(self.frame, text=initial_message)
            self.message_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=2)
            
            # Create the progress bar if requested
            self.progress_bar = None
            if show_progress:
                self.progress_bar = ttk.Progressbar(
                    self.frame, 
                    mode="determinate", 
                    length=100
                )
                self.progress_bar.pack(side=tk.RIGHT, padx=5, pady=2)
        except Exception as e:
            error_msg = "Failed to create StatusBar"
            raise UIError(error_msg, component_name="StatusBar", cause=e)
    
    def set_message(self, message: str) -> None:
        """Set the status message.
        
        Args:
            message: The status message to display
            
        Raises:
            UIError: If the message cannot be set
        """
        try:
            self.message_label.config(text=message)
            
            # Update the UI
            self.frame.update_idletasks()
        except Exception as e:
            error_msg = f"Failed to set status message: {message}"
            raise UIError(error_msg, component_name="StatusBar", cause=e)
    
    def set_progress(self, value: float) -> None:
        """Set the progress value.
        
        Args:
            value: The progress value (0-100)
            
        Raises:
            UIError: If the progress cannot be set
        """
        if not self.progress_bar:
            return
        
        try:
            # Ensure the value is within range
            value = max(0, min(100, value))
            
            # Set the progress value
            self.progress_bar["value"] = value
            
            # Update the UI
            self.frame.update_idletasks()
        except Exception as e:
            error_msg = f"Failed to set progress value: {value}"
            raise UIError(error_msg, component_name="StatusBar", cause=e)
    
    def start_progress(self) -> None:
        """Start the progress bar in indeterminate mode.
        
        Raises:
            UIError: If the progress bar cannot be started
        """
        if not self.progress_bar:
            return
        
        try:
            # Set the progress bar to indeterminate mode
            self.progress_bar.config(mode="indeterminate")
            
            # Start the progress bar
            self.progress_bar.start()
            
            # Update the UI
            self.frame.update_idletasks()
        except Exception as e:
            error_msg = "Failed to start progress bar"
            raise UIError(error_msg, component_name="StatusBar", cause=e)
    
    def stop_progress(self) -> None:
        """Stop the progress bar.
        
        Raises:
            UIError: If the progress bar cannot be stopped
        """
        if not self.progress_bar:
            return
        
        try:
            # Stop the progress bar
            self.progress_bar.stop()
            
            # Set the progress bar back to determinate mode
            self.progress_bar.config(mode="determinate")
            
            # Reset the progress value
            self.progress_bar["value"] = 0
            
            # Update the UI
            self.frame.update_idletasks()
        except Exception as e:
            error_msg = "Failed to stop progress bar"
            raise UIError(error_msg, component_name="StatusBar", cause=e)
