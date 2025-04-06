"""Workflow runner view implementation for AutoQliq."""

import tkinter as tk
from tkinter import ttk, scrolledtext
import logging
from typing import List, Optional, Dict, Any

# Core / Infrastructure
from src.core.exceptions import UIError

# UI elements
from src.ui.interfaces.presenter import IWorkflowRunnerPresenter
from src.ui.interfaces.view import IWorkflowRunnerView
from src.ui.views.base_view import BaseView
from src.ui.common.ui_factory import UIFactory


class WorkflowRunnerView(BaseView, IWorkflowRunnerView):
    """
    View component for the workflow runner. Displays workflows and credentials,
    allows starting/stopping execution, and shows logs. Forwards user interactions
    to the WorkflowRunnerPresenter.
    """

    def __init__(self, root: tk.Widget, presenter: IWorkflowRunnerPresenter):
        """
        Initialize the workflow runner view.

        Args:
            root: The parent widget (e.g., a frame in a notebook).
            presenter: The presenter handling the logic for this view.
        """
        super().__init__(root, presenter)
        self.presenter: IWorkflowRunnerPresenter # Type hint

        # Widgets specific to this view
        self.workflow_list_widget: Optional[tk.Listbox] = None
        self.credential_combobox: Optional[ttk.Combobox] = None
        self.credential_var: Optional[tk.StringVar] = None # To hold selected credential name
        self.run_button: Optional[ttk.Button] = None
        self.stop_button: Optional[ttk.Button] = None
        self.log_text_widget: Optional[tk.Text] = None

        try:
            self._create_widgets()
            self.logger.info("WorkflowRunnerView initialized successfully.")
            # Initial population is handled by presenter.initialize_view()
        except Exception as e:
            error_msg = "Failed to create WorkflowRunnerView widgets"
            self.logger.exception(error_msg)
            self.display_error("Initialization Error", f"{error_msg}: {e}")
            raise UIError(error_msg, component_name="WorkflowRunnerView", cause=e) from e

    def _create_widgets(self) -> None:
        """Create the UI elements for the runner view."""
        self.logger.debug("Creating runner widgets.")

        # Configure grid weights for main_frame resizing
        # Let log area take most space, list/controls fixed width
        self.main_frame.rowconfigure(0, weight=1) # Top row (list & controls)
        self.main_frame.rowconfigure(1, weight=3) # Bottom row (log area)
        self.main_frame.columnconfigure(0, weight=1, minsize=150) # Workflow list column
        self.main_frame.columnconfigure(1, weight=0) # Controls column (fixed)
        self.main_frame.columnconfigure(2, weight=3, minsize=300) # Log area column

        # --- Workflow List Section ---
        wf_list_frame = UIFactory.create_label_frame(self.main_frame, text="Workflows")
        wf_list_frame.grid(row=0, column=0, rowspan=2, sticky=tk.NSEW, padx=(0, 5), pady=(0, 5))
        wf_list_frame.rowconfigure(0, weight=1)
        wf_list_frame.columnconfigure(0, weight=1)

        wf_scrolled_list = UIFactory.create_scrolled_listbox(wf_list_frame, height=15, selectmode=tk.BROWSE)
        self.workflow_list_widget = wf_scrolled_list["listbox"]
        wf_scrolled_list["frame"].grid(row=0, column=0, sticky=tk.NSEW)
        # Bind selection change to enable/disable run button
        self.workflow_list_widget.bind("<<ListboxSelect>>", self._on_selection_change)

        # --- Controls Section ---
        control_frame = UIFactory.create_label_frame(self.main_frame, text="Controls")
        control_frame.grid(row=0, column=1, sticky=tk.NSEW, padx=(0, 5), pady=(0, 5))
        # Prevent control frame from expanding vertically much
        # self.main_frame.rowconfigure(0, weight=0) # Revisit this if layout is bad

        # Credential selection
        cred_label = UIFactory.create_label(control_frame, text="Credential:")
        cred_label.pack(anchor=tk.W, padx=5, pady=(5, 0))

        self.credential_var = tk.StringVar(self.main_frame)
        self.credential_combobox = UIFactory.create_combobox(
            control_frame,
            textvariable=self.credential_var,
            state="readonly", # User must select from list
            width=25 # Adjust width as needed
        )
        self.credential_combobox.pack(anchor=tk.W, padx=5, pady=(0, 10), fill=tk.X)
        self.credential_combobox.bind("<<ComboboxSelected>>", self._on_selection_change)

        # Run/Stop Buttons
        button_frame = UIFactory.create_frame(control_frame, padding=0)
        button_frame.pack(anchor=tk.CENTER, pady=(10, 5)) # Center buttons

        self.run_button = UIFactory.create_button(button_frame, text="Run Workflow", command=self._on_run_workflow, state=tk.DISABLED)
        self.run_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = UIFactory.create_button(button_frame, text="Stop Workflow", command=self._on_stop_workflow, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        # --- Log Area Section ---
        log_frame = UIFactory.create_label_frame(self.main_frame, text="Execution Log")
        log_frame.grid(row=0, column=2, rowspan=2, sticky=tk.NSEW, pady=(0,5)) # Span both rows
        log_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)

        log_scrolled_text = UIFactory.create_scrolled_text(log_frame, state=tk.DISABLED, height=20)
        self.log_text_widget = log_scrolled_text["text"]
        log_scrolled_text["frame"].grid(row=0, column=0, sticky=tk.NSEW)

        self.logger.debug("Runner widgets created.")

     # --- IWorkflowRunnerView Implementation ---

    def set_workflow_list(self, workflow_names: List[str]) -> None:
        """Populate the workflow listbox."""
        if not self.workflow_list_widget: return
        self.logger.debug(f"Setting workflow list with {len(workflow_names)} items.")
        # Store current selection
        selected_name = self.get_selected_workflow_name()
        # Clear and repopulate
        self.workflow_list_widget.delete(0, tk.END)
        for name in sorted(workflow_names):
            self.workflow_list_widget.insert(tk.END, name)
        # Try re-selecting
        if selected_name in workflow_names:
             try:
                  idx = workflow_names.index(selected_name)
                  self.workflow_list_widget.selection_set(idx)
                  self.workflow_list_widget.activate(idx)
                  self.workflow_list_widget.see(idx)
             except ValueError: pass
        self._on_selection_change() # Update button state

    def set_credential_list(self, credential_names: List[str]) -> None:
        """Populate the credential combobox."""
        if not self.credential_combobox: return
        self.logger.debug(f"Setting credential list with {len(credential_names)} items.")
        current_value = self.credential_var.get() if self.credential_var else None
        sorted_names = sorted(credential_names)
        self.credential_combobox['values'] = sorted_names
        # Try re-selecting or select first item
        if current_value in sorted_names:
            self.credential_var.set(current_value)
        elif sorted_names:
            self.credential_var.set(sorted_names[0])
        else:
             self.credential_var.set("") # Clear if list is empty
        self._on_selection_change() # Update button state

    def get_selected_workflow_name(self) -> Optional[str]:
        """Get the name of the currently selected workflow."""
        if not self.workflow_list_widget: return None
        selection_indices = self.workflow_list_widget.curselection()
        return self.workflow_list_widget.get(selection_indices[0]) if selection_indices else None

    def get_selected_credential_name(self) -> Optional[str]:
        """Get the name of the currently selected credential."""
        return self.credential_var.get() if self.credential_var and self.credential_var.get() else None

    def log_message(self, message: str) -> None:
        """Append a message to the execution log."""
        if not self.log_text_widget: return
        try:
            # Ensure widget is enabled for modification
            current_state = self.log_text_widget['state']
            self.log_text_widget.config(state=tk.NORMAL)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.log_text_widget.insert(tk.END, f"[{timestamp}] {message}\n")
            self.log_text_widget.see(tk.END) # Scroll to the end
            self.log_text_widget.config(state=current_state) # Restore original state
        except tk.TclError as e:
             self.logger.error(f"Failed to log message to text widget: {e}")
        except Exception as e:
             self.logger.exception(f"Unexpected error logging message: {e}")


    def clear_log(self) -> None:
        """Clear the execution log."""
        if not self.log_text_widget: return
        try:
            current_state = self.log_text_widget['state']
            self.log_text_widget.config(state=tk.NORMAL)
            self.log_text_widget.delete('1.0', tk.END)
            self.log_text_widget.config(state=current_state)
            self.logger.debug("Log cleared.")
        except tk.TclError as e:
             self.logger.error(f"Failed to clear log text widget: {e}")

    def set_running_state(self, is_running: bool) -> None:
        """Update UI controls based on running state."""
        self.logger.debug(f"Setting running state: {is_running}")
        run_state = tk.DISABLED if is_running else tk.NORMAL
        stop_state = tk.NORMAL if is_running else tk.DISABLED
        # Disable list/combo when running? Maybe allow selection but disable Run?
        select_state = tk.DISABLED if is_running else tk.NORMAL
        combo_select_state = tk.DISABLED if is_running else "readonly"

        if self.run_button: self.run_button.config(state=run_state)
        if self.stop_button: self.stop_button.config(state=stop_state)
        if self.workflow_list_widget: self.workflow_list_widget.config(state=select_state)
        if self.credential_combobox: self.credential_combobox.config(state=combo_select_state)
        # Also update general status bar if integrated
        status_msg = "Workflow running..." if is_running else "Ready."
        self.set_status(status_msg)

    def clear(self) -> None:
        """Clear lists and log."""
        self.logger.debug("Clearing runner view.")
        if self.workflow_list_widget: self.workflow_list_widget.delete(0, tk.END)
        if self.credential_combobox: self.credential_combobox['values'] = []
        if self.credential_var: self.credential_var.set("")
        self.clear_log()
        self.set_running_state(False) # Ensure buttons are in correct default state

    # --- Internal Event Handlers ---

    def _on_selection_change(self, event: Optional[tk.Event] = None) -> None:
        """Enable/disable run button based on selections."""
        can_run = self.get_selected_workflow_name() is not None and self.get_selected_credential_name() is not None
        if self.run_button:
            self.run_button.config(state=tk.NORMAL if can_run else tk.DISABLED)

    def _on_run_workflow(self) -> None:
        """Handle 'Run Workflow' button press."""
        self.logger.debug("Run workflow button pressed.")
        workflow = self.get_selected_workflow_name()
        credential = self.get_selected_credential_name()
        if workflow: # Credential might be optional, presenter handles None
            self.presenter.run_workflow(workflow, credential)
        else:
             self.display_message("Run Error", "Please select a workflow to run.")


    def _on_stop_workflow(self) -> None:
        """Handle 'Stop Workflow' button press."""
        self.logger.debug("Stop workflow button pressed.")
        self.presenter.stop_workflow()