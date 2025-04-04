import unittest
from unittest.mock import Mock
from src.core.actions import (
    NavigateAction,
    ClickAction,
    TypeAction,
    WaitAction,
    ScreenshotAction,
    ActionFactory,
)
from src.core.interfaces import IWebDriver, ICredentialRepository
from src.core.action_result import ActionResult

class TestNavigateAction(unittest.TestCase):
    def test_execute(self):
        driver = Mock(spec=IWebDriver)
        action = NavigateAction(url="https://example.com")
        result = action.execute(driver)
        driver.get.assert_called_once_with("https://example.com")
        self.assertTrue(result.is_success())

    def test_to_dict(self):
        action = NavigateAction(url="https://example.com")
        result = action.to_dict()
        self.assertEqual(result["type"], "Navigate")
        self.assertEqual(result["url"], "https://example.com")

class TestClickAction(unittest.TestCase):
    def test_execute_success(self):
        driver = Mock(spec=IWebDriver)
        driver.is_element_present.side_effect = lambda selector: selector == "#dashboard-title"
        action = ClickAction(selector="#login-button", check_success_selector="#dashboard-title")
        result = action.execute(driver)
        driver.click_element.assert_called_once_with("#login-button")
        self.assertTrue(result.is_success())

    def test_execute_failure(self):
        driver = Mock(spec=IWebDriver)
        driver.is_element_present.side_effect = lambda selector: selector == "#login-error-message"
        action = ClickAction(selector="#login-button", check_success_selector="#dashboard-title", check_failure_selector="#login-error-message")
        result = action.execute(driver)
        driver.click_element.assert_called_once_with("#login-button")
        self.assertFalse(result.is_success())
        self.assertEqual(result.message, "Login failed due to presence of failure element.")

    def test_to_dict(self):
        action = ClickAction(selector="#login-button", check_success_selector="#dashboard-title", check_failure_selector="#login-error-message")
        result = action.to_dict()
        self.assertEqual(result["type"], "Click")
        self.assertEqual(result["selector"], "#login-button")
        self.assertEqual(result["check_success_selector"], "#dashboard-title")
        self.assertEqual(result["check_failure_selector"], "#login-error-message")

class TestTypeAction(unittest.TestCase):
    def setUp(self):
        # Create a mock credential repository
        self.credential_repo = Mock(spec=ICredentialRepository)
        self.credential_repo.get_by_name.return_value = {
            "name": "example_login",
            "username": "user@example.com",
            "password": "password123"
        }

        # No need to set class-level credential repository anymore

    def test_execute(self):
        driver = Mock(spec=IWebDriver)
        action = TypeAction(selector="#username-input", value_type="credential", value_key="example_login.username", credential_repository=self.credential_repo)
        result = action.execute(driver)

        # Verify the credential repository was used
        self.credential_repo.get_by_name.assert_called_once_with("example_login")

        # Verify the driver was called with the correct parameters
        driver.type_text.assert_called_once_with("#username-input", "user@example.com")
        self.assertTrue(result.is_success())

    def test_to_dict(self):
        action = TypeAction(selector="#username-input", value_type="credential", value_key="example_login.username", credential_repository=self.credential_repo)
        result = action.to_dict()
        self.assertEqual(result["type"], "Type")
        self.assertEqual(result["selector"], "#username-input")
        self.assertEqual(result["value_type"], "credential")
        self.assertEqual(result["value_key"], "example_login.username")

class TestWaitAction(unittest.TestCase):
    def test_execute(self):
        driver = Mock(spec=IWebDriver)
        action = WaitAction(duration_seconds=3)
        with unittest.mock.patch("time.sleep", return_value=None) as mock_sleep:
            result = action.execute(driver)
        mock_sleep.assert_called_once_with(3)
        self.assertTrue(result.is_success())

    def test_to_dict(self):
        action = WaitAction(duration_seconds=3)
        result = action.to_dict()
        self.assertEqual(result["type"], "Wait")
        self.assertEqual(result["duration_seconds"], 3)

class TestScreenshotAction(unittest.TestCase):
    def test_execute(self):
        driver = Mock(spec=IWebDriver)
        action = ScreenshotAction(file_path="screenshot.png")
        result = action.execute(driver)
        driver.take_screenshot.assert_called_once_with("screenshot.png")
        self.assertTrue(result.is_success())

    def test_to_dict(self):
        action = ScreenshotAction(file_path="screenshot.png")
        result = action.to_dict()
        self.assertEqual(result["type"], "Screenshot")
        self.assertEqual(result["file_path"], "screenshot.png")

class TestActionFactory(unittest.TestCase):
    def test_create_action_navigate(self):
        action_data = {"type": "Navigate", "url": "https://example.com"}
        action = ActionFactory.create_action(action_data)
        self.assertIsInstance(action, NavigateAction)
        self.assertEqual(action.url, "https://example.com")

    def test_create_action_click(self):
        action_data = {
            "type": "Click",
            "selector": "#login-button",
            "check_success_selector": "#dashboard-title",
            "check_failure_selector": "#login-error-message",
        }
        action = ActionFactory.create_action(action_data)
        self.assertIsInstance(action, ClickAction)
        self.assertEqual(action.selector, "#login-button")
        self.assertEqual(action.check_success_selector, "#dashboard-title")
        self.assertEqual(action.check_failure_selector, "#login-error-message")

    def test_create_action_type(self):
        action_data = {
            "type": "Type",
            "selector": "#username-input",
            "value_type": "credential",
            "value_key": "example_login.username",
        }
        action = ActionFactory.create_action(action_data)
        self.assertIsInstance(action, TypeAction)
        self.assertEqual(action.selector, "#username-input")
        self.assertEqual(action.value_type, "credential")
        self.assertEqual(action.value_key, "example_login.username")

    def test_create_action_wait(self):
        action_data = {"type": "Wait", "duration_seconds": 3}
        action = ActionFactory.create_action(action_data)
        self.assertIsInstance(action, WaitAction)
        self.assertEqual(action.duration_seconds, 3)

    def test_create_action_screenshot(self):
        action_data = {"type": "Screenshot", "file_path": "screenshot.png"}
        action = ActionFactory.create_action(action_data)
        self.assertIsInstance(action, ScreenshotAction)
        self.assertEqual(action.file_path, "screenshot.png")

if __name__ == "__main__":
    unittest.main()
