"""Unit tests for JavaScriptCondition action."""

import unittest
from unittest.mock import MagicMock, patch, call

from src.core.actions.javascript_condition import JavaScriptCondition
from src.core.interfaces import IWebDriver
from src.core.action_result import ActionResult, ActionStatus
from src.core.exceptions import ValidationError, WebDriverError

# Mock IWebDriver for testing action execution
MockWebDriver = MagicMock(spec=IWebDriver)

class TestJavaScriptCondition(unittest.TestCase):
    """Test cases for the JavaScriptCondition action."""

    def setUp(self):
        """Set up test environment."""
        self.mock_driver = MockWebDriver()
        self.mock_driver.execute_script.reset_mock()

    def test_init_success(self):
        """Test successful initialization."""
        action = JavaScriptCondition(name="TestJS", script="return true;")
        self.assertEqual(action.name, "TestJS")
        self.assertEqual(action.script, "return true;")
        self.assertEqual(action.action_type, "JavaScriptCondition")

    def test_init_missing_script(self):
        """Test initialization fails if script is missing."""
        with self.assertRaisesRegex(ValidationError, "'script' parameter is required"):
            JavaScriptCondition(name="TestJS", script=None)
        with self.assertRaisesRegex(ValidationError, "'script' parameter is required"):
            JavaScriptCondition(name="TestJS", script="")

    def test_validate_success(self):
        """Test successful validation."""
        action = JavaScriptCondition(name="TestJS", script="return context.value > 10;")
        self.assertTrue(action.validate())

    def test_validate_invalid_script(self):
        """Test validation fails with invalid script type."""
        action = JavaScriptCondition(name="TestJS", script=123) # type: ignore
        with self.assertRaisesRegex(ValidationError, "must be a non-empty string"):
            action.validate()

    def test_execute_success_true(self):
        """Test successful execution returning true."""
        self.mock_driver.execute_script.return_value = True
        action = JavaScriptCondition(name="TestJS", script="return arguments[0].x > 5;")
        context = {"x": 10}
        result = action.execute(self.mock_driver, context=context)

        self.assertTrue(result.is_success())
        self.assertEqual(result.status, ActionStatus.SUCCESS)
        self.assertEqual(result.message, "Script evaluated to True")
        self.assertEqual(result.data, True)
        self.mock_driver.execute_script.assert_called_once_with(
            "return (function(ctx) { return arguments[0].x > 5; })(arguments[0]);",
            context
        )

    def test_execute_success_false(self):
        """Test successful execution returning false."""
        self.mock_driver.execute_script.return_value = False
        action = JavaScriptCondition(name="TestJS", script="return arguments[0].x > 5;")
        context = {"x": 3}
        result = action.execute(self.mock_driver, context=context)

        self.assertTrue(result.is_success())
        self.assertEqual(result.status, ActionStatus.SUCCESS)
        self.assertEqual(result.message, "Script evaluated to False")
        self.assertEqual(result.data, False)
        self.mock_driver.execute_script.assert_called_once_with(
            "return (function(ctx) { return arguments[0].x > 5; })(arguments[0]);",
            context
        )

    def test_execute_no_context(self):
        """Test execution with no context provided."""
        self.mock_driver.execute_script.return_value = True
        action = JavaScriptCondition(name="TestJS", script="return true;")
        result = action.execute(self.mock_driver, context=None)

        self.assertTrue(result.is_success())
        self.assertEqual(result.data, True)
        self.mock_driver.execute_script.assert_called_once_with(
            "return (function(ctx) { return true; })(arguments[0]);",
            {}
        )

    def test_execute_script_returns_non_boolean(self):
        """Test execution fails if script doesn't return boolean."""
        self.mock_driver.execute_script.return_value = "not a boolean"
        action = JavaScriptCondition(name="TestJS", script="return 'oops';")
        result = action.execute(self.mock_driver)

        self.assertFalse(result.is_success())
        self.assertEqual(result.status, ActionStatus.FAILURE)
        self.assertIn("did not return a boolean value", result.message)
        self.assertIn("returned str", result.message)

    def test_execute_webdriver_error(self):
        """Test execution fails on WebDriverError."""
        error_message = "Browser crashed"
        self.mock_driver.execute_script.side_effect = WebDriverError(error_message)
        action = JavaScriptCondition(name="TestJS", script="return true;")
        result = action.execute(self.mock_driver)

        self.assertFalse(result.is_success())
        self.assertEqual(result.status, ActionStatus.FAILURE)
        self.assertIn("WebDriver error executing script", result.message)
        self.assertIn(error_message, result.message)

    def test_execute_javascript_syntax_error(self):
        """Test execution fails on JavaScript syntax/runtime error."""
        # WebDriver often raises a generic exception or WebDriverException for JS errors
        error_message = "SyntaxError: Unexpected token '{'"
        self.mock_driver.execute_script.side_effect = Exception(error_message)
        action = JavaScriptCondition(name="TestJS", script="return {;")
        result = action.execute(self.mock_driver)

        self.assertFalse(result.is_success())
        self.assertEqual(result.status, ActionStatus.FAILURE)
        self.assertIn("Error executing JavaScript", result.message)
        self.assertIn(error_message, result.message)

    def test_execute_validation_error(self):
        """Test execute fails if validation fails."""
        action = JavaScriptCondition(name="TestJS", script=None) # Invalid init
        # Need to bypass init validation to test execute validation
        action.script = None # type: ignore
        result = action.execute(self.mock_driver)

        self.assertFalse(result.is_success())
        self.assertEqual(result.status, ActionStatus.FAILURE)
        self.assertIn("Validation failed", result.message)
        self.assertIn("must be a non-empty string", result.message)

    def test_to_dict(self):
        """Test serialization to dictionary."""
        action = JavaScriptCondition(name="CheckValue", script="return ctx.val > 0;")
        expected_dict = {
            "type": "JavaScriptCondition",
            "name": "CheckValue",
            "script": "return ctx.val > 0;"
        }
        self.assertEqual(action.to_dict(), expected_dict)

    def test_repr(self):
        """Test the __repr__ method."""
        action = JavaScriptCondition(name="Test", script="short script")
        self.assertEqual(repr(action), "JavaScriptCondition(name='Test', script='short script...')")
        long_script = "a" * 100
        action_long = JavaScriptCondition(name="LongTest", script=long_script)
        self.assertEqual(repr(action_long), f"JavaScriptCondition(name='LongTest', script='{long_script[:50]}...')")


if __name__ == '__main__':
    unittest.main()

# STATUS: COMPLETE ✓
