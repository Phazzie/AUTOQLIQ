"""Custom dialog for adding/editing workflow actions."""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging
import os
from typing import Optional, Dict, Any, List

from src.core.exceptions import ValidationError, UIError, ActionError
from src.core.actions.factory import ActionFactory # To get action types and create for validation
from src.ui.common.ui_factory import UIFactory
from src.ui.dialogs.action_selection_dialog import ActionSelectionDialog
# Assuming Action parameter specs are defined or accessible
# For now, use the hardcoded spec within this file.
# from .action_param_specs import ACTION_PARAMS # Ideal approach

logger = logging.getLogger(__name__)

class ActionEditorDialog(tk.Toplevel):
    """
    A modal dialog window for creating or editing workflow action parameters.
    Dynamically displays input fields based on the selected action type.
    Includes improved validation feedback.
    """
    # Define parameter specs for each action type
    # Format: { 'param_key': {'label': 'Label Text', 'widget': 'widget_type', 'options': {<widget_options>}, 'required': bool, 'tooltip': '...' } }
    # Widget Types: 'entry', 'combobox', 'entry_with_browse', 'label_readonly', 'number_entry' (future), 'checkbox' (future)
    ACTION_PARAMS = {
        # ActionBase params (handled separately) - "name"
        "Navigate": {
            "url": {"label": "URL:", "widget": "entry", "required": True, "tooltip": "Full URL (e.g., https://example.com)"}
        },
        "Click": {
            "selector": {"label": "CSS Selector:", "widget": "entry", "required": True, "tooltip": "CSS selector for the element"}
        },
        "Type": {
            "selector": {"label": "CSS Selector:", "widget": "entry", "required": True, "tooltip": "CSS selector for the input field"},
            "value_type": {"label": "Value Type:", "widget": "combobox", "required": True, "options": {"values": ["text", "credential"]}, "tooltip": "Source of the text"},
            "value_key": {"label": "Text / Key:", "widget": "entry", "required": True, "tooltip": "Literal text or credential key (e.g., login.username)"}
        },
        "Wait": {
            "duration_seconds": {"label": "Duration (sec):", "widget": "entry", "required": True, "options": {"width": 10}, "tooltip": "Pause time in seconds (e.g., 1.5)"}
        },
        "Screenshot": {
            "file_path": {"label": "File Path:", "widget": "entry_with_browse", "required": True, "options": {"browse_type": "save_as"}, "tooltip": "Path to save the PNG file"}
        },
        "Conditional": {
            "condition_type": {"label": "Condition:", "widget": "combobox", "required": True, "options": {"values": ["element_present", "element_not_present", "variable_equals"]}, "tooltip": "Condition to evaluate"},
            "selector": {"label": "CSS Selector:", "widget": "entry", "required": False, "tooltip": "Required for element conditions"}, # Required conditionally
            "variable_name": {"label": "Variable Name:", "widget": "entry", "required": False, "tooltip": "Required for variable conditions"},
            "expected_value": {"label": "Expected Value:", "widget": "entry", "required": False, "tooltip": "Required for variable conditions"},
            "true_branch": {"label": "True Actions:", "widget": "label_readonly", "required": False, "tooltip": "Edit in main list"},
            "false_branch": {"label": "False Actions:", "widget": "label_readonly", "required": False, "tooltip": "Edit in main list"}
        },
        "Loop": {
            "loop_type": {"label": "Loop Type:", "widget": "combobox", "required": True, "options": {"values": ["count", "for_each"]}, "tooltip": "Type of loop"},
            "count": {"label": "Iterations:", "widget": "entry", "required": False, "options": {"width": 10}, "tooltip": "Required for 'count' loop"},
            "list_variable_name": {"label": "List Variable:", "widget": "entry", "required": False, "tooltip": "Context variable name holding list for 'for_each'"},
            "loop_actions": {"label": "Loop Actions:", "widget": "label_readonly", "required": False, "tooltip": "Edit in main list"}
        },
        "ErrorHandling": {
             "try_actions": {"label": "Try Actions:", "widget": "label_readonly", "required": False, "tooltip": "Edit in main list"},
             "catch_actions": {"label": "Catch Actions:", "widget": "label_readonly", "required": False, "tooltip": "Edit in main list"}
        },
        "Template": {
            "template_name": {"label": "Template Name:", "widget": "entry", "required": True, "tooltip": "Name of the saved template to execute"}
        }
        # Add new action types and their parameters here
    }


    def __init__(self, parent: tk.Widget, initial_data: Optional[Dict[str, Any]] = None):
        """Initialize the Action Editor Dialog."""
        super().__init__(parent)
        self.parent = parent
        self.initial_data = initial_data or {}
        self.result: Optional[Dict[str, Any]] = None

        self.is_edit_mode = bool(initial_data)
        self.title("Edit Action" if self.is_edit_mode else "Add Action")

        self.resizable(False, False)
        self.transient(parent)
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

        self._action_type_var = tk.StringVar(self)
        # Stores {'param_key': {'label': Label, 'widget': Widget, 'var': StringVar/IntVar, 'frame': Frame (optional)}}
        self._param_widgets: Dict[str, Dict[str, Any]] = {}
        self._param_frame: Optional[ttk.Frame] = None

        try:
            self._create_widgets()
            self._populate_initial_data()
        except Exception as e:
            logger.exception("Failed to create ActionEditorDialog UI.")
            messagebox.showerror("Dialog Error", f"Failed to initialize action editor: {e}", parent=parent)
            self.destroy()
            return # Exit init if UI fails

        self.grab_set() # Make modal AFTER widgets potentially created
        self._center_window()
        # Don't call wait_window here; call show() externally


    def _create_widgets(self):
        """Create the widgets for the dialog."""
        main_frame = UIFactory.create_frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(1, weight=1)

        # --- Action Type ---
        row = 0
        UIFactory.create_label(main_frame, text="Action Type:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        action_types = ActionFactory.get_registered_action_types()
        if not action_types: raise UIError("No action types registered.")

        # Create a frame for the action type selection
        type_frame = UIFactory.create_frame(main_frame)
        type_frame.grid(row=row, column=1, sticky=tk.EW, padx=5, pady=5)
        type_frame.columnconfigure(0, weight=1)

        # Create a label to display the selected action type
        self._type_label = UIFactory.create_label(
            type_frame,
            textvariable=self._action_type_var,
            width=30,
            anchor=tk.W,
            relief=tk.SUNKEN,
            borderwidth=1,
            padding=(5, 2)
        )
        self._type_label.grid(row=0, column=0, sticky=tk.EW)

        # Create a button to open the action selection dialog
        select_button = UIFactory.create_button(
            type_frame,
            text="Select...",
            command=self._show_action_selection_dialog,
            width=10
        )
        select_button.grid(row=0, column=1, padx=(5, 0))

        # Set initial type before trace, otherwise trace runs with default empty value first
        initial_type = self.initial_data.get("type", action_types[0])
        if initial_type not in action_types: initial_type = action_types[0]
        self._action_type_var.set(initial_type)
        self._action_type_var.trace_add("write", self._on_type_change)

        # --- Action Name ---
        row += 1
        # Use helper to create + store name widget references
        self._create_parameter_widget(main_frame, "name", "Action Name:", "entry", row=row, options={'width': 50})

        # --- Dynamic Parameter Frame ---
        row += 1
        self._param_frame = UIFactory.create_label_frame(main_frame, text="Parameters")
        self._param_frame.grid(row=row, column=0, columnspan=2, sticky=tk.NSEW, pady=10)
        self._param_frame.columnconfigure(1, weight=1)

        # --- Buttons ---
        row += 1
        button_frame = UIFactory.create_frame(main_frame, padding="5 0 0 0")
        button_frame.grid(row=row, column=0, columnspan=2, sticky=tk.E, pady=(10, 0))

        cancel_button = UIFactory.create_button(button_frame, text="Cancel", command=self._on_cancel)
        cancel_button.pack(side=tk.RIGHT, padx=5)
        ok_button = UIFactory.create_button(button_frame, text="OK", command=self._on_ok)
        ok_button.pack(side=tk.RIGHT)
        self.bind('<Return>', lambda e: self._on_ok())
        self.bind('<Escape>', lambda e: self._on_cancel())

    def _populate_initial_data(self):
        """Fill fields with initial data if in edit mode."""
        # Name is populated separately
        name_var = self._param_widgets.get("name", {}).get("var")
        if name_var:
             # Use initial name if present, otherwise default to action type
             name_val = self.initial_data.get("name", self._action_type_var.get())
             name_var.set(name_val)

        # Populate dynamic fields based on current (initial) type
        self._update_parameter_fields() # This will now populate values for the initial type


    def _on_type_change(self, *args):
        """Callback when the action type combobox value changes."""
        action_type = self._action_type_var.get()
        # Update default name if name hasn't been manually changed
        name_var = self._param_widgets["name"]["var"]
        current_name = name_var.get()
        registered_types = ActionFactory.get_registered_action_types()
        if current_name in registered_types or not current_name: # Update if default or empty
             name_var.set(action_type)

        self._update_parameter_fields() # Regenerate fields for new type

    def _update_parameter_fields(self):
        """Clear and recreate parameter widgets based on selected action type."""
        if not self._param_frame: return
        action_type = self._action_type_var.get()
        logger.debug(f"Updating parameters for action type: {action_type}")

        # Clear existing dynamic widgets
        for widget in self._param_frame.winfo_children(): widget.destroy()
        # Clear non-name entries from _param_widgets dict
        keys_to_delete = [k for k in self._param_widgets if k != 'name']
        for key in keys_to_delete: del self._param_widgets[key]

        # --- Create Fields for Selected Action Type ---
        param_specs = self.ACTION_PARAMS.get(action_type, {})
        row = 0
        for key, spec in param_specs.items():
            initial_val = self.initial_data.get(key) if self.is_edit_mode else None
            # Create widget using helper, which now handles initial value setting
            self._create_parameter_widget(
                self._param_frame, key,
                spec.get("label", key.replace('_', ' ').title() + ":"),
                spec.get("widget", "entry"),
                row=row, options=spec.get("options", {}), initial_value=initial_val
            )
            row += 1

    def _create_parameter_widget(self, parent: tk.Widget, key: str, label_text: str, widget_type: str, row: int, options: Optional[Dict]=None, initial_value: Optional[Any]=None):
        """Helper to create label, input widget, store references, and set initial value."""
        options = options or {}
        var: Optional[tk.Variable] = None
        widget: Optional[tk.Widget] = None
        browse_btn: Optional[tk.Widget] = None
        width = options.get('width', 40)

        # Determine variable type and create var
        # Add more types like BooleanVar if Checkbox is used
        var = tk.StringVar(self)
        self._param_widgets[key] = {'label': None, 'widget': None, 'var': var, 'browse_btn': None} # Store var first

        label = UIFactory.create_label(parent, text=label_text)
        label.grid(row=row, column=0, sticky=tk.W, padx=5, pady=3)
        self._param_widgets[key]['label'] = label

        # Create widget
        widget_frame_needed = widget_type == "entry_with_browse"
        container = UIFactory.create_frame(parent, padding=0) if widget_frame_needed else parent

        if widget_type == "entry":
             widget = UIFactory.create_entry(container, textvariable=var, width=width, **options.get('config', {}))
        elif widget_type == "combobox":
             widget = UIFactory.create_combobox(
                  container, textvariable=var, values=options.get('values', []),
                  state=options.get('state', 'readonly'), width=width-2
             )
        elif widget_type == "entry_with_browse":
             entry_frame = container # Use the frame created above
             entry_frame.columnconfigure(0, weight=1)
             widget = UIFactory.create_entry(entry_frame, textvariable=var, width=width-5)
             widget.grid(row=0, column=0, sticky=tk.EW)
             browse_type = options.get('browse_type', 'open')
             browse_cmd = lambda k=key, btype=browse_type: self._browse_for_path(k, btype)
             browse_btn = UIFactory.create_button(entry_frame, text="...", command=browse_cmd, width=3)
             browse_btn.grid(row=0, column=1, padx=(2,0))
             widget = entry_frame # Main widget for grid placement is the frame
        elif widget_type == "label_readonly":
             display_text = ""
             if initial_value is not None and isinstance(initial_value, list):
                  display_text = f"({len(initial_value)} actions, edit in main list)"
             else:
                  display_text = str(initial_value) if initial_value is not None else "(Not editable)"
             var.set(display_text)
             widget = UIFactory.create_label(container, textvariable=var, anchor=tk.W, relief=tk.SUNKEN, borderwidth=1, padding=(3,1))
        # Add other widget types here

        # Grid the widget/container
        if widget:
            grid_target = container if widget_frame_needed else widget
            grid_target.grid(row=row, column=1, sticky=tk.EW, padx=5, pady=3)
            self._param_widgets[key]['widget'] = widget
            self._param_widgets[key]['browse_btn'] = browse_btn

        # Set initial value *after* widget creation
        if initial_value is not None and widget_type != "label_readonly":
             try: var.set(str(initial_value))
             except tk.TclError as e: logger.warning(f"Could not set initial value for '{key}': {e}")


    def _browse_for_path(self, setting_key: str, browse_type: str):
         """Handles browsing for file or directory for a parameter field."""
         if setting_key not in self._param_widgets: return
         var = self._param_widgets[setting_key]['var']
         current_path = var.get()
         initial_dir = os.path.abspath(".")
         if current_path:
              potential_dir = os.path.dirname(current_path)
              if os.path.isdir(potential_dir): initial_dir = potential_dir
              elif os.path.isfile(current_path): initial_dir = os.path.dirname(current_path)

         new_path: Optional[str] = None
         parent_window = self # Use dialog as parent
         try:
              if browse_type == "directory": new_path = filedialog.askdirectory(initialdir=initial_dir, title=f"Select Directory", parent=parent_window)
              elif browse_type == "open": new_path = filedialog.askopenfilename(initialdir=initial_dir, title=f"Select File", parent=parent_window)
              elif browse_type == "save_as": new_path = filedialog.asksaveasfilename(initialdir=initial_dir, initialfile=os.path.basename(current_path), title=f"Select File Path", parent=parent_window)

              if new_path: var.set(new_path); logger.debug(f"Path selected for {setting_key}: {new_path}")
              else: logger.debug(f"Browse cancelled for {setting_key}")
         except Exception as e:
              logger.error(f"Error during file dialog browse: {e}", exc_info=True)
              messagebox.showerror("Browse Error", f"Could not open file dialog: {e}", parent=self)

    def _on_ok(self):
        """Validate data using ActionFactory/Action.validate and close dialog."""
        action_data = {"type": self._action_type_var.get()}
        validation_errors = {}
        action_params_spec = self.ACTION_PARAMS.get(action_data["type"], {})

        # Collect data and perform basic type conversion
        for key, widgets in self._param_widgets.items():
            spec = action_params_spec.get(key, {})
            widget_type = spec.get('widget', 'entry')

            if widget_type == "label_readonly": # Skip read-only display fields
                # Keep original nested data if editing, otherwise empty list
                action_data[key] = self.initial_data.get(key, []) if self.is_edit_mode else []
                continue

            try:
                value_str = widgets["var"].get()
                value: Any = value_str # Start as string

                # Attempt type conversion based on known param names or hints
                if key == "count":
                     try: value = int(value_str) if value_str else None # Allow empty count? No, validation handles it.
                     except (ValueError, TypeError): validation_errors[key] = "Iterations must be an integer."
                elif key == "duration_seconds":
                     try: value = float(value_str) if value_str else None
                     except (ValueError, TypeError): validation_errors[key] = "Duration must be a number."
                # Add boolean conversion if checkbox is added

                action_data[key] = value # Store potentially converted value

            except Exception as e:
                 logger.error(f"Error retrieving value for param '{key}': {e}")
                 validation_errors[key] = "Error retrieving value."

        if validation_errors:
             error_msg = "Input Errors:\n\n" + "\n".join([f"- {k}: {v}" for k, v in validation_errors.items()])
             messagebox.showerror("Validation Failed", error_msg, parent=self)
             return

        # --- Final validation using ActionFactory and Action's validate() ---
        try:
            # Create temporary instance to run validation
            temp_action = ActionFactory.create_action(action_data)
            temp_action.validate() # This should raise ValidationError if invalid
            logger.debug("Action data validated successfully using action class.")
            # If valid, set result and close
            self.result = action_data
            self.destroy()
        except ValidationError as e:
             logger.warning(f"Action validation failed: {e}. Data: {action_data}")
             # Display the specific validation error message from the action
             messagebox.showerror("Validation Failed", f"Invalid action parameters:\n\n{e}", parent=self)
        except (ActionError, TypeError) as e: # Catch factory errors too
             logger.error(f"Action creation/validation failed: {e}. Data: {action_data}")
             messagebox.showerror("Validation Failed", f"Could not validate action:\n\n{e}", parent=self)
        except Exception as e:
             logger.error(f"Unexpected error validating action: {e}. Data: {action_data}", exc_info=True)
             messagebox.showerror("Validation Error", f"Unexpected error validating action:\n\n{e}", parent=self)

    def _on_cancel(self):
        """Close the dialog without setting a result."""
        self.result = None
        self.destroy()

    def _center_window(self):
        """Centers the dialog window on the parent."""
        self.update_idletasks()
        parent_win = self.parent.winfo_toplevel()
        parent_x = parent_win.winfo_rootx(); parent_y = parent_win.winfo_rooty()
        parent_w = parent_win.winfo_width(); parent_h = parent_win.winfo_height()
        win_w = self.winfo_reqwidth(); win_h = self.winfo_reqheight()
        pos_x = parent_x + (parent_w // 2) - (win_w // 2)
        pos_y = parent_y + (parent_h // 2) - (win_h // 2)
        screen_w = self.winfo_screenwidth(); screen_h = self.winfo_screenheight()
        pos_x = max(0, min(pos_x, screen_w - win_w)); pos_y = max(0, min(pos_y, screen_h - win_h))
        self.geometry(f"+{pos_x}+{pos_y}")


    def _show_action_selection_dialog(self):
        """Show the action selection dialog and update the action type."""
        try:
            # Create and show the action selection dialog
            dialog = ActionSelectionDialog(self)
            selected_action = dialog.show()

            # Update the action type if an action was selected
            if selected_action:
                self._action_type_var.set(selected_action)
                # The trace callback will handle updating the parameter fields
        except Exception as e:
            logger.error(f"Error showing action selection dialog: {e}", exc_info=True)
            messagebox.showerror("Dialog Error", f"Could not open action selection dialog: {e}", parent=self)

    def show(self) -> Optional[Dict[str, Any]]:
        """Make the dialog visible and wait for user interaction."""
        self.wait_window() # Blocks until destroy() is called
        return self.result