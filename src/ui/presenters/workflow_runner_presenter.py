"""Workflow runner presenter implementation for AutoQliq."""

import logging
import threading
import time
import tkinter as tk # Only needed for type hints potentially, avoid direct use
from typing import List, Optional, Dict, Any, Callable

# Core dependencies
from src.core.exceptions import WorkflowError, CredentialError, WebDriverError, AutoQliqError, ValidationError, ActionError
from src.core.interfaces.service import IWorkflowService, ICredentialService, IWebDriverService # Use Service Interfaces
from src.infrastructure.webdrivers.base import BrowserType # Use BrowserType enum
# Configuration
from src.config import config

# UI dependencies
from src.ui.interfaces.presenter import IWorkflowRunnerPresenter
from src.ui.interfaces.view import IWorkflowRunnerView
from src.ui.presenters.base_presenter import BasePresenter

class WorkflowRunnerPresenter(BasePresenter[IWorkflowRunnerView], IWorkflowRunnerPresenter):
    """
    Presenter for the workflow runner view. Handles logic for listing workflows/credentials,
    initiating, and stopping workflow execution via application services.
    Manages background execution thread.
    """

    def __init__(
        self,
        workflow_service: IWorkflowService,
        credential_service: ICredentialService,
        webdriver_service: IWebDriverService, # Expect the service now
        view: Optional[IWorkflowRunnerView] = None
    ):
        """Initialize the presenter."""
        super().__init__(view)
        if workflow_service is None: raise ValueError("Workflow service cannot be None.")
        if credential_service is None: raise ValueError("Credential service cannot be None.")
        if webdriver_service is None: raise ValueError("WebDriver service cannot be None.")

        self.workflow_service = workflow_service
        self.credential_service = credential_service
        self.webdriver_service = webdriver_service

        # State management for execution thread
        self._is_running = False
        self._stop_event = threading.Event() # Use Event for clearer stop signal
        self._execution_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock() # For thread safety accessing state
        self.logger.info("WorkflowRunnerPresenter initialized.")

    def set_view(self, view: IWorkflowRunnerView) -> None:
        """Set the view and perform initial population."""
        super().set_view(view)
        self.initialize_view()

    @BasePresenter.handle_errors("Initializing runner view")
    def initialize_view(self) -> None:
        """Populate the view with initial data using services."""
        if not self.view: return
        self.logger.debug("Initializing runner view...")
        workflows = self._get_workflows_from_service()
        credentials = self._get_credentials_from_service()
        self.view.set_workflow_list(workflows or [])
        self.view.set_credential_list(credentials or [])
        self.view.set_running_state(self._is_running) # Ensure UI reflects initial state
        self.view.set_status("Ready. Select workflow and credential.")
        self.logger.debug("Runner view initialized.")

    def get_workflow_list(self) -> List[str]:
         return self._get_workflows_from_service()

    def get_credential_list(self) -> List[str]:
         return self._get_credentials_from_service()

    @BasePresenter.handle_errors("Getting workflow list")
    def _get_workflows_from_service(self) -> List[str]:
        self.logger.debug("Fetching workflow list from service.")
        return self.workflow_service.list_workflows()

    @BasePresenter.handle_errors("Getting credential list")
    def _get_credentials_from_service(self) -> List[str]:
        self.logger.debug("Fetching credential list from service.")
        return self.credential_service.list_credentials()


    # --- Workflow Execution ---

    def run_workflow(self, workflow_name: str, credential_name: Optional[str]) -> None:
        """Start executing the specified workflow in a background thread via the WorkflowService."""
        if not self.view: return

        with self._lock:
             if self._is_running:
                  self.logger.warning("Run requested while already running.")
                  self._schedule_ui_update(lambda: self.view.display_message("Busy", "A workflow is already running."))
                  return
             self._is_running = True
             self._stop_event.clear() # Reset stop flag for new run

        if not workflow_name:
             self.logger.warning("Run workflow called with empty workflow name.")
             self._handle_error(ValidationError("Workflow name must be selected."), "starting workflow run")
             with self._lock: self._is_running = False # Reset flag
             return

        log_cred = f"with credential '{credential_name}'" if credential_name else "without specific credentials"
        self.logger.info(f"Initiating run for workflow '{workflow_name}' {log_cred}.")

        # --- Update UI immediately ---
        self._schedule_ui_update(self.view.clear_log)
        self._schedule_ui_update(lambda: self.view.log_message(f"Starting workflow '{workflow_name}'..."))
        self._schedule_ui_update(lambda: self.view.set_running_state(True))

        # --- Launch Thread ---
        self._execution_thread = threading.Thread(
            target=self._execute_workflow_thread, # Target the internal method
            args=(workflow_name, credential_name),
            daemon=True
        )
        self._execution_thread.start()
        self.logger.info(f"Execution thread started for workflow '{workflow_name}'.")

    def _execute_workflow_thread(self, workflow_name: str, credential_name: Optional[str]) -> None:
        """Target function for background thread. Calls WorkflowService.run_workflow."""
        start_time = time.time()
        final_status = "UNKNOWN"
        error_occurred: Optional[Exception] = None
        execution_log: Optional[Dict[str, Any]] = None

        try:
            # --- Call the Service ---
            browser_type_str = config.default_browser
            browser_enum = BrowserType.from_string(browser_type_str)

            # Pass the stop event to the service call
            execution_log = self.workflow_service.run_workflow(
                name=workflow_name,
                credential_name=credential_name,
                browser_type=browser_enum,
                stop_event=self._stop_event, # Pass the event
                log_callback=lambda msg: self._schedule_ui_update(lambda m=msg: self.view.log_message(m)) if self.view else None
            )
            final_status = execution_log.get("final_status", "UNKNOWN")
            if final_status == "SUCCESS":
                 self.logger.info(f"[Thread] Workflow service call for '{workflow_name}' completed successfully.")
            elif final_status == "STOPPED":
                 self.logger.info(f"[Thread] Workflow '{workflow_name}' execution stopped by request.")
                 error_occurred = WorkflowError("Workflow execution stopped by user.") # Set error for logging
            else: # FAILED or UNKNOWN
                 error_message = execution_log.get("error_message", "Unknown error from service.")
                 error_occurred = WorkflowError(error_message) # Create error object
                 self.logger.error(f"[Thread] Workflow service call failed for '{workflow_name}': {error_message}")

        # Catch exceptions raised *by the service call itself*
        except (WorkflowError, CredentialError, WebDriverError, ActionError, ValidationError, ConfigError, AutoQliqError) as e:
            error_occurred = e
            final_status = "FAILED"
            if self._stop_event.is_set(): final_status = "STOPPED"
            error_msg = f"Workflow '{workflow_name}' failed: {str(e)}"
            self.logger.error(f"[Thread] {error_msg}")
            self._schedule_ui_update(lambda msg=f"ERROR: {error_msg}": self.view.log_message(msg))
        except Exception as e:
            error_occurred = e
            final_status = "UNEXPECTED ERROR"
            if self._stop_event.is_set(): final_status = "STOPPED"
            error_msg = f"Unexpected error during service call for workflow '{workflow_name}': {str(e)}"
            self.logger.exception(f"[Thread] {error_msg}")
            self._schedule_ui_update(lambda msg=f"CRITICAL ERROR: {error_msg}": self.view.log_message(msg))
        finally:
            # --- Final State Reset & UI Update ---
            with self._lock: self._is_running = False # Reset running flag

            end_time = time.time()
            duration = end_time - start_time
            final_log_msg = f"Workflow execution finished. Status: {final_status}. Duration: {duration:.2f}s"

            self._schedule_ui_update(lambda msg=final_log_msg: self.view.log_message(msg))
            self._schedule_ui_update(lambda: self.view.set_running_state(False)) # Update button states etc.

            self.logger.info(f"[Thread] {final_log_msg}")


    def stop_workflow(self) -> None:
        """Request to stop the currently running workflow by setting the event."""
        with self._lock:
             if not self._is_running:
                  self.logger.warning("Stop requested but no workflow is running.")
                  self._schedule_ui_update(lambda: self.view.display_message("Info", "No workflow is currently running."))
                  return
             if self._stop_event.is_set():
                  self.logger.warning("Stop already requested.")
                  return
             self.logger.info("Requesting workflow stop via event...")
             self._stop_event.set() # Signal the event

        if self.view:
             self._schedule_ui_update(lambda: self.view.log_message("Stop requested... (Signaling running workflow)"))
             if self.view.stop_button:
                  self._schedule_ui_update(lambda: self.view.stop_button.config(state=tk.DISABLED))


    def _schedule_ui_update(self, callback: Callable):
        """Safely schedule a callback to run on the main Tkinter thread."""
        if self.view and hasattr(self.view, 'widget') and self.view.widget.winfo_exists():
            try: self.view.widget.after(0, callback)
            except Exception as e: self.logger.error(f"Failed to schedule UI update: {e}")
        else: self.logger.warning("Cannot schedule UI update: View/widget not available.")