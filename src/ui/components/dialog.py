"""Dialog component for AutoQliq UI."""
import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, List, Optional, Callable, Union, Tuple

from src.core.exceptions import UIError
from src.ui.common.ui_factory import UIFactory
from src.ui.components.form import Form


class Dialog:
    """A dialog component for displaying messages and collecting user input.
    
    This component provides a dialog with various input fields and buttons.
    
    Attributes:
        window: The dialog window
        result: The result of the dialog
    """
    
    def __init__(
        self, 
        parent: tk.Widget, 
        title: str,
        message: Optional[str] = None,
        fields: Optional[List[Dict[str, Any]]] = None,
        buttons: Optional[List[Dict[str, Any]]] = None,
        modal: bool = True,
        width: int = 400,
        height: int = 300
    ):
        """Initialize a Dialog.
        
        Args:
            parent: The parent widget
            title: The title of the dialog
            message: The message to display
            fields: A list of field definitions
            buttons: A list of button definitions
            modal: Whether the dialog is modal
            width: The width of the dialog
            height: The height of the dialog
            
        Raises:
            UIError: If the component cannot be created
            
        Example:
            ```python
            fields = [
                {"name": "username", "label": "Username", "type": "entry"},
                {"name": "password", "label": "Password", "type": "entry", "show": "*"}
            ]
            buttons = [
                {"text": "OK", "command": lambda: dialog.close("ok")},
                {"text": "Cancel", "command": lambda: dialog.close("cancel")}
            ]
            dialog = Dialog(parent, "Login", "Please enter your credentials", fields, buttons)
            result = dialog.show()
            ```
        """
        try:
            # Create the dialog window
            self.window = tk.Toplevel(parent)
            self.window.title(title)
            self.window.geometry(f"{width}x{height}")
            self.window.resizable(False, False)
            
            # Make the dialog modal if requested
            if modal:
                self.window.transient(parent)
                self.window.grab_set()
            
            # Create the main frame
            main_frame = UIFactory.create_frame(self.window)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Create the message label if provided
            if message:
                message_label = UIFactory.create_label(main_frame, text=message)
                message_label.pack(fill=tk.X, pady=10)
            
            # Create the form if fields are provided
            self.form = None
            if fields:
                self.form = Form(main_frame, fields)
                self.form.frame.pack(fill=tk.BOTH, expand=True)
            
            # Create the buttons
            button_frame = UIFactory.create_frame(main_frame)
            button_frame.pack(fill=tk.X, pady=10)
            
            # Create the default buttons if none are provided
            if not buttons:
                buttons = [
                    {"text": "OK", "command": lambda: self.close("ok")}
                ]
            
            # Create the buttons
            for button in buttons:
                btn = UIFactory.create_button(
                    button_frame, 
                    text=button.get("text", "Button"),
                    command=button.get("command", lambda: None),
                    width=button.get("width")
                )
                btn.pack(side=tk.LEFT, padx=5)
            
            # Initialize the result
            self.result = None
            
            # Center the dialog on the parent
            self._center_on_parent(parent)
            
            # Configure the dialog to close when the window is closed
            self.window.protocol("WM_DELETE_WINDOW", lambda: self.close("cancel"))
        except Exception as e:
            error_msg = "Failed to create Dialog"
            raise UIError(error_msg, component_name="Dialog", cause=e)
    
    def _center_on_parent(self, parent: tk.Widget) -> None:
        """Center the dialog on the parent widget.
        
        Args:
            parent: The parent widget
        """
        # Wait for the window to be created
        self.window.update_idletasks()
        
        # Get the window size
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        
        # Get the parent position and size
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        # Calculate the position
        x = parent_x + (parent_width - width) // 2
        y = parent_y + (parent_height - height) // 2
        
        # Set the position
        self.window.geometry(f"+{x}+{y}")
    
    def show(self) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """Show the dialog and wait for it to be closed.
        
        Returns:
            A tuple containing the result and the form data, or (None, None) if the dialog was cancelled
        """
        # Wait for the dialog to be closed
        self.window.wait_window()
        
        # Get the form data if a form was created
        form_data = self.form.get_data() if self.form else None
        
        # Return the result and form data
        return self.result, form_data
    
    def close(self, result: Optional[str] = None) -> None:
        """Close the dialog.
        
        Args:
            result: The result to return
        """
        # Set the result
        self.result = result
        
        # Destroy the window
        self.window.destroy()
    
    @staticmethod
    def show_message(
        parent: tk.Widget, 
        title: str, 
        message: str, 
        button_text: str = "OK"
    ) -> None:
        """Show a message dialog.
        
        Args:
            parent: The parent widget
            title: The title of the dialog
            message: The message to display
            button_text: The text for the OK button
            
        Example:
            ```python
            Dialog.show_message(parent, "Information", "Operation completed successfully")
            ```
        """
        dialog = Dialog(
            parent, 
            title, 
            message, 
            buttons=[{"text": button_text, "command": lambda: dialog.close("ok")}],
            width=300,
            height=150
        )
        dialog.show()
    
    @staticmethod
    def show_confirmation(
        parent: tk.Widget, 
        title: str, 
        message: str, 
        ok_text: str = "OK", 
        cancel_text: str = "Cancel"
    ) -> bool:
        """Show a confirmation dialog.
        
        Args:
            parent: The parent widget
            title: The title of the dialog
            message: The message to display
            ok_text: The text for the OK button
            cancel_text: The text for the Cancel button
            
        Returns:
            True if the user clicked OK, False otherwise
            
        Example:
            ```python
            if Dialog.show_confirmation(parent, "Confirmation", "Are you sure you want to delete this item?"):
                # Delete the item
            ```
        """
        dialog = Dialog(
            parent, 
            title, 
            message, 
            buttons=[
                {"text": ok_text, "command": lambda: dialog.close("ok")},
                {"text": cancel_text, "command": lambda: dialog.close("cancel")}
            ],
            width=300,
            height=150
        )
        result, _ = dialog.show()
        return result == "ok"
    
    @staticmethod
    def show_input(
        parent: tk.Widget, 
        title: str, 
        message: str, 
        field_name: str = "input",
        field_label: str = "Input",
        default_value: str = "",
        ok_text: str = "OK", 
        cancel_text: str = "Cancel"
    ) -> Tuple[bool, Optional[str]]:
        """Show an input dialog.
        
        Args:
            parent: The parent widget
            title: The title of the dialog
            message: The message to display
            field_name: The name of the input field
            field_label: The label for the input field
            default_value: The default value for the input field
            ok_text: The text for the OK button
            cancel_text: The text for the Cancel button
            
        Returns:
            A tuple containing a boolean indicating whether the user clicked OK and the input value
            
        Example:
            ```python
            ok, value = Dialog.show_input(parent, "Input", "Enter your name")
            if ok:
                print(f"Hello, {value}!")
            ```
        """
        fields = [
            {
                "name": field_name, 
                "label": field_label, 
                "type": "entry", 
                "value": default_value
            }
        ]
        
        dialog = Dialog(
            parent, 
            title, 
            message, 
            fields=fields,
            buttons=[
                {"text": ok_text, "command": lambda: dialog.close("ok")},
                {"text": cancel_text, "command": lambda: dialog.close("cancel")}
            ],
            width=300,
            height=200
        )
        
        result, form_data = dialog.show()
        
        if result == "ok" and form_data:
            return True, form_data.get(field_name)
        else:
            return False, None
