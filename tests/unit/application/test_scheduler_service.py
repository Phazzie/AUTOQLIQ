"""Unit tests for the SchedulerService."""

import unittest
from unittest.mock import MagicMock, patch, ANY

# Assuming correct paths for imports
from src.application.services.scheduler_service import SchedulerService, APS_AVAILABLE, JobLookupError
from src.core.interfaces.service import IWorkflowService
from src.core.exceptions import AutoQliqError, WorkflowError
# Need BrowserType for checking run call
from src.infrastructure.webdrivers.base import BrowserType

# Conditionally skip tests if APScheduler is not installed
skip_if_aps_unavailable = unittest.skipUnless(APS_AVAILABLE, "APScheduler library not found, skipping scheduler tests.")

# Mock APScheduler classes only if available
if APS_AVAILABLE:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    from apscheduler.triggers.interval import IntervalTrigger
    from apscheduler.job import Job

@skip_if_aps_unavailable
class TestSchedulerService(unittest.TestCase):
    """Test suite for SchedulerService (when APScheduler is available)."""

    def setUp(self):
        """Set up mocks for each test."""
        self.mock_workflow_service = MagicMock(spec=IWorkflowService)

        # Patch the BackgroundScheduler within the service module
        self.scheduler_patcher = patch('src.application.services.scheduler_service.BackgroundScheduler', autospec=True)
        self.mock_scheduler_class = self.scheduler_patcher.start()
        self.mock_scheduler_instance = self.mock_scheduler_class.return_value

        # Create service instance, injecting the mocked workflow service
        self.service = SchedulerService(self.mock_workflow_service)

    def tearDown(self):
        """Clean up after tests."""
        self.scheduler_patcher.stop()

    def test_init_starts_scheduler(self):
        """Test that scheduler is initialized and started."""
        self.mock_scheduler_class.assert_called_once_with(jobstores=ANY, executors=ANY, job_defaults=ANY, timezone=ANY)
        self.mock_scheduler_instance.start.assert_called_once()

    @patch('src.application.services.scheduler_service.CronTrigger', autospec=True)
    def test_schedule_workflow_cron(self, mock_cron_trigger):
        """Test scheduling with a cron trigger."""
        wf_name="c_wf"; cred="c1"; cfg={'trigger':'cron','hour':'3','id':'j1'}; mock_job=MagicMock(spec=Job); mock_job.id='j1'
        self.mock_scheduler_instance.add_job.return_value = mock_job
        job_id = self.service.schedule_workflow(wf_name, cred, cfg)
        self.assertEqual(job_id, 'j1'); mock_cron_trigger.assert_called_once_with(hour='3')
        self.mock_scheduler_instance.add_job.assert_called_once()
        _, kwargs = self.mock_scheduler_instance.add_job.call_args
        self.assertEqual(kwargs['id'], 'j1'); self.assertEqual(kwargs['func'], self.service._run_scheduled_workflow); self.assertEqual(kwargs['args'], ['j1', wf_name, cred])

    @patch('src.application.services.scheduler_service.IntervalTrigger', autospec=True)
    def test_schedule_workflow_interval(self, mock_interval_trigger):
        """Test scheduling with an interval trigger."""
        wf_name="i_wf"; cred=None; cfg={'trigger':'interval','minutes':30}; mock_job=MagicMock(spec=Job); mock_job.id=f"wf_{wf_name}_123"
        self.mock_scheduler_instance.add_job.return_value = mock_job
        with patch('src.application.services.scheduler_service.time.time', return_value=123.0): job_id = self.service.schedule_workflow(wf_name, cred, cfg)
        self.assertTrue(job_id.startswith(f"wf_{wf_name}_")); mock_interval_trigger.assert_called_once_with(minutes=30)
        self.mock_scheduler_instance.add_job.assert_called_once()

    def test_schedule_workflow_invalid_trigger(self):
        """Test scheduling with an invalid trigger type raises error."""
        with self.assertRaisesRegex(AutoQliqError, "Unsupported trigger type"): self.service.schedule_workflow("wf", None, {'trigger': 'bad'})

    def test_list_scheduled_jobs(self):
        """Test listing scheduled jobs."""
        from datetime import datetime # Import locally for mock
        mock_job1 = MagicMock(spec=Job); mock_job1.id='j1'; mock_job1.name='N1'; mock_job1.next_run_time=datetime(2024,1,1); mock_job1.trigger=MagicMock(__str__=lambda s:'T1'); mock_job1.args=['j1','W1','C1']
        mock_job2 = MagicMock(spec=Job); mock_job2.id='j2'; mock_job2.name='N2'; mock_job2.next_run_time=None; mock_job2.trigger=MagicMock(__str__=lambda s:'T2'); mock_job2.args=['j2','W2', None]
        self.mock_scheduler_instance.get_jobs.return_value = [mock_job1, mock_job2]
        jobs = self.service.list_scheduled_jobs()
        self.assertEqual(len(jobs), 2); self.assertEqual(jobs[0]['id'], 'j1'); self.assertEqual(jobs[0]['workflow_name'], 'W1'); self.assertEqual(jobs[0]['credential_name'], 'C1')
        self.assertEqual(jobs[1]['id'], 'j2'); self.assertEqual(jobs[1]['workflow_name'], 'W2'); self.assertIsNone(jobs[1]['credential_name'])

    def test_cancel_scheduled_job_success(self):
        """Test cancelling an existing job."""
        job_id = "j_cancel"; self.mock_scheduler_instance.remove_job.return_value = None
        result = self.service.cancel_scheduled_job(job_id); self.assertTrue(result)
        self.mock_scheduler_instance.remove_job.assert_called_once_with(job_id)

    def test_cancel_scheduled_job_not_found(self):
        """Test cancelling a non-existent job."""
        job_id = "not_j"; self.mock_scheduler_instance.remove_job.side_effect = JobLookupError("Not found")
        result = self.service.cancel_scheduled_job(job_id); self.assertFalse(result)
        self.mock_scheduler_instance.remove_job.assert_called_once_with(job_id)

    @patch('src.application.services.scheduler_service.config') # Patch config import
    def test_internal_run_job_calls_workflow_service(self, mock_config):
         """Test the internal job function calls the injected workflow service."""
         mock_config.default_browser = 'chrome' # Mock config value
         job_id = "j1"; wf_name = "wf1"; cred_name = "c1"
         self.service._run_scheduled_workflow(job_id, wf_name, cred_name) # Call directly
         self.mock_workflow_service.run_workflow.assert_called_once()
         _, call_kwargs = self.mock_workflow_service.run_workflow.call_args
         self.assertEqual(call_kwargs.get('name'), wf_name); self.assertEqual(call_kwargs.get('credential_name'), cred_name)
         self.assertEqual(call_kwargs.get('browser_type'), BrowserType.CHROME) # Check browser from config mock

    def test_internal_run_job_handles_service_error(self):
         """Test the internal job function logs errors from workflow service."""
         job_id = "j_err"; wf_name = "wf_err"; cred_name = None
         self.mock_workflow_service.run_workflow.side_effect = WorkflowError("Run failed")
         logger_name = 'src.application.services.scheduler_service'
         with self.assertLogs(logger_name, level='ERROR') as log: self.service._run_scheduled_workflow(job_id, wf_name, cred_name)
         self.assertIn(f"Error running scheduled job '{job_id}'", log.output[0]); self.assertIn("Run failed", log.output[0])


if __name__ == '__main__':
    # Need to import datetime for mocking job list result if APS is available
    if APS_AVAILABLE: from datetime import datetime
    unittest.main(argv=['first-arg-is-ignored'], exit=False)