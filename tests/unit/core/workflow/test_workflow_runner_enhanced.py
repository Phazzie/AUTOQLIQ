#!/usr/bin/env python3
"""
Enhanced unit tests for WorkflowRunner class in src/core/workflow/runner.py.
"""

import unittest
from unittest.mock import MagicMock, patch, call
import threading
import time
from typing import Dict, Any, List, Optional

# Import the module under test
from src.core.workflow.runner import WorkflowRunner
from src.core.interfaces import IWebDriver, IAction, ICredentialRepository, IWorkflowRepository
from src.core.action_result import ActionResult, ActionStatus
from src.core.exceptions import WorkflowError, ActionError, ValidationError
from src.core.actions.conditional_action import ConditionalAction
from src.core.actions.loop_action import LoopAction
from src.core.actions.error_handling_action import ErrorHandlingAction
from src.core.actions.template_action import TemplateAction


# Mock actions for testing
class MockAction(IAction):
    """Mock action for testing."""
    
    def __init__(self, name="MockAction", action_type="MockType", should_fail=False, 
                 validate_fails=False, should_raise=False, exception_type=None):
        """Initialize a mock action with configurable behavior."""
        self.name = name
        self.action_type = action_type
        self.should_fail = should_fail
        self.validate_fails = validate_fails
        self.should_raise = should_raise
        self.exception_type = exception_type or Exception
        
        # For tracking calls
        self.execute_called = False
        self.validate_called = False
        self.context_received = None
        
    def execute(self, driver, credential_repo=None, context=None):
        """Mock execution."""
        self.execute_called = True
        self.context_received = context
        
        if self.should_raise:
            raise self.exception_type(f"{self.name} raised test exception")
            
        if self.should_fail:
            return ActionResult.failure(f"{self.name} failed intentionally")
        
        return ActionResult.success(f"{self.name} succeeded")
    
    def validate(self):
        """Mock validation."""
        self.validate_called = True
        if self.validate_fails:
            raise ValidationError(f"Validation failed for {self.name}")
        return True
    
    def to_dict(self):
        """Mock serialization."""
        return {"type": self.action_type, "name": self.name}
    
    def get_nested_actions(self):
        """Mock getting nested actions."""
        return []


class TestWorkflowRunner(unittest.TestCase):
    """
    Test cases for the WorkflowRunner class to ensure it follows SOLID, KISS, and DRY principles.
    
    These tests cover the 7 main responsibilities of WorkflowRunner:
    1. Action execution management (running individual actions)
    2. Template expansion (for template actions)
    3. Handling control flow (conditionals, loops, error handlers)
    4. Context management during execution
    5. Stop event/cancellation handling
    6. Error handling and reporting
    7. Execution logging and result collection
    """
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mocks
        self.mock_driver = MagicMock(spec=IWebDriver)
        self.mock_credential_repo = MagicMock(spec=ICredentialRepository)
        self.mock_workflow_repo = MagicMock(spec=IWorkflowRepository)
        self.stop_event = threading.Event()
        
        # Create the runner
        self.runner = WorkflowRunner(
            driver=self.mock_driver,
            credential_repo=self.mock_credential_repo,
            workflow_repo=self.mock_workflow_repo,
            stop_event=self.stop_event
        )
    
    def test_init(self):
        """Test initialization."""
        # Test with valid parameters
        runner = WorkflowRunner(self.mock_driver)
        self.assertEqual(runner.driver, self.mock_driver)
        self.assertIsNone(runner.credential_repo)
        self.assertIsNone(runner.workflow_repo)
        self.assertIsNone(runner.stop_event)
        
        # Test with all parameters
        runner = WorkflowRunner(
            driver=self.mock_driver,
            credential_repo=self.mock_credential_repo,
            workflow_repo=self.mock_workflow_repo,
            stop_event=self.stop_event
        )
        self.assertEqual(runner.driver, self.mock_driver)
        self.assertEqual(runner.credential_repo, self.mock_credential_repo)
        self.assertEqual(runner.workflow_repo, self.mock_workflow_repo)
        self.assertEqual(runner.stop_event, self.stop_event)
        
        # Test with None driver (should raise)
        with self.assertRaises(ValueError):
            WorkflowRunner(driver=None)
    
    def test_run_single_action_success(self):
        """Test running a single action successfully."""
        # Create a mock action
        action = MockAction(name="TestAction")
        
        # Run the action
        result = self.runner.run_single_action(action, {})
        
        # Verify the action was executed
        self.assertTrue(action.execute_called)
        self.assertTrue(action.validate_called)
        self.assertTrue(result.is_success())
        self.assertEqual(result.message, "TestAction succeeded")
    
    def test_run_single_action_validation_failure(self):
        """Test running a single action with validation failure."""
        # Create a mock action that fails validation
        action = MockAction(name="TestAction", validate_fails=True)
        
        # Run the action
        result = self.runner.run_single_action(action, {})
        
        # Verify validation was called but execution was not
        self.assertTrue(action.validate_called)
        self.assertFalse(action.execute_called)
        self.assertFalse(result.is_success())
        self.assertIn("Validation failed", result.message)
    
    def test_run_single_action_execution_failure(self):
        """Test running a single action with execution failure."""
        # Create a mock action that fails execution
        action = MockAction(name="TestAction", should_fail=True)
        
        # Run the action
        result = self.runner.run_single_action(action, {})
        
        # Verify the action was executed but failed
        self.assertTrue(action.execute_called)
        self.assertTrue(action.validate_called)
        self.assertFalse(result.is_success())
        self.assertIn("failed intentionally", result.message)
    
    def test_run_single_action_exception(self):
        """Test running a single action that raises an exception."""
        # Create a mock action that raises an exception
        action = MockAction(name="TestAction", should_raise=True)
        
        # Run the action
        result = self.runner.run_single_action(action, {})
        
        # Verify the action was executed but failed
        self.assertTrue(action.validate_called)
        self.assertTrue(action.execute_called)
        self.assertFalse(result.is_success())
        self.assertIn("raised test exception", result.message)
    
    def test_run_single_action_with_stop_event(self):
        """Test running a single action with a stop event set."""
        # Create a mock action
        action = MockAction(name="TestAction")
        
        # Set the stop event
        self.stop_event.set()
        
        # Run the action - should raise WorkflowError
        with self.assertRaises(WorkflowError):
            self.runner.run_single_action(action, {})
        
        # Verify the action was not executed
        self.assertFalse(action.execute_called)
        self.assertFalse(action.validate_called)
        
        # Reset the stop event for other tests
        self.stop_event.clear()
    
    def test_run_with_empty_actions(self):
        """Test running a workflow with no actions."""
        # Run an empty workflow
        result = self.runner.run([], "EmptyWorkflow")
        
        # Verify the result
        self.assertEqual(result["workflow_name"], "EmptyWorkflow")
        self.assertEqual(result["final_status"], "SUCCESS")
        self.assertEqual(len(result["action_results"]), 0)
    
    def test_run_with_single_successful_action(self):
        """Test running a workflow with a single successful action."""
        # Create a mock action
        action = MockAction(name="TestAction")
        
        # Run the workflow
        result = self.runner.run([action], "SingleActionWorkflow")
        
        # Verify the result
        self.assertEqual(result["workflow_name"], "SingleActionWorkflow")
        self.assertEqual(result["final_status"], "SUCCESS")
        self.assertEqual(len(result["action_results"]), 1)
        self.assertEqual(result["action_results"][0]["status"], "SUCCESS")
    
    def test_run_with_failing_action(self):
        """Test running a workflow with a failing action."""
        # Create a mock action that fails
        action = MockAction(name="FailingAction", should_fail=True)
        
        # Run the workflow
        result = self.runner.run([action], "FailingWorkflow")
        
        # Verify the result
        self.assertEqual(result["workflow_name"], "FailingWorkflow")
        self.assertEqual(result["final_status"], "FAILED")
        self.assertIn("failed intentionally", result["error_message"])
        self.assertEqual(len(result["action_results"]), 0)  # No results because it failed
    
    def test_run_with_multiple_actions(self):
        """Test running a workflow with multiple actions."""
        # Create mock actions
        actions = [
            MockAction(name="Action1"),
            MockAction(name="Action2"),
            MockAction(name="Action3")
        ]
        
        # Run the workflow
        result = self.runner.run(actions, "MultiActionWorkflow")
        
        # Verify the result
        self.assertEqual(result["workflow_name"], "MultiActionWorkflow")
        self.assertEqual(result["final_status"], "SUCCESS")
        self.assertEqual(len(result["action_results"]), 3)
        for i, action_result in enumerate(result["action_results"]):
            self.assertEqual(action_result["status"], "SUCCESS")
            self.assertIn(f"Action{i+1}", action_result["message"])
    
    def test_expand_template(self):
        """Test template expansion."""
        # Create a mock template action
        template_action = MagicMock(spec=TemplateAction)
        template_action.name = "TestTemplate"
        template_action.template_name = "my_template"
        
        # Configure mock workflow repo to return template actions
        template_actions_data = [
            {"type": "MockType", "name": "TemplateAction1"},
            {"type": "MockType", "name": "TemplateAction2"}
        ]
        self.mock_workflow_repo.load_template.return_value = template_actions_data
        
        # Mock ActionFactory.create_action
        with patch('src.core.actions.factory.ActionFactory.create_action') as mock_create_action:
            # Configure mock to return MockAction instances
            mock_create_action.side_effect = lambda data: MockAction(
                name=data["name"], 
                action_type=data["type"]
            )
            
            # Expand the template
            expanded_actions = self.runner._expand_template(template_action, {})
            
            # Verify the result
            self.assertEqual(len(expanded_actions), 2)
            self.assertEqual(expanded_actions[0].name, "TemplateAction1")
            self.assertEqual(expanded_actions[1].name, "TemplateAction2")
            
            # Verify repo was called with correct template name
            self.mock_workflow_repo.load_template.assert_called_once_with("my_template")
    
    def test_expand_template_no_repo(self):
        """Test template expansion with no workflow repo."""
        # Create a runner without a workflow repo
        runner = WorkflowRunner(driver=self.mock_driver)
        
        # Create a mock template action
        template_action = MagicMock(spec=TemplateAction)
        template_action.name = "TestTemplate"
        template_action.template_name = "my_template"
        
        # Try to expand template - should raise ActionError
        with self.assertRaises(ActionError):
            runner._expand_template(template_action, {})
    
    def test_execute_conditional_true_branch(self):
        """Test executing a conditional action with true condition."""
        # Create mock actions for true branch
        true_actions = [MockAction(name="TrueAction1"), MockAction(name="TrueAction2")]
        
        # Create a mock conditional action that evaluates to True
        conditional = MagicMock(spec=ConditionalAction)
        conditional.name = "TestConditional"
        conditional.condition_type = "test_condition"
        conditional._evaluate_condition.return_value = True
        conditional.true_branch = true_actions
        conditional.false_branch = [MockAction(name="FalseAction")]
        
        # Execute the conditional
        result = self.runner._execute_conditional(conditional, {}, "TestWorkflow", "Test: ")
        
        # Verify the result
        self.assertTrue(result.is_success())
        self.assertIn("true executed", result.message)
        
        # Verify the true branch was evaluated
        conditional._evaluate_condition.assert_called_once()
        
        # Verify true actions were executed
        self.assertTrue(true_actions[0].execute_called)
        self.assertTrue(true_actions[1].execute_called)
    
    def test_execute_conditional_false_branch(self):
        """Test executing a conditional action with false condition."""
        # Create mock actions for false branch
        false_actions = [MockAction(name="FalseAction")]
        
        # Create a mock conditional action that evaluates to False
        conditional = MagicMock(spec=ConditionalAction)
        conditional.name = "TestConditional"
        conditional.condition_type = "test_condition"
        conditional._evaluate_condition.return_value = False
        conditional.true_branch = [MockAction(name="TrueAction")]
        conditional.false_branch = false_actions
        
        # Execute the conditional
        result = self.runner._execute_conditional(conditional, {}, "TestWorkflow", "Test: ")
        
        # Verify the result
        self.assertTrue(result.is_success())
        self.assertIn("false executed", result.message)
        
        # Verify the condition was evaluated
        conditional._evaluate_condition.assert_called_once()
        
        # Verify false actions were executed
        self.assertTrue(false_actions[0].execute_called)
    
    def test_execute_count_loop(self):
        """Test executing a count loop."""
        # Create mock actions for the loop
        loop_actions = [MockAction(name="LoopAction")]
        
        # Create a mock loop action
        loop = MagicMock(spec=LoopAction)
        loop.name = "TestLoop"
        loop.loop_type = "count"
        loop.count = 3
        loop.loop_actions = loop_actions
        
        # Execute the loop
        result = self.runner._execute_loop(loop, {}, "TestWorkflow", "Loop: ")
        
        # Verify the result
        self.assertTrue(result.is_success())
        self.assertIn("completed 3 iterations", result.message)
        
        # Verify action was executed 3 times
        self.assertEqual(loop_actions[0].execute_called, True)
        
        # Verify context was updated correctly for each iteration
        iterations_seen = set()
        for call_args in loop_actions[0].context_received.items():
            if call_args[0] == 'loop_iteration':
                iterations_seen.add(call_args[1])
        
        self.assertEqual(iterations_seen, {1, 2, 3})
    
    def test_execute_for_each_loop(self):
        """Test executing a for_each loop."""
        # Create mock actions for the loop
        loop_actions = [MockAction(name="LoopAction")]
        
        # Create a mock loop action
        loop = MagicMock(spec=LoopAction)
        loop.name = "TestLoop"
        loop.loop_type = "for_each"
        loop.list_variable_name = "test_list"
        loop.loop_actions = loop_actions
        
        # Execute the loop with a context containing the list
        context = {"test_list": ["item1", "item2", "item3"]}
        result = self.runner._execute_loop(loop, context, "TestWorkflow", "Loop: ")
        
        # Verify the result
        self.assertTrue(result.is_success())
        self.assertIn("completed 3 iterations", result.message)
        
        # Verify action was executed for each item
        self.assertEqual(loop_actions[0].execute_called, True)
        
        # Verify context was updated correctly for each iteration
        items_seen = set()
        for call_args in loop_actions[0].context_received.items():
            if call_args[0] == 'loop_item':
                items_seen.add(call_args[1])
        
        self.assertEqual(items_seen, {"item1", "item2", "item3"})
    
    def test_execute_while_loop(self):
        """Test executing a while loop."""
        # Create mock actions for the loop
        loop_actions = [MockAction(name="LoopAction")]
        
        # Create a mock loop action that stops after 3 iterations
        loop = MagicMock(spec=LoopAction)
        loop.name = "TestLoop"
        loop.loop_type = "while"
        loop.loop_actions = loop_actions
        
        # Configure _evaluate_while_condition to return True 3 times then False
        condition_results = [True, True, True, False]
        loop._evaluate_while_condition.side_effect = lambda driver, context: condition_results.pop(0)
        
        # Execute the loop
        result = self.runner._execute_loop(loop, {}, "TestWorkflow", "Loop: ")
        
        # Verify the result
        self.assertTrue(result.is_success())
        self.assertIn("completed 3 iterations", result.message)
        
        # Verify action was executed 3 times
        self.assertEqual(loop_actions[0].execute_called, True)
        
        # Verify condition was evaluated 4 times (3 True, 1 False)
        self.assertEqual(loop._evaluate_while_condition.call_count, 4)
    
    def test_execute_error_handler_try_succeeds(self):
        """Test executing error handler where try block succeeds."""
        # Create mock actions for try and catch blocks
        try_actions = [MockAction(name="TryAction")]
        catch_actions = [MockAction(name="CatchAction")]
        
        # Create a mock error handling action
        error_handler = MagicMock(spec=ErrorHandlingAction)
        error_handler.name = "TestErrorHandler"
        error_handler.try_actions = try_actions
        error_handler.catch_actions = catch_actions
        
        # Execute the error handler
        result = self.runner._execute_error_handler(error_handler, {}, "TestWorkflow", "ErrorHandler: ")
        
        # Verify the result
        self.assertTrue(result.is_success())
        self.assertIn("Try block succeeded", result.message)
        
        # Verify try actions were executed
        self.assertTrue(try_actions[0].execute_called)
        
        # Verify catch actions were not executed
        self.assertFalse(catch_actions[0].execute_called)
    
    def test_execute_error_handler_try_fails(self):
        """Test executing error handler where try block fails."""
        # Create mock actions for try and catch blocks
        try_actions = [MockAction(name="TryAction", should_fail=True)]
        catch_actions = [MockAction(name="CatchAction")]
        
        # Create a mock error handling action
        error_handler = MagicMock(spec=ErrorHandlingAction)
        error_handler.name = "TestErrorHandler"
        error_handler.try_actions = try_actions
        error_handler.catch_actions = catch_actions
        
        # Execute the error handler
        result = self.runner._execute_error_handler(error_handler, {}, "TestWorkflow", "ErrorHandler: ")
        
        # Verify the result
        self.assertTrue(result.is_success())
        self.assertIn("Error handled by 'catch'", result.message)
        
        # Verify try actions were executed
        self.assertTrue(try_actions[0].execute_called)
        
        # Verify catch actions were executed
        self.assertTrue(catch_actions[0].execute_called)
        
        # Verify error info was passed to catch block
        self.assertIn('try_block_error_message', catch_actions[0].context_received)
        self.assertIn('try_block_error_type', catch_actions[0].context_received)
    
    def test_execute_error_handler_try_fails_no_catch(self):
        """Test executing error handler where try block fails and there's no catch block."""
        # Create mock actions for try block
        try_actions = [MockAction(name="TryAction", should_fail=True)]
        
        # Create a mock error handling action without catch block
        error_handler = MagicMock(spec=ErrorHandlingAction)
        error_handler.name = "TestErrorHandler"
        error_handler.try_actions = try_actions
        error_handler.catch_actions = []
        
        # Execute the error handler - should raise ActionError
        with self.assertRaises(Exception):
            self.runner._execute_error_handler(error_handler, {}, "TestWorkflow", "ErrorHandler: ")
        
        # Verify try actions were executed
        self.assertTrue(try_actions[0].execute_called)
    
    def test_execute_actions_with_template(self):
        """Test that _execute_actions properly handles template expansion."""
        # Create a mock template action
        template_action = MagicMock(spec=TemplateAction)
        template_action.name = "TestTemplate"
        template_action.template_name = "my_template"
        
        # Create mock actions to be expanded from the template
        expanded_actions = [
            MockAction(name="ExpandedAction1"),
            MockAction(name="ExpandedAction2")
        ]
        
        # Patch _expand_template to return the expanded actions
        with patch.object(self.runner, '_expand_template', return_value=expanded_actions):
            # Execute actions with the template
            results = self.runner._execute_actions([template_action], {}, "TestWorkflow", "")
            
            # Verify _expand_template was called
            self.runner._expand_template.assert_called_once_with(template_action, {})
            
            # Verify expanded actions were executed
            self.assertTrue(expanded_actions[0].execute_called)
            self.assertTrue(expanded_actions[1].execute_called)
            
            # Verify results include all expanded actions
            self.assertEqual(len(results), 2)
    
    def test_run_with_stop_event(self):
        """Test that running a workflow respects the stop event."""
        # Create a mock action
        action = MockAction(name="TestAction")
        
        # Set the stop event
        self.stop_event.set()
        
        # Run the workflow
        result = self.runner.run([action], "StoppedWorkflow")
        
        # Verify the result
        self.assertEqual(result["workflow_name"], "StoppedWorkflow")
        self.assertEqual(result["final_status"], "STOPPED")
        self.assertIn("stopped by user request", result["error_message"])
        
        # Verify action was not executed
        self.assertFalse(action.execute_called)
        
        # Reset the stop event for other tests
        self.stop_event.clear()
    
    def test_context_passing(self):
        """Test that context is properly passed between actions."""
        # Create actions that modify and read context
        action1 = MockAction(name="ContextWriter")
        
        # Override execute to add to context
        original_execute = action1.execute
        def modified_execute(driver, credential_repo=None, context=None):
            context["test_value"] = "context_data"
            return original_execute(driver, credential_repo, context)
        action1.execute = modified_execute
        
        action2 = MockAction(name="ContextReader")
        
        # Run the workflow
        self.runner.run([action1, action2], "ContextWorkflow")
        
        # Verify action2 received the context from action1
        self.assertIn("test_value", action2.context_received)
        self.assertEqual(action2.context_received["test_value"], "context_data")
    
    def test_execution_log_format(self):
        """Test that the execution log has the expected format."""
        # Create a mock action
        action = MockAction(name="TestAction")
        
        # Run the workflow
        result = self.runner.run([action], "LogWorkflow")
        
        # Verify log structure
        self.assertIn("workflow_name", result)
        self.assertIn("start_time_iso", result)
        self.assertIn("end_time_iso", result)
        self.assertIn("duration_seconds", result)
        self.assertIn("final_status", result)
        self.assertIn("action_results", result)
        
        # Verify times and duration are correct
        self.assertLess(result["duration_seconds"], 1.0)  # Should be quick
        
        # Verify action results
        self.assertEqual(len(result["action_results"]), 1)
        self.assertEqual(result["action_results"][0]["status"], "SUCCESS")


if __name__ == '__main__':
    unittest.main()