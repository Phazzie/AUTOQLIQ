"""Enhanced workflow runner presenter implementation for AutoQliq."""

import logging
import threading
import time
from typing import List, Optional, Dict, Any

# Core dependencies
from src.core.interfaces import IWorkflowRepository, ICredentialRepository
from src.core.exceptions import WorkflowError, CredentialError, WebDriverError, AutoQliqError
from src.infrastructure.webdrivers import WebDriverFactory, BrowserType

# UI dependencies
from src.ui.interfaces.presenter import IWorkflowRunnerPresenter
from src.ui.interfaces.view import IWorkflowRunnerView
from src.ui.presenters.base_presenter import BasePresenter

logger = logging.getLogger(__name__)


class WorkflowRunnerPresenterEnhanced(BasePresenter[IWorkflowRunnerView], IWorkflowRunnerPresenter):
    """
    Enhanced presenter for the workflow runner view. Handles logic for listing workflows/credentials,
    initiating, and stopping workflow execution.
    """
    
    def __init__(
        self,
        workflow_repository: IWorkflowRepository,
        credential_repository: ICredentialRepository,
        webdriver_factory: WebDriverFactory,
        view: Optional[IWorkflowRunnerView] = None
    ):
        """
        Initialize the presenter.
        
        Args:
            workflow_repository: Repository for workflow persistence
            credential_repository: Repository for credential persistence
            webdriver_factory: Factory for creating WebDriver instances
            view: The associated view instance (optional)
        """
        super().__init__(view)
        self.workflow_repository = workflow_repository
        self.credential_repository = credential_repository
        self.webdriver_factory = webdriver_factory
        
        # Execution state
        self._execution_thread: Optional[threading.Thread] = None
        self._stop_requested: bool = False
        
        self.logger.info("WorkflowRunnerPresenterEnhanced initialized")
    
    # --- IWorkflowRunnerPresenter Implementation ---
    
    def get_workflow_list(self) -> List[str]:
        """
        Get the list of available workflow names.
        
        Returns:
            List of workflow names
        """
        try:
            workflow_names = self.workflow_repository.list_workflows()
            self.logger.debug(f"Retrieved {len(workflow_names)} workflows from repository")
            return workflow_names
        except Exception as e:
            self.logger.error(f"Failed to get workflow list: {e}")
            self._handle_view_error(e, "retrieving workflow list")
            return []
    
    def get_credential_list(self) -> List[str]:
        """
        Get the list of available credential names.
        
        Returns:
            List of credential names
        """
        try:
            credential_names = self.credential_repository.list_credentials()
            self.logger.debug(f"Retrieved {len(credential_names)} credentials from repository")
            return credential_names
        except Exception as e:
            self.logger.error(f"Failed to get credential list: {e}")
            self._handle_view_error(e, "retrieving credential list")
            return []
    
    def run_workflow(self, workflow_name: str, credential_name: Optional[str]) -> None:
        """
        Start executing the specified workflow using the selected credential.
        
        Args:
            workflow_name: The name of the workflow to run
            credential_name: The name of the credential to use (optional)
        """
        try:
            self.logger.info(f"Running workflow: {workflow_name} with credential: {credential_name}")
            
            # Check if a workflow is already running
            if self._execution_thread and self._execution_thread.is_alive():
                self.logger.warning("Cannot start workflow: Another workflow is already running")
                self._set_view_status("Cannot start workflow: Another workflow is already running")
                return
            
            # Reset the stop flag
            self._stop_requested = False
            
            # Update the view
            if self.view:
                self.view.clear_log()
                self.view.set_running_state(True)
                self.view.log_message(f"Starting workflow: {workflow_name}")
                if credential_name:
                    self.view.log_message(f"Using credential: {credential_name}")
            
            # Start the execution thread
            self._execution_thread = threading.Thread(
                target=self._execute_workflow,
                args=(workflow_name, credential_name),
                daemon=True
            )
            self._execution_thread.start()
            
            self.logger.info(f"Started execution thread for workflow: {workflow_name}")
        except Exception as e:
            self.logger.error(f"Failed to run workflow '{workflow_name}': {e}")
            self._handle_view_error(e, f"running workflow '{workflow_name}'")
            
            # Reset the view
            if self.view:
                self.view.set_running_state(False)
    
    def stop_workflow(self) -> None:
        """Stop the currently running workflow execution (if any)."""
        try:
            self.logger.info("Stopping workflow execution")
            
            # Set the stop flag
            self._stop_requested = True
            
            # Log the stop request
            if self.view:
                self.view.log_message("Stop requested. Waiting for workflow to terminate...")
                self._set_view_status("Stopping workflow...")
            
            self.logger.info("Stop requested for workflow execution")
        except Exception as e:
            self.logger.error(f"Failed to stop workflow: {e}")
            self._handle_view_error(e, "stopping workflow")
    
    # --- BasePresenter Implementation ---
    
    def initialize_view(self) -> None:
        """Initialize the associated view with necessary data."""
        if self.view:
            try:
                self.logger.debug("Initializing view")
                
                # Set the workflow list
                workflow_names = self.get_workflow_list()
                self.view.set_workflow_list(workflow_names)
                
                # Set the credential list
                credential_names = self.get_credential_list()
                self.view.set_credential_list(credential_names)
                
                # Clear the log
                self.view.clear_log()
                
                # Set the initial running state
                self.view.set_running_state(False)
                
                self.logger.debug("View initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize view: {e}")
                self._handle_view_error(e, "initializing view")
    
    # --- Helper Methods ---
    
    def _execute_workflow(self, workflow_name: str, credential_name: Optional[str]) -> None:
        """
        Execute a workflow in a background thread.
        
        Args:
            workflow_name: The name of the workflow to execute
            credential_name: The name of the credential to use (optional)
        """
        driver = None
        try:
            self.logger.info(f"Executing workflow: {workflow_name}")
            
            # Log the start of execution
            self._log_message(f"Executing workflow: {workflow_name}")
            
            # Load the workflow
            try:
                actions = self.workflow_repository.load(workflow_name)
                self._log_message(f"Loaded workflow with {len(actions)} actions")
            except Exception as e:
                self.logger.error(f"Failed to load workflow '{workflow_name}': {e}")
                self._log_message(f"ERROR: Failed to load workflow: {e}")
                return
            
            # Load the credential if specified
            credential = None
            if credential_name:
                try:
                    credential = self.credential_repository.get_by_name(credential_name)
                    if credential:
                        self._log_message(f"Loaded credential: {credential_name}")
                    else:
                        self._log_message(f"WARNING: Credential not found: {credential_name}")
                except Exception as e:
                    self.logger.error(f"Failed to load credential '{credential_name}': {e}")
                    self._log_message(f"WARNING: Failed to load credential: {e}")
            
            # Create the WebDriver
            try:
                self._log_message("Initializing WebDriver...")
                driver = self.webdriver_factory.create_driver(
                    browser_type=BrowserType.CHROME,
                    implicit_wait_seconds=5,
                    headless=False
                )
                self._log_message("WebDriver initialized")
            except Exception as e:
                self.logger.error(f"Failed to create WebDriver: {e}")
                self._log_message(f"ERROR: Failed to create WebDriver: {e}")
                return
            
            # Execute each action
            for i, action in enumerate(actions):
                # Check if stop was requested
                if self._stop_requested:
                    self._log_message("Execution stopped by user")
                    break
                
                try:
                    # Log the action
                    self._log_message(f"Executing action {i+1}/{len(actions)}: {action.name} ({action.action_type})")
                    
                    # Execute the action
                    result = action.execute(driver, self.credential_repository)
                    
                    # Log the result
                    if result.success:
                        self._log_message(f"Action completed: {result.message}")
                    else:
                        self._log_message(f"ERROR: Action failed: {result.message}")
                        # Stop execution on failure
                        break
                except Exception as e:
                    self.logger.error(f"Failed to execute action {action.name}: {e}")
                    self._log_message(f"ERROR: Failed to execute action {action.name}: {e}")
                    # Stop execution on error
                    break
            
            # Log the completion of execution
            if not self._stop_requested:
                self._log_message("Workflow execution completed")
            
            self.logger.info(f"Workflow execution completed: {workflow_name}")
        except Exception as e:
            self.logger.error(f"Error during workflow execution: {e}")
            self._log_message(f"ERROR: Workflow execution failed: {e}")
        finally:
            # Clean up the WebDriver
            if driver:
                try:
                    self._log_message("Closing WebDriver...")
                    driver.quit()
                    self._log_message("WebDriver closed")
                except Exception as e:
                    self.logger.error(f"Failed to close WebDriver: {e}")
                    self._log_message(f"WARNING: Failed to close WebDriver: {e}")
            
            # Reset the view
            self._update_view_on_completion()
    
    def _log_message(self, message: str) -> None:
        """
        Log a message to the view.
        
        Args:
            message: The message to log
        """
        # Log to the logger
        self.logger.info(message)
        
        # Log to the view
        if self.view:
            try:
                # Use the view's thread-safe logging method
                self.view.log_message(message)
            except Exception as e:
                self.logger.error(f"Failed to log message to view: {e}")
    
    def _update_view_on_completion(self) -> None:
        """Update the view when workflow execution completes."""
        if self.view:
            try:
                # Schedule the update on the main thread
                # This is a bit of a hack, but it works for now
                # In a real application, we would use a proper thread-safe mechanism
                threading.Timer(0.1, self._update_view_on_main_thread).start()
            except Exception as e:
                self.logger.error(f"Failed to schedule view update: {e}")
    
    def _update_view_on_main_thread(self) -> None:
        """Update the view on the main thread."""
        if self.view:
            try:
                self.view.set_running_state(False)
                self._set_view_status("Workflow execution completed")
            except Exception as e:
                self.logger.error(f"Failed to update view on main thread: {e}")
    
    def _set_view_status(self, message: str) -> None:
        """
        Set the status message in the view.
        
        Args:
            message: The status message
        """
        if self.view:
            try:
                self.view.set_status(message)
            except Exception as e:
                self.logger.error(f"Failed to set view status: {e}")
    
    def _handle_view_error(self, error: Exception, context: str) -> None:
        """
        Handle an error by displaying it in the view.
        
        Args:
            error: The error that occurred
            context: The context in which the error occurred
        """
        if self.view:
            try:
                self.view.display_error("Error", f"An error occurred while {context}: {error}")
            except Exception as e:
                self.logger.error(f"Failed to display error in view: {e}")
                # Fall back to setting the status
                self._set_view_status(f"Error: {error}")
