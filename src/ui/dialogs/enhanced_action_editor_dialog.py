"""Enhanced action editor dialog for AutoQliq."""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import Dict, Any, Optional, List, Callable, Type

from src.core.exceptions import ValidationError, UIError, ActionError
from src.core.actions.factory import ActionFactory
from src.ui.common.ui_factory import UIFactory

logger = logging.getLogger(__name__)


class EnhancedActionEditorDialog(tk.Toplevel):
    """
    Enhanced dialog for editing workflow actions.
    
    This dialog provides a more modular and maintainable approach to editing
    actions, with better validation and user feedback.
    """
    
    def __init__(
        self,
        parent: tk.Widget,
        action_data: Optional[Dict[str, Any]] = None,
        title: str = None
    ):
        """
        Initialize the action editor dialog.
        
        Args:
            parent: The parent widget
            action_data: Initial action data (for editing an existing action)
            title: Custom title for the dialog
        """
        super().__init__(parent)
        self.parent = parent
        self.action_data = action_data or {}
        self.result = None
        
        # Set up the dialog
        self.is_edit_mode = bool(action_data)
        self.title(title or ("Edit Action" if self.is_edit_mode else "Add Action"))
        self.resizable(False, False)
        self.transient(parent)
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        
        # Create variables
        self.action_type_var = tk.StringVar(self)
        self.param_widgets = {}
        
        # Create widgets
        self._create_widgets()
        
        # Initialize with action data if provided
        if action_data:
            self._initialize_from_data(action_data)
        
        # Center the dialog on the parent
        self.update_idletasks()
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        dialog_width = self.winfo_width()
        dialog_height = self.winfo_height()
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        self.geometry(f"+{x}+{y}")
        
        logger.debug("EnhancedActionEditorDialog initialized")
    
    def _create_widgets(self):
        """Create the dialog widgets."""
        # Create the main frame
        self.main_frame = ttk.Frame(self, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create the action type selection
        type_frame = ttk.Frame(self.main_frame)
        type_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(type_frame, text="Action Type:").pack(side=tk.LEFT, padx=(0, 5))
        
        # Get registered action types
        action_types = ActionFactory.get_registered_action_types()
        if not action_types:
            raise UIError("No action types registered")
        
        # Create the action type combobox
        self.type_combobox = ttk.Combobox(
            type_frame,
            textvariable=self.action_type_var,
            values=action_types,
            state="readonly",
            width=30
        )
        self.type_combobox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Bind the action type change event
        self.action_type_var.trace_add("write", self._on_action_type_changed)
        
        # Create a separator
        ttk.Separator(self.main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)
        
        # Create the parameters frame
        self.params_frame = ttk.Frame(self.main_frame)
        self.params_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Create the name field (common to all action types)
        name_frame = ttk.Frame(self.params_frame)
        name_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(name_frame, text="Action Name:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.name_var = tk.StringVar(self)
        self.name_entry = ttk.Entry(name_frame, textvariable=self.name_var, width=30)
        self.name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Create a frame for the dynamic parameters
        self.dynamic_params_frame = ttk.Frame(self.params_frame)
        self.dynamic_params_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create the button frame
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Create the buttons
        self.cancel_button = ttk.Button(
            button_frame,
            text="Cancel",
            command=self._on_cancel
        )
        self.cancel_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        self.ok_button = ttk.Button(
            button_frame,
            text="OK",
            command=self._on_ok
        )
        self.ok_button.pack(side=tk.RIGHT)
    
    def _initialize_from_data(self, action_data: Dict[str, Any]):
        """
        Initialize the dialog with the provided action data.
        
        Args:
            action_data: The action data to initialize with
        """
        # Set the action type
        action_type = action_data.get("type")
        if action_type:
            self.action_type_var.set(action_type)
        
        # Set the action name
        name = action_data.get("name")
        if name:
            self.name_var.set(name)
        
        # The action type change handler will create the parameter widgets
        # and initialize them with the action data
    
    def _on_action_type_changed(self, *args):
        """Handle changes to the action type."""
        action_type = self.action_type_var.get()
        if not action_type:
            return
        
        logger.debug(f"Action type changed to: {action_type}")
        
        # Clear the dynamic parameters frame
        for widget in self.dynamic_params_frame.winfo_children():
            widget.destroy()
        
        # Clear the parameter widgets dictionary
        self.param_widgets.clear()
        
        # Create the parameter widgets for the selected action type
        self._create_parameter_widgets(action_type)
        
        # Initialize the parameter widgets with the action data if in edit mode
        if self.is_edit_mode and self.action_data.get("type") == action_type:
            self._initialize_parameter_widgets(self.action_data)
    
    def _create_parameter_widgets(self, action_type: str):
        """
        Create the parameter widgets for the selected action type.
        
        Args:
            action_type: The action type
        """
        # Get the parameter specifications for the action type
        param_specs = self._get_parameter_specs(action_type)
        
        # Create a widget for each parameter
        for param_name, param_spec in param_specs.items():
            self._create_parameter_widget(param_name, param_spec)
    
    def _get_parameter_specs(self, action_type: str) -> Dict[str, Dict[str, Any]]:
        """
        Get the parameter specifications for the action type.
        
        Args:
            action_type: The action type
            
        Returns:
            A dictionary of parameter specifications
        """
        # Define parameter specifications for each action type
        # This could be moved to a separate file or loaded from a configuration
        specs = {
            "Navigate": {
                "url": {
                    "label": "URL:",
                    "widget_type": "entry",
                    "required": True,
                    "tooltip": "The URL to navigate to (e.g., https://example.com)"
                }
            },
            "Click": {
                "selector": {
                    "label": "CSS Selector:",
                    "widget_type": "entry",
                    "required": True,
                    "tooltip": "The CSS selector for the element to click"
                }
            },
            "Type": {
                "selector": {
                    "label": "CSS Selector:",
                    "widget_type": "entry",
                    "required": True,
                    "tooltip": "The CSS selector for the input field"
                },
                "value_type": {
                    "label": "Value Type:",
                    "widget_type": "combobox",
                    "values": ["text", "credential"],
                    "required": True,
                    "tooltip": "The type of value to enter (text or credential)"
                },
                "value_key": {
                    "label": "Value:",
                    "widget_type": "entry",
                    "required": True,
                    "tooltip": "The text to type or the credential key"
                }
            },
            "Wait": {
                "duration_seconds": {
                    "label": "Duration (seconds):",
                    "widget_type": "entry",
                    "required": True,
                    "tooltip": "The number of seconds to wait"
                }
            },
            "Screenshot": {
                "file_path": {
                    "label": "File Path:",
                    "widget_type": "entry",
                    "required": True,
                    "tooltip": "The path where the screenshot will be saved"
                }
            }
        }
        
        return specs.get(action_type, {})
    
    def _create_parameter_widget(self, param_name: str, param_spec: Dict[str, Any]):
        """
        Create a widget for a parameter.
        
        Args:
            param_name: The parameter name
            param_spec: The parameter specification
        """
        # Create a frame for the parameter
        param_frame = ttk.Frame(self.dynamic_params_frame)
        param_frame.pack(fill=tk.X, pady=2)
        
        # Create a label for the parameter
        label = ttk.Label(param_frame, text=param_spec.get("label", param_name))
        label.pack(side=tk.LEFT, padx=(0, 5))
        
        # Create a variable for the parameter value
        var = tk.StringVar(self)
        
        # Create the widget based on the widget type
        widget_type = param_spec.get("widget_type", "entry")
        widget = None
        
        if widget_type == "entry":
            widget = ttk.Entry(param_frame, textvariable=var, width=30)
            widget.pack(side=tk.LEFT, fill=tk.X, expand=True)
        elif widget_type == "combobox":
            values = param_spec.get("values", [])
            widget = ttk.Combobox(
                param_frame,
                textvariable=var,
                values=values,
                state="readonly",
                width=30
            )
            widget.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Store the widget and variable in the parameter widgets dictionary
        self.param_widgets[param_name] = {
            "widget": widget,
            "var": var,
            "spec": param_spec
        }
    
    def _initialize_parameter_widgets(self, action_data: Dict[str, Any]):
        """
        Initialize the parameter widgets with the action data.
        
        Args:
            action_data: The action data
        """
        for param_name, param_info in self.param_widgets.items():
            if param_name in action_data:
                param_info["var"].set(str(action_data[param_name]))
    
    def _validate_parameters(self) -> Dict[str, str]:
        """
        Validate the parameter values.
        
        Returns:
            A dictionary of validation errors (empty if all parameters are valid)
        """
        errors = {}
        
        # Validate the action name
        name = self.name_var.get().strip()
        if not name:
            errors["name"] = "Action name is required"
        
        # Validate the action type
        action_type = self.action_type_var.get()
        if not action_type:
            errors["type"] = "Action type is required"
        
        # Validate the parameters
        for param_name, param_info in self.param_widgets.items():
            spec = param_info["spec"]
            value = param_info["var"].get().strip()
            
            # Check if the parameter is required
            if spec.get("required", False) and not value:
                errors[param_name] = f"{spec.get('label', param_name)} is required"
            
            # Add additional validation based on parameter type
            if param_name == "duration_seconds" and value:
                try:
                    float_value = float(value)
                    if float_value < 0:
                        errors[param_name] = "Duration must be a positive number"
                except ValueError:
                    errors[param_name] = "Duration must be a number"
            
            if param_name == "url" and value:
                if not value.startswith(("http://", "https://")):
                    errors[param_name] = "URL must start with http:// or https://"
        
        return errors
    
    def _collect_action_data(self) -> Dict[str, Any]:
        """
        Collect the action data from the widgets.
        
        Returns:
            The action data
        """
        action_data = {
            "type": self.action_type_var.get(),
            "name": self.name_var.get().strip()
        }
        
        # Collect the parameter values
        for param_name, param_info in self.param_widgets.items():
            value = param_info["var"].get().strip()
            
            # Convert numeric values
            if param_name == "duration_seconds" and value:
                try:
                    value = float(value)
                except ValueError:
                    pass
            
            action_data[param_name] = value
        
        return action_data
    
    def _on_ok(self):
        """Handle the OK button click."""
        # Validate the parameters
        errors = self._validate_parameters()
        
        if errors:
            # Show the validation errors
            error_message = "Please correct the following errors:\n\n"
            for field, error in errors.items():
                error_message += f"• {error}\n"
            
            messagebox.showerror("Validation Error", error_message, parent=self)
            return
        
        # Collect the action data
        action_data = self._collect_action_data()
        
        # Validate the action data using the ActionFactory
        try:
            action = ActionFactory.create_action(action_data)
            action.validate()
        except (ValidationError, ActionError, TypeError) as e:
            messagebox.showerror(
                "Validation Error",
                f"The action data is invalid:\n\n{str(e)}",
                parent=self
            )
            return
        
        # Set the result and close the dialog
        self.result = action_data
        self.destroy()
    
    def _on_cancel(self):
        """Handle the Cancel button click."""
        self.result = None
        self.destroy()
    
    def show(self) -> Optional[Dict[str, Any]]:
        """
        Show the dialog and wait for the user to close it.
        
        Returns:
            The action data if the user clicked OK, None if the user cancelled
        """
        self.grab_set()
        self.wait_window()
        return self.result
