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
from src.core.interfaces import IWebDriver
from src.core.exceptions import LoginFailedError

class TestNavigateAction(unittest.TestCase):
    def test_execute(self):
        driver = Mock(spec=IWebDriver)
        action = NavigateAction(url="https://example.com")
        action.execute(driver)
        driver.get.assert_called_once_with("https://example.com")

    def test_to_dict(self):
        action = NavigateAction(url="https://example.com")
        expected_dict = {"type": "Navigate", "url": "https://example.com"}
        self.assertEqual(action.to_dict(), expected_dict)

class TestClickAction(unittest.TestCase):
    def test_execute_success(self):
        driver = Mock(spec=IWebDriver)
        driver.is_element_present.side_effect = lambda selector: selector == "#dashboard-title"
        action = ClickAction(selector="#login-button", check_success_selector="#dashboard-title")
        action.execute(driver)
        driver.click_element.assert_called_once_with("#login-button")

    def test_execute_failure(self):
        driver = Mock(spec=IWebDriver)
        driver.is_element_present.side_effect = lambda selector: selector == "#login-error-message"
        action = ClickAction(selector="#login-button", check_success_selector="#dashboard-title", check_failure_selector="#login-error-message")
        with self.assertRaises(LoginFailedError):
            action.execute(driver)
        driver.click_element.assert_called_once_with("#login-button")

    def test_to_dict(self):
        action = ClickAction(selector="#login-button", check_success_selector="#dashboard-title", check_failure_selector="#login-error-message")
        expected_dict = {
            "type": "Click",
            "selector": "#login-button",
            "check_success_selector": "#dashboard-title",
            "check_failure_selector": "#login-error-message",
        }
        self.assertEqual(action.to_dict(), expected_dict)

class TestTypeAction(unittest.TestCase):
    def test_execute(self):
        driver = Mock(spec=IWebDriver)
        action = TypeAction(selector="#username-input", value_type="credential", value_key="example_login.username")
        with unittest.mock.patch("builtins.open", unittest.mock.mock_open(read_data='[{"name": "example_login", "username": "user@example.com", "password": "password123"}]')):
            action.execute(driver)
        driver.type_text.assert_called_once_with("#username-input", "user@example.com")

    def test_to_dict(self):
        action = TypeAction(selector="#username-input", value_type="credential", value_key="example_login.username")
        expected_dict = {
            "type": "Type",
            "selector": "#username-input",
            "value_type": "credential",
            "value_key": "example_login.username",
        }
        self.assertEqual(action.to_dict(), expected_dict)

class TestWaitAction(unittest.TestCase):
    def test_execute(self):
        driver = Mock(spec=IWebDriver)
        action = WaitAction(duration_seconds=3)
        with unittest.mock.patch("time.sleep", return_value=None) as mock_sleep:
            action.execute(driver)
        mock_sleep.assert_called_once_with(3)

    def test_to_dict(self):
        action = WaitAction(duration_seconds=3)
        expected_dict = {"type": "Wait", "duration_seconds": 3}
        self.assertEqual(action.to_dict(), expected_dict)

class TestScreenshotAction(unittest.TestCase):
    def test_execute(self):
        driver = Mock(spec=IWebDriver)
        action = ScreenshotAction(file_path="screenshot.png")
        action.execute(driver)
        driver.take_screenshot.assert_called_once_with("screenshot.png")

    def test_to_dict(self):
        action = ScreenshotAction(file_path="screenshot.png")
        expected_dict = {"type": "Screenshot", "file_path": "screenshot.png"}
        self.assertEqual(action.to_dict(), expected_dict)

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
