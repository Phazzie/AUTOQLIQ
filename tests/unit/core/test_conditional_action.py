"""Unit tests for the ConditionalAction."""

import unittest
from unittest.mock import MagicMock, call, ANY

# Assuming correct paths for imports
from src.core.actions.conditional_action import ConditionalAction
from src.core.interfaces import IWebDriver, IAction, ICredentialRepository
from src.core.action_result import ActionResult, ActionStatus
from src.core.exceptions import ValidationError, WebDriverError, ActionError
# Need runner for nested execution tests
from src.core.workflow.runner import WorkflowRunner

# Mock Actions for testing branches
class MockBranchAction(IAction):
    action_type = "MockBranch"
    def __init__(self, name="BranchAction", succeed=True, msg=""):
        self.name=name; self.succeed=succeed; self.msg=msg
        self.execute = MagicMock(side_effect=self._mock_execute) # type: ignore
        self.validate = MagicMock(return_value=True)
        self.get_nested_actions = MagicMock(return_value=[])
    def _mock_execute(self, driver, credential_repo=None, context=None):
         if self.succeed: return ActionResult.success(self.msg or f"{self.name} OK")
         else: return ActionResult.failure(self.msg or f"{self.name} FAILED")
    def to_dict(self): return {"type":self.action_type, "name":self.name}


class TestConditionalAction(unittest.TestCase):
    """Tests for ConditionalAction."""

    def setUp(self):
        """Set up mocks for each test."""
        self.mock_driver = MagicMock(spec=IWebDriver)
        self.mock_repo = MagicMock(spec=ICredentialRepository)
        # Mock runner used internally by ConditionalAction execute
        self.runner_patcher = patch('src.core.actions.conditional_action.WorkflowRunner', autospec=True)
        self.mock_runner_class = self.runner_patcher.start()
        self.mock_runner_instance = self.mock_runner_class.return_value
        # Simulate runner's _execute_actions succeeding by default
        self.mock_runner_instance._execute_actions.return_value = [ActionResult.success("Nested OK")]


    def tearDown(self):
        self.runner_patcher.stop()

    def test_init_validation(self):
        """Test initialization validation."""
        ConditionalAction(condition_type="element_present", selector="#id")
        ConditionalAction(condition_type="variable_equals", variable_name="v", expected_value="abc")
        ConditionalAction(condition_type="javascript_eval", script="return true;")
        with self.assertRaisesRegex(ValidationError, "Selector required"): ConditionalAction(condition_type="element_present", selector="")
        with self.assertRaisesRegex(ValidationError, "variable_name required"): ConditionalAction(condition_type="variable_equals", expected_value="a")
        with self.assertRaisesRegex(ValidationError, "'script' required"): ConditionalAction(condition_type="javascript_eval", script="")
        with self.assertRaisesRegex(ValidationError, "Unsupported condition_type"): ConditionalAction(condition_type="bad_type", selector="#id")

    def test_validate_nested_actions(self):
         """Test that validation checks nested actions."""
         valid_action = MockBranchAction(); invalid_action = MockBranchAction()
         invalid_action.validate = MagicMock(side_effect=ValidationError("Nested invalid"))
         action_ok = ConditionalAction(selector="#id", true_branch=[valid_action]); self.assertTrue(action_ok.validate())
         action_bad = ConditionalAction(selector="#id", true_branch=[invalid_action])
         with self.assertRaisesRegex(ValidationError, "Action 1 in true_branch failed validation"): action_bad.validate()

    def test_execute_true_branch_element(self):
        """Test execution when element_present condition is true."""
        true_action = MockBranchAction("True1"); false_action = MockBranchAction("False1")
        self.mock_driver.is_element_present.return_value = True
        action = ConditionalAction(condition_type="element_present", selector="#elem", true_branch=[true_action], false_branch=[false_action])
        test_context = {"id": 1}

        result = action.execute(self.mock_driver, self.mock_repo, test_context)

        self.assertTrue(result.is_success()); self.assertIn("'true' branch executed", result.message)
        self.mock_driver.is_element_present.assert_called_once_with("#elem")
        # Check runner's _execute_actions was called for the true branch
        self.mock_runner_instance._execute_actions.assert_called_once_with([true_action], test_context, action.name, ANY)


    def test_execute_false_branch_element(self):
        """Test execution when element_present condition is false."""
        true_action = MockBranchAction("True1"); false_action = MockBranchAction("False1")
        self.mock_driver.is_element_present.return_value = False
        action = ConditionalAction(condition_type="element_present", selector="#elem", true_branch=[true_action], false_branch=[false_action])

        result = action.execute(self.mock_driver, self.mock_repo)

        self.assertTrue(result.is_success()); self.assertIn("'false' branch executed", result.message)
        self.mock_driver.is_element_present.assert_called_once_with("#elem")
        self.mock_runner_instance._execute_actions.assert_called_once_with([false_action], {}, action.name, ANY)

    # --- Variable Condition Tests ---
    def test_execute_variable_equals_true(self):
        true_action = MockBranchAction("TrueVar")
        action = ConditionalAction(condition_type="variable_equals", variable_name="status", expected_value="completed", true_branch=[true_action])
        context = {"status": "completed"}
        result = action.execute(self.mock_driver, self.mock_repo, context)
        self.assertTrue(result.is_success())
        self.mock_runner_instance._execute_actions.assert_called_once_with([true_action], context, action.name, ANY)

    def test_execute_variable_equals_false(self):
        false_action = MockBranchAction("FalseVar")
        action = ConditionalAction(condition_type="variable_equals", variable_name="status", expected_value="completed", false_branch=[false_action])
        context = {"status": "pending"}
        result = action.execute(self.mock_driver, self.mock_repo, context)
        self.assertTrue(result.is_success())
        self.mock_runner_instance._execute_actions.assert_called_once_with([false_action], context, action.name, ANY)

    # --- JavaScript Condition Tests ---
    def test_execute_javascript_eval_true(self):
        true_action = MockBranchAction("TrueJS"); self.mock_driver.execute_script.return_value = True
        action = ConditionalAction(condition_type="javascript_eval", script="return 1;", true_branch=[true_action])
        result = action.execute(self.mock_driver, self.mock_repo)
        self.assertTrue(result.is_success()); self.mock_driver.execute_script.assert_called_once_with("return 1;")
        self.mock_runner_instance._execute_actions.assert_called_once_with([true_action], {}, action.name, ANY)

    def test_execute_javascript_eval_false(self):
        false_action = MockBranchAction("FalseJS"); self.mock_driver.execute_script.return_value = 0
        action = ConditionalAction(condition_type="javascript_eval", script="return 0;", false_branch=[false_action])
        result = action.execute(self.mock_driver, self.mock_repo)
        self.assertTrue(result.is_success()); self.mock_driver.execute_script.assert_called_once_with("return 0;")
        self.mock_runner_instance._execute_actions.assert_called_once_with([false_action], {}, action.name, ANY)

    def test_execute_javascript_eval_driver_error(self):
        self.mock_driver.execute_script.side_effect = WebDriverError("JS engine error")
        action = ConditionalAction(condition_type="javascript_eval", script="bad code;")
        result = action.execute(self.mock_driver, self.mock_repo)
        self.assertFalse(result.is_success()); self.assertIn("Conditional failed", result.message); self.assertIn("JS engine error", result.message)
        self.mock_runner_instance._execute_actions.assert_not_called() # Branch execution not reached

    # --- Failure Path Tests ---
    def test_execute_true_branch_action_fails(self):
        """Test failure when an action in the true branch fails (raises ActionError)."""
        true_action1 = MockBranchAction("True1")
        true_action2 = MockBranchAction("True2Fail")
        self.mock_driver.is_element_present.return_value = True
        # Simulate _execute_actions raising ActionError when executing true_branch
        nested_error = ActionError("Nested Fail", action_name="True2Fail")
        self.mock_runner_instance._execute_actions.side_effect = nested_error

        action = ConditionalAction(condition_type="element_present", selector="#elem", true_branch=[true_action1, true_action2])
        result = action.execute(self.mock_driver, self.mock_repo)

        self.assertFalse(result.is_success())
        self.assertIn("Conditional failed: Nested Fail", result.message)
        self.mock_runner_instance._execute_actions.assert_called_once_with([true_action1, true_action2], {}, action.name, ANY)


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)