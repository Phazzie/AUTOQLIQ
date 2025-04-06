"""Workflow runner presenter implementation for AutoQliq."""

import logging
import threading
import time # For potential simulated delays
from typing import List, Dict, Any, Optional

# Core dependencies
from src.core.interfaces import IWorkflowRepository, ICredentialRepository, IWebDriver
from src.core.exceptions import WorkflowError, CredentialError, WebDriverError, AutoQliqError, ValidationError
from src.core.workflow.runner import WorkflowRunner # Assuming runner logic is here

# Infrastructure dependencies
from src.infrastructure.webdrivers.factory import WebDriverFactory

# UI dependencies
from src.ui.interfaces.presenter import IWorkflowRunnerPresenter
from src.ui.interfaces.view import IWorkflowRunnerView
from src.ui.presenters.base_presenter import BasePresenter

class WorkflowRunnerPresenter(BasePresenter[IWorkflowRunnerView], IWorkflowRunnerPresenter):
    """
    Presenter for the workflow runner view. Handles logic for listing workflows/credentials,
    initiating, and stopping workflow execution.
    """

    def __init__(
        self,
        workflow_repository: IWorkflowRepository,
        credential_repository: ICredentialRepository,
        webdriver_factory: WebDriverFactory, # Expecting the factory
        view: Optional[IWorkflowRunnerView] = None
    ):
        """
        Initialize the presenter.

        Args:
            workflow_repository: Repository for workflow persistence.
            credential_repository: Repository for credential persistence.
            webdriver_factory: Factory to create WebDriver instances.
            view: The associated view instance (optional).
        """
        super().__init__(view)
        self.workflow_repository = workflow_repository
        self.credential_repository = credential_repository
        self.webdriver_factory = webdriver_factory
        self._current_driver: Optional[IWebDriver] = None
        self._is_running = False
        self._stop_requested = False
        self._execution_thread: Optional[threading.Thread] = None
        self.logger.info("WorkflowRunnerPresenter initialized.")

    def set_view(self, view: IWorkflowRunnerView) -> None:
        """Set the view and perform initial population."""
        super().set_view(view)
        self.initialize_view()

    @BasePresenter.handle_errors("Initializing runner view")
    def initialize_view(self) -> None:
        """Populate the view with initial data (workflow and credential lists)."""
        if not self.view: return
        self.logger.debug("Initializing view...")
        workflows = self.get_workflow_list() # Calls method below
        credentials = self.get_credential_list() # Calls method below
        self.view.set_workflow_list(workflows or [])
        self.view.set_credential_list(credentials or [])
        self.view.set_running_state(self._is_running)
        self.logger.debug("View initialized.")

    @BasePresenter.handle_errors("Getting workflow list")
    def get_workflow_list(self) -> List[str]:
        """Get the list of available workflow names from the repository."""
        self.logger.debug("Fetching workflow list from repository.")
        return self.workflow_repository.list_workflows()

    @BasePresenter.handle_errors("Getting credential list")
    def get_credential_list(self) -> List[str]:
        """Get the list of available credential names from the repository."""
        self.logger.debug("Fetching credential list from repository.")
        return self.credential_repository.list_credentials()

    # --- Workflow Execution ---

    def run_workflow(self, workflow_name: str, credential_name: Optional[str]) -> None:
        """Start executing the specified workflow in a background thread."""
        if not self.view: return
        if self._is_running:
             self.logger.warning("Attempted to run workflow while another is already running.")
             self.view.display_message("Busy", "A workflow is already running.")
             return

        if not workflow_name:
             self.logger.warning("Run workflow called with empty workflow name.")
             self._handle_error(ValidationError("Workflow name must be selected."), "starting workflow run")
             return
        # Credential might be optional depending on workflow needs, validation happens later
        if credential_name is None:
             self.logger.info(f"Running workflow '{workflow_name}' without specific credentials.")
             # Optionally show warning if credential name is usually expected
             # self.view.display_message("Warning", "No credential selected. Workflow might fail if credentials are needed.")


        self._is_running = True
        self._stop_requested = False
        self.view.clear_log()
        self.view.log_message(f"Starting workflow '{workflow_name}'...")
        self.view.set_running_state(True)
        # Potentially start progress indicator here if view supports it
        # self.view.start_progress()

        # Run the actual execution in a separate thread to avoid blocking the UI
        self._execution_thread = threading.Thread(
            target=self._execute_workflow_thread,
            args=(workflow_name, credential_name),
            daemon=True # Allows application to exit even if thread is running
        )
        self._execution_thread.start()

    def _execute_workflow_thread(self, workflow_name: str, credential_name: Optional[str]) -> None:
        """Target function for the background execution thread."""
        start_time = time.time()
        final_status = "ERROR"
        try:
            # --- Setup ---
            self.logger.info(f"[Thread] Loading workflow: {workflow_name}")
            actions = self.workflow_repository.load(workflow_name) # Raises WorkflowError

            # --- Driver Creation ---
            # TODO: Get browser type from configuration or UI
            browser_type = BrowserType.CHROME
            self.logger.info(f"[Thread] Creating WebDriver: {browser_type.value}")
            if self._stop_requested: raise WorkflowError("Stop requested before driver creation.")
            self._current_driver = self.webdriver_factory.create_driver(browser_type) # Raises WebDriverError

            # --- Workflow Execution ---
            runner = WorkflowRunner(self._current_driver, self.credential_repository)
            self.logger.info(f"[Thread] Starting runner for workflow: {workflow_name}")
            # The runner iterates through actions
            results = []
            for i, action in enumerate(actions):
                if self._stop_requested:
                    self.logger.info(f"[Thread] Stop requested during action {i+1} ('{action.name}')")
                    self.view.log_message(f"Execution stopped by user during action {i+1}.")
                    raise WorkflowError("Workflow execution stopped by user.")

                self.view.log_message(f"Executing action {i+1}: {action.name} ({action.action_type})")
                action_result = runner.run_single_action(action) # Assuming runner has this method
                results.append(action_result)
                if not action_result.is_success():
                    self.view.log_message(f"Action {i+1} FAILED: {action_result.message}")
                    # Raise error to stop workflow execution within the thread
                    raise ActionError(action_result.message or "Action failed", action_name=action.name, action_type=action.action_type)
                else:
                    self.view.log_message(f"Action {i+1} SUCCEEDED. {action_result.message or ''}")

            # --- Success ---
            final_status = "SUCCESS"
            self.logger.info(f"[Thread] Workflow '{workflow_name}' completed successfully.")
            self.view.log_message(f"Workflow '{workflow_name}' finished successfully.")

        except (WorkflowError, CredentialError, WebDriverError, ActionError, ValidationError, ConfigError, SerializationError, AutoQliqError) as e:
            # Handle known AutoQliq errors
            final_status = "FAILED"
            error_msg = f"Workflow '{workflow_name}' failed: {str(e)}"
            self.logger.error(f"[Thread] {error_msg}")
            self.view.log_message(f"ERROR: {error_msg}")
            # Show error in main thread via messagebox? Risky from background thread.
            # Log message is safer. Could schedule messagebox via root.after.

        except Exception as e:
            # Handle unexpected errors
            final_status = "UNEXPECTED ERROR"
            error_msg = f"Unexpected error during workflow '{workflow_name}': {str(e)}"
            self.logger.exception(f"[Thread] {error_msg}") # Log full traceback
            self.view.log_message(f"CRITICAL ERROR: {error_msg}")

        finally:
            # --- Cleanup ---
            self.logger.info("[Thread] Cleaning up workflow execution.")
            if self._current_driver:
                try:
                    self._current_driver.quit()
                    self.logger.info("[Thread] WebDriver quit.")
                except Exception as q_e:
                    self.logger.error(f"[Thread] Error quitting WebDriver: {q_e}")
            self._current_driver = None
            self._is_running = False
            self._stop_requested = False # Reset stop flag

            # Update UI (must be done safely in the main thread)
            end_time = time.time()
            duration = end_time - start_time
            final_log = f"Workflow execution finished. Status: {final_status}. Duration: {duration:.2f}s"
            if self.view and self.view.widget.winfo_exists(): # Check if view still exists
                 # Schedule UI updates to run in the main Tkinter thread
                 self.view.widget.after(0, lambda: self.view.log_message(final_log))
                 self.view.widget.after(0, lambda: self.view.set_running_state(False))
                 # self.view.widget.after(0, self.view.stop_progress) # If using progress indicator

            self.logger.info(f"[Thread] {final_log}")


    def stop_workflow(self) -> None:
        """Request to stop the currently running workflow."""
        if not self._is_running:
            self.logger.warning("Stop requested but no workflow is running.")
            if self.view: self.view.display_message("Info", "No workflow is currently running.")
            return

        if self._stop_requested:
             self.logger.warning("Stop already requested.")
             return

        self.logger.info("Requesting workflow stop...")
        self._stop_requested = True
        if self.view:
             self.view.log_message("Stop requested by user...")
             # Optionally disable stop button here immediately
             # self.view.set_running_state(True) # Keep UI showing 'running' until thread finishes cleanup

        # Note: The actual stopping happens within the execution loop checking the flag.
        # For immediate termination (e.g., killing browser), more complex handling is needed.