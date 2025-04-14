"""Tests for refactored workflow runner."""

import unittest
from unittest.mock import MagicMock, patch, call
import threading
import time

from src.core.interfaces import IWebDriver, IAction, ICredentialRepository, IWorkflowRepository
from src.core.action_result import ActionResult
from src.core.exceptions import ActionError, WorkflowError
from src.core.actions.conditional_action import ConditionalAction
from src.core.actions.loop_action import LoopAction
from src.core.actions.error_handling_action import ErrorHandlingAction
from src.core.actions.template_action import TemplateAction
from src.core.workflow.runner import ErrorHandlingStrategy
from src.core.workflow.runner_refactored import WorkflowRunner


class TestWorkflowRunnerRefactored(unittest.TestCase):
    """Test cases for refactored workflow runner."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_driver = MagicMock(spec=IWebDriver)
        self.mock_credential_repo = MagicMock(spec=ICredentialRepository)
        self.mock_workflow_repo = MagicMock(spec=IWorkflowRepository)
        self.stop_event = threading.Event()
        
        # Create the runner
        self.runner = WorkflowRunner(
            self.mock_driver,
            self.mock_credential_repo,
            self.mock_workflow_repo,
            self.stop_event,
            ErrorHandlingStrategy.STOP_ON_ERROR
        )
        
        # Mock the components
        self.runner.action_executor = MagicMock()
        self.runner.action_executor.execute_action.return_value = ActionResult.success("Test success")
        
        self.runner.control_flow_handlers = {
            "conditional": MagicMock(),
            "loop": MagicMock(),
            "error_handling": MagicMock(),
            "template": MagicMock()
        }
        for handler in self.runner.control_flow_handlers.values():
            handler.handle.return_value = ActionResult.success("Test success")
        
        self.runner.result_processor = MagicMock()
        self.runner.result_processor.create_execution_log.return_value = {
            "workflow_name": "TestWorkflow",
            "final_status": "SUCCESS",
            "action_results": []
        }
        
        # Create test actions
        self.mock_action = MagicMock(spec=IAction)
        self.mock_action.name = "TestAction"
        self.mock_action.action_type = "test"
        
        self.mock_conditional = MagicMock(spec=ConditionalAction)
        self.mock_conditional.name = "TestConditional"
        self.mock_conditional.action_type = "conditional"
        
        self.mock_loop = MagicMock(spec=LoopAction)
        self.mock_loop.name = "TestLoop"
        self.mock_loop.action_type = "loop"
        
        self.mock_error_handling = MagicMock(spec=ErrorHandlingAction)
        self.mock_error_handling.name = "TestErrorHandling"
        self.mock_error_handling.action_type = "error_handling"
        
        self.mock_template = MagicMock(spec=TemplateAction)
        self.mock_template.name = "TestTemplate"
        self.mock_template.action_type = "template"

    def test_run_with_regular_actions(self):
        """Test running a workflow with regular actions."""
        actions = [self.mock_action, self.mock_action]
        
        result = self.runner.run(actions, "TestWorkflow")
        
        self.assertEqual(self.runner.action_executor.execute_action.call_count, 2)
        self.runner.result_processor.create_execution_log.assert_called_once()
        self.assertEqual(result["workflow_name"], "TestWorkflow")
        self.assertEqual(result["final_status"], "SUCCESS")

    def test_run_with_control_flow_actions(self):
        """Test running a workflow with control flow actions."""
        actions = [
            self.mock_conditional,
            self.mock_loop,
            self.mock_error_handling,
            self.mock_template
        ]
        
        result = self.runner.run(actions, "TestWorkflow")
        
        self.runner.control_flow_handlers["conditional"].handle.assert_called_once()
        self.runner.control_flow_handlers["loop"].handle.assert_called_once()
        self.runner.control_flow_handlers["error_handling"].handle.assert_called_once()
        self.runner.control_flow_handlers["template"].handle.assert_called_once()
        self.runner.result_processor.create_execution_log.assert_called_once()
        self.assertEqual(result["workflow_name"], "TestWorkflow")
        self.assertEqual(result["final_status"], "SUCCESS")

    def test_run_with_action_error(self):
        """Test running a workflow with an action that raises an error."""
        self.runner.action_executor.execute_action.side_effect = ActionError("Test error")
        
        actions = [self.mock_action]
        
        result = self.runner.run(actions, "TestWorkflow")
        
        self.runner.action_executor.execute_action.assert_called_once()
        self.runner.result_processor.create_execution_log.assert_called_once()
        self.assertEqual(result["workflow_name"], "TestWorkflow")
        self.assertEqual(result["final_status"], "SUCCESS")  # Mock returns SUCCESS

    def test_run_with_stop_event(self):
        """Test running a workflow with a stop event that is set."""
        self.stop_event.set()
        
        actions = [self.mock_action]
        
        result = self.runner.run(actions, "TestWorkflow")
        
        self.runner.action_executor.execute_action.assert_not_called()
        self.runner.result_processor.create_execution_log.assert_called_once()
        self.assertEqual(result["workflow_name"], "TestWorkflow")
        self.assertEqual(result["final_status"], "SUCCESS")  # Mock returns SUCCESS

    def test_run_with_invalid_actions(self):
        """Test running a workflow with invalid actions."""
        with self.assertRaises(TypeError):
            self.runner.run("not a list", "TestWorkflow")

    def test_execute_actions_with_regular_actions(self):
        """Test executing regular actions."""
        actions = [self.mock_action, self.mock_action]
        context = {"test_var": "test_value"}
        
        results = self.runner._execute_actions(actions, context, "TestWorkflow")
        
        self.assertEqual(len(results), 2)
        self.assertEqual(self.runner.action_executor.execute_action.call_count, 2)
        for result in results:
            self.assertTrue(result.is_success())

    def test_execute_actions_with_control_flow_actions(self):
        """Test executing control flow actions."""
        actions = [
            self.mock_conditional,
            self.mock_loop,
            self.mock_error_handling,
            self.mock_template
        ]
        context = {"test_var": "test_value"}
        
        results = self.runner._execute_actions(actions, context, "TestWorkflow")
        
        self.assertEqual(len(results), 4)
        self.runner.control_flow_handlers["conditional"].handle.assert_called_once()
        self.runner.control_flow_handlers["loop"].handle.assert_called_once()
        self.runner.control_flow_handlers["error_handling"].handle.assert_called_once()
        self.runner.control_flow_handlers["template"].handle.assert_called_once()
        for result in results:
            self.assertTrue(result.is_success())

    def test_execute_actions_with_stop_event(self):
        """Test executing actions with a stop event that is set."""
        self.stop_event.set()
        
        actions = [self.mock_action]
        context = {"test_var": "test_value"}
        
        with self.assertRaises(WorkflowError):
            self.runner._execute_actions(actions, context, "TestWorkflow")
        
        self.runner.action_executor.execute_action.assert_not_called()


if __name__ == "__main__":
    unittest.main()
