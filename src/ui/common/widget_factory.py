"""Factory for creating basic UI widgets.

This module provides a factory for creating basic UI widgets with consistent styling.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, Dict, Any, List, Union

from src.core.exceptions import UIError


class WidgetFactory:
    """Factory for creating basic UI widgets.
    
    This class provides methods for creating basic UI widgets with consistent
    styling and behavior.
    """
    
    @staticmethod
    def create_frame(parent: tk.Widget, padding: str = "10") -> ttk.Frame:
        """Create a frame with consistent styling.
        
        Args:
            parent: The parent widget
            padding: The padding to apply to the frame
            
        Returns:
            A configured frame
            
        Raises:
            UIError: If the frame cannot be created
        """
        try:
            frame = ttk.Frame(parent, padding=padding)
            return frame
        except Exception as e:
            error_msg = "Failed to create frame"
            raise UIError(error_msg, component_name="Frame", cause=e)
    
    @staticmethod
    def create_button(
        parent: tk.Widget, 
        text: str, 
        command: Callable[[], None],
        width: Optional[int] = None,
        state: str = tk.NORMAL
    ) -> ttk.Button:
        """Create a button with consistent styling.
        
        Args:
            parent: The parent widget
            text: The text to display on the button
            command: The callback to execute when the button is clicked
            width: The width of the button in characters
            state: The initial state of the button (NORMAL, DISABLED)
            
        Returns:
            A configured button
            
        Raises:
            UIError: If the button cannot be created
        """
        try:
            button = ttk.Button(parent, text=text, command=command, width=width, state=state)
            return button
        except Exception as e:
            error_msg = f"Failed to create button: {text}"
            raise UIError(error_msg, component_name="Button", cause=e)
    
    @staticmethod
    def create_label(
        parent: tk.Widget, 
        text: str,
        width: Optional[int] = None
    ) -> ttk.Label:
        """Create a label with consistent styling.
        
        Args:
            parent: The parent widget
            text: The text to display on the label
            width: The width of the label in characters
            
        Returns:
            A configured label
            
        Raises:
            UIError: If the label cannot be created
        """
        try:
            label = ttk.Label(parent, text=text, width=width)
            return label
        except Exception as e:
            error_msg = f"Failed to create label: {text}"
            raise UIError(error_msg, component_name="Label", cause=e)
    
    @staticmethod
    def create_entry(
        parent: tk.Widget, 
        textvariable: Optional[tk.StringVar] = None,
        width: Optional[int] = None,
        state: str = tk.NORMAL
    ) -> ttk.Entry:
        """Create an entry with consistent styling.
        
        Args:
            parent: The parent widget
            textvariable: The variable to bind to the entry
            width: The width of the entry in characters
            state: The initial state of the entry (NORMAL, DISABLED, READONLY)
            
        Returns:
            A configured entry
            
        Raises:
            UIError: If the entry cannot be created
        """
        try:
            entry = ttk.Entry(parent, textvariable=textvariable, width=width, state=state)
            return entry
        except Exception as e:
            error_msg = "Failed to create entry"
            raise UIError(error_msg, component_name="Entry", cause=e)
    
    @staticmethod
    def create_combobox(
        parent: tk.Widget, 
        textvariable: Optional[tk.StringVar] = None,
        values: Optional[List[str]] = None,
        width: Optional[int] = None,
        state: str = "readonly"
    ) -> ttk.Combobox:
        """Create a combobox with consistent styling.
        
        Args:
            parent: The parent widget
            textvariable: The variable to bind to the combobox
            values: The values to display in the combobox
            width: The width of the combobox in characters
            state: The initial state of the combobox (NORMAL, DISABLED, READONLY)
            
        Returns:
            A configured combobox
            
        Raises:
            UIError: If the combobox cannot be created
        """
        try:
            combobox = ttk.Combobox(
                parent, 
                textvariable=textvariable, 
                values=values or [], 
                width=width,
                state=state
            )
            return combobox
        except Exception as e:
            error_msg = "Failed to create combobox"
            raise UIError(error_msg, component_name="Combobox", cause=e)
    
    @staticmethod
    def create_listbox(
        parent: tk.Widget, 
        height: int = 10,
        width: int = 50,
        selectmode: str = tk.SINGLE
    ) -> tk.Listbox:
        """Create a listbox with consistent styling.
        
        Args:
            parent: The parent widget
            height: The height of the listbox in lines
            width: The width of the listbox in characters
            selectmode: The selection mode (SINGLE, MULTIPLE, EXTENDED, BROWSE)
            
        Returns:
            A configured listbox
            
        Raises:
            UIError: If the listbox cannot be created
        """
        try:
            listbox = tk.Listbox(parent, height=height, width=width, selectmode=selectmode)
            return listbox
        except Exception as e:
            error_msg = "Failed to create listbox"
            raise UIError(error_msg, component_name="Listbox", cause=e)
    
    @staticmethod
    def create_scrollbar(
        parent: tk.Widget, 
        orient: str = tk.VERTICAL,
        command: Optional[Callable] = None
    ) -> ttk.Scrollbar:
        """Create a scrollbar with consistent styling.
        
        Args:
            parent: The parent widget
            orient: The orientation of the scrollbar (VERTICAL, HORIZONTAL)
            command: The command to execute when the scrollbar is moved
            
        Returns:
            A configured scrollbar
            
        Raises:
            UIError: If the scrollbar cannot be created
        """
        try:
            scrollbar = ttk.Scrollbar(parent, orient=orient, command=command)
            return scrollbar
        except Exception as e:
            error_msg = "Failed to create scrollbar"
            raise UIError(error_msg, component_name="Scrollbar", cause=e)
    
    @staticmethod
    def create_text(
        parent: tk.Widget, 
        height: int = 10,
        width: int = 50,
        wrap: str = tk.WORD,
        state: str = tk.NORMAL
    ) -> tk.Text:
        """Create a text widget with consistent styling.
        
        Args:
            parent: The parent widget
            height: The height of the text widget in lines
            width: The width of the text widget in characters
            wrap: The wrap mode (WORD, CHAR, NONE)
            state: The initial state of the text widget (NORMAL, DISABLED)
            
        Returns:
            A configured text widget
            
        Raises:
            UIError: If the text widget cannot be created
        """
        try:
            text = tk.Text(parent, height=height, width=width, wrap=wrap, state=state)
            return text
        except Exception as e:
            error_msg = "Failed to create text widget"
            raise UIError(error_msg, component_name="Text", cause=e)
