"""Enhanced workflow runner view implementation for AutoQliq."""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import List, Optional, Dict, Any

# Core / Infrastructure
from src.core.exceptions import UIError

# UI elements
from src.ui.interfaces.presenter import IWorkflowRunnerPresenter
from src.ui.interfaces.view import IWorkflowRunnerView
from src.ui.views.base_view import BaseView
from src.ui.components.workflow_list import WorkflowList
from src.ui.components.credential_list import CredentialList
from src.ui.components.execution_log import ExecutionLog

logger = logging.getLogger(__name__)


class WorkflowRunnerViewEnhanced(BaseView, IWorkflowRunnerView):
    """
    Enhanced view component for the workflow runner. Displays workflows and credentials,
    allows starting/stopping execution, and shows logs. Forwards user interactions
    to the WorkflowRunnerPresenter.
    """
    
    def __init__(self, root: tk.Widget, presenter: IWorkflowRunnerPresenter):
        """
        Initialize the workflow runner view.
        
        Args:
            root: The parent widget (e.g., a frame in a notebook)
            presenter: The presenter handling the logic for this view
        """
        super().__init__(root, presenter)
        self.presenter: IWorkflowRunnerPresenter  # Type hint
        
        try:
            # Create a vertical split with controls on top and log on bottom
            self.paned_window = ttk.PanedWindow(self.main_frame, orient=tk.VERTICAL)
            self.paned_window.pack(fill=tk.BOTH, expand=True)
            
            # Create the top frame for controls
            self.top_frame = ttk.Frame(self.paned_window, padding="5")
            self.paned_window.add(self.top_frame, weight=1)
            
            # Create the bottom frame for the log
            self.bottom_frame = ttk.Frame(self.paned_window, padding="5")
            self.paned_window.add(self.bottom_frame, weight=2)
            
            # Create a horizontal split in the top frame for workflows and credentials
            self.top_paned = ttk.PanedWindow(self.top_frame, orient=tk.HORIZONTAL)
            self.top_paned.pack(fill=tk.BOTH, expand=True)
            
            # Create the left frame for workflows
            self.left_frame = ttk.Frame(self.top_paned, padding="5")
            self.top_paned.add(self.left_frame, weight=2)
            
            # Create the right frame for credentials
            self.right_frame = ttk.Frame(self.top_paned, padding="5")
            self.top_paned.add(self.right_frame, weight=1)
            
            # Create the workflow list component
            self.workflow_list = WorkflowList(
                self.left_frame,
                on_select=self._on_workflow_selected
            )
            self.workflow_list.widget.pack(fill=tk.BOTH, expand=True)
            
            # Create the credential list component
            self.credential_list = CredentialList(
                self.right_frame,
                on_select=self._on_credential_selected,
                on_create=self._on_create_credential,
                on_edit=self._on_edit_credential,
                on_delete=self._on_delete_credential
            )
            self.credential_list.widget.pack(fill=tk.BOTH, expand=True)
            
            # Create a frame for the run/stop buttons
            self.button_frame = ttk.Frame(self.top_frame, padding="5")
            self.button_frame.pack(fill=tk.X, pady=(5, 0))
            
            # Create the run button
            self.run_button = ttk.Button(
                self.button_frame,
                text="Run Workflow",
                command=self._on_run_workflow
            )
            self.run_button.pack(side=tk.LEFT, padx=(0, 5))
            
            # Create the stop button
            self.stop_button = ttk.Button(
                self.button_frame,
                text="Stop Workflow",
                command=self._on_stop_workflow,
                state=tk.DISABLED
            )
            self.stop_button.pack(side=tk.LEFT)
            
            # Create the execution log component
            self.execution_log = ExecutionLog(
                self.bottom_frame,
                on_clear=self._on_clear_log,
                on_save=self._on_save_log
            )
            self.execution_log.widget.pack(fill=tk.BOTH, expand=True)
            
            # Initialize the view
            self.presenter.initialize_view()
            
            self.logger.info("WorkflowRunnerViewEnhanced initialized")
        except Exception as e:
            error_msg = "Failed to initialize WorkflowRunnerViewEnhanced"
            self.logger.exception(error_msg)
            raise UIError(error_msg, component_name="WorkflowRunnerViewEnhanced", cause=e) from e
    
    # --- IWorkflowRunnerView Implementation ---
    
    def set_workflow_list(self, workflow_names: List[str]) -> None:
        """
        Populate the list of available workflows.
        
        Args:
            workflow_names: List of workflow names
        """
        try:
            self.workflow_list.set_workflows(workflow_names)
            self.logger.debug(f"Set workflow list with {len(workflow_names)} workflows")
        except Exception as e:
            self.error_handler.handle_error(e, "setting workflow list")
    
    def set_credential_list(self, credential_names: List[str]) -> None:
        """
        Populate the list of available credentials.
        
        Args:
            credential_names: List of credential names
        """
        try:
            self.credential_list.set_credentials(credential_names)
            self.logger.debug(f"Set credential list with {len(credential_names)} credentials")
        except Exception as e:
            self.error_handler.handle_error(e, "setting credential list")
    
    def get_selected_workflow_name(self) -> Optional[str]:
        """
        Get the name of the workflow selected by the user.
        
        Returns:
            The selected workflow name, or None if no workflow is selected
        """
        return self.workflow_list.get_selected_workflow()
    
    def get_selected_credential_name(self) -> Optional[str]:
        """
        Get the name of the credential selected by the user.
        
        Returns:
            The selected credential name, or None if no credential is selected
        """
        return self.credential_list.get_selected_credential()
    
    def log_message(self, message: str) -> None:
        """
        Append a message to the execution log display.
        
        Args:
            message: The message to append
        """
        try:
            # Determine the log level based on the message content
            if "ERROR" in message or "FAILED" in message:
                level = "ERROR"
            elif "WARNING" in message:
                level = "WARNING"
            elif "DEBUG" in message:
                level = "DEBUG"
            else:
                level = "INFO"
            
            self.execution_log.log(message, level)
        except Exception as e:
            self.error_handler.handle_error(e, "logging message")
    
    def clear_log(self) -> None:
        """Clear the execution log display."""
        try:
            self.execution_log.clear()
        except Exception as e:
            self.error_handler.handle_error(e, "clearing log")
    
    def set_running_state(self, is_running: bool) -> None:
        """
        Update the UI elements based on whether a workflow is running.
        
        Args:
            is_running: Whether a workflow is currently running
        """
        try:
            if is_running:
                # Disable the run button and enable the stop button
                self.run_button.config(state=tk.DISABLED)
                self.stop_button.config(state=tk.NORMAL)
                
                # Disable the workflow and credential lists
                self.workflow_list.listbox.config(state=tk.DISABLED)
                self.credential_list.listbox.config(state=tk.DISABLED)
                
                # Update the status bar
                self.set_status("Workflow running...")
            else:
                # Enable the run button and disable the stop button
                self.run_button.config(state=tk.NORMAL)
                self.stop_button.config(state=tk.DISABLED)
                
                # Enable the workflow and credential lists
                self.workflow_list.listbox.config(state=tk.NORMAL)
                self.credential_list.listbox.config(state=tk.NORMAL)
                
                # Update the status bar
                self.set_status("Ready")
        except Exception as e:
            self.error_handler.handle_error(e, "setting running state")
    
    # --- Event Handlers ---
    
    def _on_workflow_selected(self, workflow_name: str) -> None:
        """
        Handle selection of a workflow in the list.
        
        Args:
            workflow_name: The name of the selected workflow
        """
        try:
            self.set_status(f"Selected workflow: {workflow_name}")
        except Exception as e:
            self.error_handler.handle_error(e, f"selecting workflow '{workflow_name}'")
    
    def _on_credential_selected(self, credential_name: str) -> None:
        """
        Handle selection of a credential in the list.
        
        Args:
            credential_name: The name of the selected credential
        """
        try:
            self.set_status(f"Selected credential: {credential_name}")
        except Exception as e:
            self.error_handler.handle_error(e, f"selecting credential '{credential_name}'")
    
    def _on_create_credential(self) -> None:
        """Handle clicks on the create credential button."""
        try:
            # This would require a create_credential method in the presenter
            # For now, we'll just show a message
            messagebox.showinfo(
                "Not Implemented",
                "Creating credentials is not yet implemented in this view.",
                parent=self.root.winfo_toplevel()
            )
        except Exception as e:
            self.error_handler.handle_error(e, "creating credential")
    
    def _on_edit_credential(self, credential_name: str) -> None:
        """
        Handle clicks on the edit credential button.
        
        Args:
            credential_name: The name of the credential to edit
        """
        try:
            # This would require an edit_credential method in the presenter
            # For now, we'll just show a message
            messagebox.showinfo(
                "Not Implemented",
                f"Editing credential '{credential_name}' is not yet implemented in this view.",
                parent=self.root.winfo_toplevel()
            )
        except Exception as e:
            self.error_handler.handle_error(e, f"editing credential '{credential_name}'")
    
    def _on_delete_credential(self, credential_name: str) -> None:
        """
        Handle clicks on the delete credential button.
        
        Args:
            credential_name: The name of the credential to delete
        """
        try:
            # This would require a delete_credential method in the presenter
            # For now, we'll just show a message
            messagebox.showinfo(
                "Not Implemented",
                f"Deleting credential '{credential_name}' is not yet implemented in this view.",
                parent=self.root.winfo_toplevel()
            )
        except Exception as e:
            self.error_handler.handle_error(e, f"deleting credential '{credential_name}'")
    
    def _on_run_workflow(self) -> None:
        """Handle clicks on the run workflow button."""
        try:
            # Get the selected workflow and credential
            workflow_name = self.get_selected_workflow_name()
            credential_name = self.get_selected_credential_name()
            
            if workflow_name:
                # Run the workflow
                self.presenter.run_workflow(workflow_name, credential_name)
            else:
                messagebox.showwarning(
                    "No Workflow Selected",
                    "Please select a workflow to run.",
                    parent=self.root.winfo_toplevel()
                )
        except Exception as e:
            self.error_handler.handle_error(e, "running workflow")
    
    def _on_stop_workflow(self) -> None:
        """Handle clicks on the stop workflow button."""
        try:
            # Stop the workflow
            self.presenter.stop_workflow()
        except Exception as e:
            self.error_handler.handle_error(e, "stopping workflow")
    
    def _on_clear_log(self) -> None:
        """Handle clicks on the clear log button."""
        try:
            self.clear_log()
        except Exception as e:
            self.error_handler.handle_error(e, "clearing log")
    
    def _on_save_log(self) -> None:
        """Handle clicks on the save log button."""
        try:
            # This would require a save_log method in the presenter
            # For now, we'll just show a message
            messagebox.showinfo(
                "Not Implemented",
                "Saving logs is not yet implemented in this view.",
                parent=self.root.winfo_toplevel()
            )
        except Exception as e:
            self.error_handler.handle_error(e, "saving log")
    
    # --- BaseView Implementation ---
    
    def clear(self) -> None:
        """Clear or reset the view's state."""
        super().clear()
        try:
            # Clear the workflow list
            self.workflow_list.set_workflows([])
            
            # Clear the credential list
            self.credential_list.set_credentials([])
            
            # Clear the log
            self.clear_log()
            
            # Reset the running state
            self.set_running_state(False)
        except Exception as e:
            self.error_handler.handle_error(e, "clearing view")
