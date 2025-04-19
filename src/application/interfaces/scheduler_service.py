"""Scheduler service interface for AutoQliq.

This module defines the interface for the scheduler service, which is responsible
for scheduling workflows to run at specific times or intervals.
"""

import abc
from typing import Dict, List, Any, Optional


class ISchedulerService(abc.ABC):
    """Interface for the scheduler service.
    
    This service is responsible for scheduling workflows to run at specific times
    or intervals, and for managing scheduled jobs.
    """
    
    @abc.abstractmethod
    def schedule_workflow(
        self,
        workflow_name: str,
        credential_name: Optional[str],
        schedule_config: Dict[str, Any]
    ) -> str:
        """Schedule a workflow to run according to the specified configuration.
        
        Args:
            workflow_name: The name of the workflow to schedule
            credential_name: The name of the credential to use (optional)
            schedule_config: Configuration for the schedule, including:
                - trigger: The type of trigger ('interval', 'cron', or 'date')
                - For interval triggers: seconds, minutes, hours, days, or weeks
                - For cron triggers: minute, hour, day, month, day_of_week
                - For date triggers: run_date
                
        Returns:
            The ID of the scheduled job
            
        Raises:
            ValueError: If the configuration is invalid
            ConfigError: If there's a problem with the configuration
            AutoQliqError: If there's a problem scheduling the workflow
        """
        pass
    
    @abc.abstractmethod
    def list_scheduled_jobs(self) -> List[Dict[str, Any]]:
        """Get a list of all scheduled jobs.
        
        Returns:
            A list of dictionaries containing job information:
                - id: The job ID
                - workflow_name: The name of the workflow
                - credential_name: The name of the credential (or None)
                - next_run_time: The next time the job will run
                - trigger: A string representation of the trigger
                
        Raises:
            AutoQliqError: If there's a problem retrieving the jobs
        """
        pass
    
    @abc.abstractmethod
    def cancel_scheduled_job(self, job_id: str) -> bool:
        """Cancel a scheduled job.
        
        Args:
            job_id: The ID of the job to cancel
            
        Returns:
            True if the job was canceled, False if it wasn't found
            
        Raises:
            AutoQliqError: If there's a problem canceling the job
        """
        pass
