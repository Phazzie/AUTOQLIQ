"""Factory for creating composite UI components.

This module provides a factory for creating composite UI components with consistent styling.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, List, Optional, Callable, Union

from src.core.exceptions import UIError
from src.ui.common.widget_factory import WidgetFactory
from src.ui.common.service_provider import ServiceProvider


class ComponentFactory:
    """Factory for creating composite UI components.
    
    This class provides methods for creating composite UI components with consistent
    styling and behavior.
    
    Attributes:
        service_provider: The service provider for dependency injection
    """
    
    def __init__(self, service_provider: Optional[ServiceProvider] = None):
        """Initialize a new ComponentFactory.
        
        Args:
            service_provider: The service provider for dependency injection
        """
        self.service_provider = service_provider or ServiceProvider()
    
    def create_scrolled_listbox(
        self,
        parent: tk.Widget, 
        height: int = 10,
        width: int = 50,
        selectmode: str = tk.SINGLE
    ) -> Dict[str, Union[tk.Listbox, ttk.Scrollbar, ttk.Frame]]:
        """Create a listbox with a scrollbar.
        
        Args:
            parent: The parent widget
            height: The height of the listbox in lines
            width: The width of the listbox in characters
            selectmode: The selection mode (SINGLE, MULTIPLE, EXTENDED, BROWSE)
            
        Returns:
            A dictionary containing the frame, listbox, and scrollbar
            
        Raises:
            UIError: If the scrolled listbox cannot be created
        """
        try:
            # Create a frame to hold the listbox and scrollbar
            frame = WidgetFactory.create_frame(parent)
            
            # Create the listbox
            listbox = WidgetFactory.create_listbox(frame, height=height, width=width, selectmode=selectmode)
            
            # Create the scrollbar
            scrollbar = WidgetFactory.create_scrollbar(frame, command=listbox.yview)
            
            # Configure the listbox to use the scrollbar
            listbox.configure(yscrollcommand=scrollbar.set)
            
            # Pack the widgets
            listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            return {"frame": frame, "listbox": listbox, "scrollbar": scrollbar}
        except Exception as e:
            error_msg = "Failed to create scrolled listbox"
            raise UIError(error_msg, component_name="ScrolledListbox", cause=e)
    
    def create_scrolled_text(
        self,
        parent: tk.Widget, 
        height: int = 10,
        width: int = 50,
        wrap: str = tk.WORD,
        state: str = tk.NORMAL
    ) -> Dict[str, Union[tk.Text, ttk.Scrollbar, ttk.Frame]]:
        """Create a text widget with a scrollbar.
        
        Args:
            parent: The parent widget
            height: The height of the text widget in lines
            width: The width of the text widget in characters
            wrap: The wrap mode (WORD, CHAR, NONE)
            state: The initial state of the text widget (NORMAL, DISABLED)
            
        Returns:
            A dictionary containing the frame, text widget, and scrollbar
            
        Raises:
            UIError: If the scrolled text widget cannot be created
        """
        try:
            # Create a frame to hold the text widget and scrollbar
            frame = WidgetFactory.create_frame(parent)
            
            # Create the text widget
            text = WidgetFactory.create_text(frame, height=height, width=width, wrap=wrap, state=state)
            
            # Create the scrollbar
            scrollbar = WidgetFactory.create_scrollbar(frame, command=text.yview)
            
            # Configure the text widget to use the scrollbar
            text.configure(yscrollcommand=scrollbar.set)
            
            # Pack the widgets
            text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            return {"frame": frame, "text": text, "scrollbar": scrollbar}
        except Exception as e:
            error_msg = "Failed to create scrolled text widget"
            raise UIError(error_msg, component_name="ScrolledText", cause=e)
    
    def create_form_field(
        self,
        parent: tk.Widget,
        label_text: str,
        field_type: str = "entry",
        field_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a form field with a label and input widget.
        
        Args:
            parent: The parent widget
            label_text: The text for the label
            field_type: The type of field to create (entry, combobox, checkbox, text)
            field_options: Options for the field
            
        Returns:
            A dictionary containing the label and field widgets
            
        Raises:
            UIError: If the form field cannot be created
        """
        try:
            # Create a frame to hold the label and field
            frame = WidgetFactory.create_frame(parent)
            
            # Create the label
            label = WidgetFactory.create_label(frame, text=label_text)
            label.pack(side=tk.LEFT, padx=(0, 5))
            
            # Get the field options
            options = field_options or {}
            
            # Create the field based on its type
            field = None
            variable = None
            
            if field_type == "entry":
                # Create a string variable
                variable = tk.StringVar(value=options.get("value", ""))
                
                # Create an entry widget
                field = WidgetFactory.create_entry(
                    frame, 
                    textvariable=variable,
                    width=options.get("width", 30),
                    state=options.get("state", tk.NORMAL)
                )
                
                # Configure the entry to show asterisks for passwords
                if options.get("show"):
                    field.config(show=options.get("show"))
            
            elif field_type == "combobox":
                # Create a string variable
                variable = tk.StringVar(value=options.get("value", ""))
                
                # Create a combobox widget
                field = WidgetFactory.create_combobox(
                    frame, 
                    textvariable=variable,
                    values=options.get("values", []),
                    width=options.get("width", 30),
                    state=options.get("state", "readonly")
                )
            
            elif field_type == "checkbox":
                # Create a boolean variable
                variable = tk.BooleanVar(value=options.get("value", False))
                
                # Create a checkbox widget
                field = ttk.Checkbutton(frame, variable=variable)
            
            elif field_type == "text":
                # Create a text widget
                field = WidgetFactory.create_text(
                    frame, 
                    height=options.get("height", 5),
                    width=options.get("width", 30),
                    wrap=options.get("wrap", tk.WORD),
                    state=options.get("state", tk.NORMAL)
                )
                
                # Insert the initial value
                if "value" in options:
                    field.insert("1.0", options["value"])
            
            else:
                raise ValueError(f"Unsupported field type: {field_type}")
            
            # Pack the field
            if field:
                field.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            return {"frame": frame, "label": label, "field": field, "variable": variable}
        except Exception as e:
            error_msg = f"Failed to create form field: {label_text}"
            raise UIError(error_msg, component_name="FormField", cause=e)
    
    def create_button_bar(
        self,
        parent: tk.Widget,
        buttons: List[Dict[str, Any]],
        orientation: str = tk.HORIZONTAL
    ) -> Dict[str, Any]:
        """Create a bar of buttons.
        
        Args:
            parent: The parent widget
            buttons: A list of button definitions
            orientation: The orientation of the button bar (HORIZONTAL, VERTICAL)
            
        Returns:
            A dictionary containing the frame and buttons
            
        Raises:
            UIError: If the button bar cannot be created
        """
        try:
            # Create a frame to hold the buttons
            frame = WidgetFactory.create_frame(parent)
            
            # Create a dictionary to store the buttons
            button_widgets = {}
            
            # Create the buttons
            for button_def in buttons:
                # Get the button properties
                name = button_def.get("name", "button")
                text = button_def.get("text", name.capitalize())
                command = button_def.get("command", lambda: None)
                width = button_def.get("width")
                state = button_def.get("state", tk.NORMAL)
                
                # Create the button
                button = WidgetFactory.create_button(
                    frame, 
                    text=text, 
                    command=command,
                    width=width,
                    state=state
                )
                
                # Pack the button
                if orientation == tk.HORIZONTAL:
                    button.pack(side=tk.LEFT, padx=2, pady=2)
                else:
                    button.pack(side=tk.TOP, padx=2, pady=2)
                
                # Store the button
                button_widgets[name] = button
            
            return {"frame": frame, "buttons": button_widgets}
        except Exception as e:
            error_msg = "Failed to create button bar"
            raise UIError(error_msg, component_name="ButtonBar", cause=e)
    
    def create_status_bar(
        self,
        parent: tk.Widget,
        show_progress: bool = True,
        initial_message: str = "Ready"
    ) -> Dict[str, Any]:
        """Create a status bar with a message label and optional progress bar.
        
        Args:
            parent: The parent widget
            show_progress: Whether to show a progress bar
            initial_message: The initial status message
            
        Returns:
            A dictionary containing the frame, message label, and progress bar
            
        Raises:
            UIError: If the status bar cannot be created
        """
        try:
            # Create a frame to hold the status bar
            frame = WidgetFactory.create_frame(parent)
            
            # Create the message label
            message_label = WidgetFactory.create_label(frame, text=initial_message)
            message_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=2)
            
            # Create the progress bar if requested
            progress_bar = None
            if show_progress:
                progress_bar = ttk.Progressbar(
                    frame, 
                    mode="determinate", 
                    length=100
                )
                progress_bar.pack(side=tk.RIGHT, padx=5, pady=2)
            
            return {"frame": frame, "message_label": message_label, "progress_bar": progress_bar}
        except Exception as e:
            error_msg = "Failed to create status bar"
            raise UIError(error_msg, component_name="StatusBar", cause=e)
