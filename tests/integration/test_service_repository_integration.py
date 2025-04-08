################################################################################
"""Integration tests for Application Services interacting with mocked Repositories."""

import unittest
from unittest.mock import MagicMock, patch, ANY

# Assuming correct paths for imports
from src.application.services import CredentialService, WorkflowService, WebDriverService, ReportingService, SchedulerService
from src.core.interfaces import ICredentialRepository, IWorkflowRepository, IWebDriver, IAction, IReportingRepository, ISchedulerService
from src.core.interfaces.service import IWebDriverService # For WebDriverService test
from src.infrastructure.webdrivers.factory import WebDriverFactory
from src.infrastructure.webdrivers.base import BrowserType
from src.core.exceptions import CredentialError, WorkflowError, RepositoryError, ValidationError, ActionError
from src.core.action_result import ActionResult

# Mock Action
class MockServiceIntAction(IAction):
    action_type = "MockSI"; name = "MockSIAction"
    def execute(self, d, cr=None, ctx=None): return ActionResult.success("OK")
    def to_dict(self): return {"type":self.action_type, "name":self.name}
    def validate(self): return True


# Mock werkzeug hashing functions for CredentialService tests
MOCK_HASH_PREFIX = "mock_hash_prefix:"
def mock_generate_hash(password, method, salt_length): return MOCK_HASH_PREFIX + password
def mock_check_hash(pwhash, password): return pwhash == MOCK_HASH_PREFIX + password

@patch('src.application.services.credential_service.generate_password_hash', side_effect=mock_generate_hash)
@patch('src.application.services.credential_service.check_password_hash', side_effect=mock_check_hash)
class TestServiceRepositoryIntegration(unittest.TestCase):
    """
    Tests interaction between Services and Repositories (using mocks for repositories).
    Verifies that services call the correct repository methods with expected data.
    """

    def setUp(self, mock_check, mock_generate): # Mocks passed by decorators
        """Set up mocked repositories and services."""
        self.mock_cred_repo = MagicMock(spec=ICredentialRepository)
        self.mock_wf_repo = MagicMock(spec=IWorkflowRepository)
        self.mock_webdriver_factory = MagicMock(spec=WebDriverFactory)
        self.mock_webdriver_service = MagicMock(spec=IWebDriverService)
        self.mock_reporting_service = MagicMock(spec=IReportingService) # Mock reporting service
        # Scheduler service doesn't interact with repos directly in these tests

        # Services under test, injected with mocks
        self.cred_service = CredentialService(self.mock_cred_repo)
        self.wd_service = WebDriverService(self.mock_webdriver_factory)
        # Inject mock reporting service into workflow service
        self.wf_service = WorkflowService(
            self.mock_wf_repo,
            self.mock_cred_repo,
            self.wd_service, # Inject real WD Service (which uses mocked factory)
            self.mock_reporting_service # Inject mocked reporting
        )
        # Store hash mocks if needed
        self.mock_generate_hash = mock_generate
        self.mock_check_hash = mock_check


    def tearDown(self, mock_check, mock_generate): # Mocks passed by decorators
        pass # No explicit teardown needed for mocks

    # --- Credential Service Tests ---
    def test_cred_service_create_calls_repo_save(self, mock_check, mock_generate):
        """Verify CredentialService.create_credential calls repo.save with hashed password."""
        name="t"; user="u"; pwd="p"; expected_hash = MOCK_HASH_PREFIX + pwd
        self.mock_cred_repo.get_by_name.return_value = None; self.mock_cred_repo.save.return_value = None
        self.cred_service.create_credential(name, user, pwd)
        self.mock_cred_repo.get_by_name.assert_called_once_with(name)
        self.mock_cred_repo.save.assert_called_once_with({"name": name, "username": user, "password": expected_hash})
        self.mock_generate_hash.assert_called_once()

    def test_cred_service_verify_calls_repo_get_and_checks_hash(self, mock_check, mock_generate):
        """Verify CredentialService.verify_credential calls repo.get_by_name and checks hash."""
        name="t"; pwd_correct="p"; stored_hash = MOCK_HASH_PREFIX + pwd_correct
        self.mock_cred_repo.get_by_name.return_value = {"name": name, "username": "u", "password": stored_hash}
        result_ok = self.cred_service.verify_credential(name, pwd_correct); self.assertTrue(result_ok)
        self.mock_cred_repo.get_by_name.assert_called_with(name) # Called multiple times potentially
        self.mock_check_hash.assert_called_with(stored_hash, pwd_correct)

    def test_cred_service_delete_calls_repo_delete(self, mock_check, mock_generate):
        """Verify CredentialService.delete_credential calls repo.delete."""
        name = "test_del"; self.mock_cred_repo.delete.return_value = True
        self.cred_service.delete_credential(name); self.mock_cred_repo.delete.assert_called_once_with(name)

    # --- Workflow Service Tests ---
    def test_wf_service_get_workflow_calls_repo_load(self, mock_check, mock_generate):
        """Verify WorkflowService.get_workflow calls repo.load."""
        name = "wf1"; mock_actions = [MockServiceIntAction()]
        self.mock_wf_repo.load.return_value = mock_actions
        actions = self.wf_service.get_workflow(name)
        self.assertEqual(actions, mock_actions); self.mock_wf_repo.load.assert_called_once_with(name)

    def test_wf_service_save_workflow_calls_repo_save(self, mock_check, mock_generate):
        """Verify WorkflowService.save_workflow calls repo.save."""
        name = "wf_save"; actions = [MockServiceIntAction()]
        self.mock_wf_repo.save.return_value = None
        self.wf_service.save_workflow(name, actions); self.mock_wf_repo.save.assert_called_once_with(name, actions)

    @patch('src.application.services.workflow_service.WorkflowRunner', autospec=True) # Patch runner used by service
    def test_wf_service_run_orchestration_and_logs(self, mock_runner_class, mock_check, mock_generate):
        """Verify WorkflowService.run_workflow orchestrates load, driver create/dispose, run, log save."""
        name = "wf_run"; cred_name = "c1"; browser = BrowserType.CHROME
        mock_actions = [MockServiceIntAction("A1")]
        mock_driver_instance = MagicMock(spec=IWebDriver)
        mock_runner_instance = mock_runner_class.return_value
        run_log_dict = {"workflow_name": name, "final_status": "SUCCESS", "action_results": [{"status":"success", "message":"OK"}],
                        "start_time_iso": "t1", "end_time_iso": "t2", "duration_seconds": 1.0, "error_message": None}
        mock_runner_instance.run.return_value = run_log_dict

        self.mock_wf_repo.load.return_value = mock_actions
        # Mock the *service* call now, not the factory directly
        self.mock_webdriver_service.create_web_driver.return_value = mock_driver_instance
        self.mock_webdriver_service.dispose_web_driver.return_value = True
        self.mock_reporting_service.save_execution_log.return_value = None

        result_log = self.wf_service.run_workflow(name, cred_name, browser, stop_event=None, log_callback=None)

        self.mock_wf_repo.load.assert_called_once_with(name)
        self.mock_webdriver_service.create_web_driver.assert_called_once_with(browser_type_str=browser.value)
        mock_runner_class.assert_called_once_with(mock_driver_instance, self.mock_cred_repo, self.mock_wf_repo, None) # Runner gets repos/driver/stop_event
        mock_runner_instance.run.assert_called_once_with(mock_actions, workflow_name=name)
        self.mock_webdriver_service.dispose_web_driver.assert_called_once_with(mock_driver_instance)
        self.mock_reporting_service.save_execution_log.assert_called_once_with(run_log_dict) # Verify log saved
        self.assertEqual(result_log, run_log_dict)


    # --- WebDriver Service Tests ---
    @patch('src.application.services.webdriver_service.config') # Mock config access
    def test_wd_service_create_calls_factory(self, mock_config, mock_check, mock_generate):
        """Verify WebDriverService.create_web_driver calls the factory with config."""
        mock_config.default_browser = 'firefox'; mock_config.implicit_wait = 7
        mock_config.get_driver_path.return_value = "/path/to/geckodriver"
        browser_str = "firefox"; browser_enum = BrowserType.FIREFOX
        mock_driver = MagicMock(spec=IWebDriver); self.mock_webdriver_factory.create_driver.return_value = mock_driver

        driver = self.wd_service.create_web_driver(browser_type_str=browser_str, implicit_wait_seconds=10) # Kwarg overrides config

        self.assertEqual(driver, mock_driver)
        self.mock_webdriver_factory.create_driver.assert_called_once_with(
            browser_type=browser_enum, driver_type="selenium", selenium_options=None,
            playwright_options=None, implicit_wait_seconds=10, webdriver_path="/path/to/geckodriver"
        )
        mock_config.get_driver_path.assert_called_once_with(browser_str)

    def test_wd_service_dispose_calls_driver_quit(self, mock_check, mock_generate):
        """Verify WebDriverService.dispose_web_driver calls driver.quit."""
        mock_driver = MagicMock(spec=IWebDriver)
        self.wd_service.dispose_web_driver(mock_driver); mock_driver.quit.assert_called_once()


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

################################################################################