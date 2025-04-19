"""Settings view implementation for AutoQliq."""

import tkinter as tk
from tkinter import ttk, filedialog
import logging
from typing import List, Dict, Any, Optional

# Core / Infrastructure
from src.core.exceptions import UIError
from src.config import RepositoryType, BrowserTypeStr # Import literals

# UI elements
from src.ui.interfaces.presenter import IPresenter # Use base presenter interface for now
from src.ui.interfaces.view import IView # Use base view interface
from src.ui.views.base_view import BaseView
from src.ui.common.ui_factory import UIFactory
# Type hint for the specific presenter
from src.ui.presenters.settings_presenter import SettingsPresenter, ISettingsView


class SettingsView(BaseView, ISettingsView):
    """
    View component for managing application settings. Allows users to view and
    modify settings stored in config.ini.
    """
    # Define allowed values for dropdowns (simplified per YAGNI)
    REPO_TYPES: List[RepositoryType] = ["file_system"]
    BROWSER_TYPES: List[BrowserTypeStr] = ["chrome", "firefox", "edge", "safari"]
    LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

    def __init__(self, root: tk.Widget, presenter: SettingsPresenter):
        """
        Initialize the settings view.

        Args:
            root: The parent widget (e.g., a frame in a notebook).
            presenter: The presenter handling the logic for this view.
        """
        super().__init__(root, presenter)
        self.presenter: SettingsPresenter # Type hint

        # Dictionary to hold the tk.StringVar instances for settings
        self.setting_vars: Dict[str, tk.StringVar] = {}

        try:
            self._create_widgets()
            self.logger.info("SettingsView initialized successfully.")
            # Initial population happens via presenter.initialize_view -> presenter.load_settings -> view.set_settings_values
        except Exception as e:
            error_msg = "Failed to create SettingsView widgets"
            self.logger.exception(error_msg) # Log traceback
            self.display_error("Initialization Error", f"{error_msg}: {e}")
            raise UIError(error_msg, component_name="SettingsView", cause=e) from e

    def _create_widgets(self) -> None:
        """Create the UI elements for the settings view."""
        self.logger.debug("Creating settings widgets.")
        # Use grid layout within the main_frame provided by BaseView
        content_frame = UIFactory.create_frame(self.main_frame, padding=10)
        content_frame.pack(fill=tk.BOTH, expand=True)
        content_frame.columnconfigure(1, weight=1) # Allow entry/path fields to expand

        row_index = 0

        # --- General Settings ---
        general_frame = UIFactory.create_label_frame(content_frame, text="General")
        general_frame.grid(row=row_index, column=0, columnspan=3, sticky=tk.NSEW, padx=5, pady=5)
        general_frame.columnconfigure(1, weight=1)
        row_index += 1

        self._create_setting_row(general_frame, 0, "Log Level:", "log_level", "combobox", options={'values': self.LOG_LEVELS})
        self._create_setting_row(general_frame, 1, "Log File:", "log_file", "entry_with_browse", options={'browse_type': 'save_as'})

        # --- Repository Settings ---
        repo_frame = UIFactory.create_label_frame(content_frame, text="Repository")
        repo_frame.grid(row=row_index, column=0, columnspan=3, sticky=tk.NSEW, padx=5, pady=5)
        repo_frame.columnconfigure(1, weight=1)
        row_index += 1

        # Simplified repository settings per YAGNI
        self._create_setting_row(repo_frame, 0, "Workflows Path:", "workflows_path", "entry_with_browse", options={'browse_type': 'directory'})
        self._create_setting_row(repo_frame, 1, "Credentials Path:", "credentials_path", "entry_with_browse", options={'browse_type': 'save_as'})

        # --- WebDriver Settings ---
        wd_frame = UIFactory.create_label_frame(content_frame, text="WebDriver")
        wd_frame.grid(row=row_index, column=0, columnspan=3, sticky=tk.NSEW, padx=5, pady=5)
        wd_frame.columnconfigure(1, weight=1)
        row_index += 1

        self._create_setting_row(wd_frame, 0, "Default Browser:", "default_browser", "combobox", options={'values': self.BROWSER_TYPES})
        self._create_setting_row(wd_frame, 1, "Implicit Wait (sec):", "implicit_wait", "entry", options={'width': 5})
        self._create_setting_row(wd_frame, 2, "ChromeDriver Path:", "chrome_driver_path", "entry_with_browse", options={'browse_type': 'open', 'label_note': '(Optional)'})
        self._create_setting_row(wd_frame, 3, "GeckoDriver Path (FF):", "firefox_driver_path", "entry_with_browse", options={'browse_type': 'open', 'label_note': '(Optional)'})
        self._create_setting_row(wd_frame, 4, "EdgeDriver Path:", "edge_driver_path", "entry_with_browse", options={'browse_type': 'open', 'label_note': '(Optional)'})

        # --- Action Buttons ---
        row_index += 1
        button_frame = UIFactory.create_frame(content_frame, padding="10 10 0 0") # Padding top only
        button_frame.grid(row=row_index, column=0, columnspan=3, sticky=tk.E, pady=10)

        save_btn = UIFactory.create_button(button_frame, text="Save Settings", command=self._on_save)
        save_btn.pack(side=tk.RIGHT, padx=5)
        reload_btn = UIFactory.create_button(button_frame, text="Reload Settings", command=self._on_reload)
        reload_btn.pack(side=tk.RIGHT, padx=5)


        self.logger.debug("Settings widgets created.")

    def _create_setting_row(self, parent: tk.Widget, row: int, label_text: str, setting_key: str, widget_type: str, options: Optional[Dict]=None):
        """Helper to create a label and input widget for a setting."""
        options = options or {}
        var = tk.StringVar()
        self.setting_vars[setting_key] = var

        label = UIFactory.create_label(parent, text=label_text)
        label.grid(row=row, column=0, sticky=tk.W, padx=5, pady=3)
        # Add tooltip/note if provided
        if options.get('label_note'):
             # Simple way: modify label text. Better way: use a tooltip library.
             label.config(text=f"{label_text} {options['label_note']}")


        widget_frame = UIFactory.create_frame(parent, padding=0) # Frame to hold widget + potential button
        widget_frame.grid(row=row, column=1, sticky=tk.EW, padx=5, pady=3)
        widget_frame.columnconfigure(0, weight=1) # Make widget expand

        widget: Optional[tk.Widget] = None

        width = options.get('width', 40) # Default width slightly smaller
        if widget_type == "entry":
             widget = UIFactory.create_entry(widget_frame, textvariable=var, width=width)
             widget.grid(row=0, column=0, sticky=tk.EW)
        elif widget_type == "combobox":
             widget = UIFactory.create_combobox(
                  widget_frame, textvariable=var, values=options.get('values', []),
                  state=options.get('state', 'readonly'), width=width
             )
             widget.grid(row=0, column=0, sticky=tk.EW)
        elif widget_type == "entry_with_browse":
             widget = UIFactory.create_entry(widget_frame, textvariable=var, width=width-5) # Adjust width for button
             widget.grid(row=0, column=0, sticky=tk.EW)
             browse_type = options.get('browse_type', 'open')
             browse_cmd = lambda key=setting_key, btype=browse_type: self._browse_for_path(key, btype)
             browse_btn = UIFactory.create_button(widget_frame, text="...", command=browse_cmd, width=3)
             browse_btn.grid(row=0, column=1, padx=(2,0))
        else:
             self.logger.error(f"Unsupported widget type '{widget_type}' for setting '{setting_key}'")


    def _browse_for_path(self, setting_key: str, browse_type: str):
        """Handles browsing for file or directory."""
        self.logger.debug(f"Browsing for path: Key={setting_key}, Type={browse_type}")
        if setting_key not in self.setting_vars: return
        var = self.setting_vars[setting_key]
        current_path = var.get()
        # Robust initial directory finding
        initial_dir = os.path.abspath(".") # Default to current dir
        if current_path:
             potential_dir = os.path.dirname(current_path)
             if os.path.isdir(potential_dir):
                  initial_dir = potential_dir
             elif os.path.isfile(current_path): # If current path is file, use its dir
                  initial_dir = os.path.dirname(current_path)

        new_path: Optional[str] = None
        parent_window = self.main_frame.winfo_toplevel() # Use toplevel as parent
        try:
             if browse_type == "directory":
                  new_path = filedialog.askdirectory(initialdir=initial_dir, title=f"Select Directory for {setting_key}", parent=parent_window)
             elif browse_type == "open":
                  new_path = filedialog.askopenfilename(initialdir=initial_dir, title=f"Select File for {setting_key}", parent=parent_window)
             elif browse_type == "save_as":
                   new_path = filedialog.asksaveasfilename(initialdir=initial_dir, initialfile=os.path.basename(current_path), title=f"Select File for {setting_key}", parent=parent_window)

             if new_path: var.set(new_path); logger.debug(f"Path selected for {setting_key}: {new_path}")
             else: logger.debug(f"Browse cancelled for {setting_key}")
        except Exception as e:
             self.logger.error(f"Error during file dialog browse: {e}", exc_info=True)
             self.display_error("Browse Error", f"Could not open file dialog: {e}")

    # --- ISettingsView Implementation ---

    def set_settings_values(self, settings: Dict[str, Any]) -> None:
        """Update the view widgets with values from the settings dictionary."""
        self.logger.debug(f"Setting settings values in view: {list(settings.keys())}")
        for key, var in self.setting_vars.items():
            if key in settings:
                 value = settings[key]
                 try: var.set(str(value) if value is not None else "") # Handle None, ensure string
                 except Exception as e: self.logger.error(f"Failed to set view variable '{key}' to '{value}': {e}")
            else:
                 self.logger.warning(f"Setting key '{key}' not found in provided settings data during set.")
                 var.set("") # Clear field if key missing from data


    def get_settings_values(self) -> Dict[str, Any]:
        """Retrieve the current values from the view widgets, attempting type conversion."""
        self.logger.debug("Getting settings values from view.")
        data = {}
        for key, var in self.setting_vars.items():
             try:
                  value_str = var.get()
                  # Attempt type conversion based on key name (heuristic)
                  if key == 'implicit_wait': data[key] = int(value_str)
                  elif key == 'repo_create_if_missing': data[key] = value_str.lower() in ['true', '1', 'yes'] # Basic bool conversion
                  else: data[key] = value_str # Keep others as strings by default
             except (ValueError, TypeError) as e:
                  self.logger.error(f"Error converting value for setting '{key}': {e}. Storing as string.")
                  data[key] = var.get() # Store as string on conversion error
             except Exception as e:
                  self.logger.error(f"Failed to get view variable for setting '{key}': {e}")
                  data[key] = None
        return data

    # --- Internal Event Handlers ---

    def _on_save(self):
        """Handle Save button click."""
        self.logger.debug("Save settings button clicked.")
        # Confirmation before potentially overwriting config.ini
        if self.confirm_action("Save Settings", "Save current settings to config.ini?\nThis may require restarting the application for some changes to take effect."):
            self.presenter.save_settings() # Delegate to presenter

    def _on_reload(self):
        """Handle Reload button click."""
        self.logger.debug("Reload settings button clicked.")
        if self.confirm_action("Reload Settings", "Discard any unsaved changes and reload settings from config.ini?"):
             self.presenter.load_settings() # Delegate reload to presenter