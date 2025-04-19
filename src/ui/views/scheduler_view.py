"""Scheduler view implementation for AutoQliq."""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime, timedelta

# Core / Infrastructure
from src.core.exceptions import UIError

# UI elements
from src.ui.interfaces.presenter import ISchedulerPresenter
from src.ui.interfaces.view import ISchedulerView
from src.ui.views.base_view import BaseView
from src.ui.common.ui_factory import UIFactory


class SchedulerView(BaseView, ISchedulerView):
    """
    View component for the workflow scheduler. Displays scheduled jobs,
    allows creating new schedules, and managing existing ones.
    """

    def __init__(self, root: tk.Widget, presenter: ISchedulerPresenter):
        """
        Initialize the scheduler view.

        Args:
            root: The parent widget (e.g., a frame in a notebook).
            presenter: The presenter handling the logic for this view.
        """
        super().__init__(root, presenter)
        self.presenter: ISchedulerPresenter  # Type hint

        # Widgets specific to this view
        self.job_list_widget: Optional[ttk.Treeview] = None
        self.workflow_combobox: Optional[ttk.Combobox] = None
        self.credential_combobox: Optional[ttk.Combobox] = None
        self.schedule_type_combobox: Optional[ttk.Combobox] = None
        self.schedule_config_frame: Optional[ttk.Frame] = None
        self.schedule_config_widgets: Dict[str, Dict[str, tk.Widget]] = {}
        
        # Create the UI components
        self._create_ui()
        
    def _create_ui(self) -> None:
        """Create the UI components."""
        # Main layout: split into two frames (left for job list, right for config)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(0, weight=1)
        
        # Left side: Job list
        job_list_frame = ttk.LabelFrame(self.main_frame, text="Scheduled Jobs")
        job_list_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=(0, 5), pady=5)
        job_list_frame.rowconfigure(0, weight=1)
        job_list_frame.columnconfigure(0, weight=1)
        
        # Create treeview for job list
        self.job_list_widget = ttk.Treeview(
            job_list_frame, 
            columns=("workflow", "next_run", "schedule"),
            show="headings"
        )
        self.job_list_widget.heading("workflow", text="Workflow")
        self.job_list_widget.heading("next_run", text="Next Run")
        self.job_list_widget.heading("schedule", text="Schedule")
        self.job_list_widget.column("workflow", width=150)
        self.job_list_widget.column("next_run", width=150)
        self.job_list_widget.column("schedule", width=150)
        
        # Add scrollbar to treeview
        job_list_scrollbar = ttk.Scrollbar(job_list_frame, orient=tk.VERTICAL, command=self.job_list_widget.yview)
        self.job_list_widget.configure(yscrollcommand=job_list_scrollbar.set)
        
        # Pack treeview and scrollbar
        self.job_list_widget.grid(row=0, column=0, sticky=tk.NSEW)
        job_list_scrollbar.grid(row=0, column=1, sticky=tk.NS)
        
        # Add buttons for job management
        job_buttons_frame = ttk.Frame(job_list_frame)
        job_buttons_frame.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=5)
        
        refresh_button = ttk.Button(job_buttons_frame, text="Refresh", command=self._on_refresh_jobs)
        refresh_button.pack(side=tk.LEFT, padx=5)
        
        cancel_button = ttk.Button(job_buttons_frame, text="Cancel Job", command=self._on_cancel_job)
        cancel_button.pack(side=tk.LEFT, padx=5)
        
        # Right side: Schedule configuration
        config_frame = ttk.LabelFrame(self.main_frame, text="Create Schedule")
        config_frame.grid(row=0, column=1, sticky=tk.NSEW, padx=(5, 0), pady=5)
        config_frame.columnconfigure(1, weight=1)
        
        # Workflow selection
        ttk.Label(config_frame, text="Workflow:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.workflow_combobox = ttk.Combobox(config_frame, state="readonly")
        self.workflow_combobox.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        self.workflow_combobox.bind("<<ComboboxSelected>>", lambda e: self._update_ui_state())
        
        # Credential selection
        ttk.Label(config_frame, text="Credential:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.credential_combobox = ttk.Combobox(config_frame, state="readonly")
        self.credential_combobox.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # Schedule type selection
        ttk.Label(config_frame, text="Schedule Type:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.schedule_type_combobox = ttk.Combobox(config_frame, state="readonly", 
                                                  values=["Interval", "Cron", "One-time"])
        self.schedule_type_combobox.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        self.schedule_type_combobox.bind("<<ComboboxSelected>>", self._on_schedule_type_changed)
        
        # Frame for schedule configuration (changes based on schedule type)
        self.schedule_config_frame = ttk.Frame(config_frame)
        self.schedule_config_frame.grid(row=3, column=0, columnspan=2, sticky=tk.NSEW, padx=5, pady=5)
        
        # Create schedule button
        schedule_button = ttk.Button(config_frame, text="Create Schedule", command=self._on_create_schedule)
        schedule_button.grid(row=4, column=0, columnspan=2, pady=10)
        
        # Initialize the UI state
        self._update_ui_state()
        
    def _create_interval_config(self) -> None:
        """Create configuration widgets for interval schedule."""
        # Clear existing widgets
        for widget in self.schedule_config_frame.winfo_children():
            widget.destroy()
            
        # Create new widgets for interval schedule
        self.schedule_config_widgets["interval"] = {}
        
        # Interval value
        ttk.Label(self.schedule_config_frame, text="Run every:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        interval_frame = ttk.Frame(self.schedule_config_frame)
        interval_frame.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        interval_value = tk.StringVar(value="1")
        interval_entry = ttk.Entry(interval_frame, width=5, textvariable=interval_value)
        interval_entry.pack(side=tk.LEFT, padx=(0, 5))
        self.schedule_config_widgets["interval"]["value"] = interval_entry
        
        interval_unit = tk.StringVar(value="hours")
        interval_unit_combo = ttk.Combobox(interval_frame, width=10, textvariable=interval_unit, 
                                          state="readonly", values=["seconds", "minutes", "hours", "days", "weeks"])
        interval_unit_combo.pack(side=tk.LEFT)
        self.schedule_config_widgets["interval"]["unit"] = interval_unit_combo
        
        # Start date/time
        ttk.Label(self.schedule_config_frame, text="Start at:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        start_frame = ttk.Frame(self.schedule_config_frame)
        start_frame.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # Default to current time + 1 minute, rounded to nearest minute
        now = datetime.now() + timedelta(minutes=1)
        now = now.replace(second=0, microsecond=0)
        
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M")
        
        date_var = tk.StringVar(value=date_str)
        date_entry = ttk.Entry(start_frame, width=10, textvariable=date_var)
        date_entry.pack(side=tk.LEFT, padx=(0, 5))
        self.schedule_config_widgets["interval"]["start_date"] = date_entry
        
        time_var = tk.StringVar(value=time_str)
        time_entry = ttk.Entry(start_frame, width=5, textvariable=time_var)
        time_entry.pack(side=tk.LEFT)
        self.schedule_config_widgets["interval"]["start_time"] = time_entry
        
        # Help text
        ttk.Label(self.schedule_config_frame, 
                 text="Date format: YYYY-MM-DD, Time format: HH:MM").grid(
                     row=2, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
    def _create_cron_config(self) -> None:
        """Create configuration widgets for cron schedule."""
        # Clear existing widgets
        for widget in self.schedule_config_frame.winfo_children():
            widget.destroy()
            
        # Create new widgets for cron schedule
        self.schedule_config_widgets["cron"] = {}
        
        # Cron expression fields
        cron_fields = [
            ("Minute (0-59)", "minute", "0"),
            ("Hour (0-23)", "hour", "*"),
            ("Day of month (1-31)", "day", "*"),
            ("Month (1-12)", "month", "*"),
            ("Day of week (0-6, 0=Monday)", "day_of_week", "*")
        ]
        
        for i, (label_text, field_name, default_value) in enumerate(cron_fields):
            ttk.Label(self.schedule_config_frame, text=label_text).grid(
                row=i, column=0, sticky=tk.W, padx=5, pady=5)
            
            value_var = tk.StringVar(value=default_value)
            entry = ttk.Entry(self.schedule_config_frame, textvariable=value_var)
            entry.grid(row=i, column=1, sticky=tk.EW, padx=5, pady=5)
            self.schedule_config_widgets["cron"][field_name] = entry
            
        # Help text
        ttk.Label(self.schedule_config_frame, 
                 text="Use * for any, */n for every n, or comma-separated values").grid(
                     row=len(cron_fields), column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
    def _create_date_config(self) -> None:
        """Create configuration widgets for one-time schedule."""
        # Clear existing widgets
        for widget in self.schedule_config_frame.winfo_children():
            widget.destroy()
            
        # Create new widgets for one-time schedule
        self.schedule_config_widgets["date"] = {}
        
        # Run date/time
        ttk.Label(self.schedule_config_frame, text="Run at:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        date_time_frame = ttk.Frame(self.schedule_config_frame)
        date_time_frame.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # Default to current time + 1 hour, rounded to nearest minute
        now = datetime.now() + timedelta(hours=1)
        now = now.replace(second=0, microsecond=0)
        
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M")
        
        date_var = tk.StringVar(value=date_str)
        date_entry = ttk.Entry(date_time_frame, width=10, textvariable=date_var)
        date_entry.pack(side=tk.LEFT, padx=(0, 5))
        self.schedule_config_widgets["date"]["run_date"] = date_entry
        
        time_var = tk.StringVar(value=time_str)
        time_entry = ttk.Entry(date_time_frame, width=5, textvariable=time_var)
        time_entry.pack(side=tk.LEFT)
        self.schedule_config_widgets["date"]["run_time"] = time_entry
        
        # Help text
        ttk.Label(self.schedule_config_frame, 
                 text="Date format: YYYY-MM-DD, Time format: HH:MM").grid(
                     row=1, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
    def _on_schedule_type_changed(self, event=None) -> None:
        """Handle schedule type change."""
        schedule_type = self.schedule_type_combobox.get().lower()
        
        if schedule_type == "interval":
            self._create_interval_config()
        elif schedule_type == "cron":
            self._create_cron_config()
        elif schedule_type == "one-time":
            self._create_date_config()
            
    def _on_refresh_jobs(self) -> None:
        """Refresh the job list."""
        if self.presenter:
            self.presenter.refresh_jobs()
            
    def _on_cancel_job(self) -> None:
        """Cancel the selected job."""
        selected_items = self.job_list_widget.selection()
        if not selected_items:
            messagebox.showinfo("No Selection", "Please select a job to cancel.")
            return
            
        job_id = selected_items[0]  # The job ID is the item ID in the treeview
        
        if messagebox.askyesno("Confirm Cancel", f"Are you sure you want to cancel the selected job?"):
            if self.presenter:
                self.presenter.cancel_job(job_id)
                
    def _on_create_schedule(self) -> None:
        """Create a new schedule."""
        # Get workflow and credential
        workflow_name = self.workflow_combobox.get()
        if not workflow_name:
            messagebox.showinfo("Missing Information", "Please select a workflow.")
            return
            
        credential_name = self.credential_combobox.get() or None  # None if empty
        
        # Get schedule type and configuration
        schedule_type = self.schedule_type_combobox.get().lower()
        if not schedule_type:
            messagebox.showinfo("Missing Information", "Please select a schedule type.")
            return
            
        # Convert schedule type to trigger type
        if schedule_type == "one-time":
            trigger_type = "date"
        else:
            trigger_type = schedule_type
            
        # Build schedule configuration
        schedule_config = {"trigger": trigger_type}
        
        try:
            if trigger_type == "interval":
                # Get interval value and unit
                interval_value = self.schedule_config_widgets["interval"]["value"].get()
                interval_unit = self.schedule_config_widgets["interval"]["unit"].get()
                
                if not interval_value or not interval_unit:
                    messagebox.showinfo("Missing Information", "Please specify interval value and unit.")
                    return
                    
                try:
                    interval_value = int(interval_value)
                    if interval_value <= 0:
                        raise ValueError("Interval must be positive")
                except ValueError:
                    messagebox.showerror("Invalid Input", "Interval value must be a positive integer.")
                    return
                    
                # Add to config
                schedule_config[interval_unit] = interval_value
                
                # Get start date/time if provided
                start_date = self.schedule_config_widgets["interval"]["start_date"].get()
                start_time = self.schedule_config_widgets["interval"]["start_time"].get()
                
                if start_date and start_time:
                    try:
                        # Validate and convert to datetime
                        start_datetime = datetime.strptime(f"{start_date} {start_time}", "%Y-%m-%d %H:%M")
                        schedule_config["start_date"] = start_datetime.strftime("%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        messagebox.showerror("Invalid Input", "Invalid date/time format. Use YYYY-MM-DD HH:MM.")
                        return
                        
            elif trigger_type == "cron":
                # Get cron fields
                for field_name in ["minute", "hour", "day", "month", "day_of_week"]:
                    field_value = self.schedule_config_widgets["cron"][field_name].get()
                    if field_value:  # Only add non-empty fields
                        schedule_config[field_name] = field_value
                        
            elif trigger_type == "date":
                # Get run date/time
                run_date = self.schedule_config_widgets["date"]["run_date"].get()
                run_time = self.schedule_config_widgets["date"]["run_time"].get()
                
                if not run_date or not run_time:
                    messagebox.showinfo("Missing Information", "Please specify run date and time.")
                    return
                    
                try:
                    # Validate and convert to datetime
                    run_datetime = datetime.strptime(f"{run_date} {run_time}", "%Y-%m-%d %H:%M")
                    schedule_config["run_date"] = run_datetime.strftime("%Y-%m-%d %H:%M:%S")
                except ValueError:
                    messagebox.showerror("Invalid Input", "Invalid date/time format. Use YYYY-MM-DD HH:MM.")
                    return
                    
            # Create the schedule
            if self.presenter:
                self.presenter.create_schedule(workflow_name, credential_name, schedule_config)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create schedule: {str(e)}")
            
    def _update_ui_state(self) -> None:
        """Update the UI state based on current selections."""
        # Enable/disable buttons based on selections
        workflow_selected = bool(self.workflow_combobox.get())
        schedule_type_selected = bool(self.schedule_type_combobox.get())
        
        # If no schedule type is selected, select interval by default
        if not schedule_type_selected and self.schedule_type_combobox["values"]:
            self.schedule_type_combobox.current(0)  # Select first item
            self._on_schedule_type_changed()
            
    def set_workflow_list(self, workflow_names: List[str]) -> None:
        """Set the list of available workflows."""
        if self.workflow_combobox:
            self.workflow_combobox["values"] = sorted(workflow_names)
            
    def set_credential_list(self, credential_names: List[str]) -> None:
        """Set the list of available credentials."""
        if self.credential_combobox:
            # Add empty option for no credential
            self.credential_combobox["values"] = [""] + sorted(credential_names)
            
    def set_job_list(self, jobs: List[Dict[str, Any]]) -> None:
        """Set the list of scheduled jobs."""
        if self.job_list_widget:
            # Clear existing items
            for item in self.job_list_widget.get_children():
                self.job_list_widget.delete(item)
                
            # Add new items
            for job in jobs:
                job_id = job.get("id", "")
                workflow_name = job.get("workflow_name", "")
                next_run_time = job.get("next_run_time", "")
                trigger = job.get("trigger", "")
                
                self.job_list_widget.insert("", "end", iid=job_id, values=(workflow_name, next_run_time, trigger))
                
    def display_message(self, title: str, message: str) -> None:
        """Display a message to the user."""
        messagebox.showinfo(title, message)
        
    def display_error(self, title: str, message: str) -> None:
        """Display an error message to the user."""
        messagebox.showerror(title, message)
