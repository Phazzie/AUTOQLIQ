"""Loop action editor dialog for AutoQliq."""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import Dict, Any, Optional, List, Callable, Type

from src.core.exceptions import ValidationError, UIError, ActionError
from src.core.actions.factory import ActionFactory
from src.ui.common.ui_factory import UIFactory

logger = logging.getLogger(__name__)


class LoopActionEditorDialog(tk.Toplevel):
    """
    Dialog for editing loop actions.
    
    Loop actions are more complex than regular actions, as they have
    loop parameters and a list of actions to execute in the loop.
    """
    
    def __init__(
        self,
        parent: tk.Widget,
        action_data: Optional[Dict[str, Any]] = None,
        workflow_presenter: Any = None
    ):
        """
        Initialize the loop action editor dialog.
        
        Args:
            parent: The parent widget
            action_data: Initial action data (for editing an existing action)
            workflow_presenter: The workflow presenter for accessing actions
        """
        super().__init__(parent)
        self.parent = parent
        self.action_data = action_data or {"type": "Loop"}
        self.workflow_presenter = workflow_presenter
        self.result = None
        
        # Set up the dialog
        self.is_edit_mode = bool(action_data and action_data.get("type") == "Loop")
        self.title("Edit Loop Action" if self.is_edit_mode else "Add Loop Action")
        self.geometry("600x500")
        self.minsize(500, 400)
        self.resizable(True, True)
        self.transient(parent)
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        
        # Create variables
        self.name_var = tk.StringVar(self)
        self.loop_type_var = tk.StringVar(self)
        self.count_var = tk.StringVar(self)
        self.variable_name_var = tk.StringVar(self)
        self.items_var = tk.StringVar(self)
        self.condition_var = tk.StringVar(self)
        
        # Create widgets
        self._create_widgets()
        
        # Initialize with action data if provided
        if self.is_edit_mode:
            self._initialize_from_data(self.action_data)
        
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
        
        logger.debug("LoopActionEditorDialog initialized")
    
    def _create_widgets(self):
        """Create the dialog widgets."""
        # Create the main frame
        self.main_frame = ttk.Frame(self, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create the basic info frame
        basic_frame = ttk.LabelFrame(self.main_frame, text="Basic Information")
        basic_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Create the name field
        name_frame = ttk.Frame(basic_frame)
        name_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(name_frame, text="Action Name:").pack(side=tk.LEFT, padx=(0, 5))
        
        name_entry = ttk.Entry(name_frame, textvariable=self.name_var, width=30)
        name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Create the loop frame
        loop_frame = ttk.LabelFrame(self.main_frame, text="Loop Configuration")
        loop_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Create the loop type field
        type_frame = ttk.Frame(loop_frame)
        type_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(type_frame, text="Loop Type:").pack(side=tk.LEFT, padx=(0, 5))
        
        loop_types = [
            "count",
            "for_each",
            "while"
        ]
        
        loop_type_combo = ttk.Combobox(
            type_frame,
            textvariable=self.loop_type_var,
            values=loop_types,
            state="readonly",
            width=30
        )
        loop_type_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Bind the loop type change event
        self.loop_type_var.trace_add("write", self._on_loop_type_changed)
        
        # Create the dynamic loop parameters frame
        self.loop_params_frame = ttk.Frame(loop_frame)
        self.loop_params_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Create the actions frame
        actions_frame = ttk.LabelFrame(self.main_frame, text="Loop Actions")
        actions_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create the actions list
        actions_label = ttk.Label(actions_frame, text="Actions to execute in the loop:")
        actions_label.pack(anchor=tk.W, padx=5, pady=5)
        
        self.actions_listbox = tk.Listbox(actions_frame, height=10)
        self.actions_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        actions_buttons = ttk.Frame(actions_frame)
        actions_buttons.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(
            actions_buttons,
            text="Add Action",
            command=self._add_action
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            actions_buttons,
            text="Remove Action",
            command=self._remove_action
        ).pack(side=tk.LEFT)
        
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
        
        # Initialize the loop type
        if not self.loop_type_var.get():
            self.loop_type_var.set("count")
    
    def _on_loop_type_changed(self, *args):
        """Handle changes to the loop type."""
        loop_type = self.loop_type_var.get()
        if not loop_type:
            return
        
        logger.debug(f"Loop type changed to: {loop_type}")
        
        # Clear the loop parameters frame
        for widget in self.loop_params_frame.winfo_children():
            widget.destroy()
        
        # Create the appropriate widgets based on the loop type
        if loop_type == "count":
            self._create_count_widget()
        elif loop_type == "for_each":
            self._create_for_each_widgets()
        elif loop_type == "while":
            self._create_while_widget()
    
    def _create_count_widget(self):
        """Create the count widget for count loops."""
        count_frame = ttk.Frame(self.loop_params_frame)
        count_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(count_frame, text="Count:").pack(side=tk.LEFT, padx=(0, 5))
        
        count_entry = ttk.Entry(count_frame, textvariable=self.count_var, width=10)
        count_entry.pack(side=tk.LEFT)
        
        ttk.Label(count_frame, text="(Number of iterations)").pack(side=tk.LEFT, padx=(5, 0))
    
    def _create_for_each_widgets(self):
        """Create the widgets for for_each loops."""
        variable_frame = ttk.Frame(self.loop_params_frame)
        variable_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(variable_frame, text="Variable Name:").pack(side=tk.LEFT, padx=(0, 5))
        
        variable_entry = ttk.Entry(variable_frame, textvariable=self.variable_name_var, width=30)
        variable_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        items_frame = ttk.Frame(self.loop_params_frame)
        items_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(items_frame, text="Items:").pack(side=tk.LEFT, padx=(0, 5))
        
        items_entry = ttk.Entry(items_frame, textvariable=self.items_var, width=30)
        items_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(items_frame, text="(Comma-separated list or variable name)").pack(side=tk.LEFT, padx=(5, 0))
    
    def _create_while_widget(self):
        """Create the widget for while loops."""
        condition_frame = ttk.Frame(self.loop_params_frame)
        condition_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(condition_frame, text="Condition:").pack(side=tk.LEFT, padx=(0, 5))
        
        condition_entry = ttk.Entry(condition_frame, textvariable=self.condition_var, width=30)
        condition_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(condition_frame, text="(JavaScript expression that evaluates to true/false)").pack(side=tk.LEFT, padx=(5, 0))
    
    def _initialize_from_data(self, action_data: Dict[str, Any]):
        """
        Initialize the dialog with the provided action data.
        
        Args:
            action_data: The action data to initialize with
        """
        # Set the action name
        name = action_data.get("name")
        if name:
            self.name_var.set(name)
        
        # Set the loop type
        loop_type = action_data.get("loop_type")
        if loop_type:
            self.loop_type_var.set(loop_type)
        
        # Set the loop parameters
        count = action_data.get("count")
        if count is not None:
            self.count_var.set(str(count))
        
        variable_name = action_data.get("variable_name")
        if variable_name:
            self.variable_name_var.set(variable_name)
        
        items = action_data.get("items")
        if items:
            if isinstance(items, list):
                self.items_var.set(", ".join(str(item) for item in items))
            else:
                self.items_var.set(str(items))
        
        condition = action_data.get("condition")
        if condition:
            self.condition_var.set(condition)
        
        # Initialize the actions
        actions = action_data.get("actions", [])
        for action in actions:
            self._add_action_item(action)
    
    def _add_action(self):
        """Add an action to the loop."""
        # Show an action editor dialog
        from src.ui.factories.dialog_factory import DialogFactory
        
        action_data = DialogFactory.show_action_editor(self)
        if action_data:
            self._add_action_item(action_data)
    
    def _add_action_item(self, action_data: Dict[str, Any]):
        """
        Add an action item to the actions listbox.
        
        Args:
            action_data: The action data
        """
        # Format the action for display
        action_type = action_data.get("type", "Unknown")
        action_name = action_data.get("name", action_type)
        
        # Add the action to the listbox
        self.actions_listbox.insert(tk.END, f"{action_name} ({action_type})")
        
        # Store the action data in the listbox
        index = self.actions_listbox.size() - 1
        self.actions_listbox.itemconfig(index, {"action_data": action_data})
    
    def _remove_action(self):
        """Remove an action from the loop."""
        # Get the selected index
        selected = self.actions_listbox.curselection()
        if not selected:
            messagebox.showinfo("No Selection", "Please select an action to remove.", parent=self)
            return
        
        # Remove the action from the listbox
        self.actions_listbox.delete(selected[0])
    
    def _validate(self) -> Dict[str, str]:
        """
        Validate the dialog inputs.
        
        Returns:
            A dictionary of validation errors (empty if all inputs are valid)
        """
        errors = {}
        
        # Validate the action name
        name = self.name_var.get().strip()
        if not name:
            errors["name"] = "Action name is required"
        
        # Validate the loop type
        loop_type = self.loop_type_var.get()
        if not loop_type:
            errors["loop_type"] = "Loop type is required"
        
        # Validate the loop parameters based on the loop type
        if loop_type == "count":
            count = self.count_var.get().strip()
            if not count:
                errors["count"] = "Count is required"
            else:
                try:
                    count_value = int(count)
                    if count_value <= 0:
                        errors["count"] = "Count must be a positive integer"
                except ValueError:
                    errors["count"] = "Count must be a valid integer"
        elif loop_type == "for_each":
            variable_name = self.variable_name_var.get().strip()
            if not variable_name:
                errors["variable_name"] = "Variable name is required"
            
            items = self.items_var.get().strip()
            if not items:
                errors["items"] = "Items are required"
        elif loop_type == "while":
            condition = self.condition_var.get().strip()
            if not condition:
                errors["condition"] = "Condition is required"
        
        # Validate that there are actions in the loop
        if self.actions_listbox.size() == 0:
            errors["actions"] = "At least one action is required in the loop"
        
        return errors
    
    def _collect_action_data(self) -> Dict[str, Any]:
        """
        Collect the action data from the dialog inputs.
        
        Returns:
            The action data
        """
        action_data = {
            "type": "Loop",
            "name": self.name_var.get().strip(),
            "loop_type": self.loop_type_var.get()
        }
        
        # Collect the loop parameters based on the loop type
        if action_data["loop_type"] == "count":
            try:
                action_data["count"] = int(self.count_var.get().strip())
            except ValueError:
                action_data["count"] = 0
        elif action_data["loop_type"] == "for_each":
            action_data["variable_name"] = self.variable_name_var.get().strip()
            
            items = self.items_var.get().strip()
            if "," in items:
                # Parse as a comma-separated list
                action_data["items"] = [item.strip() for item in items.split(",")]
            else:
                # Treat as a variable name
                action_data["items"] = items
        elif action_data["loop_type"] == "while":
            action_data["condition"] = self.condition_var.get().strip()
        
        # Collect the actions
        action_data["actions"] = []
        for i in range(self.actions_listbox.size()):
            action_data_item = self.actions_listbox.itemcget(i, "action_data")
            if action_data_item:
                action_data["actions"].append(action_data_item)
        
        return action_data
    
    def _on_ok(self):
        """Handle the OK button click."""
        # Validate the inputs
        errors = self._validate()
        
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
