"""Scheduler presenter implementation for AutoQliq."""

import logging
from typing import List, Dict, Any, Optional, Callable

# Core / Infrastructure
from src.core.exceptions import AutoQliqError, ConfigError

# Application services
from src.application.interfaces.workflow_service import IWorkflowService
from src.application.interfaces.scheduler_service import ISchedulerService
from src.application.interfaces.credential_service import ICredentialService

# UI interfaces
from src.ui.interfaces.presenter import ISchedulerPresenter
from src.ui.interfaces.view import ISchedulerView


class SchedulerPresenter(ISchedulerPresenter):
    """
    Presenter for the scheduler view. Handles the logic for scheduling workflows,
    listing scheduled jobs, and canceling jobs.
    """

    def __init__(
        self,
        scheduler_service: ISchedulerService,
        workflow_service: IWorkflowService,
        credential_service: ICredentialService
    ):
        """
        Initialize the scheduler presenter.

        Args:
            scheduler_service: Service for scheduling workflows.
            workflow_service: Service for accessing workflows.
            credential_service: Service for accessing credentials.
        """
        self.logger = logging.getLogger(__name__)
        self.scheduler_service = scheduler_service
        self.workflow_service = workflow_service
        self.credential_service = credential_service
        self.view: Optional[ISchedulerView] = None

    def set_view(self, view: ISchedulerView) -> None:
        """
        Set the view for this presenter.

        Args:
            view: The view to set.
        """
        self.view = view
        self._initialize_view()

    def _initialize_view(self) -> None:
        """Initialize the view with data."""
        if not self.view:
            return

        try:
            # Load workflows
            workflows = self.workflow_service.list_workflows()
            workflow_names = [wf.name for wf in workflows]
            self.view.set_workflow_list(workflow_names)

            # Load credentials
            credentials = self.credential_service.list_credentials()
            credential_names = [cred.name for cred in credentials]
            self.view.set_credential_list(credential_names)

            # Load scheduled jobs
            self.refresh_jobs()
        except Exception as e:
            self.logger.error(f"Failed to initialize scheduler view: {e}", exc_info=True)
            if self.view:
                self.view.display_error("Initialization Error", f"Failed to load data: {str(e)}")

    def refresh_jobs(self) -> None:
        """Refresh the list of scheduled jobs."""
        if not self.view:
            return

        try:
            jobs = self.scheduler_service.list_scheduled_jobs()
            self.view.set_job_list(jobs)
        except Exception as e:
            self.logger.error(f"Failed to refresh job list: {e}", exc_info=True)
            if self.view:
                self.view.display_error("Refresh Error", f"Failed to refresh job list: {str(e)}")

    def create_schedule(
        self, workflow_name: str, credential_name: Optional[str], schedule_config: Dict[str, Any]
    ) -> None:
        """
        Create a new schedule for a workflow.

        Args:
            workflow_name: Name of the workflow to schedule.
            credential_name: Name of the credential to use, or None.
            schedule_config: Configuration for the schedule.
        """
        if not self.view:
            return

        try:
            # Validate workflow exists
            workflows = self.workflow_service.list_workflows()
            workflow_names = [wf.name for wf in workflows]
            if workflow_name not in workflow_names:
                raise ValueError(f"Workflow '{workflow_name}' not found")

            # Validate credential exists if provided
            if credential_name:
                credentials = self.credential_service.list_credentials()
                credential_names = [cred.name for cred in credentials]
                if credential_name not in credential_names:
                    raise ValueError(f"Credential '{credential_name}' not found")

            # Create the schedule
            job_id = self.scheduler_service.schedule_workflow(
                workflow_name, credential_name, schedule_config
            )

            # Refresh the job list
            self.refresh_jobs()

            # Show success message
            if self.view:
                self.view.display_message(
                    "Schedule Created",
                    f"Successfully scheduled workflow '{workflow_name}' (Job ID: {job_id})"
                )
        except (ValueError, ConfigError) as e:
            self.logger.error(f"Invalid schedule configuration: {e}", exc_info=True)
            if self.view:
                self.view.display_error("Configuration Error", str(e))
        except Exception as e:
            self.logger.error(f"Failed to create schedule: {e}", exc_info=True)
            if self.view:
                self.view.display_error("Scheduling Error", f"Failed to create schedule: {str(e)}")

    def cancel_job(self, job_id: str) -> None:
        """
        Cancel a scheduled job.

        Args:
            job_id: ID of the job to cancel.
        """
        if not self.view:
            return

        try:
            success = self.scheduler_service.cancel_scheduled_job(job_id)
            if success:
                # Refresh the job list
                self.refresh_jobs()
                # Show success message
                if self.view:
                    self.view.display_message("Job Canceled", f"Successfully canceled job '{job_id}'")
            else:
                if self.view:
                    self.view.display_error("Job Not Found", f"Job '{job_id}' not found or already canceled")
        except Exception as e:
            self.logger.error(f"Failed to cancel job: {e}", exc_info=True)
            if self.view:
                self.view.display_error("Cancellation Error", f"Failed to cancel job: {str(e)}")
