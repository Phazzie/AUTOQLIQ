"""Unit tests for WhileLoopAction."""

import unittest
import threading
from unittest.mock import MagicMock, patch, call, ANY

# Core imports
from src.core.actions.base import ActionBase
from src.core.actions.while_loop_action import WhileLoopAction, MAX_WHILE_ITERATIONS
from src.core.actions.javascript_condition import JavaScriptCondition # Example condition
from src.core.interfaces import IWebDriver, IAction, ICredentialRepository
from src.core.action_result import ActionResult, ActionStatus
from src.core.exceptions import ValidationError, ActionError, WorkflowError

# Mock Interfaces
MockWebDriver = MagicMock(spec=IWebDriver)
MockCredentialRepo = MagicMock(spec=ICredentialRepository)

# Mock Action for loop body and condition
class MockLoopBodyAction(ActionBase):
    action_type = "MockLoopBody"
    def __init__(self, name="MockLoopBodyAction", succeed=True, msg="", raise_exc=None, data=None):
        super().__init__(name)
        self.succeed = succeed
        self.msg = msg
        self.raise_exc = raise_exc
        self.data = data
        self.execute_call_count = 0
        self.last_context = None

    def execute(self, driver, credential_repo=None, context=None):
        self.execute_call_count += 1
        self.last_context = context.copy() if context else None
        if self.raise_exc:
            raise self.raise_exc
        if self.succeed:
            return ActionResult.success(self.msg or f"{self.name} OK", data=self.data)
        else:
            return ActionResult.failure(self.msg or f"{self.name} FAILED", data=self.data)

    def to_dict(self): return {"type": self.action_type, "name": self.name}
    def validate(self): return True # Assume valid for tests

class MockConditionAction(MockLoopBodyAction):
     action_type = "MockCondition"
     # Inherits execute, but data should typically be boolean for conditions


class TestWhileLoopAction(unittest.TestCase):
    """Test cases for the WhileLoopAction."""

    def setUp(self):
        self.mock_driver = MockWebDriver()
        self.mock_repo = MockCredentialRepo()
        # Patch the WorkflowRunner used internally by WhileLoopAction.execute
        self.runner_patcher = patch('src.core.actions.while_loop_action.WorkflowRunner')
        self.MockWorkflowRunner = self.runner_patcher.start()
        self.mock_runner_instance = self.MockWorkflowRunner.return_value
        # Mock the _execute_actions method which is called internally
        self.mock_runner_instance._execute_actions.return_value = [ActionResult.success("Nested OK")]

    def tearDown(self):
        self.runner_patcher.stop()

    # --- Initialization and Validation Tests --- 

    def test_init_success(self):
        """Test successful initialization."""
        cond_action = MockConditionAction(name="Cond1")
        loop_action = MockLoopBodyAction(name="Loop1")
        action = WhileLoopAction(name="TestWhile", condition_action=cond_action, loop_actions=[loop_action], max_iterations=50)
        self.assertEqual(action.name, "TestWhile")
        self.assertEqual(action.condition_action, cond_action)
        self.assertEqual(action.loop_actions, [loop_action])
        self.assertEqual(action.max_iterations, 50)
        self.assertEqual(action.action_type, "WhileLoop")

    def test_init_missing_condition(self):
        """Test init fails if condition_action is missing or invalid."""
        with self.assertRaisesRegex(ValidationError, "'condition_action' parameter is required"):
            WhileLoopAction(name="Test", condition_action=None, loop_actions=[])
        with self.assertRaisesRegex(ValidationError, "must be a valid Action"):
            WhileLoopAction(name="Test", condition_action="not an action", loop_actions=[]) # type: ignore

    def test_init_invalid_loop_actions(self):
        """Test init fails if loop_actions is not a list or contains invalid items."""
        cond = MockConditionAction()
        with self.assertRaisesRegex(ValidationError, "must be a list"):
            WhileLoopAction(name="Test", condition_action=cond, loop_actions="not a list") # type: ignore
        with self.assertRaisesRegex(ValidationError, "must be valid Action objects"):
            WhileLoopAction(name="Test", condition_action=cond, loop_actions=[MockLoopBodyAction(), "not an action"]) # type: ignore

    def test_init_default_max_iterations(self):
        """Test max_iterations defaults correctly."""
        action = WhileLoopAction(name="Test", condition_action=MockConditionAction(), loop_actions=[])
        self.assertEqual(action.max_iterations, MAX_WHILE_ITERATIONS)
        action_invalid = WhileLoopAction(name="Test", condition_action=MockConditionAction(), loop_actions=[], max_iterations=-5)
        self.assertEqual(action_invalid.max_iterations, MAX_WHILE_ITERATIONS)

    def test_validate_success(self):
        """Test successful validation."""
        cond_action = MockConditionAction(name="Cond1")
        loop_action = MockLoopBodyAction(name="Loop1")
        action = WhileLoopAction(name="TestWhile", condition_action=cond_action, loop_actions=[loop_action])
        self.assertTrue(action.validate())

    def test_validate_invalid_condition_action(self):
        """Test validation fails if condition action is invalid or fails validation."""
        cond_action_invalid = MagicMock(spec=IAction)
        cond_action_invalid.validate.side_effect = ValidationError("Cond invalid")
        action = WhileLoopAction(name="Test", condition_action=cond_action_invalid, loop_actions=[])
        with self.assertRaisesRegex(ValidationError, "Validation failed for nested condition action"):
            action.validate()

    def test_validate_invalid_loop_action(self):
        """Test validation fails if a loop action is invalid or fails validation."""
        cond_action = MockConditionAction()
        loop_action_invalid = MagicMock(spec=IAction)
        loop_action_invalid.validate.side_effect = ValidationError("Loop invalid")
        action = WhileLoopAction(name="Test", condition_action=cond_action, loop_actions=[loop_action_invalid])
        with self.assertRaisesRegex(ValidationError, "Validation failed for nested loop action"):
            action.validate()

    # --- Execution Tests --- 

    def test_execute_condition_initially_false(self):
        """Test loop doesn't run if condition is false initially."""
        cond_action = MockConditionAction(name="CondFalse", succeed=True, data=False)
        loop_action = MockLoopBodyAction(name="LoopBody")
        action = WhileLoopAction(name="TestWhile", condition_action=cond_action, loop_actions=[loop_action])

        result = action.execute(self.mock_driver, self.mock_repo, context={})

        self.assertTrue(result.is_success())
        self.assertIn("Loop completed after 0 iterations", result.message)
        self.assertEqual(result.data, {'iterations_executed': 0})
        cond_action.execute.assert_called_once() # Condition checked once
        self.mock_runner_instance._execute_actions.assert_not_called() # Loop body not called

    def test_execute_runs_until_condition_false(self):
        """Test loop runs multiple times and stops when condition becomes false."""
        # Condition returns True twice, then False
        cond_action = MockConditionAction(name="CondToggle", succeed=True)
        cond_action.execute.side_effect = [
            ActionResult.success("Cond True", data=True),
            ActionResult.success("Cond True", data=True),
            ActionResult.success("Cond False", data=False)
        ]
        loop_action = MockLoopBodyAction(name="LoopBody")
        action = WhileLoopAction(name="TestWhile", condition_action=cond_action, loop_actions=[loop_action])

        result = action.execute(self.mock_driver, self.mock_repo, context={})

        self.assertTrue(result.is_success())
        self.assertIn("Loop completed after 2 iterations", result.message)
        self.assertEqual(result.data, {'iterations_executed': 2})
        self.assertEqual(cond_action.execute.call_count, 3) # Called 3 times (T, T, F)
        self.assertEqual(self.mock_runner_instance._execute_actions.call_count, 2) # Loop body called twice

        # Check context passed to loop body actions
        expected_calls = [
            call([loop_action], {'loop_index': 0, 'loop_iteration': 1}, workflow_name='TestWhile', log_prefix=ANY),
            call([loop_action], {'loop_index': 1, 'loop_iteration': 2}, workflow_name='TestWhile', log_prefix=ANY)
        ]
        self.mock_runner_instance._execute_actions.assert_has_calls(expected_calls)

    def test_execute_reaches_max_iterations(self):
        """Test loop stops and warns if max_iterations is reached."""
        max_iter = 3
        cond_action = MockConditionAction(name="CondAlwaysTrue", succeed=True, data=True)
        loop_action = MockLoopBodyAction(name="LoopBody")
        action = WhileLoopAction(name="TestWhileMax", condition_action=cond_action, loop_actions=[loop_action], max_iterations=max_iter)

        result = action.execute(self.mock_driver, self.mock_repo, context={})

        self.assertTrue(result.is_success()) # Still success, but with a warning message
        self.assertIn(f"Loop finished after reaching max {max_iter} iterations", result.message)
        self.assertEqual(result.data, {'iterations_executed': max_iter})
        self.assertEqual(cond_action.execute.call_count, max_iter) # Condition checked max_iter times
        self.assertEqual(self.mock_runner_instance._execute_actions.call_count, max_iter) # Loop body called max_iter times

    def test_execute_condition_action_fails(self):
        """Test loop fails if the condition action itself fails."""
        cond_action = MockConditionAction(name="CondFail", succeed=False, msg="Condition Error")
        loop_action = MockLoopBodyAction(name="LoopBody")
        action = WhileLoopAction(name="TestWhileCondFail", condition_action=cond_action, loop_actions=[loop_action])

        with self.assertRaisesRegex(ActionError, "Condition action 'CondFail' failed: Condition Error"):
            action.execute(self.mock_driver, self.mock_repo, context={})

        cond_action.execute.assert_called_once()
        self.mock_runner_instance._execute_actions.assert_not_called()

    def test_execute_condition_action_raises_exception(self):
        """Test loop fails if the condition action raises an exception."""
        cond_action = MockConditionAction(name="CondExcept", raise_exc=ValueError("Cond Boom"))
        loop_action = MockLoopBodyAction(name="LoopBody")
        action = WhileLoopAction(name="TestWhileCondExcept", condition_action=cond_action, loop_actions=[loop_action])

        with self.assertRaisesRegex(ActionError, "Error evaluating condition: Cond Boom"):
            action.execute(self.mock_driver, self.mock_repo, context={})

        cond_action.execute.assert_called_once()
        self.mock_runner_instance._execute_actions.assert_not_called()

    def test_execute_condition_returns_non_boolean(self):
        """Test loop fails if condition action returns non-boolean data."""
        cond_action = MockConditionAction(name="CondNonBool", succeed=True, data="not a bool")
        loop_action = MockLoopBodyAction(name="LoopBody")
        action = WhileLoopAction(name="TestWhileNonBool", condition_action=cond_action, loop_actions=[loop_action])

        with self.assertRaisesRegex(ActionError, "did not return a boolean result in its data field"):
            action.execute(self.mock_driver, self.mock_repo, context={})

        cond_action.execute.assert_called_once()
        self.mock_runner_instance._execute_actions.assert_not_called()

    def test_execute_loop_action_fails(self):
        """Test loop fails if an action inside the loop fails (using default STOP_ON_ERROR)."""
        cond_action = MockConditionAction(name="CondTrue", succeed=True, data=True)
        loop_action_fail = MockLoopBodyAction(name="LoopFail", succeed=False, msg="Loop Body Failed")
        action = WhileLoopAction(name="TestWhileLoopFail", condition_action=cond_action, loop_actions=[loop_action_fail])

        # Mock the internal runner's _execute_actions to raise ActionError
        self.mock_runner_instance._execute_actions.side_effect = ActionError("Nested action failed", action_name="LoopFail")

        with self.assertRaisesRegex(ActionError, "Nested action failed"):
            action.execute(self.mock_driver, self.mock_repo, context={})

        cond_action.execute.assert_called_once() # Condition checked once
        self.mock_runner_instance._execute_actions.assert_called_once() # Loop body attempted once

    def test_execute_loop_action_raises_exception(self):
        """Test loop fails if an action inside the loop raises an exception."""
        cond_action = MockConditionAction(name="CondTrue", succeed=True, data=True)
        loop_action_exc = MockLoopBodyAction(name="LoopExc", raise_exc=ValueError("Loop Boom"))
        action = WhileLoopAction(name="TestWhileLoopExc", condition_action=cond_action, loop_actions=[loop_action_exc])

        # Mock the internal runner's _execute_actions to raise the exception
        self.mock_runner_instance._execute_actions.side_effect = ActionError("Loop Boom", action_name="LoopExc", cause=ValueError("Loop Boom"))

        with self.assertRaisesRegex(ActionError, "Loop Boom"):
            action.execute(self.mock_driver, self.mock_repo, context={})

        cond_action.execute.assert_called_once()
        self.mock_runner_instance._execute_actions.assert_called_once()

    def test_execute_empty_loop_actions(self):
        """Test loop completes immediately if loop_actions is empty."""
        cond_action = MockConditionAction(name="CondTrue", succeed=True, data=True)
        action = WhileLoopAction(name="TestWhileEmpty", condition_action=cond_action, loop_actions=[])

        result = action.execute(self.mock_driver, self.mock_repo, context={})

        self.assertTrue(result.is_success())
        self.assertIn("Loop completed (no actions)", result.message)
        cond_action.execute.assert_not_called() # Condition shouldn't even be checked
        self.mock_runner_instance._execute_actions.assert_not_called()

    def test_execute_stop_event_triggered(self):
        """Test loop stops if stop event is set in context."""
        cond_action = MockConditionAction(name="CondTrue", succeed=True, data=True)
        loop_action = MockLoopBodyAction(name="LoopBody")
        action = WhileLoopAction(name="TestWhileStop", condition_action=cond_action, loop_actions=[loop_action])

        stop_event = threading.Event()
        context = {'_stop_event_runner': stop_event}

        # Simulate stop event being set after the first condition check
        def condition_side_effect(*args, **kwargs):
            if cond_action.execute.call_count == 1:
                return ActionResult.success("Cond True", data=True)
            else:
                # Should not get here if stop event works
                return ActionResult.success("Cond True", data=True)
        
        def check_stop_then_condition(*args, **kwargs):
            ctx = args[2] # context is the 3rd arg in _evaluate_condition call signature
            stop_ev = ctx.get('_stop_event_runner')
            if stop_ev and stop_ev.is_set():
                 raise WorkflowError("Stopped") # Simulate runner raising error
            # Set stop event after first successful condition eval
            if cond_action.execute.call_count == 1:
                 stop_event.set()
            return condition_side_effect(*args, **kwargs)

        cond_action.execute.side_effect = check_stop_then_condition

        with self.assertRaises(WorkflowError): # Expect WorkflowError due to stop
             action.execute(self.mock_driver, self.mock_repo, context=context)

        # Condition was evaluated once, loop body executed once, then stop checked before 2nd condition eval
        self.assertEqual(cond_action.execute.call_count, 1)
        self.assertEqual(self.mock_runner_instance._execute_actions.call_count, 1)

    # --- Serialization and Representation --- 

    def test_to_dict(self):
        """Test serialization to dictionary."""
        cond_action = MockConditionAction(name="Cond1")
        loop_action1 = MockLoopBodyAction(name="Loop1")
        loop_action2 = MockLoopBodyAction(name="Loop2")
        action = WhileLoopAction(name="SerializeWhile", condition_action=cond_action, loop_actions=[loop_action1, loop_action2], max_iterations=100)
        expected = {
            "type": "WhileLoop",
            "name": "SerializeWhile",
            "condition_action": {"type": "MockCondition", "name": "Cond1"},
            "loop_actions": [
                {"type": "MockLoopBody", "name": "Loop1"},
                {"type": "MockLoopBody", "name": "Loop2"}
            ],
            "max_iterations": 100
        }
        self.assertEqual(action.to_dict(), expected)

    def test_get_nested_actions(self):
        """Test retrieving nested actions."""
        cond_action = MockConditionAction(name="Cond1")
        loop_action1 = MockLoopBodyAction(name="Loop1")
        action = WhileLoopAction(name="NestedWhile", condition_action=cond_action, loop_actions=[loop_action1])
        nested = action.get_nested_actions()
        self.assertEqual(len(nested), 2)
        self.assertIn(cond_action, nested)
        self.assertIn(loop_action1, nested)

    def test_repr(self):
        """Test the __repr__ method."""
        cond_action = MockConditionAction(name="MyCond")
        loop_actions = [MockLoopBodyAction(), MockLoopBodyAction()]
        action = WhileLoopAction(name="ReprWhile", condition_action=cond_action, loop_actions=loop_actions, max_iterations=500)
        expected_repr = "WhileLoopAction(name='ReprWhile', condition=MyCond, actions=[2 actions], max_iter=500)"
        self.assertEqual(repr(action), expected_repr)

if __name__ == '__main__':
    unittest.main()

# STATUS: COMPLETE ✓
