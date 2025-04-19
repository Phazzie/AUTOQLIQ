################################################################################
"""Scheduler service stub implementation for AutoQliq."""

import logging
import time # For job ID generation example
from typing import Dict, List, Any, Optional

# Core interfaces
from src.core.interfaces.service import ISchedulerService, IWorkflowService # Need IWorkflowService to run
from src.core.exceptions import AutoQliqError, ConfigError, WorkflowError # Use specific errors
# Need BrowserType for run call
from src.infrastructure.webdrivers.base import BrowserType

# External libraries (optional import)
try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    from apscheduler.triggers.interval import IntervalTrigger
    from apscheduler.jobstores.base import JobLookupError
    from apscheduler.jobstores.memory import MemoryJobStore
    # Add other stores like SQLAlchemyJobStore if needed
    APS_AVAILABLE = True
except ImportError:
    logging.getLogger(__name__).warning("APScheduler not found. Scheduling functionality disabled. Install using: pip install apscheduler")
    APS_AVAILABLE = False
    # Define dummy classes if not available
    class BackgroundScheduler: # type: ignore
        def add_job(self,*a,**kw): pass
        def get_jobs(self,*a,**kw): return []
        def remove_job(self,*a,**kw): raise JobLookupError()
        def start(self): pass
        def shutdown(self): pass
    class CronTrigger: pass # type: ignore
    class IntervalTrigger: pass # type: ignore
    class JobLookupError(Exception): pass # type: ignore
    class MemoryJobStore: pass # type: ignore

# Common utilities
from src.infrastructure.common.logging_utils import log_method_call
# Need WorkflowService instance to run jobs
# Ideally injected, but passed via method for now if needed? No, init.

logger = logging.getLogger(__name__)


class SchedulerService(ISchedulerService):
    """
    Basic implementation of ISchedulerService using APScheduler (if available).

    Manages scheduled workflow runs using a background scheduler.
    Requires WorkflowService instance to execute the actual workflows.
    Uses MemoryJobStore by default (jobs lost on restart).
    """

    def __init__(self, workflow_service: IWorkflowService):
        """Initialize the SchedulerService."""
        self.scheduler: Optional[BackgroundScheduler] = None
        if workflow_service is None:
             raise ValueError("WorkflowService instance is required for SchedulerService.")
        self.workflow_service = workflow_service # Store injected service

        if APS_AVAILABLE:
            try:
                # TODO: Configure persistent job store (e.g., SQLAlchemyJobStore) via config
                jobstores = {'default': MemoryJobStore()}
                executors = {'default': {'type': 'threadpool', 'max_workers': 5}} # Basic thread pool
                job_defaults = {'coalesce': False, 'max_instances': 1} # Prevent concurrent runs of same job

                self.scheduler = BackgroundScheduler( # type: ignore
                    jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone='UTC' # Or local timezone
                )
                self.scheduler.start()
                logger.info("SchedulerService initialized with APScheduler BackgroundScheduler.")
            except Exception as e:
                logger.error(f"Failed to initialize APScheduler: {e}. Scheduling disabled.", exc_info=True)
                self.scheduler = None
        else:
            logger.warning("SchedulerService initialized (APScheduler not available). Scheduling disabled.")

    def _run_scheduled_workflow(self, job_id: str, workflow_name: str, credential_name: Optional[str]):
         """Internal function called by the scheduler to run a workflow."""
         logger.info(f"SCHEDULER: Triggering run for job '{job_id}' (Workflow: {workflow_name})")
         try:
              # Use the injected WorkflowService instance
              from src.config import config # Import config locally if needed for browser type
              browser_type = BrowserType.from_string(config.default_browser)

              # WorkflowService.run_workflow handles its own logging and error reporting (via ReportingService)
              # It also handles its own exceptions internally now, returning a log dict.
              execution_log = self.workflow_service.run_workflow(
                   name=workflow_name,
                   credential_name=credential_name,
                   browser_type=browser_type
                   # Pass stop_event? Not applicable for scheduled runs.
                   # Pass log_callback? Could integrate with APScheduler logging.
              )
              # Log success/failure based on returned status
              final_status = execution_log.get("final_status", "UNKNOWN")
              logger.info(f"SCHEDULER: Scheduled job '{job_id}' completed with status: {final_status}")

         except Exception as e:
              # Log errors from the scheduled run prominently
              # This catches errors if run_workflow itself fails unexpectedly or raises something new
              logger.error(f"SCHEDULER: Error running scheduled job '{job_id}' for workflow '{workflow_name}': {e}", exc_info=True)
              # TODO: Add logic for handling repeated failures (e.g., disable job)


    @log_method_call(logger)
    def schedule_workflow(self, workflow_name: str, credential_name: Optional[str], schedule_config: Dict[str, Any]) -> str:
        """Schedule a workflow to run based on APScheduler trigger config."""
        if not self.scheduler: raise AutoQliqError("Scheduler not available or failed to initialize.")

        logger.info(f"Attempting schedule workflow '{workflow_name}' config: {schedule_config}")
        trigger = None
        # Use provided ID or generate one
        job_id = schedule_config.get("id", f"wf_{workflow_name}_{int(time.time())}")

        try:
            trigger_type = schedule_config.get("trigger", "interval")
            # Filter out non-trigger args before passing to trigger constructor
            trigger_args = {k:v for k,v in schedule_config.items() if k not in ['trigger', 'id', 'name']}

            # Convert numeric args from string if needed (APScheduler might handle this)
            for k, v in trigger_args.items():
                 if isinstance(v, str) and v.isdigit():
                      trigger_args[k] = int(v)
                 elif isinstance(v, str):
                      try: trigger_args[k] = float(v) # Try float for things like seconds
                      except ValueError: pass # Keep as string if not float

            if trigger_type == "cron": trigger = CronTrigger(**trigger_args)
            elif trigger_type == "interval": trigger = IntervalTrigger(**trigger_args)
            # Add 'date' trigger support if needed

            if trigger is None: raise ValueError(f"Unsupported trigger type: {trigger_type}")

            # Add the job - use self._run_scheduled_workflow as the target function
            added_job = self.scheduler.add_job(
                 func=self._run_scheduled_workflow,
                 trigger=trigger,
                 args=[job_id, workflow_name, credential_name], # Args passed to _run_scheduled_workflow
                 id=job_id,
                 name=schedule_config.get('name', f"Run '{workflow_name}' ({trigger_type})"),
                 replace_existing=True # Update if job with same ID exists
            )
            if added_job is None: # Should not happen with replace_existing=True unless error
                 raise AutoQliqError(f"Scheduler returned None for job '{job_id}'. Scheduling might have failed silently.")

            logger.info(f"Successfully scheduled job '{added_job.id}' for workflow '{workflow_name}'.")
            return added_job.id

        except (ValueError, TypeError) as e: # Catch errors creating trigger or converting args
             logger.error(f"Invalid schedule configuration for '{workflow_name}': {e}", exc_info=True)
             raise ConfigError(f"Invalid schedule config for '{workflow_name}': {e}", cause=e) from e
        except Exception as e: # Catch errors from scheduler.add_job
             logger.error(f"Failed schedule job for '{workflow_name}': {e}", exc_info=True)
             raise AutoQliqError(f"Failed schedule workflow '{workflow_name}': {e}", cause=e) from e


    @log_method_call(logger)
    def list_scheduled_jobs(self) -> List[Dict[str, Any]]:
        """List currently scheduled jobs from APScheduler."""
        if not self.scheduler: return []
        logger.debug("Listing scheduled jobs.")
        try:
            jobs = self.scheduler.get_jobs()
            job_list = []
            for job in jobs:
                 # Extract args safely
                 job_args = job.args if isinstance(job.args, (list, tuple)) else []
                 # Args passed were: [job_id, workflow_name, credential_name]
                 wf_name = job_args[1] if len(job_args) > 1 else "Unknown WF"
                 cred_name = job_args[2] if len(job_args) > 2 else None

                 job_list.append({
                      "id": job.id,
                      "name": job.name,
                      "workflow_name": wf_name, # Add workflow name from args
                      "credential_name": cred_name, # Add credential name from args
                      "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                      "trigger": str(job.trigger)
                 })
            return job_list
        except Exception as e:
             logger.error(f"Failed list scheduled jobs: {e}", exc_info=True)
             raise AutoQliqError(f"Failed list jobs: {e}", cause=e) from e


    @log_method_call(logger)
    def cancel_scheduled_job(self, job_id: str) -> bool:
        """Cancel a scheduled job by its ID using APScheduler."""
        if not self.scheduler: return False
        logger.info(f"Attempting cancel scheduled job '{job_id}'.")
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"Successfully cancelled scheduled job '{job_id}'.")
            return True
        except JobLookupError:
             logger.warning(f"Scheduled job ID '{job_id}' not found.")
             return False
        except Exception as e:
             logger.error(f"Failed cancel scheduled job '{job_id}': {e}", exc_info=True)
             raise AutoQliqError(f"Failed cancel job '{job_id}': {e}", cause=e) from e


    def shutdown(self):
        """Shutdown the scheduler."""
        if self.scheduler and hasattr(self.scheduler, 'running') and self.scheduler.running:
            try:
                 self.scheduler.shutdown()
                 logger.info("SchedulerService shut down.")
            except Exception as e: logger.error(f"Error shutting down scheduler: {e}", exc_info=True)
        else: logger.info("SchedulerService shutdown (scheduler not running or unavailable).")

################################################################################