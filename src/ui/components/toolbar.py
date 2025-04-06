"""Toolbar component for AutoQliq UI."""
import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, List, Optional, Callable, Union

from src.core.exceptions import UIError
from src.ui.common.ui_factory import UIFactory


class Toolbar:
    """A toolbar component for displaying buttons.
    
    This component provides a toolbar with buttons for common actions.
    
    Attributes:
        frame: The frame containing the toolbar
        buttons: A dictionary of button names and widgets
    """
    
    def __init__(
        self, 
        parent: tk.Widget, 
        buttons: List[Dict[str, Any]],
        orientation: str = tk.HORIZONTAL
    ):
        """Initialize a Toolbar.
        
        Args:
            parent: The parent widget
            buttons: A list of button definitions
            orientation: The orientation of the toolbar (HORIZONTAL, VERTICAL)
            
        Raises:
            UIError: If the component cannot be created
            
        Example:
            ```python
            buttons = [
                {"name": "new", "text": "New", "command": create_new},
                {"name": "open", "text": "Open", "command": open_file},
                {"name": "save", "text": "Save", "command": save_file}
            ]
            toolbar = Toolbar(parent, buttons)
            ```
        """
        try:
            # Create the frame
            self.frame = UIFactory.create_frame(parent)
            
            # Create a dictionary to store the buttons
            self.buttons: Dict[str, ttk.Button] = {}
            
            # Create the buttons
            for button in buttons:
                # Get the button properties
                name = button.get("name", "button")
                text = button.get("text", name.capitalize())
                command = button.get("command", lambda: None)
                width = button.get("width")
                state = button.get("state", tk.NORMAL)
                
                # Create the button
                btn = UIFactory.create_button(
                    self.frame, 
                    text=text, 
                    command=command,
                    width=width,
                    state=state
                )
                
                # Pack the button
                if orientation == tk.HORIZONTAL:
                    btn.pack(side=tk.LEFT, padx=2, pady=2)
                else:
                    btn.pack(side=tk.TOP, padx=2, pady=2)
                
                # Store the button
                self.buttons[name] = btn
        except Exception as e:
            error_msg = "Failed to create Toolbar"
            raise UIError(error_msg, component_name="Toolbar", cause=e)
    
    def get_button(self, name: str) -> Optional[ttk.Button]:
        """Get a button by name.
        
        Args:
            name: The name of the button
            
        Returns:
            The button widget, or None if not found
        """
        return self.buttons.get(name)
    
    def enable_button(self, name: str) -> None:
        """Enable a button.
        
        Args:
            name: The name of the button
            
        Raises:
            UIError: If the button cannot be enabled
        """
        button = self.get_button(name)
        if button:
            try:
                button.config(state=tk.NORMAL)
            except Exception as e:
                error_msg = f"Failed to enable button: {name}"
                raise UIError(error_msg, component_name="Toolbar", cause=e)
    
    def disable_button(self, name: str) -> None:
        """Disable a button.
        
        Args:
            name: The name of the button
            
        Raises:
            UIError: If the button cannot be disabled
        """
        button = self.get_button(name)
        if button:
            try:
                button.config(state=tk.DISABLED)
            except Exception as e:
                error_msg = f"Failed to disable button: {name}"
                raise UIError(error_msg, component_name="Toolbar", cause=e)
    
    def set_button_text(self, name: str, text: str) -> None:
        """Set the text of a button.
        
        Args:
            name: The name of the button
            text: The text to set
            
        Raises:
            UIError: If the button text cannot be set
        """
        button = self.get_button(name)
        if button:
            try:
                button.config(text=text)
            except Exception as e:
                error_msg = f"Failed to set button text: {name}"
                raise UIError(error_msg, component_name="Toolbar", cause=e)
    
    def set_button_command(self, name: str, command: Callable[[], None]) -> None:
        """Set the command of a button.
        
        Args:
            name: The name of the button
            command: The command to set
            
        Raises:
            UIError: If the button command cannot be set
        """
        button = self.get_button(name)
        if button:
            try:
                button.config(command=command)
            except Exception as e:
                error_msg = f"Failed to set button command: {name}"
                raise UIError(error_msg, component_name="Toolbar", cause=e)
