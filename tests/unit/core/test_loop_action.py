"""Unit tests for the LoopAction."""

import unittest
from unittest.mock import MagicMock, call, ANY, patch

# Assuming correct paths for imports
from src.core.actions.loop_action import LoopAction
from src.core.interfaces import IWebDriver, IAction, ICredentialRepository
from src.core.action_result import ActionResult, ActionStatus
from src.core.exceptions import ValidationError, ActionError, WebDriverError

# Mock Actions for testing branches from conditional test can be reused
from tests.unit.core.test_conditional_action import MockBranchAction

class TestLoopAction(unittest.TestCase):
    """Tests for LoopAction."""

    def setUp(self):
        """Set up mocks for each test."""
        self.mock_driver = MagicMock(spec=IWebDriver)
        self.mock_repo = MagicMock(spec=ICredentialRepository)
        # Patch the internal helper to isolate testing of the main execute loop structure
        self.exec_nested_patcher = patch.object(LoopAction, '_execute_nested_block', return_value=None)
        self.mock_exec_nested_block = self.exec_nested_patcher.start()
        # Patch condition evaluator for while loops
        self.eval_while_patcher = patch.object(LoopAction, '_evaluate_while_condition')
        self.mock_eval_while_cond = self.eval_while_patcher.start()


    def tearDown(self):
        self.exec_nested_patcher.stop()
        self.eval_while_patcher.stop()

    def test_init_validation_count(self):
        LoopAction(loop_type="count", count=3, loop_actions=[MockBranchAction()])
        with self.assertRaises(ValidationError): LoopAction(loop_type="count")
        with self.assertRaises(ValidationError): LoopAction(loop_type="count", count=0)

    def test_init_validation_foreach(self):
        LoopAction(loop_type="for_each", list_variable_name="my_list", loop_actions=[MockBranchAction()])
        with self.assertRaises(ValidationError): LoopAction(loop_type="for_each")

    def test_init_validation_while(self):
         LoopAction(loop_type="while", condition_type="element_present", selector="#id")
         with self.assertRaises(ValidationError): LoopAction(loop_type="while")
         with self.assertRaises(ValidationError): LoopAction(loop_type="while", condition_type="element_present")

    def test_validate_nested_actions(self):
         invalid_action = MockBranchAction(); invalid_action.validate = MagicMock(side_effect=ValidationError("Nested invalid"))
         action_bad = LoopAction(loop_type="count", count=1, loop_actions=[invalid_action])
         with self.assertRaisesRegex(ValidationError, "Action 1 in loop_actions failed validation"): action_bad.validate()

    def test_execute_count_loop_success(self):
        """Test successful 'count' loop and context passing."""
        loop_count = 3; inner_action = MockBranchAction()
        action = LoopAction(loop_type="count", count=loop_count, loop_actions=[inner_action])
        parent_context = {"parent_var": "abc"}
        result = action.execute(self.mock_driver, self.mock_repo, parent_context)
        self.assertTrue(result.is_success()); self.assertIn(f"completed {loop_count} iterations", result.message)
        self.assertEqual(self.mock_exec_nested_block.call_count, loop_count)
        # Check context passed for first and last iteration
        ctx1 = self.mock_exec_nested_block.call_args_list[0][0][2]; self.assertEqual(ctx1, {'parent_var': 'abc', 'loop_index': 0, 'loop_iteration': 1, 'loop_total': 3})
        ctx_last = self.mock_exec_nested_block.call_args_list[-1][0][2]; self.assertEqual(ctx_last, {'parent_var': 'abc', 'loop_index': 2, 'loop_iteration': 3, 'loop_total': 3})

    def test_execute_count_loop_nested_failure(self):
        """Test loop stops if a nested action fails (raises ActionError)."""
        self.mock_exec_nested_block.side_effect = ActionError("Nested failed")
        action = LoopAction(loop_type="count", count=5, loop_actions=[MockBranchAction()])
        result = action.execute(self.mock_driver, self.mock_repo)
        self.assertFalse(result.is_success()); self.assertIn("Loop failed on iteration 1: Nested failed", result.message)
        self.mock_exec_nested_block.assert_called_once()

    def test_execute_foreach_loop_success(self):
        """Test successful 'for_each' loop and context passing."""
        list_var = "items"; items = ["apple", "banana"]
        action = LoopAction(loop_type="for_each", list_variable_name=list_var, loop_actions=[MockBranchAction()])
        parent_context = {list_var: items}
        result = action.execute(self.mock_driver, self.mock_repo, parent_context)
        self.assertTrue(result.is_success()); self.assertIn(f"completed {len(items)} iterations", result.message)
        self.assertEqual(self.mock_exec_nested_block.call_count, len(items))
        # Check context for items
        ctx1 = self.mock_exec_nested_block.call_args_list[0][0][2]; self.assertEqual(ctx1['loop_item'], 'apple')
        ctx2 = self.mock_exec_nested_block.call_args_list[1][0][2]; self.assertEqual(ctx2['loop_item'], 'banana')

    def test_execute_foreach_variable_not_list(self):
        """Test 'for_each' fails if context variable isn't a list."""
        action = LoopAction(loop_type="for_each", list_variable_name="my_var", loop_actions=[MockBranchAction()])
        result = action.execute(self.mock_driver, self.mock_repo, {"my_var": "string"})
        self.assertFalse(result.is_success()); self.assertIn("Context var 'my_var' not list", result.message)

    def test_execute_while_loop_success(self):
        """Test successful 'while' loop execution."""
        self.mock_eval_while_cond.side_effect = [True, True, False] # Condition true twice
        action = LoopAction(loop_type="while", condition_type="element_present", selector="#ok", loop_actions=[MockBranchAction()])
        result = action.execute(self.mock_driver, self.mock_repo, {"id":1})
        self.assertTrue(result.is_success()); self.assertIn("completed 2 iterations", result.message)
        self.assertEqual(self.mock_eval_while_cond.call_count, 3); self.assertEqual(self.mock_exec_nested_block.call_count, 2)
        # Check context passed to block
        ctx1 = self.mock_exec_nested_block.call_args_list[0][0][2]; self.assertEqual(ctx1, {'id': 1, 'loop_index': 0, 'loop_iteration': 1})
        ctx2 = self.mock_exec_nested_block.call_args_list[1][0][2]; self.assertEqual(ctx2, {'id': 1, 'loop_index': 1, 'loop_iteration': 2})

    def test_execute_while_condition_error(self):
        """Test 'while' loop fails if condition evaluation errors."""
        self.mock_eval_while_cond.side_effect = ActionError("Condition failed")
        action = LoopAction(loop_type="while", condition_type="javascript_eval", script="bad;", loop_actions=[MockBranchAction()])
        result = action.execute(self.mock_driver, self.mock_repo)
        self.assertFalse(result.is_success()); self.assertIn("Loop failed: Condition failed", result.message)

    def test_execute_while_loop_max_iterations(self):
        """Test 'while' loop stops after max iterations."""
        self.mock_eval_while_cond.return_value = True # Condition always true
        action = LoopAction(loop_type="while", condition_type="element_present", selector="#always", loop_actions=[MockBranchAction()])
        result = action.execute(self.mock_driver, self.mock_repo)
        self.assertFalse(result.is_success()); self.assertIn("exceeded max iterations", result.message)
        self.assertEqual(self.mock_exec_nested_block.call_count, 1000)

    @patch('src.core.actions.loop_action.serialize_actions')
    def test_to_dict_serialization(self, mock_serialize):
        """Test serialization includes type-specific params."""
        mock_serialize.return_value = []
        d_count = LoopAction(loop_type="count", count=5).to_dict(); self.assertEqual(d_count['count'], 5)
        d_each = LoopAction(loop_type="for_each", list_variable_name="items").to_dict(); self.assertEqual(d_each['list_variable_name'], 'items')
        d_while = LoopAction(loop_type="while", condition_type="variable_equals", variable_name="v", expected_value="k").to_dict()
        self.assertEqual(d_while['condition_type'], 'variable_equals'); self.assertEqual(d_while['variable_name'], 'v')

    def test_get_nested_actions(self):
        inner = MockBranchAction("Inner"); action = LoopAction(loop_type="count", count=1, loop_actions=[inner])
        self.assertEqual(action.get_nested_actions(), [inner])


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)