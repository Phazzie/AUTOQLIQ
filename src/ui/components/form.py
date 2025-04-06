"""Form component for AutoQliq UI."""
import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, List, Optional, Callable, Union

from src.core.exceptions import UIError
from src.ui.common.ui_factory import UIFactory
from src.ui.common.form_validator import FormValidator


class Form:
    """A form component for collecting user input.
    
    This component provides a form with various input fields and validation.
    
    Attributes:
        frame: The frame containing the form
        fields: A dictionary of field names and their widgets
        variables: A dictionary of field names and their variables
    """
    
    def __init__(
        self, 
        parent: tk.Widget, 
        fields: List[Dict[str, Any]],
        on_submit: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_cancel: Optional[Callable[[], None]] = None
    ):
        """Initialize a Form.
        
        Args:
            parent: The parent widget
            fields: A list of field definitions
            on_submit: A callback to execute when the form is submitted
            on_cancel: A callback to execute when the form is cancelled
            
        Raises:
            UIError: If the component cannot be created
            
        Example:
            ```python
            fields = [
                {"name": "username", "label": "Username", "type": "entry"},
                {"name": "password", "label": "Password", "type": "entry", "show": "*"},
                {"name": "remember", "label": "Remember Me", "type": "checkbox"}
            ]
            form = Form(parent, fields, on_submit=handle_submit)
            ```
        """
        try:
            # Create the frame
            self.frame = UIFactory.create_frame(parent)
            
            # Store the callbacks
            self.on_submit = on_submit
            self.on_cancel = on_cancel
            
            # Create dictionaries to store the fields and variables
            self.fields: Dict[str, Any] = {}
            self.variables: Dict[str, Any] = {}
            
            # Create the fields
            self._create_fields(fields)
            
            # Create the buttons
            self._create_buttons()
        except Exception as e:
            error_msg = "Failed to create Form"
            raise UIError(error_msg, component_name="Form", cause=e)
    
    def _create_fields(self, fields: List[Dict[str, Any]]) -> None:
        """Create the form fields.
        
        Args:
            fields: A list of field definitions
            
        Raises:
            UIError: If the fields cannot be created
        """
        try:
            # Create each field
            for i, field in enumerate(fields):
                field_name = field.get("name", f"field_{i}")
                field_label = field.get("label", field_name.capitalize())
                field_type = field.get("type", "entry")
                
                # Create a label for the field
                label = UIFactory.create_label(self.frame, text=field_label)
                label.grid(row=i, column=0, sticky=tk.W, padx=5, pady=5)
                
                # Create the field based on its type
                if field_type == "entry":
                    # Create a string variable
                    var = tk.StringVar(value=field.get("value", ""))
                    self.variables[field_name] = var
                    
                    # Create an entry widget
                    entry = UIFactory.create_entry(
                        self.frame, 
                        textvariable=var,
                        width=field.get("width", 30)
                    )
                    
                    # Configure the entry to show asterisks for passwords
                    if field.get("show"):
                        entry.config(show=field.get("show"))
                    
                    # Grid the entry
                    entry.grid(row=i, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
                    
                    # Store the field
                    self.fields[field_name] = entry
                
                elif field_type == "combobox":
                    # Create a string variable
                    var = tk.StringVar(value=field.get("value", ""))
                    self.variables[field_name] = var
                    
                    # Create a combobox widget
                    combobox = UIFactory.create_combobox(
                        self.frame, 
                        textvariable=var,
                        values=field.get("values", []),
                        width=field.get("width", 30)
                    )
                    
                    # Grid the combobox
                    combobox.grid(row=i, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
                    
                    # Store the field
                    self.fields[field_name] = combobox
                
                elif field_type == "checkbox":
                    # Create a boolean variable
                    var = tk.BooleanVar(value=field.get("value", False))
                    self.variables[field_name] = var
                    
                    # Create a checkbox widget
                    checkbox = ttk.Checkbutton(self.frame, variable=var)
                    
                    # Grid the checkbox
                    checkbox.grid(row=i, column=1, sticky=tk.W, padx=5, pady=5)
                    
                    # Store the field
                    self.fields[field_name] = checkbox
                
                elif field_type == "text":
                    # Create a string variable
                    var = tk.StringVar(value=field.get("value", ""))
                    self.variables[field_name] = var
                    
                    # Create a text widget
                    text = UIFactory.create_text(
                        self.frame, 
                        height=field.get("height", 5),
                        width=field.get("width", 30)
                    )
                    
                    # Insert the initial value
                    text.insert("1.0", field.get("value", ""))
                    
                    # Grid the text widget
                    text.grid(row=i, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
                    
                    # Store the field
                    self.fields[field_name] = text
        except Exception as e:
            error_msg = "Failed to create form fields"
            raise UIError(error_msg, component_name="Form", cause=e)
    
    def _create_buttons(self) -> None:
        """Create the form buttons.
        
        Raises:
            UIError: If the buttons cannot be created
        """
        try:
            # Create a frame for the buttons
            button_frame = UIFactory.create_frame(self.frame)
            button_frame.grid(row=len(self.fields), column=0, columnspan=2, pady=10)
            
            # Create the submit button
            submit_button = UIFactory.create_button(
                button_frame, 
                text="Submit", 
                command=self._handle_submit
            )
            submit_button.pack(side=tk.LEFT, padx=5)
            
            # Create the cancel button
            cancel_button = UIFactory.create_button(
                button_frame, 
                text="Cancel", 
                command=self._handle_cancel
            )
            cancel_button.pack(side=tk.LEFT, padx=5)
        except Exception as e:
            error_msg = "Failed to create form buttons"
            raise UIError(error_msg, component_name="Form", cause=e)
    
    def _handle_submit(self) -> None:
        """Handle the submit button click.
        
        This method collects the form data and calls the on_submit callback.
        """
        if self.on_submit:
            # Collect the form data
            data = self.get_data()
            
            # Call the callback
            self.on_submit(data)
    
    def _handle_cancel(self) -> None:
        """Handle the cancel button click.
        
        This method calls the on_cancel callback.
        """
        if self.on_cancel:
            self.on_cancel()
    
    def get_data(self) -> Dict[str, Any]:
        """Get the form data.
        
        Returns:
            A dictionary of field names and values
            
        Raises:
            UIError: If the data cannot be retrieved
        """
        try:
            data: Dict[str, Any] = {}
            
            # Collect the data from each field
            for field_name, var in self.variables.items():
                # Get the field
                field = self.fields.get(field_name)
                
                # Get the value based on the field type
                if isinstance(field, tk.Text):
                    data[field_name] = field.get("1.0", tk.END).strip()
                else:
                    data[field_name] = var.get()
            
            return data
        except Exception as e:
            error_msg = "Failed to get form data"
            raise UIError(error_msg, component_name="Form", cause=e)
    
    def set_data(self, data: Dict[str, Any]) -> None:
        """Set the form data.
        
        Args:
            data: A dictionary of field names and values
            
        Raises:
            UIError: If the data cannot be set
        """
        try:
            # Set the data for each field
            for field_name, value in data.items():
                # Get the field and variable
                field = self.fields.get(field_name)
                var = self.variables.get(field_name)
                
                # Set the value based on the field type
                if field and var:
                    if isinstance(field, tk.Text):
                        # Clear the text widget
                        field.delete("1.0", tk.END)
                        
                        # Insert the new value
                        field.insert("1.0", str(value))
                    else:
                        # Set the variable value
                        var.set(value)
        except Exception as e:
            error_msg = "Failed to set form data"
            raise UIError(error_msg, component_name="Form", cause=e)
    
    def validate(self, rules: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[str]]:
        """Validate the form data.
        
        Args:
            rules: A dictionary of field names and validation rules
            
        Returns:
            A dictionary of field names and error messages, or an empty dictionary if validation passes
            
        Raises:
            UIError: If the validation cannot be performed
        """
        try:
            # Get the form data
            data = self.get_data()
            
            # Validate the data
            return FormValidator.validate_form(data, rules)
        except Exception as e:
            error_msg = "Failed to validate form"
            raise UIError(error_msg, component_name="Form", cause=e)
    
    def clear(self) -> None:
        """Clear the form data.
        
        Raises:
            UIError: If the form cannot be cleared
        """
        try:
            # Clear each field
            for field_name, field in self.fields.items():
                var = self.variables.get(field_name)
                
                # Clear the field based on its type
                if isinstance(field, tk.Text):
                    field.delete("1.0", tk.END)
                elif var:
                    if isinstance(var, tk.BooleanVar):
                        var.set(False)
                    else:
                        var.set("")
        except Exception as e:
            error_msg = "Failed to clear form"
            raise UIError(error_msg, component_name="Form", cause=e)
