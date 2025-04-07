"""Unit tests for the core Action classes."""

import unittest
from unittest.mock import MagicMock, patch

# Assuming correct paths for imports
from src.core.actions.base import ActionBase
from src.core.actions.navigation import NavigateAction
from src.core.actions.interaction import ClickAction, TypeAction
from src.core.actions.utility import WaitAction, ScreenshotAction
from src.core.actions.conditional_action import ConditionalAction # Import for completeness check
from src.core.actions.loop_action import LoopAction # Import for completeness check
from src.core.actions.error_handling_action import ErrorHandlingAction # Import for completeness check
from src.core.actions.template_action import TemplateAction # Import for completeness check
from src.core.interfaces import IWebDriver, ICredentialRepository, IAction # Import IAction
from src.core.action_result import ActionResult, ActionStatus
from src.core.exceptions import ValidationError, CredentialError, WebDriverError, ActionError

# Mock IWebDriver for testing action execution
MockWebDriver = MagicMock(spec=IWebDriver)
# Mock ICredentialRepository for testing TypeAction
MockCredentialRepo = MagicMock(spec=ICredentialRepository)

class TestActionBase(unittest.TestCase):
    """Tests for the ActionBase abstract class."""

    def test_init_sets_name(self):
        """Test that name is set correctly."""
        class ConcreteAction(ActionBase):
            action_type = "Concrete"
            def execute(self, d, cr=None, ctx=None): return ActionResult.success()
            def to_dict(self): return {"type": "Concrete", "name": self.name}
        action1 = ConcreteAction(name="My Action"); self.assertEqual(action1.name, "My Action")
        action2 = ConcreteAction(); self.assertEqual(action2.name, "Concrete") # Defaults to action_type

    def test_init_invalid_name(self):
        """Test that invalid names raise errors or default."""
        class ConcreteAction(ActionBase):
            action_type = "Concrete"
            def execute(self, d, cr=None, ctx=None): return ActionResult.success()
            def to_dict(self): return {"type": "Concrete", "name": self.name}
        with self.assertLogs(level='WARNING') as log: action_empty = ConcreteAction(name="")
        self.assertEqual(action_empty.name, "Concrete"); self.assertIn("Invalid or empty name", log.output[0])
        with self.assertLogs(level='WARNING') as log: action_none = ConcreteAction(name=None)
        self.assertEqual(action_none.name, "Concrete")
        action_int_name = ConcreteAction(name=123) # type: ignore
        with self.assertRaisesRegex(ValidationError, "Action name must be a non-empty string"): action_int_name.validate()

    def test_base_validate_success(self):
        """Test the default validate method returns True for valid name."""
        class ConcreteAction(ActionBase):
            action_type = "Concrete"; def execute(self,d,c=None,x=None): pass; def to_dict(self): return{}
        action = ConcreteAction(name="ValidName"); self.assertTrue(action.validate())

    def test_base_to_dict_includes_type_and_name(self):
        """Test the base to_dict includes essential keys."""
        class ConcreteAction(ActionBase):
            action_type = "MyType"; def execute(self,d,c=None,x=None): pass; def to_dict(self): return super().to_dict()
        action = ConcreteAction(name="TestAction"); expected = {"type": "MyType", "name": "TestAction"}; self.assertEqual(action.to_dict(), expected)


class TestNavigateAction(unittest.TestCase):
    """Tests for NavigateAction."""
    def test_init_and_validate(self):
        action = NavigateAction(url="http://example.com"); self.assertTrue(action.validate())
        with self.assertRaises(ValidationError): NavigateAction(url="")
        with self.assertLogs(level='WARNING'): action_bad = NavigateAction(url="invalid"); self.assertTrue(action_bad.validate())

    def test_to_dict(self):
        action = NavigateAction(url="http://dict.com", name="Nav"); self.assertEqual(action.to_dict(), {"type": "Navigate", "name": "Nav", "url": "http://dict.com"})

    def test_execute_success(self):
        mock_driver = MagicMock(spec=IWebDriver); action = NavigateAction(url="http://ok.com")
        result = action.execute(mock_driver); mock_driver.get.assert_called_once_with("http://ok.com"); self.assertTrue(result.is_success())

    def test_execute_driver_error(self):
        mock_driver = MagicMock(spec=IWebDriver); mock_driver.get.side_effect = WebDriverError("Timeout")
        action = NavigateAction(url="http://fail.com"); result = action.execute(mock_driver)
        self.assertFalse(result.is_success()); self.assertIn("Timeout", result.message)


class TestClickAction(unittest.TestCase):
    """Tests for ClickAction."""
    def test_init_and_validate(self):
        action = ClickAction(selector="#btn"); self.assertTrue(action.validate())
        with self.assertRaises(ValidationError): ClickAction(selector="")

    def test_to_dict(self):
        action = ClickAction(selector="a.link", name="ClickLink"); self.assertEqual(action.to_dict(), {"type": "Click", "name": "ClickLink", "selector": "a.link"})

    def test_execute_success(self):
        mock_driver = MagicMock(spec=IWebDriver); action = ClickAction(selector="#submit")
        result = action.execute(mock_driver); mock_driver.click_element.assert_called_once_with("#submit"); self.assertTrue(result.is_success())

    def test_execute_driver_error(self):
        mock_driver = MagicMock(spec=IWebDriver); mock_driver.click_element.side_effect = WebDriverError("Not clickable")
        action = ClickAction(selector="#id"); result = action.execute(mock_driver)
        self.assertFalse(result.is_success()); self.assertIn("Not clickable", result.message)


class TestTypeAction(unittest.TestCase):
    """Tests for TypeAction."""
    def setUp(self): self.mock_cred_repo = MagicMock(spec=ICredentialRepository)
    def test_init_and_validate(self):
        TypeAction(selector="#id", value_key="k", value_type="text"); TypeAction(selector="#id", value_key="k.f", value_type="credential")
        with self.assertRaises(ValidationError): TypeAction(selector="", value_key="k", value_type="text")
        with self.assertRaises(ValidationError): TypeAction(selector="#id", value_key="k", value_type="bad")
        with self.assertRaises(ValidationError): TypeAction(selector="#id", value_key="", value_type="credential")
        with self.assertRaises(ValidationError): TypeAction(selector="#id", value_key="nokey", value_type="credential") # Format check

    def test_to_dict(self):
        a_txt = TypeAction("s", "k", "text", "N"); self.assertEqual(a_txt.to_dict(), {"type":"Type", "name":"N", "selector":"s", "value_key":"k", "value_type":"text"})
        a_cred = TypeAction("s", "k.f", "credential", "N"); self.assertEqual(a_cred.to_dict(), {"type":"Type", "name":"N", "selector":"s", "value_key":"k.f", "value_type":"credential"})

    def test_execute_text(self):
        mock_driver = MagicMock(spec=IWebDriver); action = TypeAction("#f", "hi", "text")
        result = action.execute(mock_driver); mock_driver.type_text.assert_called_once_with("#f", "hi"); self.assertTrue(result.is_success())

    def test_execute_credential_success(self):
        mock_driver = MagicMock(spec=IWebDriver); action = TypeAction("#p", "l.pwd", "credential")
        self.mock_cred_repo.get_by_name.return_value = {"name":"l", "username":"u", "password":"pw"}
        result = action.execute(mock_driver, self.mock_cred_repo)
        self.mock_cred_repo.get_by_name.assert_called_once_with("l"); mock_driver.type_text.assert_called_once_with("#p", "pw"); self.assertTrue(result.is_success())

    def test_execute_credential_repo_missing(self):
        mock_driver = MagicMock(spec=IWebDriver); action = TypeAction("#p", "l.pwd", "credential")
        result = action.execute(mock_driver, None); self.assertFalse(result.is_success()); self.assertIn("repo needed", result.message)

    def test_execute_credential_key_not_found(self):
        mock_driver = MagicMock(spec=IWebDriver); action = TypeAction("#p", "bad.pwd", "credential")
        self.mock_cred_repo.get_by_name.return_value = None
        result = action.execute(mock_driver, self.mock_cred_repo); self.assertFalse(result.is_success()); self.assertIn("not found", result.message)

    def test_execute_credential_field_not_found(self):
        mock_driver = MagicMock(spec=IWebDriver); action = TypeAction("#p", "l.bad", "credential")
        self.mock_cred_repo.get_by_name.return_value = {"name":"l", "username":"u", "password":"pw"}
        result = action.execute(mock_driver, self.mock_cred_repo); self.assertFalse(result.is_success()); self.assertIn("Field 'bad' not found", result.message)


class TestWaitAction(unittest.TestCase):
    """Tests for WaitAction."""
    @patch('time.sleep')
    def test_execute_success(self, mock_sleep):
        action = WaitAction(duration_seconds=0.5); result = action.execute(MagicMock())
        mock_sleep.assert_called_once_with(0.5); self.assertTrue(result.is_success())

    def test_init_and_validate(self):
        WaitAction(duration_seconds=1); WaitAction(duration_seconds=0.0)
        with self.assertRaises(ValidationError): WaitAction(duration_seconds=-1)
        with self.assertRaises(ValidationError): WaitAction(duration_seconds="a") # type: ignore


class TestScreenshotAction(unittest.TestCase):
    """Tests for ScreenshotAction."""
    @patch('os.path.exists', return_value=True)
    @patch('os.makedirs')
    def test_execute_success(self, mock_makedirs, mock_exists):
        mock_driver = MagicMock(spec=IWebDriver); action = ScreenshotAction("f.png")
        result = action.execute(mock_driver)
        mock_makedirs.assert_not_called(); mock_driver.take_screenshot.assert_called_once_with("f.png"); self.assertTrue(result.is_success())

    @patch('os.path.exists', return_value=False)
    @patch('os.makedirs')
    def test_execute_creates_dir(self, mock_makedirs, mock_exists):
        mock_driver = MagicMock(spec=IWebDriver); action = ScreenshotAction("d/f.png")
        result = action.execute(mock_driver)
        mock_makedirs.assert_called_once_with("d", exist_ok=True); mock_driver.take_screenshot.assert_called_once_with("d/f.png"); self.assertTrue(result.is_success())

    def test_init_and_validate(self):
        ScreenshotAction(file_path="a.png"); ScreenshotAction(file_path="/abs/path/b.png")
        with self.assertRaises(ValidationError): ScreenshotAction(file_path="")

# Add imports needed for new tests
import time
from datetime import datetime, timedelta, timezone
from src.core.actions.conditional_action import ConditionalAction
from src.core.actions.loop_action import LoopAction
from src.core.actions.error_handling_action import ErrorHandlingAction
from src.core.actions.template_action import TemplateAction

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)