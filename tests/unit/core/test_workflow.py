"""Unit tests for the WorkflowRunner."""

import unittest
from unittest.mock import MagicMock, call, ANY, patch
import threading # For stop event

# Assuming correct paths for imports
from src.core.workflow.runner import WorkflowRunner
from src.core.interfaces import IWebDriver, ICredentialRepository, IWorkflowRepository, IAction
from src.core.action_result import ActionResult, ActionStatus
from src.core.exceptions import WorkflowError, ActionError, RepositoryError, ValidationError, SerializationError
# Import action types used in tests
from src.core.actions.base import ActionBase
from src.core.actions.conditional_action import ConditionalAction
from src.core.actions.loop_action import LoopAction
from src.core.actions.error_handling_action import ErrorHandlingAction
from src.core.actions.template_action import TemplateAction
# Mock ActionFactory for template tests
# from src.core.actions.factory import ActionFactory # Not needed directly if mocking expander

# --- Mock Actions ---
class MockWFAction(ActionBase):
    action_type = "MockWF"
    def __init__(self, name="MockWFAction", succeed=True, msg="", raise_exc=None, delay=0):
        super().__init__(name); self.succeed = succeed; self.msg = msg; self.raise_exc = raise_exc; self.delay = delay
        self.execute = MagicMock(side_effect=self._mock_execute) # type: ignore
        self.validate = MagicMock(return_value=True)
    def _mock_execute(self, driver, credential_repo=None, context=None):
         if self.delay > 0: time.sleep(self.delay)
         stop_event = context.get('_stop_event_runner') if context else None # Check internal flag if needed
         if stop_event and stop_event.is_set(): raise WorkflowError("Stopped during action execute")
         if self.raise_exc: raise self.raise_exc
         if self.succeed: return ActionResult.success(self.msg or f"{self.name} OK")
         else: return ActionResult.failure(self.msg or f"{self.name} FAILED")
    def to_dict(self): return {"type":self.action_type, "name":self.name}

# --- Test Suite ---
class TestWorkflowRunner(unittest.TestCase):
    """Test suite for WorkflowRunner."""

    def setUp(self):
        """Set up mocks for each test."""
        self.mock_driver = MagicMock(spec=IWebDriver)
        self.mock_cred_repo = MagicMock(spec=ICredentialRepository)
        self.mock_wf_repo = MagicMock(spec=IWorkflowRepository)
        self.mock_stop_event = MagicMock(spec=threading.Event)
        self.mock_stop_event.is_set.return_value = False

        self.runner = WorkflowRunner(self.mock_driver, self.mock_cred_repo, self.mock_wf_repo, self.mock_stop_event)
        # Patch _execute_actions to track calls to it if needed for complex flow tests
        self.exec_actions_patcher = patch.object(self.runner, '_execute_actions', wraps=self.runner._execute_actions)
        self.mock_execute_actions = self.exec_actions_patcher.start()
        # Patch _expand_template for tests not focusing on it
        self.expand_template_patcher = patch.object(self.runner, '_expand_template', wraps=self.runner._expand_template)
        self.mock_expand_template = self.expand_template_patcher.start()


    def tearDown(self):
        self.exec_actions_patcher.stop()
        self.expand_template_patcher.stop()

    # --- Basic Execution Tests ---
    def test_run_success_returns_log_dict(self):
        """Test successful run returns a detailed log dictionary."""
        action1 = MockWFAction("Action1"); action2 = MockWFAction("Action2")
        actions = [action1, action2]; start_time = time.time()
        log_data = self.runner.run(actions, "SuccessWF")
        end_time = time.time()
        self.assertEqual(log_data['final_status'], "SUCCESS"); self.assertIsNone(log_data['error_message'])
        self.assertEqual(len(log_data['action_results']), 2)
        self.assertEqual(log_data['action_results'][0], {"status": "success", "message": "Action1 OK"})
        action1.execute.assert_called_once_with(self.mock_driver, self.mock_cred_repo, ANY)
        action2.execute.assert_called_once_with(self.mock_driver, self.mock_cred_repo, ANY)
        self.assertEqual(action1.execute.call_args[0][2], {}) # Check context
        self.assertEqual(action2.execute.call_args[0][2], {})

    def test_run_failure_returns_log_dict_and_raises(self):
        """Test failing run raises WorkflowError but returns log dict in finally block (if applicable)."""
        # Note: The current runner `run` method raises on failure, it doesn't return the log dict in that case.
        # The caller (WorkflowService) catches the exception and builds the final log.
        # This test verifies the exception is raised correctly.
        action1 = MockWFAction("Action1"); action2 = MockWFAction("Action2", succeed=False, msg="It failed")
        actions = [action1, action2]
        with self.assertRaises(WorkflowError) as cm: self.runner.run(actions, "FailureWF")
        self.assertIsInstance(cm.exception.__cause__, ActionError); self.assertIn("It failed", str(cm.exception.__cause__))
        action1.execute.assert_called_once(); action2.execute.assert_called_once()

    def test_run_exception_returns_log_dict_and_raises(self):
        """Test run with exception raises WorkflowError."""
        action1 = MockWFAction("Action1"); action2 = MockWFAction("Action2", raise_exc=ValueError("Action broke"))
        actions = [action1, action2]
        with self.assertRaises(WorkflowError) as cm: self.runner.run(actions, "ExceptionWF")
        self.assertIsInstance(cm.exception.__cause__, ActionError) # run_single_action wraps it
        self.assertIsInstance(cm.exception.__cause__.__cause__, ValueError)
        action1.execute.assert_called_once(); action2.execute.assert_called_once()

    # --- Context and Control Flow Tests ---
    def test_run_loop_passes_context(self):
         """Test context (loop vars) is passed correctly during loop execution."""
         inner_action = MockWFAction("Inner")
         loop_action = LoopAction(name="Loop3", count=2, loop_actions=[inner_action])
         # Mock LoopAction's execute to check context passed to _execute_actions
         loop_action.execute = MagicMock(wraps=loop_action.execute)

         self.runner.run([loop_action], "LoopContextWF")

         # Check _execute_actions was called inside the loop's execute
         # Need to inspect calls made *by* the real LoopAction.execute
         # This requires patching _execute_actions on the *runner instance* used inside LoopAction.
         # Simpler: Check the context received by the inner action's mock.
         self.assertEqual(inner_action.execute.call_count, 2)
         ctx1 = inner_action.execute.call_args_list[0][0][2]; self.assertEqual(ctx1, {'loop_index': 0, 'loop_iteration': 1, 'loop_total': 2})
         ctx2 = inner_action.execute.call_args_list[1][0][2]; self.assertEqual(ctx2, {'loop_index': 1, 'loop_iteration': 2, 'loop_total': 2})

    # --- Template Expansion Tests ---
    @patch('src.core.workflow.runner.ActionFactory', MagicMock()) # Mock factory within runner module
    def test_run_template_expansion(self, MockActionFactory):
         """Test runner expands TemplateAction using WorkflowRepository."""
         action1 = MockWFAction("Action1"); template_name = "my_tmpl"
         template_action = TemplateAction(name="UseTemplate", template_name=template_name)
         action3 = MockWFAction("Action3"); workflow_actions = [action1, template_action, action3]
         t_action1 = MockWFAction("TmplAct1"); t_action2 = MockWFAction("TmplAct2")
         template_data = [{"type":"MockWF", "name":"TmplAct1"}, {"type":"MockWF", "name":"TmplAct2"}]
         template_actions_objs = [t_action1, t_action2]
         self.mock_wf_repo.load_template.return_value = template_data
         MockActionFactory.create_action.side_effect = lambda data: MockWFAction(name=data['name'])

         log_data = self.runner.run(workflow_actions, "TemplateWF")

         self.mock_wf_repo.load_template.assert_called_once_with(template_name)
         MockActionFactory.create_action.assert_has_calls([call(template_data[0]), call(template_data[1])])
         # Verify execution order via mocks on action instances
         action1.execute.assert_called_once()
         t_action1.execute.assert_called_once()
         t_action2.execute.assert_called_once()
         action3.execute.assert_called_once()
         self.assertEqual(log_data['final_status'], "SUCCESS"); self.assertEqual(len(log_data['action_results']), 4)

    def test_run_template_load_fails(self):
         """Test runner fails workflow if template load fails."""
         template_name = "bad_tmpl"; action1 = MockWFAction("Action1")
         template_action = TemplateAction(name="UseBadTemplate", template_name=template_name)
         actions = [action1, template_action]
         repo_error = RepositoryError("Template not found"); self.mock_wf_repo.load_template.side_effect = repo_error

         with self.assertRaises(WorkflowError) as cm: self.runner.run(actions, "TemplateFailWF")
         self.assertIsInstance(cm.exception.__cause__, ActionError); self.assertIn("Template expansion failed", str(cm.exception.__cause__))
         self.assertIsInstance(cm.exception.__cause__.__cause__, RepositoryError)
         action1.execute.assert_called_once() # Action 1 ran

    # --- Stop Event Tests ---
    def test_run_checks_stop_event(self):
         """Test runner checks stop event before each action."""
         action1 = MockWFAction("Action1"); action2 = MockWFAction("Action2"); actions = [action1, action2]
         call_count = 0
         def stop_side_effect(): nonlocal call_count; call_count += 1; return call_count > 1
         self.mock_stop_event.is_set.side_effect = stop_side_effect

         with self.assertRaisesRegex(WorkflowError, "Stop requested"): self.runner.run(actions, "StopWF")
         self.assertEqual(self.mock_stop_event.is_set.call_count, 2); action1.execute.assert_called_once(); action2.execute.assert_not_called()

# Need time and timedelta for log dict checks
import time
from datetime import datetime, timedelta

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)