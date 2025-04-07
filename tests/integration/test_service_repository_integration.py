"""Integration tests for Application Services interacting with mocked Repositories."""

import unittest
from unittest.mock import MagicMock, patch, ANY

# Assuming correct paths for imports
from src.application.services import CredentialService, WorkflowService, WebDriverService
from src.core.interfaces import ICredentialRepository, IWorkflowRepository, IWebDriver, IAction
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


class TestServiceRepositoryIntegration(unittest.TestCase):
    """
    Tests interaction between Services and Repositories (using mocks for repositories).
    Verifies that services call the correct repository methods.
    """

    def setUp(self):
        """Set up mocked repositories and services."""
        self.mock_cred_repo = MagicMock(spec=ICredentialRepository)
        self.mock_wf_repo = MagicMock(spec=IWorkflowRepository)
        self.mock_webdriver_factory = MagicMock(spec=WebDriverFactory) # Factory for WDService
        self.mock_webdriver_service = MagicMock(spec=IWebDriverService) # Service for WFService

        # Services under test, injected with mocks
        self.cred_service = CredentialService(self.mock_cred_repo)
        # Patch hashing functions for credential service tests
        self.hash_patcher = patch.dict('src.application.services.credential_service.__dict__', {
            'generate_password_hash': MagicMock(side_effect=lambda p, method, salt_length: f"hashed:{p}"),
            'check_password_hash': MagicMock(side_effect=lambda h, p: h == f"hashed:{p}")
        })
        self.hash_patcher.start()

        self.wd_service = WebDriverService(self.mock_webdriver_factory)
        self.wf_service = WorkflowService(self.mock_wf_repo, self.mock_cred_repo, self.wd_service) # Inject real WDService

    def tearDown(self):
        self.hash_patcher.stop()

    # --- Credential Service Tests ---
    def test_cred_service_create_calls_repo_save(self):
        """Verify CredentialService.create_credential calls repo.save with hashed password."""
        name, user, pwd = "test", "user", "pass"
        expected_hash = f"hashed:{pwd}"
        self.mock_cred_repo.get_by_name.return_value = None # Simulate not exists
        self.mock_cred_repo.save.return_value = None

        self.cred_service.create_credential(name, user, pwd)

        self.mock_cred_repo.get_by_name.assert_called_once_with(name)
        self.mock_cred_repo.save.assert_called_once_with({"name": name, "username": user, "password": expected_hash})

    def test_cred_service_verify_calls_repo_get_and_checks_hash(self):
        """Verify CredentialService.verify_credential calls repo.get_by_name and checks hash."""
        name, pwd_correct, pwd_wrong = "test", "pass", "wrong"
        stored_hash = f"hashed:{pwd_correct}"
        self.mock_cred_repo.get_by_name.return_value = {"name": name, "username": "u", "password": stored_hash}

        # Correct password
        result_ok = self.cred_service.verify_credential(name, pwd_correct)
        self.assertTrue(result_ok)
        self.mock_cred_repo.get_by_name.assert_called_once_with(name)
        # Check hash function was called by service
        self.assertTrue(any(call(stored_hash, pwd_correct) in self.cred_service.check_password_hash.call_args_list))


        # Wrong password
        self.mock_cred_repo.get_by_name.reset_mock() # Reset repo mock for next call
        result_fail = self.cred_service.verify_credential(name, pwd_wrong)
        self.assertFalse(result_fail)
        self.mock_cred_repo.get_by_name.assert_called_once_with(name)
        self.assertTrue(any(call(stored_hash, pwd_wrong) in self.cred_service.check_password_hash.call_args_list))


    def test_cred_service_delete_calls_repo_delete(self):
        """Verify CredentialService.delete_credential calls repo.delete."""
        name = "test_del"
        self.mock_cred_repo.delete.return_value = True
        self.cred_service.delete_credential(name)
        self.mock_cred_repo.delete.assert_called_once_with(name)

    # --- Workflow Service Tests ---
    def test_wf_service_get_workflow_calls_repo_load(self):
        """Verify WorkflowService.get_workflow calls repo.load."""
        name = "wf1"
        mock_actions = [MockServiceIntAction()]
        self.mock_wf_repo.load.return_value = mock_actions
        actions = self.wf_service.get_workflow(name)
        self.assertEqual(actions, mock_actions)
        self.mock_wf_repo.load.assert_called_once_with(name)

    def test_wf_service_save_workflow_calls_repo_save(self):
        """Verify WorkflowService.save_workflow calls repo.save."""
        name = "wf_save"; actions = [MockServiceIntAction()]
        self.mock_wf_repo.save.return_value = None
        self.wf_service.save_workflow(name, actions)
        self.mock_wf_repo.save.assert_called_once_with(name, actions)

    @patch('src.application.services.workflow_service.WorkflowRunner', autospec=True)
    def test_wf_service_run_calls_repo_load_and_runner(self, mock_runner_class):
        """Verify WorkflowService.run_workflow orchestrates load, driver creation, run, dispose."""
        name = "wf_run"; cred_name = "c1"; browser = BrowserType.CHROME
        mock_actions = [MockServiceIntAction("A1")]
        mock_driver_instance = MagicMock(spec=IWebDriver)
        mock_runner_instance = mock_runner_class.return_value
        mock_runner_instance.run.return_value = [ActionResult.success("OK")] # Runner returns list of ActionResult

        # Mock repo load and webdriver service create/dispose
        self.mock_wf_repo.load.return_value = mock_actions
        self.mock_webdriver_service.create_web_driver.return_value = mock_driver_instance
        self.mock_webdriver_service.dispose_web_driver.return_value = True

        # Call the service method
        result_dicts = self.wf_service.run_workflow(name, cred_name, browser)

        # Verify sequence
        self.mock_wf_repo.load.assert_called_once_with(name)
        self.mock_webdriver_service.create_web_driver.assert_called_once_with(browser_type_str=browser.value)
        mock_runner_class.assert_called_once_with(mock_driver_instance, self.mock_cred_repo) # Check runner init
        mock_runner_instance.run.assert_called_once_with(mock_actions, workflow_name=name) # Check runner run
        self.mock_webdriver_service.dispose_web_driver.assert_called_once_with(mock_driver_instance) # Check driver disposal

        # Check result format
        self.assertEqual(result_dicts, [{"status": "success", "message": "OK"}])


    # --- WebDriver Service Tests ---
    def test_wd_service_create_calls_factory(self):
        """Verify WebDriverService.create_web_driver calls the factory."""
        browser_str = "firefox"; browser_enum = BrowserType.FIREFOX
        mock_driver = MagicMock(spec=IWebDriver)
        self.mock_webdriver_factory.create_driver.return_value = mock_driver

        driver = self.wd_service.create_web_driver(browser_type_str=browser_str, implicit_wait_seconds=10)

        self.assertEqual(driver, mock_driver)
        self.mock_webdriver_factory.create_driver.assert_called_once_with(
            browser_type=browser_enum,
            driver_type="selenium", # Default
            selenium_options=None,
            playwright_options=None,
            implicit_wait_seconds=10, # Passed kwarg
            webdriver_path=None # Resolved from config (mocked as None here)
        )

    def test_wd_service_dispose_calls_driver_quit(self):
        """Verify WebDriverService.dispose_web_driver calls driver.quit."""
        mock_driver = MagicMock(spec=IWebDriver)
        self.wd_service.dispose_web_driver(mock_driver)
        mock_driver.quit.assert_called_once()


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)