"""Execution service implementation for AutoQliq.

This module provides the ExecutionService implementation that manages
workflow execution with status tracking and cancellation support.
"""

import logging
import threading
import time
from typing import List, Optional, Dict, Any
from datetime import datetime
from src.core.interfaces import IWorkflowRepository, ICredentialRepository, IWebDriver
from src.core.workflow.workflow_entity import Workflow
from src.core.credentials import Credential
from src.core.workflow.runner import WorkflowRunner
from src.core.action_result import ActionResult
from src.infrastructure.webdrivers.webdriver_factory import WebDriverFactory
from src.application.interfaces.service_interfaces import IExecutionService
from src.core.exceptions import RepositoryError, ValidationError, ServiceError, WebDriverError

logger = logging.getLogger(__name__)

class ExecutionService(IExecutionService):
    """Service for executing workflows with status tracking and cancellation support."""

    def __init__(
        self,
        workflow_repository: IWorkflowRepository,
        credential_repository: ICredentialRepository,
        webdriver_factory: WebDriverFactory
    ):
        """Initialize with repository and factory dependencies."""
        self.workflow_repository = workflow_repository
        self.credential_repository = credential_repository
        self.webdriver_factory = webdriver_factory

        # Execution state
        self._execution_lock = threading.RLock()
        self._current_execution = None
        self._execution_thread = None
        self._stop_event = threading.Event()
        self._execution_results = []
        self._execution_status = {
            "status": "idle",
            "workflow_name": None,
            "start_time": None,
            "progress": 0,
            "current_action": None,
            "error": None
        }

        logger.debug("ExecutionService initialized")

    def execute_workflow(self, workflow_id: str, credential_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a workflow by ID, optionally using specified credentials.

        Returns execution context with initial status. The execution runs in a background
        thread and can be monitored via get_execution_status().
        """
        logger.info(f"Executing workflow: {workflow_id} with credential: {credential_name}")

        with self._execution_lock:
            # Check if already executing
            if self._execution_thread and self._execution_thread.is_alive():
                msg = "Cannot start execution: another workflow is already running"
                logger.error(msg)
                raise ServiceError(msg)

            try:
                # Reset state
                self._stop_event.clear()
                self._execution_results = []

                # Get workflow
                workflow = self.workflow_repository.get(workflow_id)
                if not workflow:
                    raise ValidationError(f"Workflow not found: {workflow_id}")

                # Get credential if specified
                credential = None
                if credential_name:
                    credential = self.credential_repository.get(credential_name)
                    if not credential:
                        raise ValidationError(f"Credential not found: {credential_name}")

                # Update status
                self._execution_status = {
                    "status": "starting",
                    "workflow_name": workflow.name,
                    "start_time": time.time(),
                    "progress": 0,
                    "current_action": None,
                    "error": None
                }

                # Start execution in background thread
                self._execution_thread = threading.Thread(
                    target=self._execute_workflow_thread,
                    args=(workflow, credential),
                    daemon=True
                )
                self._execution_thread.start()

                logger.info(f"Started execution of workflow: {workflow.name}")
                return self._execution_status
            except (ValidationError, RepositoryError) as e:
                logger.error(f"Failed to start workflow execution: {e}")
                self._execution_status = {
                    "status": "failed",
                    "workflow_name": workflow_id,
                    "start_time": time.time(),
                    "progress": 0,
                    "current_action": None,
                    "error": str(e)
                }
                raise ServiceError(f"Failed to start workflow execution: {e}", cause=e)
            except Exception as e:
                logger.exception(f"Unexpected error starting workflow execution: {e}")
                self._execution_status = {
                    "status": "failed",
                    "workflow_name": workflow_id,
                    "start_time": time.time(),
                    "progress": 0,
                    "current_action": None,
                    "error": f"Unexpected error: {e}"
                }
                raise ServiceError(f"Unexpected error starting workflow execution: {e}", cause=e)

    def _execute_workflow_thread(self, workflow: Workflow, credential: Optional[Credential] = None) -> None:
        """
        Execute a workflow in a background thread.

        Updates execution status and results as the workflow progresses.
        """
        driver = None
        total_actions = len(workflow.actions)

        try:
            # Create WebDriver
            driver = self.webdriver_factory.create_driver()

            # Create WorkflowRunner
            runner = WorkflowRunner(driver, self.credential_repository, stop_event=self._stop_event)

            # Update status
            with self._execution_lock:
                self._execution_status["status"] = "running"

            # Execute workflow
            execution_log = runner.run(workflow.actions, workflow_name=workflow.name)

            # Store results
            with self._execution_lock:
                self._execution_results = execution_log.get("action_results", [])
                self._execution_status = {
                    "status": "completed",
                    "workflow_name": workflow.name,
                    "start_time": execution_log.get("start_time_iso"),
                    "end_time": execution_log.get("end_time_iso"),
                    "duration": execution_log.get("duration_seconds"),
                    "progress": 100,
                    "current_action": None,
                    "error": None,
                    "final_status": execution_log.get("final_status")
                }

            logger.info(f"Workflow execution completed: {workflow.name}")
        except Exception as e:
            logger.exception(f"Error executing workflow: {workflow.name}")
            with self._execution_lock:
                self._execution_status = {
                    "status": "failed",
                    "workflow_name": workflow.name,
                    "progress": (len(self._execution_results) / total_actions) * 100 if total_actions > 0 else 0,
                    "current_action": None,
                    "error": str(e),
                    "final_status": "FAILED"
                }
        finally:
            # Clean up WebDriver
            if driver:
                try:
                    driver.quit()
                except Exception as e:
                    logger.error(f"Error closing WebDriver: {e}")

    def stop_execution(self) -> bool:
        """
        Stop the currently executing workflow.

        Returns:
            bool: True if stop was requested, False if no workflow is running.
        """
        logger.info("Requesting workflow execution stop")
        with self._execution_lock:
            if self._execution_thread and self._execution_thread.is_alive():
                self._stop_event.set()
                self._execution_status["status"] = "stopping"
                logger.info("Stop request sent to workflow execution")
                return True
            else:
                logger.info("No workflow execution to stop")
                return False

    def get_execution_status(self) -> Dict[str, Any]:
        """
        Get the current execution status.

        Returns:
            Dict[str, Any]: Current execution status.
        """
        with self._execution_lock:
            return self._execution_status.copy()

    def get_execution_results(self) -> List[ActionResult]:
        """
        Get the results of the current or last execution.

        Returns:
            List[ActionResult]: List of action results.
        """
        with self._execution_lock:
            return self._execution_results.copy()
