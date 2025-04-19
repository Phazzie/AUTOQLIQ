"""Simplified Workflow Runner Presenter for AutoQliq.

This module provides a streamlined WorkflowRunnerPresenter class that focuses on:
1. Simplified interface for running workflows
2. Clear error handling
3. Proper resource management
4. Consistent logging

Following YAGNI principles, this implementation removes unnecessary complexity
while maintaining core functionality.
"""

import logging
import threading
import time
from typing import Optional, Dict, Any, List, Callable

from src.core.interfaces import IWorkflowService, ICredentialRepository
from src.core.exceptions import WorkflowError, WebDriverError, CredentialError
from src.infrastructure.webdrivers.base import BrowserType
from src.infrastructure.common.error_handling import handle_exceptions
from src.infrastructure.common.logging_utils import log_method_call

logger = logging.getLogger(__name__)


class WorkflowRunnerPresenter:
    """
    Presenter for the Workflow Runner View.
    
    This simplified implementation focuses on providing a clean interface
    for running workflows and managing resources properly.
    """
    
    def __init__(
        self,
        view,  # IWorkflowRunnerView
        workflow_service: IWorkflowService,
        credential_repository: ICredentialRepository
    ):
        """
        Initialize the WorkflowRunnerPresenter.
        
        Args:
            view: The view to present to.
            workflow_service: Service for managing and executing workflows.
            credential_repository: Repository for credentials.
        """
        if view is None:
            raise ValueError("View cannot be None.")
        if workflow_service is None:
            raise ValueError("Workflow service cannot be None.")
        if credential_repository is None:
            raise ValueError("Credential repository cannot be None.")
            
        self.view = view
        self.workflow_service = workflow_service
        self.credential_repository = credential_repository
        
        # State variables
        self.current_workflow_name: Optional[str] = None
        self.current_credential_name: Optional[str] = None
        self.current_browser_type: BrowserType = BrowserType.CHROME
        self.execution_thread: Optional[threading.Thread] = None
        self.stop_event: Optional[threading.Event] = None
        self.is_running: bool = False
        
        logger.info("WorkflowRunnerPresenter initialized.")
    
    @log_method_call(logger)
    def initialize(self) -> None:
        """Initialize the presenter and view."""
        try:
            # Load workflow list
            workflow_names = self.workflow_service.get_workflow_list()
            self.view.set_workflow_list(workflow_names)
            
            # Load credential list
            credential_names = self.credential_repository.get_all_credential_names()
            self.view.set_credential_list(credential_names)
            
            # Set browser types
            browser_types = [browser_type.value for browser_type in BrowserType]
            self.view.set_browser_types(browser_types)
            
            # Set default browser type
            self.view.set_selected_browser_type(self.current_browser_type.value)
            
            logger.info("WorkflowRunnerPresenter initialized successfully.")
            
        except Exception as e:
            logger.error(f"Error initializing WorkflowRunnerPresenter: {e}")
            self.view.show_error("Initialization Error", f"Failed to initialize: {e}")
    
    @log_method_call(logger)
    def on_workflow_selected(self, workflow_name: str) -> None:
        """
        Handle workflow selection.
        
        Args:
            workflow_name: Name of the selected workflow.
        """
        if not workflow_name:
            return
            
        self.current_workflow_name = workflow_name
        logger.debug(f"Selected workflow: {workflow_name}")
    
    @log_method_call(logger)
    def on_credential_selected(self, credential_name: str) -> None:
        """
        Handle credential selection.
        
        Args:
            credential_name: Name of the selected credential.
        """
        self.current_credential_name = credential_name
        logger.debug(f"Selected credential: {credential_name}")
    
    @log_method_call(logger)
    def on_browser_type_selected(self, browser_type_str: str) -> None:
        """
        Handle browser type selection.
        
        Args:
            browser_type_str: String representation of the selected browser type.
        """
        try:
            self.current_browser_type = BrowserType(browser_type_str)
            logger.debug(f"Selected browser type: {browser_type_str}")
        except ValueError:
            logger.error(f"Invalid browser type: {browser_type_str}")
            self.view.show_error("Invalid Browser Type", f"'{browser_type_str}' is not a valid browser type.")
    
    @log_method_call(logger)
    @handle_exceptions(Exception, "Error running workflow", log_level=logging.ERROR)
    def on_run_workflow(self) -> None:
        """Handle run workflow button click."""
        if self.is_running:
            logger.warning("Attempted to run workflow while another is already running.")
            self.view.show_warning("Workflow Running", "A workflow is already running. Please wait or stop it first.")
            return
            
        if not self.current_workflow_name:
            logger.warning("Attempted to run workflow without selecting one.")
            self.view.show_warning("No Workflow Selected", "Please select a workflow to run.")
            return
            
        # Create a stop event
        self.stop_event = threading.Event()
        
        # Update UI state
        self.is_running = True
        self.view.set_running_state(True)
        self.view.clear_log()
        self.view.add_log_message(f"Starting workflow: {self.current_workflow_name}")
        
        # Create and start the execution thread
        self.execution_thread = threading.Thread(
            target=self._run_workflow_thread,
            args=(
                self.current_workflow_name,
                self.current_credential_name,
                self.current_browser_type,
                self.stop_event
            ),
            daemon=True
        )
        self.execution_thread.start()
        
        logger.info(f"Started workflow execution thread for '{self.current_workflow_name}'")
    
    @log_method_call(logger)
    def on_stop_workflow(self) -> None:
        """Handle stop workflow button click."""
        if not self.is_running:
            logger.warning("Attempted to stop workflow when none is running.")
            return
            
        if not self.stop_event:
            logger.error("Stop event is None while workflow is running.")
            return
            
        # Request stop
        self.view.add_log_message("Requesting workflow to stop...")
        self.workflow_service.stop_workflow(self.stop_event)
        
        # Wait for a short time to see if the workflow stops
        self.view.add_log_message("Waiting for workflow to stop...")
        
        # Update UI to indicate stopping
        self.view.set_stopping_state(True)
        
        logger.info("Requested workflow to stop.")
    
    def _run_workflow_thread(
        self,
        workflow_name: str,
        credential_name: Optional[str],
        browser_type: BrowserType,
        stop_event: threading.Event
    ) -> None:
        """
        Run a workflow in a separate thread.
        
        Args:
            workflow_name: Name of the workflow to run.
            credential_name: Optional name of the credential to use.
            browser_type: Type of browser to use.
            stop_event: Event to signal a stop request.
        """
        try:
            # Log the start
            self._log_to_ui(f"Running workflow '{workflow_name}'")
            if credential_name:
                self._log_to_ui(f"Using credential: {credential_name}")
            self._log_to_ui(f"Using browser: {browser_type.value}")
            
            # Run the workflow
            execution_log = self.workflow_service.run_workflow(
                name=workflow_name,
                credential_name=credential_name,
                browser_type=browser_type,
                log_callback=self._log_to_ui,
                stop_event=stop_event
            )
            
            # Log the result
            final_status = execution_log.get("final_status", "UNKNOWN")
            duration = execution_log.get("duration_seconds", 0)
            
            if final_status == "SUCCESS":
                self._log_to_ui(f"Workflow completed successfully in {duration:.2f} seconds.")
            elif final_status == "STOPPED":
                self._log_to_ui(f"Workflow was stopped after {duration:.2f} seconds.")
            else:
                error_message = execution_log.get("error_message", "Unknown error")
                self._log_to_ui(f"Workflow failed after {duration:.2f} seconds: {error_message}")
                
            # Log summary
            summary = execution_log.get("summary", {})
            total_actions = summary.get("total_actions", 0)
            success_count = summary.get("success_count", 0)
            failure_count = summary.get("failure_count", 0)
            
            self._log_to_ui(f"Summary: {success_count}/{total_actions} actions succeeded, {failure_count} failed.")
            
        except WorkflowError as e:
            self._log_to_ui(f"Workflow error: {e}")
            logger.error(f"Workflow error: {e}")
            
        except WebDriverError as e:
            self._log_to_ui(f"WebDriver error: {e}")
            logger.error(f"WebDriver error: {e}")
            
        except CredentialError as e:
            self._log_to_ui(f"Credential error: {e}")
            logger.error(f"Credential error: {e}")
            
        except Exception as e:
            self._log_to_ui(f"Unexpected error: {e}")
            logger.exception(f"Unexpected error running workflow '{workflow_name}': {e}")
            
        finally:
            # Reset state
            self.is_running = False
            self.execution_thread = None
            
            # Update UI
            self._update_ui_after_execution()
            
            logger.info(f"Workflow execution thread for '{workflow_name}' finished.")
    
    def _log_to_ui(self, message: str) -> None:
        """
        Log a message to the UI.
        
        Args:
            message: Message to log.
        """
        try:
            # Use the view's add_log_message method
            self.view.add_log_message(message)
        except Exception as e:
            # If there's an error logging to the UI, log it to the logger
            logger.error(f"Error logging to UI: {e}")
    
    def _update_ui_after_execution(self) -> None:
        """Update the UI after workflow execution."""
        try:
            # Reset UI state on the main thread
            self.view.after(0, lambda: self.view.set_running_state(False))
            self.view.after(0, lambda: self.view.set_stopping_state(False))
        except Exception as e:
            logger.error(f"Error updating UI after execution: {e}")
