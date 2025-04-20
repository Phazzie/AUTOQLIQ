"""Conditional action editor dialog for AutoQliq."""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import Dict, Any, Optional, List, Callable, Type

from src.core.exceptions import ValidationError, UIError, ActionError
from src.core.actions.factory import ActionFactory
from src.ui.common.ui_factory import UIFactory

logger = logging.getLogger(__name__)


class ConditionalActionEditorDialog(tk.Toplevel):
    """
    Dialog for editing conditional actions.
    
    Conditional actions are more complex than regular actions, as they have
    condition parameters and branches of actions to execute based on the condition.
    """
    
    def __init__(
        self,
        parent: tk.Widget,
        action_data: Optional[Dict[str, Any]] = None,
        workflow_presenter: Any = None
    ):
        """
        Initialize the conditional action editor dialog.
        
        Args:
            parent: The parent widget
            action_data: Initial action data (for editing an existing action)
            workflow_presenter: The workflow presenter for accessing actions
        """
        super().__init__(parent)
        self.parent = parent
        self.action_data = action_data or {"type": "Conditional"}
        self.workflow_presenter = workflow_presenter
        self.result = None
        
        # Set up the dialog
        self.is_edit_mode = bool(action_data and action_data.get("type") == "Conditional")
        self.title("Edit Conditional Action" if self.is_edit_mode else "Add Conditional Action")
        self.geometry("600x500")
        self.minsize(500, 400)
        self.resizable(True, True)
        self.transient(parent)
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        
        # Create variables
        self.name_var = tk.StringVar(self)
        self.condition_type_var = tk.StringVar(self)
        self.selector_var = tk.StringVar(self)
        self.variable_name_var = tk.StringVar(self)
        self.expected_value_var = tk.StringVar(self)
        self.script_var = tk.StringVar(self)
        
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
        
        logger.debug("ConditionalActionEditorDialog initialized")
    
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
        
        # Create the condition frame
        condition_frame = ttk.LabelFrame(self.main_frame, text="Condition")
        condition_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Create the condition type field
        type_frame = ttk.Frame(condition_frame)
        type_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(type_frame, text="Condition Type:").pack(side=tk.LEFT, padx=(0, 5))
        
        condition_types = [
            "element_present",
            "element_not_present",
            "variable_equals",
            "javascript_eval"
        ]
        
        condition_type_combo = ttk.Combobox(
            type_frame,
            textvariable=self.condition_type_var,
            values=condition_types,
            state="readonly",
            width=30
        )
        condition_type_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Bind the condition type change event
        self.condition_type_var.trace_add("write", self._on_condition_type_changed)
        
        # Create the dynamic condition parameters frame
        self.condition_params_frame = ttk.Frame(condition_frame)
        self.condition_params_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Create the branches frame
        branches_frame = ttk.LabelFrame(self.main_frame, text="Action Branches")
        branches_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create a notebook for the branches
        self.branches_notebook = ttk.Notebook(branches_frame)
        self.branches_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create the true branch tab
        self.true_branch_frame = ttk.Frame(self.branches_notebook)
        self.branches_notebook.add(self.true_branch_frame, text="True Branch")
        
        # Create the false branch tab
        self.false_branch_frame = ttk.Frame(self.branches_notebook)
        self.branches_notebook.add(self.false_branch_frame, text="False Branch")
        
        # Create the true branch list
        true_branch_label = ttk.Label(self.true_branch_frame, text="Actions to execute if condition is true:")
        true_branch_label.pack(anchor=tk.W, padx=5, pady=5)
        
        self.true_branch_listbox = tk.Listbox(self.true_branch_frame, height=5)
        self.true_branch_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        true_branch_buttons = ttk.Frame(self.true_branch_frame)
        true_branch_buttons.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(
            true_branch_buttons,
            text="Add Action",
            command=lambda: self._add_branch_action("true_branch")
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            true_branch_buttons,
            text="Remove Action",
            command=lambda: self._remove_branch_action("true_branch")
        ).pack(side=tk.LEFT)
        
        # Create the false branch list
        false_branch_label = ttk.Label(self.false_branch_frame, text="Actions to execute if condition is false:")
        false_branch_label.pack(anchor=tk.W, padx=5, pady=5)
        
        self.false_branch_listbox = tk.Listbox(self.false_branch_frame, height=5)
        self.false_branch_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        false_branch_buttons = ttk.Frame(self.false_branch_frame)
        false_branch_buttons.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(
            false_branch_buttons,
            text="Add Action",
            command=lambda: self._add_branch_action("false_branch")
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            false_branch_buttons,
            text="Remove Action",
            command=lambda: self._remove_branch_action("false_branch")
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
        
        # Initialize the condition type
        if not self.condition_type_var.get():
            self.condition_type_var.set("element_present")
    
    def _on_condition_type_changed(self, *args):
        """Handle changes to the condition type."""
        condition_type = self.condition_type_var.get()
        if not condition_type:
            return
        
        logger.debug(f"Condition type changed to: {condition_type}")
        
        # Clear the condition parameters frame
        for widget in self.condition_params_frame.winfo_children():
            widget.destroy()
        
        # Create the appropriate widgets based on the condition type
        if condition_type in ["element_present", "element_not_present"]:
            self._create_selector_widget()
        elif condition_type == "variable_equals":
            self._create_variable_equals_widgets()
        elif condition_type == "javascript_eval":
            self._create_javascript_eval_widget()
    
    def _create_selector_widget(self):
        """Create the selector widget for element_present and element_not_present conditions."""
        selector_frame = ttk.Frame(self.condition_params_frame)
        selector_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(selector_frame, text="CSS Selector:").pack(side=tk.LEFT, padx=(0, 5))
        
        selector_entry = ttk.Entry(selector_frame, textvariable=self.selector_var, width=30)
        selector_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def _create_variable_equals_widgets(self):
        """Create the widgets for variable_equals conditions."""
        variable_frame = ttk.Frame(self.condition_params_frame)
        variable_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(variable_frame, text="Variable Name:").pack(side=tk.LEFT, padx=(0, 5))
        
        variable_entry = ttk.Entry(variable_frame, textvariable=self.variable_name_var, width=30)
        variable_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        value_frame = ttk.Frame(self.condition_params_frame)
        value_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(value_frame, text="Expected Value:").pack(side=tk.LEFT, padx=(0, 5))
        
        value_entry = ttk.Entry(value_frame, textvariable=self.expected_value_var, width=30)
        value_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def _create_javascript_eval_widget(self):
        """Create the widget for javascript_eval conditions."""
        script_frame = ttk.Frame(self.condition_params_frame)
        script_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(script_frame, text="JavaScript:").pack(side=tk.LEFT, padx=(0, 5))
        
        script_entry = ttk.Entry(script_frame, textvariable=self.script_var, width=30)
        script_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
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
        
        # Set the condition type
        condition_type = action_data.get("condition_type")
        if condition_type:
            self.condition_type_var.set(condition_type)
        
        # Set the condition parameters
        selector = action_data.get("selector")
        if selector:
            self.selector_var.set(selector)
        
        variable_name = action_data.get("variable_name")
        if variable_name:
            self.variable_name_var.set(variable_name)
        
        expected_value = action_data.get("expected_value")
        if expected_value:
            self.expected_value_var.set(expected_value)
        
        script = action_data.get("script")
        if script:
            self.script_var.set(script)
        
        # Initialize the branch actions
        true_branch = action_data.get("true_branch", [])
        for action in true_branch:
            self._add_branch_action_item("true_branch", action)
        
        false_branch = action_data.get("false_branch", [])
        for action in false_branch:
            self._add_branch_action_item("false_branch", action)
    
    def _add_branch_action(self, branch: str):
        """
        Add an action to a branch.
        
        Args:
            branch: The branch to add the action to ("true_branch" or "false_branch")
        """
        # Show an action editor dialog
        from src.ui.factories.dialog_factory import DialogFactory
        
        action_data = DialogFactory.show_action_editor(self)
        if action_data:
            self._add_branch_action_item(branch, action_data)
    
    def _add_branch_action_item(self, branch: str, action_data: Dict[str, Any]):
        """
        Add an action item to a branch listbox.
        
        Args:
            branch: The branch to add the action to ("true_branch" or "false_branch")
            action_data: The action data
        """
        listbox = self.true_branch_listbox if branch == "true_branch" else self.false_branch_listbox
        
        # Format the action for display
        action_type = action_data.get("type", "Unknown")
        action_name = action_data.get("name", action_type)
        
        # Add the action to the listbox
        listbox.insert(tk.END, f"{action_name} ({action_type})")
        
        # Store the action data in the listbox
        index = listbox.size() - 1
        listbox.itemconfig(index, {"action_data": action_data})
    
    def _remove_branch_action(self, branch: str):
        """
        Remove an action from a branch.
        
        Args:
            branch: The branch to remove the action from ("true_branch" or "false_branch")
        """
        listbox = self.true_branch_listbox if branch == "true_branch" else self.false_branch_listbox
        
        # Get the selected index
        selected = listbox.curselection()
        if not selected:
            messagebox.showinfo("No Selection", "Please select an action to remove.", parent=self)
            return
        
        # Remove the action from the listbox
        listbox.delete(selected[0])
    
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
        
        # Validate the condition type
        condition_type = self.condition_type_var.get()
        if not condition_type:
            errors["condition_type"] = "Condition type is required"
        
        # Validate the condition parameters based on the condition type
        if condition_type in ["element_present", "element_not_present"]:
            selector = self.selector_var.get().strip()
            if not selector:
                errors["selector"] = "CSS selector is required"
        elif condition_type == "variable_equals":
            variable_name = self.variable_name_var.get().strip()
            if not variable_name:
                errors["variable_name"] = "Variable name is required"
        elif condition_type == "javascript_eval":
            script = self.script_var.get().strip()
            if not script:
                errors["script"] = "JavaScript code is required"
        
        return errors
    
    def _collect_action_data(self) -> Dict[str, Any]:
        """
        Collect the action data from the dialog inputs.
        
        Returns:
            The action data
        """
        action_data = {
            "type": "Conditional",
            "name": self.name_var.get().strip(),
            "condition_type": self.condition_type_var.get()
        }
        
        # Collect the condition parameters based on the condition type
        if action_data["condition_type"] in ["element_present", "element_not_present"]:
            action_data["selector"] = self.selector_var.get().strip()
        elif action_data["condition_type"] == "variable_equals":
            action_data["variable_name"] = self.variable_name_var.get().strip()
            action_data["expected_value"] = self.expected_value_var.get().strip()
        elif action_data["condition_type"] == "javascript_eval":
            action_data["script"] = self.script_var.get().strip()
        
        # Collect the branch actions
        action_data["true_branch"] = []
        for i in range(self.true_branch_listbox.size()):
            action_data_item = self.true_branch_listbox.itemcget(i, "action_data")
            if action_data_item:
                action_data["true_branch"].append(action_data_item)
        
        action_data["false_branch"] = []
        for i in range(self.false_branch_listbox.size()):
            action_data_item = self.false_branch_listbox.itemcget(i, "action_data")
            if action_data_item:
                action_data["false_branch"].append(action_data_item)
        
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
